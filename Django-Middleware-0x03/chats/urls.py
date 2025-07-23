from django.urls import path, include
from rest_framework_nested import routers
from . import views

# Create a router and register our viewsets with it.
router = routers.DefaultRouter()
router.register(r'conversations', views.ConversationViewSet, basename='conversation')

# Nested router for messages within conversations
conversations_router = routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', views.MessageViewSet, basename='conversation-messages')

# The API URLs are now determined automatically by the router.
app_name = 'chats'
urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
]
