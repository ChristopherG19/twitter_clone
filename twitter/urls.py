from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

# Se colocan las rutas, la vista utilizada y el nombre para identificarlas
urlpatterns = [
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('', views.login, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('delete/<str:tweet_id>/', views.delete, name='delete'),
    path('profile/<str:username>', views.profile, name='profile'),
    path('edit/', views.edit_profile, name='edit'),
    path('follow/<str:username>/', views.follow, name='follow'),
    path('unfollow/<str:username>/', views.unfollow, name='unfollow'),
    path('dms', views.dms, name='dms'),
    path('dms/<str:contact>/', views.dmsP, name='dmsP'),
    path('notifications/', views.get_notifications, name='notifications'),
    path('notificationsB/<str:tipo>/<str:userM>/', views.view_notification, name='notificationsB'),
    path('comments/<str:TID>/', views.comments, name='comments'),
    path('liking/<str:username>/<str:TID>', views.liking, name='liking'),
    path('unliking/<str:username>/<str:TID>', views.unliking, name='unliking'),
    path('spaces', views.spaces, name='spaces'),
    path('spaces/<int:NID>', views.spacesParticipate, name='spacesParticipate' ),
    path('spacesEnd/<int:NID>', views.endSpace, name='endSpace' ),
]
