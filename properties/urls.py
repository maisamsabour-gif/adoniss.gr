from django.urls import path
from . import views

urlpatterns = [
    path('', views.property_list, name='property_list'),
    path('interest/<int:pk>/', views.property_interest, name='property_interest'),
    path('book-unit/<int:pk>/', views.book_unit, name='book_unit'),
    path('<slug:slug>/', views.property_detail, name='property_detail'),
]
