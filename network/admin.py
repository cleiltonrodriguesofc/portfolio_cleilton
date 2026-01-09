from django.contrib import admin
from .models import Follow, Post, Comment

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'target')
    search_fields = ('user__username', 'target__username')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_preview', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'content')

    def content_preview(self, obj):
        return obj.content[:50]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'comment_preview', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'content')

    def comment_preview(self, obj):
        return obj.comment[:50]
