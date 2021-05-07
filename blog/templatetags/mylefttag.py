# coding:utf-8
# 自定义 inclusion_tag
from django import template
from blog import models
from django.db.models.functions import TruncMonth  # 按月截断
# 自定义inclusion_tag固定写法
from django.db.models import Count

register = template.Library()


@register.inclusion_tag('left_list.html')
def left_inclusion_tag(username):
    user = models.User.objects.filter(username=username).first()
    # 该站点下所有分类下的文章数
    category_list = models.Categorys.objects.filter(blog=user.blog).annotate(count=Count('articles')).values('count',
                                                                                                             'name',
                                                                                                             'id')
    # 该站点下所有标签下的文章数
    tag_list = models.Tags.objects.filter(blog=user.blog).annotate(count=Count('articles')).values_list('count', 'name',
                                                                                                        'id')
    # 该站点下(以年月截断),年/月下的文章数
    month_list = models.Articles.objects.filter(blog=user.blog).annotate(month=TruncMonth('update_time')).values(
        'month').annotate(count=Count('id')).values_list('month', 'count')
    return {'username': username, 'category_list': category_list, 'tag_list': tag_list, 'month_list': month_list}
