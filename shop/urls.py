from django.contrib import admin
from django.urls import path
from . import views

app_name='shop'

urlpatterns=[
    path('',views.shop,name='shoppy'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.mylogout,name='logout'),
    path('register/',views.register,name='register'),
    path('<int:pk>/',views.read,name='read'),
    path('delete/<int:pk>/',views.delete,name='delete'),
    path('create/',views.create,name='create'),
    path('update/<int:pk>/',views.update,name='update'),
    path("thing/<int:pk>/like/", views.vote_thing, {"value": 1}, name="thing_like"),
    path("thing/<int:pk>/dislike/", views.vote_thing, {"value": -1}, name="thing_dislike"),
    path('cart/',views.view_cart,name='cart'),
    path('cart/<int:pk>',views.addtocart,name='add_cart'),
    path('/about',views.about,name='about'),
]
