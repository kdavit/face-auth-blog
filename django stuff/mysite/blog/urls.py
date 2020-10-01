from django.urls import path

from . import views, mytest

urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('log-in/', views.log_in, name='log_in'),
    path('log-out/', views.log_out, name='log_out'),
    path(r'^profile/', views.profile, name='profile'),
    path('face-auth/', mytest.face_auth, name='face_auth'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
]


