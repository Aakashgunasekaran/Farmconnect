from django.urls import path
#from .views import recommend_crop
from . import views
#from .views import register_view, login_view

# ✅ Add this line to register the namespace properly:
app_name = 'crop_recommendation'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
   # path('temp/', views.login_view, name='index'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('evaluate_model/', views.evaluate_model, name='evaluate_model'),
    path('evaluate_weather/', views.evaluate_weather, name='evaluate_weather'),
    path('pdt_dashboard/', views.pdt_dashboard, name='pdt_dashboard'),
    path('weather_form/', views.weather_form, name='weather_form'),
    path('farmerdashboard/', views.farmer_dashboard_view, name='farmer_dashboard'),
    path('form/', views.recommend_crop, name='form'),  # 👈 use the name 'form' here
    path('add/', views.add_product, name='add_product'),
    path('view/', views.view_product, name='view_product'),
    path('your-products/', views.farmer_products, name='your_products'),
    path('edit/<str:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<str:product_id>/', views.delete_product, name='delete_product')
]