from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

# Se colocan las rutas, la vista utilizada y el nombre para identificarlas
urlpatterns = [
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('', views.login, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dms', views.dms, name='dms'),
    path('dms/<str:contact>/', views.dmsP, name='dmsP')
]
