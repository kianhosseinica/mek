from django.urls import path
from . import views

app_name = "pos"

urlpatterns = [
    path("login/", views.pos_login, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),

    path('search/customers/', views.pos_search_customers, name='search_customers'),
    path('search/products/', views.pos_search_products, name='search_products'),
]
