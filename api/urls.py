from django.urls import path
from .api import UserRegistrationView,UserLoginView,UserLogoutView,MeanScoreAPIView

urlpatterns = [

    path('registration/',UserRegistrationView.as_view(),name='sign-up'),
    path('login/',UserLoginView.as_view(),name='login'),
    path('mean/',MeanScoreAPIView.as_view(),name='mean'),
    path('logout/', UserLogoutView.as_view(), name = 'logout')
    
]
