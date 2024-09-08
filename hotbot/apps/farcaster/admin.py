from datetime import datetime
import json
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

class IsReplyFilter(admin.SimpleListFilter):
    title = 'Reply Status'
    parameter_name = 'is_reply'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Is Reply'),
            ('no', 'Is Not Reply'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.is_reply()
        if self.value() == 'no':
            return queryset.is_not_reply()
        return queryset

@register(models.Cast)
class CastAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'link', 'parent', 'author', 'channel', 'tags', 'cast', 'moderation_duration', 'log']
    search_fields = ['hash', 'text', 'author__username']
    list_filter = ['timestamp', 'channel', IsReplyFilter]
    readonly_fields = ['hash']

    def cast(self, obj):
        summary = obj.short_text_summary(max_length=300)
        return format_html('<div style="max-width: 400px;">{}<br />{}</div>', summary, obj.embed_descriptions and 'Embeds: '+', '.join(obj.embed_descriptions.values()) or '')

    def tags(self, obj):
        return format_html(', '.join([tag.tag for tag in obj.cast_tags.all()]))

    def link(self, obj):
        if not obj.author:
            return None
        return format_html('<a href="https://warpcast.com/{}/{}" target="_blank">{}</a>', obj.author.username, obj.hash, obj.hash[:10])
    
    def parent(self, obj):
        if obj.parent_hash and obj.author:
            return format_html('<a href="https://warpcast.com/{}/{}" target="_blank">{}</a>', obj.author.username, obj.parent_hash, obj.parent_hash[:10])
        return None

    def log(self, obj):
        if not obj.moderation_log:
            return None
        start = datetime.fromisoformat(obj.moderation_log[0]['timestamp'])
        def log_line(log):
            duration = (datetime.fromisoformat(log['timestamp']) - start).total_seconds()
            return f"{duration:.2f}s: {log['message']}"
        return format_html('<pre>{}</pre>', '\n'.join([log_line(log) for log in obj.moderation_log]))

@register(models.Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    readonly_fields = []