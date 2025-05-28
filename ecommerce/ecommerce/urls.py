from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from store.views import error_404

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('store.urls', 'store'), namespace="store")),  # Includes store app URLs

    path('paypal/', include('paypal.standard.ipn.urls')),
    path('users/', include('users.urls', namespace="users")),  # ✅ Ensure namespace is defined
    path('orders/', include(('orders.urls', 'orders'), namespace="orders")),
    path('pos/', include(('pos.urls', 'pos'), namespace="pos")),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
