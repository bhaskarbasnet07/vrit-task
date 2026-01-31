from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from django.utils import timezone
from django.db.models import Q
import qrcode
from io import BytesIO
from django.http import HttpResponse
from .models import ShortURL, Click
from .forms import ShortURLForm
from .utils import generate_short_key


def home(request):
    """Home page - redirects to dashboard if logged in, otherwise shows landing page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'shortener/home.html')


def register_view(request):
    """User registration view."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! Please log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'shortener/register.html', {'form': form})


@login_required
def dashboard(request):
    """Dashboard view showing user's short URLs."""
    short_urls = ShortURL.objects.filter(user=request.user)
    
    # Get search query if provided
    search_query = request.GET.get('search', '')
    if search_query:
        short_urls = short_urls.filter(
            Q(original_url__icontains=search_query) |
            Q(short_key__icontains=search_query)
        )
    
    context = {
        'short_urls': short_urls,
        'search_query': search_query,
    }
    return render(request, 'shortener/dashboard.html', context)


@login_required
def create_short_url(request):
    """Create a new short URL."""
    if request.method == 'POST':
        form = ShortURLForm(request.POST)
        if form.is_valid():
            short_url = form.save(commit=False)
            short_url.user = request.user
            
            # Handle short key
            short_key = form.cleaned_data.get('short_key')
            if short_key:
                short_url.custom_key = True
                short_url.short_key = short_key
            else:
                # Generate unique short key
                while True:
                    short_key = generate_short_key()
                    if not ShortURL.objects.filter(short_key=short_key).exists():
                        break
                short_url.short_key = short_key
                short_url.custom_key = False
            
            short_url.save()
            messages.success(request, f'Short URL created successfully!')
            return redirect('dashboard')
    else:
        form = ShortURLForm()
    
    return render(request, 'shortener/create_url.html', {'form': form})


@login_required
def edit_short_url(request, pk):
    """Edit an existing short URL."""
    short_url = get_object_or_404(ShortURL, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ShortURLForm(request.POST, instance=short_url)
        if form.is_valid():
            # Handle short key change
            new_key = form.cleaned_data.get('short_key')
            if new_key and new_key != short_url.short_key:
                # Check if new key is available (form validation should catch this, but double-check)
                if ShortURL.objects.filter(short_key=new_key).exclude(pk=short_url.pk).exists():
                    messages.error(request, 'This short URL is already taken.')
                    return render(request, 'shortener/edit_url.html', {'form': form, 'short_url': short_url})
                short_url.custom_key = True
            elif not new_key and short_url.custom_key:
                # If removing custom key, generate a new one
                while True:
                    generated_key = generate_short_key()
                    if not ShortURL.objects.filter(short_key=generated_key).exists():
                        break
                form.cleaned_data['short_key'] = generated_key
                short_url.custom_key = False
            
            # Save the form (which will update all fields)
            short_url = form.save()
            # Save again to ensure custom_key is persisted
            short_url.save()
            messages.success(request, 'Short URL updated successfully!')
            return redirect('dashboard')
    else:
        form = ShortURLForm(instance=short_url)
        # Pre-fill the short_key field
        if short_url.custom_key:
            form.fields['short_key'].initial = short_url.short_key
    
    return render(request, 'shortener/edit_url.html', {'form': form, 'short_url': short_url})


@login_required
def delete_short_url(request, pk):
    """Delete a short URL."""
    short_url = get_object_or_404(ShortURL, pk=pk, user=request.user)
    
    if request.method == 'POST':
        short_url.delete()
        messages.success(request, 'Short URL deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'shortener/delete_url.html', {'short_url': short_url})


def redirect_url(request, short_key):
    """Redirect to the original URL when short URL is accessed."""
    try:
        short_url = ShortURL.objects.get(short_key=short_key)
        
        # Check if expired
        if short_url.is_expired():
            raise Http404("This short URL has expired.")
        
        # Track the click
        click = Click.objects.create(
            short_url=short_url,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            referer=request.META.get('HTTP_REFERER', '')
        )
        
        # Increment click count
        short_url.click_count += 1
        short_url.save()
        
        # Redirect to original URL
        return HttpResponseRedirect(short_url.original_url)
    
    except ShortURL.DoesNotExist:
        raise Http404("Short URL not found.")


def get_client_ip(request):
    """Get the client's IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def qr_code(request, pk):
    """Generate QR code for a short URL."""
    short_url = get_object_or_404(ShortURL, pk=pk, user=request.user)
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(short_url.get_short_url(request))
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Return as HTTP response
    response = HttpResponse(buffer.read(), content_type='image/png')
    response['Content-Disposition'] = f'inline; filename="qr_{short_url.short_key}.png"'
    return response


@login_required
def analytics(request, pk):
    """View detailed analytics for a short URL."""
    short_url = get_object_or_404(ShortURL, pk=pk, user=request.user)
    clicks = Click.objects.filter(short_url=short_url).order_by('-clicked_at')[:50]  # Last 50 clicks
    
    context = {
        'short_url': short_url,
        'clicks': clicks,
        'total_clicks': short_url.click_count,
    }
    return render(request, 'shortener/analytics.html', context)

