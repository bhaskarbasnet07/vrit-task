from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


def validate_url(value):
    """Validate that the URL is properly formatted."""
    validator = URLValidator()
    try:
        validator(value)
    except ValidationError:
        raise ValidationError('Enter a valid URL.')


class ShortURL(models.Model):
    """Model to store shortened URLs."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='short_urls')
    original_url = models.URLField(max_length=2048, validators=[validate_url])
    short_key = models.CharField(max_length=20, unique=True, db_index=True)
    custom_key = models.BooleanField(default=False)  # True if user provided custom key
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    click_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Short URL'
        verbose_name_plural = 'Short URLs'
    
    def __str__(self):
        return f"{self.short_key} -> {self.original_url}"
    
    def is_expired(self):
        """Check if the URL has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def get_short_url(self, request):
        """Get the full short URL."""
        return request.build_absolute_uri(f'/{self.short_key}/')


class Click(models.Model):
    """Model to track individual clicks for analytics."""
    short_url = models.ForeignKey(ShortURL, on_delete=models.CASCADE, related_name='clicks')
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    referer = models.URLField(null=True, blank=True)
    
    class Meta:
        ordering = ['-clicked_at']
    
    def __str__(self):
        return f"Click on {self.short_url.short_key} at {self.clicked_at}"

