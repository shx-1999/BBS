from django.contrib import admin

# Register your models here.

from blog import models

admin.site.register(models.User)
admin.site.register(models.Blog)
admin.site.register(models.Categorys)
admin.site.register(models.Articles)
admin.site.register(models.ArticlesToTags)
admin.site.register(models.UpAndDown)
admin.site.register(models.Comment)
admin.site.register(models.Tags)