from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .models import ShortURL


class ShortURLForm(forms.ModelForm):
    """Form for creating/editing short URLs."""
    original_url = forms.URLField(
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the long URL to shorten',
            'required': True
        }),
        label='Long URL'
    )
    
    short_key = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Leave blank for auto-generated (optional)',
            'pattern': '[a-zA-Z0-9_-]+',
            'title': 'Only letters, numbers, hyphens, and underscores allowed'
        }),
        label='Custom Short URL (optional)',
        help_text='Leave blank to auto-generate. Only letters, numbers, hyphens, and underscores allowed.'
    )
    
    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        label='Expiration Date (optional)',
        help_text='Optional: Set when this URL should expire'
    )
    
    class Meta:
        model = ShortURL
        fields = ['original_url', 'short_key', 'expires_at']
    
    def clean_short_key(self):
        """Validate and clean the short key."""
        short_key = self.cleaned_data.get('short_key')
        
        if short_key:
            # Check if it contains only valid characters
            if not short_key.replace('_', '').replace('-', '').isalnum():
                raise ValidationError('Short URL can only contain letters, numbers, hyphens, and underscores.')
            
            # Check if it's already taken
            existing = ShortURL.objects.filter(short_key=short_key)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError('This short URL is already taken. Please choose another one.')
        
        return short_key
    
    def clean_original_url(self):
        """Validate the original URL."""
        url = self.cleaned_data.get('original_url')
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url

