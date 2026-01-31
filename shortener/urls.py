from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home and Auth
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='shortener/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # URL Management
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_short_url, name='create_url'),
    path('edit/<int:pk>/', views.edit_short_url, name='edit_url'),
    path('delete/<int:pk>/', views.delete_short_url, name='delete_url'),
    
    # Analytics and QR Code
    path('analytics/<int:pk>/', views.analytics, name='analytics'),
    path('qr/<int:pk>/', views.qr_code, name='qr_code'),
    
    # URL Redirection (must be last to avoid conflicts)
    path('<str:short_key>/', views.redirect_url, name='redirect_url'),
]

