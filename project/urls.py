from django.urls import path
from app import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    # path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('inbox/', views.inbox, name='inbox'),
    #path('refresh-inbox/', views.refresh_inbox, name='refresh_inbox'),
    path('compose/',views.compose, name='compose'),
    path('send_email/', views.send_email, name='send_email'),
    path('read_email/<int:email_id>/', views.read_email, name='read_email'),
    path('delete_email/<int:email_id>/', views.delete_email, name='delete_email'),
    path('forward_email/<int:email_id>/', views.forward_email, name='forward_email'),
    path('sent-mails/', views.sent_emails, name='sent_emails'),
    path('attachments/<int:email_id>/', views.view_attachments, name='view_attachments'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
]






