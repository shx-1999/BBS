from django.db import models

# Create your models here.


from django.contrib.auth.models import AbstractUser


# 用户信息表,继承Abs...进行字段扩展(在settings.py文件中需要进行配置)
class User(AbstractUser):
    sex_choices = ((0, '女'), (1, '男'), (2, '未知'))
    sex = models.IntegerField(default=1, choices=sex_choices, verbose_name='性别')
    head = models.FileField(upload_to='head', default='head/default.png', verbose_name='头像')
    addr = models.CharField(max_length=64, null=True,verbose_name='住址')
    phone = models.CharField(max_length=18, verbose_name='电话')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    # 站点外键,一个用户唯一站点
    blog = models.OneToOneField(to='Blog', on_delete=models.CASCADE, null=True)

    class Meta:
        # 修改后台管理展示的表名
        verbose_name_plural = '用户信息表'

    def __str__(self):
        return self.username


# 站点表
class Blog(models.Model):
    site_name = models.CharField(max_length=32, verbose_name='站点名字')
    site_title = models.CharField(max_length=32, verbose_name='站点标题')
    site_style = models.CharField(max_length=32, verbose_name='站点样式')

    class Meta:
        verbose_name_plural = '博客站点表'

    def __str__(self):
        return self.site_title


# 文章分类表
class Categorys(models.Model):
    name = models.CharField(max_length=32, verbose_name='分类名')

    # 站点外键,一个站点多个分类
    blog = models.ForeignKey(to='Blog', on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name_plural = '分类表'

    def __str__(self):
        return self.name


# 文章表
class Articles(models.Model):
    title = models.CharField(max_length=100, verbose_name='标题')
    description = models.CharField(max_length=128, verbose_name='摘要')
    content = models.TextField(verbose_name='内容')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    # 点赞点踩评论字段
    up_num = models.BigIntegerField(default=0, verbose_name='点赞数')
    down_num = models.BigIntegerField(default=0, verbose_name='点踩数')
    comment_num = models.BigIntegerField(default=0, verbose_name='评论数')

    # 站点外键,一个站点多篇文章
    blog = models.ForeignKey(to='Blog', on_delete=models.CASCADE)
    # 分类外键,一个分类多篇文章
    categorys = models.ForeignKey(to='Categorys', on_delete=models.CASCADE)
    # 标签外键,多对多
    tags = models.ManyToManyField(to='Tags', through='ArticlesToTags', through_fields=('articles', 'tags'))

    class Meta:
        verbose_name_plural = '文章表'

    def __str__(self):
        try:
            return f'{str(self.id)}----{self.title}----{self.blog.site_title}'
        except:
            return self.title


# 文章标签表
class Tags(models.Model):
    name = models.CharField(max_length=32, verbose_name='标签名')

    # 站点外键,一个站点多个标签
    blog = models.ForeignKey(to='Blog', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '标签表'

    def __str__(self):
        return self.name


# 文章评论表
class Comment(models.Model):
    user = models.ForeignKey(to='User', on_delete=models.CASCADE)
    articles = models.ForeignKey(to='Articles', on_delete=models.CASCADE)
    content = models.CharField(max_length=256, verbose_name='评论内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')

    # 自关联(存父评论的ID号)
    comment_id = models.ForeignKey(to='self', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = '评论表'


# 点赞点踩表
class UpAndDown(models.Model):
    user = models.ForeignKey(to='User', on_delete=models.CASCADE)
    articles = models.ForeignKey(to='Articles', on_delete=models.CASCADE)
    # 存的是布尔值(赞True,踩False)
    is_up = models.BooleanField()
    # 点和踩的时间
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = '点赞点踩表'


# 文章和标签第三张表
class ArticlesToTags(models.Model):
    tags = models.ForeignKey(to='Tags', on_delete=models.CASCADE)
    articles = models.ForeignKey(to='Articles', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '文章与标签表'

    def __str__(self):
        try:
            return f'{self.tags.name}----{self.articles.title}'
        except:
            return '未知'





