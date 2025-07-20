from django.urls import path, include
import rest_framework.routers as routers
from . import views

# Create a router and register our viewsets with it.
router = routers.DefaultRouter()
router.register(r'conversations', views.ConversationViewSet, basename='conversation')
router.register(r'messages', views.MessageViewSet, basename='message')

# The API URLs are now determined automatically by the router.
app_name = 'chats'
urlpatterns = [
    path('', include(router.urls)),
]
