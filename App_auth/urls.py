from django.urls import path
from App_auth import views

app_name = "App_auth"

urlpatterns = [
    path('login/', views.login_view, name='login-page'),
    path('register/', views.signup_view, name='register-page'),
    path('logout/', views.logout_view, name='logout'),
]
