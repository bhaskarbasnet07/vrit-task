from django.contrib import admin
from .models import ShortURL, Click


@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = ['short_key', 'original_url', 'user', 'click_count', 'created_at', 'expires_at']
    list_filter = ['created_at', 'custom_key', 'expires_at']
    search_fields = ['short_key', 'original_url', 'user__username']
    readonly_fields = ['click_count', 'created_at']


@admin.register(Click)
class ClickAdmin(admin.ModelAdmin):
    list_display = ['short_url', 'clicked_at', 'ip_address']
    list_filter = ['clicked_at']
    search_fields = ['short_url__short_key', 'ip_address']
    readonly_fields = ['clicked_at']

