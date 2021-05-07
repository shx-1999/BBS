"""BBS_4_19 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from blog import views
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register_name'),
    path('login/', views.login_auth, name='login_name'),
    path('get_valid_code/', views.get_valid_code, name='get_valid_code'),
    path('home/', views.home, name='home_name'),
    path('', views.home, name='home_name'),
    path('logout/', views.logout_func, name='logout_name'),
    path('diggit/', views.upanddown, name='upanddown_name'),
    path('comment_content/', views.comment, name='comment_name'),
    path('backend/', views.backend, name='backed_name'),
    path('add_article/', views.add_article, name='add_article_name'),
    path('upload_img/', views.upload_img, name='upload_img_name'),
    re_path('^del_article/(\d+)/', views.del_article, name='del_article_name'),
    re_path('^edit_article/(\d+)/', views.edit_article, name='edit_article_name'),
    path('img_change/', views.img_change, name='img_change_name'),
    path('passwd_change/', views.passwd_change, name='passwd_change_name'),


    # serve的几个参数：request, path：路径, document_root:要开启项目的路径(这里开启media)
    re_path('^media/(?P<path>.*?)$', serve, kwargs={'document_root': settings.MEDIA_ROOT}),

    # 三种方式匹配合一 :
    re_path('^(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<params>.*).html$', views.personal_site),

    # 文章内容路由
    re_path('^(?P<username>\w+)/articles/(?P<id>\d+).html$', views.article_detail),

    # 个人站点路由(这个路径必须放在最后面，如果放在前面，其他路径都匹配不到直接匹配这个)
    re_path('^(?P<username>\w+)', views.personal_site),

]
