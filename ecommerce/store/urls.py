from django.urls import path
from . import views
from .views import checkout  # Import the function-based view


app_name = "store"
urlpatterns = [
    path('', views.index, name='index'),
    path('shop/', views.shop, name='shop'),
    path('product/<slug:slug>/', views.single_product, name='single-product'),
    path('cart/', views.cart, name='cart'),
    path("checkout/", views.checkout, name="checkout"),
    path('account/', views.account, name='account'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('thank-you/', views.thank_you, name='thank-you'),

    # Updated category routes:
    path('categories/', views.category_list, name='category-index'),

    path('cart/add/<str:item_uid>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    path("payment-success/", views.payment_success, name="payment_success"),
    path("create-paypal-order/", views.create_paypal_order, name="create_paypal_order"),  # API to create PayPal order
    path("capture-paypal-order/", views.capture_paypal_order, name="capture_paypal_order"),

    path('order-success/<uuid:order_id>/', views.order_success, name='order_success'),
    path('search/', views.search, name='search'),
    path('test/', views.test, name='test'),
    path('test-email/', views.test_email_view, name='test-email'),



    path('ctagoryes/category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('ctagoryes/subcategory/<slug:slug>/', views.subcategory_detail, name='subcategory_detail'),
    path('get-rate/', views.get_rate, name='get_rate'),
    path('cart-weight/', views.cart_total_weight, name='cart_total_weight'),
    path('test-get-rate/', views.test_get_rate, name='test_get_rate'),
    path('recommend-box/', views.recommend_box, name='recommend_box'),

]
