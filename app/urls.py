from django.urls import path
from app import views
from .views import user_login, success



urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('login/', user_login, name='login'),
    path('success/', success, name='success'),
    
    #path('refresh-inbox/', views.refresh_inbox, name='refresh_inbox'),
    path('compose/', views.compose, name='compose'),
    path('send_email/', views.send_email, name='send_email'),
    path('read_email/<int:email_id>/', views.read_email, name='read_email'),
    path('delete_email/<int:email_id>/', views.delete_email, name='delete_email'),
    path('forward_email/<int:email_id>/', views.forward_email, name='forward_email'),
]