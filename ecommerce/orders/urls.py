from django.urls import path
from . import views
app_name = "orders"
urlpatterns = [
    # ...
    path("orders/", views.user_orders, name="orders"),
    path('order/<uuid:order_id>/', views.order_detail, name='order_detail'),
    path('refund/request/<int:order_id>/', views.refund_request_view, name='request_refund'),
    path("refund/history/", views.refund_history, name="refund_history"),
    path("refund/<int:refund_id>/", views.refund_detail, name="refund_detail"),
]
