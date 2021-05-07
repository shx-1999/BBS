from django.shortcuts import render, HttpResponse, redirect
from blog.CustomForms import custom_forms
from blog import models
from django.http import JsonResponse
from PIL import Image, ImageDraw, ImageFont  # 画图(验证码)
from io import BytesIO  # (存到内存操作)
from django.contrib import auth
from django.core.paginator import Paginator  # 分页
from django.db import transaction  # 事务s
from django.db.models import F
from django.contrib.auth.decorators import login_required  # auth登入认证装饰器
from bs4 import BeautifulSoup  # 处理html格式文件(使用其找到script标签并删除)防止xss攻击
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt  # 局部禁用csrf校验
import random
import json
import os


# 注册
def register(request):
    if request.method == "GET":
        register_form = custom_forms.RegisterForms()  # 向前端返回空forms对象
        user_queryset = models.User.objects.all()
        user_name_list = []  # 用来判断用户存不存在
        for user in user_queryset:
            user_name_list.append(user.username)
        return render(request, 'register.html', locals())
    if request.is_ajax():
        response = {'status': 100, "msg": None}  # 设置一个状态信息
        # 将数据传入forms组件得到forms对象,并校验
        register_form = custom_forms.RegisterForms(request.POST)
        if register_form.is_valid():
            # 校验通过,拿到校验后的数据及文件
            clean_data = register_form.cleaned_data
            my_file = request.FILES.get('myfile')
            # 对头像进行 有/无 判断
            if my_file:
                # 将文件添加到clean_data中的head字段中
                clean_data['head'] = my_file
            # 将数据中的re_password删除(不需要存)
            clean_data.pop('re_password')
            models.User.objects.create_user(**clean_data)
            # 自动创建站点
            username = request.POST.get('username')
            blog_obj = models.Blog.objects.create(site_name=username + '的站点', site_title=username + '的title',
                                                  site_style=username + '的样式')
            user_obj = models.User.objects.filter(username=username).first()
            user_obj.blog = blog_obj  # 将创建好的站点对向添加到对应的User中去
            user_obj.save()
            # 创建个默认分类
            category_obj = models.Categorys.objects.create(name='默认分类')
            category_obj.blog = blog_obj
            category_obj.save()
            # 默认标签
            # tag_obj = models.Tags.objects.create(name='默认标签')
            # tag_obj.blog = blog_obj
            # tag_obj.save()

            response['msg'] = '恭喜你,注册成功!'
            response['next_url'] = '/login/'
        else:
            response['status'] = 101
            response['msg'] = register_form.errors
        return JsonResponse(response)


# 生成随机验证码功能(手写 / 网上有封装好的)
# 1.生成随机3个数字(三原色),用来生成随机颜色(0~255)
def get_random():
    return random.randint(0, 150), random.randint(0, 150), random.randint(0, 150)


# 2.生成随机验证码图片
def get_valid_code(request):
    # 生成一张随机颜色的图片:(颜色格式,图片大小(宽高),三原色数值)
    # organ = Image.new('RGB', (250, 30), get_random())  # 随机图片颜色
    img = Image.new('RGB', (250, 28), (225, 225, 225))  # 图片颜色我固定(浅灰色)
    # 设置字体样式:((.ttf文件)文字格式文件,字体大小)
    img_font = ImageFont.truetype('./static/font/genkaimincho.ttf', 20)
    # 创建一个画板对象，将图片放到画板上
    img_draw = ImageDraw.Draw(img)
    # 随机生成5位验证码(小写字母，大写字母，和数字)
    code = ''
    for i in range(5):
        low_char = chr(random.randint(97, 122))
        up_char = chr(random.randint(65, 90))
        number_char = str(random.randint(0, 9))
        res = random.choice([low_char, up_char, number_char])
        code += res
        # 在画板上的图片上写字,一个一个写,方便控制间隙(x/y坐标,随机一个字符,颜色,字体样式)
        img_draw.text((20 + i * 40, 0), res, fill=get_random(), font=img_font)
    # 画点和线,用来干扰爬虫识别
    # 在图片大小范围内生成随机坐标
    width = 250
    height = 28
    for i in range(5):
        x1 = random.randint(0, width)
        x2 = random.randint(0, width)
        y1 = random.randint(0, height)
        y2 = random.randint(0, height)
        # 在图片上使用随机坐标画线(两点坐标,颜色)
        img_draw.line((x1, y1, x2, y2), fill=get_random())
    for i in range(20):
        # 画点
        img_draw.point([random.randint(0, width), random.randint(0, height)], fill=get_random())
        x = random.randint(0, width)
        y = random.randint(0, height)
        # 画弧形
        img_draw.arc((x, y, x + 4, y + 4), 0, 90, fill=get_random())
    # 将验证码存入session中
    request.session['code'] = code
    bytes_io = BytesIO()
    img.save(bytes_io, 'png')  # 将图片写入内存中,后面传的是图片格式
    return HttpResponse(bytes_io.getvalue())  # 把内容读出来


# 登入
def login_auth(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.is_ajax():
        response = {'status': 201, "msg": None}
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        # 判断用户输入的code是否和生成的一致
        if request.session.get('code').lower() == code.lower():
            user_obj = models.User.objects.filter(username=username).first()
            if user_obj:
                user = auth.authenticate(request, username=username, password=password)
                if user:
                    # 将用户信息存入session
                    auth.login(request, user)
                    response['msg'] = '登入成功!'
                    response['next_url'] = '/home/'
                    response['status'] = 200
                else:
                    response['msg'] = '密码验证失败!'
            else:
                response['msg'] = '未找到该用户!'
        else:
            response['msg'] = '验证码错误!'
        return JsonResponse(response)


# 首页展示
def home(request):
    if request.method == "GET":
        # 拿到所有文章(下面进行分页操作)
        article_list = models.Articles.objects.all().order_by('update_time').reverse()
        # 拿到最新八篇展示在侧边栏
        article8_list = models.Articles.objects.all().order_by('update_time').reverse()[:9]
        # 拿到最新评论八条展示在侧边栏
        comment8_list = models.Comment.objects.all().order_by('create_time').reverse()[:9]
        # 拿到5条标签做首页展示
        tag5_list = models.Tags.objects.all().order_by('id')[:6]
        # 拿到5条分类来做首页展示
        category5_list = models.Categorys.objects.all().order_by('id')[:6]

        # 首页所有文章进行分页(下面为分页代码模板)
        current_page = int(request.GET.get('page_num', 1))  # 获取用户点击的页码,没有则默认第一页
        paginator = Paginator(article_list, 4)  # 每页展示4条商品信息

        # 🔰2.页码列表
        # 如果分页后的总页数大于11
        if paginator.num_pages > 11:
            # 总共11页,取中间页(当前页)来判断是否是第1~11页
            if current_page - 5 < 1:
                # 1~11页码列表
                page_range = range(1, 12)
            # 取11页的中间页(当前页)判断是否是最后11页
            elif current_page + 5 > paginator.num_pages:
                # 最后11页页码列表
                page_range = range(paginator.num_pages - 10, paginator.num_pages + 1)
            else:
                # 如果不是前面11页,也不是后面11页,那么页码列表动态就会随着当前列表动态加减
                page_range = range(current_page - 5, current_page + 5)
        else:
            # 总页数小于11就直接全部显示
            page_range = paginator.page_range

        # 🔰3.page对象
        try:
            # 如果前端传过来的页码小于分页后的最小页码或者大于最大页码就会报错
            page = paginator.page(current_page)
        except Exception as E:
            current_page = 1  # 如果超出或小于我们就让其默认展示第一页
            page = paginator.page(current_page)

        return render(request, 'home.html', locals())


# 退出登入
def logout_func(request):
    auth.logout(request)  # 清除session
    return redirect('login_name')


# 个人站点展示
def personal_site(request, username, **kwargs):  # 还要接收condition和params,使用**
    user = models.User.objects.filter(username=username).first()
    if user:
        article_list = user.blog.articles_set.all()
        if kwargs:
            condition = kwargs.get('condition')
            params = kwargs.get('params')
            if condition == 'category':
                article_list = article_list.filter(categorys_id=params)  # 该id分类下的所有文章
            elif condition == 'tag':
                article_list = article_list.filter(tags__id=params)  # (跨表)该id标签下的所有文章
            elif condition == 'archive':
                params_year, params_month = params.split('/')  # 归档切出年/月
                article_list = article_list.filter(update_time__year=params_year, update_time__month=params_month)

        return render(request, 'site.html', locals())
    else:
        return render(request, '404cart.html')  # 找不到返回404页面


# 文章内容展示
def article_detail(request, username, id):
    username = username
    # 拿到该id的文章
    article = models.Articles.objects.filter(id=id).first()
    # 拿到该文章下点赞点踩的用户id,并判断当前用户是否点赞点踩了
    up_list = models.Articles.objects.filter(id=id).filter(upanddown__is_up=1).values('upanddown__user_id')
    down_list = models.Articles.objects.filter(id=id).filter(upanddown__is_up=0).values('upanddown__user_id')
    user_id = request.user.id
    # 默认图片灰色,如果已经点赞了,则返回亮色(激活状态)的图片
    img_url = '/static/img/upanddown/zan.png'
    img_url2 = '/static/img/upanddown/zan2.png'
    for i in up_list:
        if user_id == i['upanddown__user_id']:  # 用户以点赞
            img_url = '/static/img/upanddown/yizan.png'

    # 点踩了激活图片
    for ii in down_list:
        if user_id == ii['upanddown__user_id']:  # 用户已点踩
            img_url2 = '/static/img/upanddown/yizan2.png'

    # 拿到改文章下的所有评论
    comment_list = article.comment_set.all()
    return render(request, 'article.html', locals())


# 点赞点踩
def upanddown(request):
    if request.is_ajax():
        response = {'status': 100, 'msg': None}
        # 判断用户是否是登入状态
        if request.user.is_authenticated:
            # 拿出前端传来的文章id以及点赞还是点踩,转换成Python中的bool类型
            article_id = request.POST.get('article_id')
            is_up = json.loads(request.POST.get('is_up'))
            # 过滤出当前用户是否点过了这篇文章
            res = models.UpAndDown.objects.filter(articles_id=article_id, user=request.user)
            if res:
                response['status'] = 101
                response['msg'] = '已经点过了!'
                return JsonResponse(response)
            # django事务:要么都成功,要么都不成功
            with transaction.atomic():
                if is_up:
                    models.Articles.objects.filter(id=article_id).update(up_num=F('up_num') + 1)
                    response['msg'] = '点赞成功!😘'
                else:
                    models.Articles.objects.filter(id=article_id).update(down_num=F('down_num') + 1)
                    response['status'] = 102
                    response['msg'] = '点踩成功!😱'
                # 点赞点踩成功同时在赞踩表里也要存记录
                models.UpAndDown.objects.create(user=request.user, articles_id=article_id, is_up=is_up)
            return JsonResponse(response)
        else:
            response['status'] = 103
            response['msg'] = '请客官先去登入!'
            return JsonResponse(response)


# 文章评论
def comment(request):
    # 敏感字段
    li = ['sb', '傻逼', '艹', '你妈', '妈的', 'fuck', 'shit']
    if request.is_ajax():
        response = {'status': 100, 'msg': '评论成功'}
        article_id = request.POST.get('article_id')
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        # 替换敏感字段
        for word in li:
            if word not in content.lower(): break
            while 1:
                res = content.lower()
                index = res.find(word)
                if index == -1: break
                res_word = content[index:index + len(word)]
                content = content.replace(res_word, '**(请文明用语)**')
        # 添加品论并将文章评论数加1
        res = models.Comment.objects.create(user=request.user, articles_id=article_id, content=content,
                                            comment_id_id=parent_id)
        models.Articles.objects.filter(id=article_id).update(comment_num=F('comment_num') + 1)
        response['username'] = request.user.username
        response['res_content'] = res.content
        if parent_id:
            response['parent_name'] = res.comment_id.user.username
            response['parent_content'] = res.comment_id.content
        return JsonResponse(response)


# 后台管理
@login_required(login_url='/login/')
def backend(request):
    article_list = models.Articles.objects.filter(blog=request.user.blog)
    # 后台所有文章进行分页(下面分页代码模板)
    current_page = int(request.GET.get('page_num', 1))  # 获取用户点击的页码,没有则默认第一页
    paginator = Paginator(article_list, 7)  # 每页展示7条商品信息

    # 🔰2.页码列表
    # 如果分页后的总页数大于11
    if paginator.num_pages > 11:
        # 总共11页,取中间页(当前页)来判断是否是第1~11页
        if current_page - 5 < 1:
            # 1~11页码列表
            page_range = range(1, 12)
        # 取11页的中间页(当前页)判断是否是最后11页
        elif current_page + 5 > paginator.num_pages:
            # 最后11页页码列表
            page_range = range(paginator.num_pages - 10, paginator.num_pages + 1)
        else:
            # 如果不是前面11页,也不是后面11页,那么页码列表动态就会随着当前列表动态加减
            page_range = range(current_page - 5, current_page + 5)
    else:
        # 总页数小于11就直接全部显示
        page_range = paginator.page_range

    # 🔰3.page对象
    try:
        # 如果前端传过来的页码小于分页后的最小页码或者大于最大页码就会报错
        page = paginator.page(current_page)
    except Exception as E:
        current_page = 1  # 如果超出或小于我们就让其默认展示第一页
        page = paginator.page(current_page)
    return render(request, 'backend/backend_index.html', locals())


# 新增文章
@login_required(login_url='/login/')
def add_article(request):
    if request.method == 'GET':
        category_list = models.Categorys.objects.filter(blog=request.user.blog)
        tag_list = models.Tags.objects.filter(blog=request.user.blog)
        return render(request, 'backend/add_article.html', locals())
    else:
        title = request.POST.get('title')
        content = request.POST.get('content')
        print(content)
        # 第一个参数是要解析的HTML文档内容(str)
        # 第二个参数是使用的解析器(主要有html.parser(默认就有)和lxml(需要下载))
        soup = BeautifulSoup(content, 'html.parser')
        # 得到去掉标签之后的文本内容
        desc = soup.text[:180]  # 取摘要
        # 找出文档中的所有script标签
        script_list = soup.find_all('script')
        for i in script_list:
            i.decompose()  # 将script标签对象从文档中删除,方式xss攻击
        category_id = request.POST.get('category')  # 一个分类
        tag_ids = request.POST.getlist('tag')  # 多个标签
        article = models.Articles.objects.create(title=title, description=desc, content=str(soup),
                                                 blog=request.user.blog,
                                                 categorys_id=category_id)
        # 只剩下tag没有添加了,因为是手写的第三张表,所以就没有api使用了
        # article.tag.add(tag_ids)

        # 手动添加进去,每循环一次就连接一次数据库,消耗非常大,不好
        # for tag_id in tag_ids:
        #     models.TagToArticle(article_id=article.id,tag_id=tag_id)

        # 使用bulk_create()进行批量插入
        tag_id_list = []
        for tag_id in tag_ids:
            tag_id_list.append(models.ArticlesToTags(tags_id=tag_id, articles_id=article.id))
        models.ArticlesToTags.objects.bulk_create(tag_id_list)

        return redirect('backed_name')


# 富文本编辑器上传图片
# 局部禁用csrf校验
@csrf_exempt
def upload_img(request):
    # print(request.FILES)  # 可以查看到文件所对应的Key是"imgFile"
    try:
        myfile = request.FILES.get('imgFile')
        path = os.path.join(settings.MEDIA_ROOT, 'organ')
        with open(f'{path}/{myfile.name}', 'wb')as f:
            for line in myfile:
                f.write(line)
        # 保存图片并返回图片的url给前端
        return JsonResponse({'error': 0, "url": '/media/organ' + myfile.name})
    except Exception as E:
        return JsonResponse({'error': 1, "message": str(E)})


# 删除文章
def del_article(request, id):
    models.Articles.objects.filter(id=id).delete()
    return redirect('backed_name')


# 编辑文章
@login_required(login_url='/login/')
def edit_article(request, id):
    if request.method == 'GET':
        category_list = models.Categorys.objects.filter(blog=request.user.blog)
        tag_list = models.Tags.objects.filter(blog=request.user.blog)
        article_obj = models.Articles.objects.filter(id=id).first()
        # 拿到所有的分类和标签
        category_id = models.Articles.objects.filter(id=id).values('categorys').first()['categorys']
        tag_id_list = models.Articles.objects.filter(id=id).values('tags').all()
        tag_id_list2 = []
        for i in tag_id_list:
            tag_id_list2.append(i['tags'])
        return render(request, 'backend/edit_article.html', locals())
    else:
        title = request.POST.get('title')
        content = request.POST.get('content')
        # 第一个参数是要解析的HTML文档内容(str)
        # 第二个参数是使用的解析器(主要有html.parser(默认就有)和lxml(需要下载))
        soup = BeautifulSoup(content, 'html.parser')
        # 得到去掉标签之后的文本内容
        desc = soup.text[:180]  # 取摘要
        # 找出文档中的所有script标签
        script_list = soup.find_all('script')
        for i in script_list:
            i.decompose()  # 将script标签对象从文档中删除,方式xss攻击
        category_id = request.POST.get('category')  # 一个分类
        tag_ids = request.POST.getlist('tag')  # 多个标签
        article = models.Articles.objects.filter(id=id).update(title=title, description=desc, content=str(soup),
                                                               blog=request.user.blog,
                                                               categorys_id=category_id)
        tag_li = models.Articles.objects.filter(id=id).values('tags').all()
        for i in tag_li:
            models.ArticlesToTags.objects.filter(tags_id=i['tags'], articles_id=id).delete()

        # 使用bulk_create()进行批量插入
        tag_id_list = []
        for tag_id in tag_ids:
            tag_id_list.append(models.ArticlesToTags(tags_id=tag_id, articles_id=id))
        models.ArticlesToTags.objects.bulk_create(tag_id_list)

        return redirect('backed_name')


# 修改头像
@csrf_exempt
def img_change(request):
    if request.is_ajax():
        my_file = request.FILES.get('myfile')
        # 对头像进行 有/无 判断
        if my_file:
            # 取出头像名字进切分,在进行随机数拼接(或者拼接作者id,时间戳等)防止图片名相同出现覆盖问题
            new_name_list = my_file.name.split(".")
            new_name = new_name_list[0] + str(random.randint(0, 100000)) + "." + new_name_list[1]
            my_file.name = new_name
            # 将改过名的用户头像从新赋值给用户head字段,save保存
            img_obj = request.user
            img_obj.head = my_file
            img_obj.save()
            return JsonResponse({'status': 200, 'msg': '头像上传成功!'})
        else:
            return JsonResponse({'status': 201, 'msg': '头像未修改!'})


# 修改密码
@login_required(login_url='/login/')
def passwd_change(request):
    if request.method == "GET":
        passwd_forms = custom_forms.PasswordForm()
        return render(request, 'backend/passwd_change.html', locals())
    if request.is_ajax():
        response = {'status': 100, "msg": None}  # 设置一个状态信息
        password1 = request.POST.get('password1')
        print(password1)
        if request.user.check_password(password1):
            change_pwd_form = custom_forms.PasswordForm(request.POST)
            # 对数据进行校验
            if change_pwd_form.is_valid():
                # 校验通过,拿到校验后的数据及文件
                clean_data = change_pwd_form.cleaned_data
                new_password = request.POST.get('password')
                request.user.set_password(new_password)
                request.user.save()
                response['msg'] = '修改成功!'
                response['next_url'] = '/login/'
            else:
                response['status'] = 101
                response['msg'] = change_pwd_form.errors
        else:
            response['status'] = 101
            # 错误信息写成errors的格式{'字段名':['错误信息1','错误2'...]}
            response['msg'] = {'password1': ['原密码不正确!', ]}
        return JsonResponse(response)
