from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name="mainapp"

urlpatterns =[
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('courses/', views.courses_view, name='courses'),
    path("mycourses/", views.mycourses_view, name="mycourses"),
    path("settings/", views.settings_view, name="settings"),
]