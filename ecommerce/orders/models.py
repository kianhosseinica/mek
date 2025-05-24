from django.db import models
from django.conf import settings  # ✅ Use AUTH_USER_MODEL
import uuid
from decimal import Decimal
from django.apps import apps  # ✅ Lazy import to avoid circular import issues
from django.db.models.signals import post_save
from django.dispatch import receiver


import uuid
from decimal import Decimal
from django.conf import settings
from django.db import models

from django.db import models
from django.conf import settings  # ✅ Use AUTH_USER_MODEL
import uuid
from decimal import Decimal, ROUND_HALF_UP
from django.db.models.signals import post_save
from django.dispatch import receiver

class Order(models.Model):
    """Represents an order placed by a user."""
    # User who placed the order
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")

    # Unique order ID (Automatically assigned before saving)
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    paypal_order_id = models.CharField(max_length=50, blank=True, null=True, unique=True)  # Store PayPal Order ID
    paypal_capture_id = models.CharField(max_length=50, blank=True, null=True, unique=True)  # Store PayPal Capture ID

    # Billing Details
    first_name = models.CharField(max_length=100, default="Guest")
    last_name = models.CharField(max_length=100, default="User")
    company_name = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100, default="Canada")
    address1 = models.CharField(max_length=255, default="Not Provided")
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, default="Unknown")
    state = models.CharField(max_length=100, default="Unknown")
    zip_code = models.CharField(max_length=20, default="00000")
    phone = models.CharField(max_length=20, default="000-000-0000")
    email = models.EmailField(default="notprovided@example.com")
    order_notes = models.TextField(blank=True, null=True)

    # Shipping Details (if different from billing)
    shipping_first_name = models.CharField(max_length=100, blank=True, null=True)
    shipping_last_name = models.CharField(max_length=100, blank=True, null=True)
    shipping_company = models.CharField(max_length=255, blank=True, null=True)
    shipping_address1 = models.CharField(max_length=255, blank=True, null=True)
    shipping_address2 = models.CharField(max_length=255, blank=True, null=True)
    shipping_city = models.CharField(max_length=100, blank=True, null=True)
    shipping_state = models.CharField(max_length=100, blank=True, null=True)
    shipping_zip_code = models.CharField(max_length=20, blank=True, null=True)
    shipping_phone = models.CharField(max_length=20, blank=True, null=True)
    shipping_email = models.EmailField(blank=True, null=True)

    # Shipping Price
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    # Order Totals (These will be provided by the front end at checkout)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total discount applied to the order"
    )

    # Payment Methods
    PAYMENT_METHODS = [
        ('bank', 'Direct Bank Transfer'),
        ('check', 'Check Payment'),
        ('pickup', 'Pay at Store'),
        ('paypal', 'PayPal'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default="paypal")

    # Fulfillment Options
    FULFILLMENT_OPTIONS = [
        ('pickup', 'Pickup at Store'),
        ('delivery', 'Delivery'),
    ]
    fulfillment_method = models.CharField(max_length=20, choices=FULFILLMENT_OPTIONS, default='pickup')

    # Order Status
    STATUS_CHOICES = [
        ('Pending', 'Pending'),  # Order placed but not yet processed
        ('Paid', 'Paid'),  # Payment received
        ('Preparing', 'Preparing'),  # Order is being prepared
        ('ReadyForPickup', 'Ready for Pickup'),  # For in-store pickup orders
        ('ReadyToShip', 'Ready to Ship'),  # For delivery orders, packed and ready
        ('Shipped', 'Shipped'),  # Shipped via courier
        ('Delivered', 'Delivered'),  # Received by customer
        ('Complete', 'Complete'),  # Final state after confirmation
        ('Cancelled', 'Cancelled'),  # Order was cancelled
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optionally, keep calculate_totals for display; totals come from front end.
    def calculate_totals(self):
        pass

    def restore_stock_on_refund(self):
        """
        Restores refunded items to stock when a refund is approved.
        """
        for refund in self.refund_requests.filter(status="approved"):
            item = refund.order_item
            item.product_variation.stock_single += refund.quantity  # Restore refunded quantity
            item.product_variation.save()

    def get_first_product_image(self):
        """Returns the first product's image in the order if available."""
        first_item = self.items.first()
        if first_item and first_item.product_variation and first_item.product_variation.product.image:
            return first_item.product_variation.product.image.url
        return "/static/images/default.jpg"  # Default placeholder

    def __str__(self):
        return f"Order {self.order_id} - {self.user.phone_number} - ${self.total_price:.2f}"


from decimal import Decimal
from django.db import models
from django.conf import settings

class OrderItem(models.Model):
    """Stores individual items within an order."""
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="items")
    product_variation = models.ForeignKey("store.ProductVariation", on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey("store.Product", on_delete=models.CASCADE, null=True, blank=True)

    PURCHASE_CHOICES = [
        ('single', 'Single'),
        ('bag', 'Bag'),
        ('box', 'Box'),
    ]
    purchase_type = models.CharField(max_length=10, choices=PURCHASE_CHOICES)
    quantity = models.PositiveIntegerField()
    refunded_quantity = models.PositiveIntegerField(default=0)  # Track refunded quantity
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_refundable = models.BooleanField(default=True)  # Ensure refund tracking

    def save(self, *args, **kwargs):
        """
        Override the save method so that the total_price is not automatically
        calculated. Instead, it is expected to be set externally (e.g., provided
        via the checkout form).
        """
        super().save(*args, **kwargs)

    def remaining_refundable_quantity(self):
        """Returns the remaining refundable quantity."""
        return self.quantity - self.refunded_quantity

    def __str__(self):
        if self.product_variation:
            return f"{self.product_variation.product.name} ({self.purchase_type} x {self.quantity}) - ${self.total_price:.2f}"
        elif self.product:
            return f"{self.product.name} (No Variation, x {self.quantity}) - ${self.total_price:.2f}"
        return "OrderItem without product"



# Since totals are provided from the front end, the post_save signal for OrderItem is no longer used.
@receiver(post_save, sender=OrderItem)
def update_order_totals(sender, instance, **kwargs):
    pass



from django.db import models
from django.conf import settings  # ✅ Import the correct user model reference

from django.db import models
from django.conf import settings

from django.db import models
from django.conf import settings

from django.db import models
from django.conf import settings
from decimal import Decimal, ROUND_DOWN


from decimal import Decimal, ROUND_DOWN
from django.db import models
from django.conf import settings

from decimal import Decimal, ROUND_DOWN
from django.db import models
from django.conf import settings

from decimal import Decimal, ROUND_DOWN
from django.db import models
from django.conf import settings

# orders/models.py

from decimal import Decimal, ROUND_DOWN
from django.db import models
from django.conf import settings

from decimal import Decimal, ROUND_DOWN
from django.db import models
from django.conf import settings

class RefundRequest(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('approved',  'Approved'),
        ('rejected',  'Rejected'),
        ('processed', 'Processed'),
    ]

    REASON_CHOICES = [
        ('damaged',         'Product damaged'),
        ('wrong_item',      'Wrong item received'),
        ('not_as_described','Product not as described'),
        ('other',           'Other'),
    ]

    user                      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order                     = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='refund_requests')
    order_item                = models.ForeignKey('orders.OrderItem', on_delete=models.CASCADE, related_name='refunds')
    quantity                  = models.PositiveIntegerField(default=1)  # in **single‐unit** terms

    refund_reason             = models.CharField(max_length=50, choices=REASON_CHOICES)
    additional_comments       = models.TextField(blank=True, null=True)

    restocking_fee_percentage = models.DecimalField(
                                   max_digits=5, decimal_places=2,
                                   default=Decimal('10.00'),
                                   help_text="Restocking fee percentage"
                               )
    refund_amount             = models.DecimalField(max_digits=10, decimal_places=2,
                                                   blank=True, null=True)

    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_response = models.TextField(blank=True, null=True)
    paypal_refund_id = models.CharField(max_length=50, blank=True, null=True)

    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        1) Count how many “packages” this is:
             pkg_count = quantity / box_size  (or bag_size)
        2) Multiply pkg_count × per‑package price (self.order_item.price)
        3) Subtract restocking fee
        4) Re‑apply the same tax rate used on the order
        5) Round down to 2 decimals
        """
        pi = self.order_item
        pkg_count = Decimal(self.quantity)
        if pi.purchase_type == "box" and pi.product_variation:
            pkg_count = pkg_count / Decimal(pi.product_variation.box_size)
        elif pi.purchase_type == "bag" and pi.product_variation:
            pkg_count = pkg_count / Decimal(pi.product_variation.bag_size)

        # Use the per‐package price (never total_price)
        per_pkg_price = Decimal(pi.price)
        line_total    = per_pkg_price * pkg_count

        fee_amount  = (self.restocking_fee_percentage / Decimal('100')) * line_total
        net_after   = line_total - fee_amount

        order_sub   = self.order.subtotal or Decimal('0.00')
        order_tax   = self.order.tax_amount or Decimal('0.00')
        tax_rate    = (order_tax / order_sub) if order_sub > 0 else Decimal('0.00')

        refund_val  = net_after * (Decimal('1.00') + tax_rate)
        self.refund_amount = refund_val.quantize(Decimal('0.01'), rounding=ROUND_DOWN)

        super().save(*args, **kwargs)

    def __str__(self):
        prod = (self.order_item.product_variation.product.name
                if self.order_item.product_variation
                else self.order_item.product.name)
        return f"Refund {self.id} for Order {self.order.order_id}: {prod} ({self.status})"








class RefundMedia(models.Model):
    """Model to store images/videos for refund requests."""

    refund_request = models.ForeignKey(RefundRequest, on_delete=models.CASCADE, related_name='media')
    media_file = models.FileField(upload_to='refund_media/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Media for Refund ID: {self.refund_request.id}"




