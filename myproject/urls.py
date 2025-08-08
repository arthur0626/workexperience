"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("",views.main, name='main'),
    path("search/", views.search, name='search'),
    path("mypage/", views.mypage, name='mypage'),
    path("survey/", views.survey, name='survey'),
    path("kakao_login/", views.kakao_login, name='kakao_login'),
    path("kakao_logout/", views.kakao_logout, name='kakao_logout'),
    path("kakao_unlink/", views.kakao_unlink, name='kakao_unlink'),
    path("recent/", views.recent, name='recent'),
    path("scrapped/", views.scrapped, name='scrapped'),
    path("reviews/", views.reviews, name='reviews'),
    path("add_profile/", views.add_profile, name='add_profile'),
    path("edit_profile/<int:profile_id>/", views.edit_profile, name='edit_profile'),
    path("delete_profile/<int:profile_id>/", views.delete_profile, name='delete_profile'),
]
