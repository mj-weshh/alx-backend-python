"""
URL configuration for messaging_app project.
"""
from django.contrib import admin
from django.urls import path, include
from chats.auth_views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView
)

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # JWT Authentication
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='auth_logout'),
    
    # API endpoints
    path('api/', include('chats.urls')),
    
    # Browsable API auth (for development only)
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
