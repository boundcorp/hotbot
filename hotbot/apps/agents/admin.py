# type: ignore

from django.contrib import admin
from django.utils.html import format_html
from hotbot.apps.agents.models import Message
from hotbot.utils.admin import register


@register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        "openai_id",
        "success",
        "workflow",
        "model",
        "duration",
        "completion_tokens",
        "prompt_tokens",
    ]
    search_fields = ["openai_id", "model"]
    list_filter = ["success", "model"]
    readonly_fields = [field.name for field in Message._meta.fields] + [
        "formatted_content"
    ]

    def formatted_content(self, obj):
        return format_html("<pre>{}</pre>", obj.content)

    formatted_content.short_description = "Content"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
