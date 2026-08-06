from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Citizen endpoints
    path('', views.index, name='index'),
    path('lodge/', views.lodge_complaint, name='lodge_complaint'),
    path('track/<str:ref_num>/', views.track_complaint, name='track_complaint'),
    
    # Boundary AJAX APIs
    path('api/get_sabhas/', views.get_sabhas, name='api_get_sabhas'),
    path('api/get_wasamas/', views.get_wasamas, name='api_get_wasamas'),
    
    # Authenticated Dashboards
    path('dashboard/router/', views.dashboard_router, name='dashboard_router'),
    path('dashboard/officer/', views.officer_dashboard, name='officer_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/officer/<int:officer_id>/delete/', views.delete_officer, name='delete_officer'),
    path('complaint/<int:complaint_id>/update/', views.update_complaint_status, name='update_complaint_status'),
    
    # Auth views
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
]
