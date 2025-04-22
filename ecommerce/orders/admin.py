from django.contrib import admin
from django.utils.html import format_html
from decimal import Decimal, InvalidOperation
from math import ceil
import logging

from .models import Order, OrderItem, RefundRequest, RefundMedia
from store.models import BoxSize  # Adjust the app name if necessary

logger = logging.getLogger(__name__)


# ✅ Order Item Inline (Displays Items Inside Order Admin)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Show one empty form for adding items
    readonly_fields = ('total_price',)


# ✅ Refund Media Inline (For Admin Display)
class RefundMediaInline(admin.TabularInline):
    model = RefundMedia
    extra = 0  # No extra empty forms
    readonly_fields = ("preview",)

    def preview(self, obj):
        """Displays refund media preview in admin."""
        if obj.media_file:
            return format_html('<img src="{}" width="100" style="border-radius:8px;" />', obj.media_file.url)
        return "No Media Uploaded"
    preview.allow_tags = True


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id', 'user', 'full_name', 'email', 'phone',
        'total_price', 'fulfillment', 'shipping_cost', 'status',
        'created_at', 'paypal_capture', 'view_order_details'
    )
    list_filter = ('status', 'payment_method', 'fulfillment_method', 'created_at')
    search_fields = ('order_id', 'user__username', 'email', 'phone', 'paypal_capture_id', 'fulfillment_method')
    readonly_fields = (
        'order_id', 'created_at', 'updated_at', 'subtotal', 'tax_amount',
        'total_price', 'paypal_capture_id', 'shipping_cost',
        'shipping_first_name', 'shipping_last_name', 'shipping_address1',
        'shipping_address2', 'shipping_city', 'shipping_state',
        'shipping_zip_code', 'shipping_phone', 'shipping_email'
    )
    inlines = [OrderItemInline]
    actions = ['mark_as_paid', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "Customer Name"

    def paypal_capture(self, obj):
        return obj.paypal_capture_id or "Not set"
    paypal_capture.short_description = "PayPal Capture ID"

    def fulfillment(self, obj):
        return obj.get_fulfillment_method_display()
    fulfillment.short_description = "Fulfillment Method"

    def view_order_details(self, obj):
        return format_html('<a href="/admin/orders/order/{}/change/">View</a>', obj.id)
    view_order_details.short_description = "Details"

    def save_model(self, request, obj, form, change):
        """
        When an order is updated in the admin panel, if its status changes to 'Cancelled',
        restore the deducted stock for each order item.
        """
        if change:
            previous_obj = Order.objects.get(pk=obj.pk)
            if previous_obj.status != 'Cancelled' and obj.status == 'Cancelled':
                for item in obj.items.all():
                    restored_qty = item.quantity
                    if item.purchase_type.lower() == 'bag':
                        restored_qty *= item.product_variation.bag_size
                    elif item.purchase_type.lower() == 'box':
                        restored_qty *= item.product_variation.box_size * item.product_variation.bag_size
                    logger.info(f"Restoring {restored_qty} units for product variation {item.product_variation}")
                    item.product_variation.stock_single += restored_qty
                    item.product_variation.save()
        super().save_model(request, obj, form, change)

    @admin.action(description="Mark selected orders as Paid")
    def mark_as_paid(self, request, queryset):
        for order in queryset:
            order.status = 'Paid'
            order.save()
        self.message_user(request, "✅ Selected orders have been marked as Paid.")

    @admin.action(description="Mark selected orders as Shipped")
    def mark_as_shipped(self, request, queryset):
        for order in queryset:
            order.status = 'Shipped'
            order.save()
        self.message_user(request, "📦 Selected orders have been marked as Shipped.")

    @admin.action(description="Mark selected orders as Delivered")
    def mark_as_delivered(self, request, queryset):
        for order in queryset:
            order.status = 'Delivered'
            order.save()
        self.message_user(request, "🚚 Selected orders have been marked as Delivered.")

    @admin.action(description="Mark selected orders as Cancelled")
    def mark_as_cancelled(self, request, queryset):
        for order in queryset:
            if order.status != 'Cancelled':
                order.status = 'Cancelled'
                order.save()
        self.message_user(
            request,
            "❌ Selected orders have been marked as Cancelled and stock has been returned."
        )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_variation', 'purchase_type', 'quantity', 'price', 'total_price', 'is_refundable')
    list_filter = ('purchase_type', 'order__status', 'is_refundable')
    search_fields = ('order__order_id', 'product_variation__product__name')
    readonly_fields = ('total_price',)


@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order', 'order_item', 'quantity', 'refund_amount_with_tax',
                    'refund_reason', 'status', 'requested_at')
    list_filter = ('status', 'requested_at', 'refund_reason')
    search_fields = ('order__order_id', 'user__username', 'order_item__product_variation__product__name')
    readonly_fields = ('refund_amount', 'requested_at', 'updated_at')
    inlines = [RefundMediaInline]
    actions = ['approve_refund', 'reject_refund']

    def refund_amount_with_tax(self, obj):
        if obj.refund_amount is None:
            return "$0.00"
        return f"${(obj.refund_amount * Decimal(1.13)).quantize(Decimal('0.01')):.2f}"
    refund_amount_with_tax.short_description = "Refund Amount (with Tax)"

    def save_model(self, request, obj, form, change):
        if obj.order_item.product_variation.is_refundable:
            item_price = obj.order_item.price * obj.quantity
            restocking_fee = (Decimal(obj.restocking_fee_percentage) / Decimal(100)) * item_price
            subtotal_after_fee = item_price - restocking_fee
            obj.refund_amount = (subtotal_after_fee * Decimal(1.13)).quantize(Decimal('0.01'))
        else:
            obj.refund_amount = Decimal(0)
        super().save_model(request, obj, form, change)

    @admin.action(description="Approve selected refunds & Restore Stock")
    def approve_refund(self, request, queryset):
        for refund in queryset:
            if refund.status.lower() == 'approved':
                self.message_user(request, f"⚠️ Refund {refund.id} is already approved!", level="warning")
                continue
            refund.status = 'approved'
            refund.save()
            order_item = refund.order_item
            product_variation = order_item.product_variation
            purchase_type = order_item.purchase_type.lower()
            restored_quantity = refund.quantity
            if purchase_type == "bag":
                restored_quantity *= product_variation.bag_size
            elif purchase_type == "box":
                restored_quantity *= product_variation.box_size * product_variation.bag_size
            logger.info(f"Restoring {restored_quantity} units for refund {refund.id}")
            product_variation.stock_single += restored_quantity
            product_variation.save(force_update=True)
            self.message_user(request, f"✅ Refund approved: {refund.id} - Restored {restored_quantity} units to stock.")

    @admin.action(description="Reject selected refunds")
    def reject_refund(self, request, queryset):
        for refund in queryset:
            refund.status = 'rejected'
            refund.save()
        self.message_user(request, "🚫 Selected refund requests have been rejected.")


@admin.register(RefundMedia)
class RefundMediaAdmin(admin.ModelAdmin):
    list_display = ("refund_request", "uploaded_at", "preview")
    readonly_fields = ("uploaded_at", "preview")

    def preview(self, obj):
        if obj.media_file:
            return format_html('<img src="{}" width="100" style="border-radius:8px;" />', obj.media_file.url)
        return "No Media Uploaded"
    preview.allow_tags = True
