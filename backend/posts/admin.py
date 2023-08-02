from django.contrib import admin
from .models import post

class PostAdmin(admin.ModelAdmin):
    list_display = ('caption', 'posted_by', 'Picture', 'video')
    search_fields = ('caption', 'posted_by__email')

admin.site.register(post, PostAdmin)