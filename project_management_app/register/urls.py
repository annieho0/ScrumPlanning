from django.urls import path
from django.contrib.auth import views as auth_views
from . import views as register_view

urlpatterns = [
    # Login URLs
    path('login/', register_view.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # Registration URLs
    path('register/', register_view.RegisterView.as_view(), name='register'),
    path('register/success/', register_view.RegisterSuccessView.as_view(), name='register_success'),
    path('activate/<str:activation_token>/', register_view.activate_account, name='activate_account'),
    # Password reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    # Admin URLs
    path('admin/hour_graph/', register_view.AdminGraphView.as_view(), name='hour_graph'),
    path('admin/hour_graph/post/', register_view.AdminGraphView.as_view(), name='graph'),
    # Logout URL
    path('logout/', auth_views.LogoutView.as_view(), name='logout')
]