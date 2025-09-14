"""
URL configuration for PersonalFinanceTracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from App import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('home', views.home,name='home'),
    path('register/', views.register, name='register'),
    path('dashboard/<str:seed>/', views.dashboard_view, name='dashboard'),
    path('graphic/<str:seed>/<str:kind>.png',views.graphic_png,name='graphic_png'),
    path('dashboard/avg-expense-image/<int:dwmy>/<str:seed>/', views.avgExpenseData, name='avg_expense_image'),
    path('dashboard/freq-categories-image/<str:seed>/', views.freq_categories_image, name='freq_categories_image'),
    path('dashboard/monthly-summary-image/<str:seed>/',views.monthly_summary_image,name='monthly_summary_image'),
    path('dashboard/<str:seed>/api/category-predict/', views.category_predict_api, name='category_predict_api'),
    path('dashboard/<str:seed>/api/amount-predict/', views.amount_predict_api, name='amount_predict_api'),
]

