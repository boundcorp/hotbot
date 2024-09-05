from django.contrib import admin
from django.utils.html import format_html
from hotbot.utils.admin import register
from . import models

@register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['fid', 'username', 'display_name', 'follower_count', 'following_count', 'active_status']
    search_fields = ['fid', 'username', 'display_name', 'custody_address', 'primary_address']
    list_filter = ['active_status', 'power_badge']
    readonly_fields = ['fid', ]

@register(models.Cast)
class CastAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'hash_link','author', 'text', 'channel']
    search_fields = ['hash', 'text', 'author__username']
    list_filter = ['timestamp', 'channel']
    readonly_fields = ['hash']

    def hash_link(self, obj):
        return format_html('<a href="https://warpcast.com/{}/{}" target="_blank">{}</a>', obj.author.username, obj.hash, obj.hash)

@register(models.Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    readonly_fields = []