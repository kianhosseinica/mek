from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from store.views import checkout  # Import the function-based view

app_name = "users"  # ✅ This must be present!

urlpatterns = [
    # ...
    path("signup/", views.signup, name="signup"),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('wishlist/remove/<int:product_id>/', views.remove_wishlist_item, name='remove_wishlist'),
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('refunds/', views.refund_list, name='refund_list'),
    path('refunds/<int:refund_id>/', views.refund_detail, name='refund_detail'),
    path('refunds/approve/<int:refund_id>/', views.approve_refund, name='approve_refund'),
    path('refunds/reject/<int:refund_id>/', views.reject_refund, name='reject_refund'),
    path("ajax/send-pin/", views.ajax_send_pin, name="ajax_send_pin"),
    path("ajax/check-user/", views.check_user_exists, name="check_user_exists"),
    path('orders/', views.order_list_view, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('change_status_ajax/<int:order_id>/', views.change_order_status_ajax, name='change_status_ajax'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    path("forgot-password/", views.forgot_password_request, name="forgot-password"),
    path("reset-password/", views.reset_password_form, name="reset-password"),
]