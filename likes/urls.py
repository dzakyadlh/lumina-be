from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LikesViewSet

router = DefaultRouter()
router.register(r'likes', LikesViewSet)
urlpatterns = [
     path('api/', include(router.urls)),
]
