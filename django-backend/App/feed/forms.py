from django.contrib import admin
from .models import post

class PostAdmin(admin.ModelAdmin):
    list_display = ('caption', 'posted_by', '', 'is_premium')
    list_filter = ('is_premium',)
    search_fields = ('caption', 'posted_by__username')

admin.site.register(post, PostAdmin)
