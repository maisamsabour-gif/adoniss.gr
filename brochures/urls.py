from django.urls import path
from . import views

urlpatterns = [
    path('',                      views.brochure_list,     name='brochure_list'),
    path('<slug:slug>/',           views.brochure_viewer,   name='brochure_viewer'),
    path('<slug:slug>/pages.json', views.brochure_pages_api, name='brochure_pages_api'),
]
