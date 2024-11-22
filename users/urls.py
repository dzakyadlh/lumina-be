from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('signup/', views.signup, name = 'signup'),
    path('signin/', TokenObtainPairView.as_view(), name = 'token_obtain_pair'),
    path('signout/', views.signout, name = 'signout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.update_profile, name='update_profile'),
]