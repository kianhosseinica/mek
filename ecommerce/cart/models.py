# cart/models.py

from django.db import models
from django.conf import settings
from decimal import Decimal
from store.models import Product, ProductVariation, PriceRule
import logging

logger = logging.getLogger(__name__)

class Cart(models.Model):
    """Shopping Cart Model linked to a user or session."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    session_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        """Sum of all CartItems' total_price."""
        return sum(item.total_price() for item in self.items.all())

    def total_original_price(self):
        """Sum of all CartItems' total_original_price."""
        return sum(item.total_original_price() for item in self.items.all())

    def total_discount(self):
        """Total discount across all CartItems."""
        return self.total_original_price() - self.total_price()

    def __str__(self):
        return f"Cart ({self.user if self.user else 'Guest'})"


class CartItem(models.Model):
    cart = models.ForeignKey('cart.Cart', on_delete=models.CASCADE, related_name="items")
    product_variation = models.ForeignKey(
        ProductVariation,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    TYPE_CHOICES = [
        ('single', 'Single'),
        ('bag', 'Bag'),
        ('box', 'Box'),
    ]
    purchase_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='single')
    quantity = models.PositiveIntegerField(default=1)

    def original_unit_price(self):
        """Returns the unit price before any discounts."""
        if self.product_variation is not None:
            return {
                'single': self.product_variation.price_single,
                'bag': self.product_variation.price_bag,
                'box': self.product_variation.price_box,
            }.get(self.purchase_type, self.product_variation.price_single)
        elif self.product is not None:
            return self.product.price
        logger.error("CartItem has neither product nor product_variation set!")
        return Decimal("0.00")

    def unit_price(self):
        """Returns the unit price after applying any discounts."""
        user = self.cart.user
        base_price = self.original_unit_price()

        if user and hasattr(user, 'customer_type') and user.customer_type != 'regular':
            price_rule = PriceRule.objects.filter(customer_type=user.customer_type).first()
            if price_rule:
                if self.product_variation:
                    product = self.product_variation.product
                    eligible = (
                        product.category in price_rule.apply_to_categories.all()
                        or product.subcategory in price_rule.apply_to_subcategories.all()
                        or (
                            price_rule.apply_to_price_list
                            and product in price_rule.apply_to_price_list.products.all()
                        )
                        or product in price_rule.apply_to_products.all()
                        or self.product_variation in price_rule.apply_to_variations.all()
                    ) and (
                        product not in price_rule.exclude_products.all()
                        and self.product_variation not in price_rule.exclude_variations.all()
                    )
                else:
                    eligible = (
                        self.product.category in price_rule.apply_to_categories.all()
                        or self.product.subcategory in price_rule.apply_to_subcategories.all()
                        or (
                            price_rule.apply_to_price_list
                            and self.product in price_rule.apply_to_price_list.products.all()
                        )
                        or self.product in price_rule.apply_to_products.all()
                    ) and self.product not in price_rule.exclude_products.all()

                if eligible:
                    discount_amount = (base_price * Decimal(price_rule.discount_percentage)) / Decimal(100)
                    return base_price - discount_amount
        return base_price

    def unit_discount(self):
        """Returns the discount amount per unit."""
        return self.original_unit_price() - self.unit_price()

    def total_original_price(self):
        """Total price before discounts."""
        price = self.original_unit_price()
        if self.product_variation:
            if self.purchase_type == "bag":
                if self.product_variation.bag_size and self.product_variation.bag_size != 0:
                    return price * (Decimal(self.quantity) / Decimal(self.product_variation.bag_size))
                else:
                    return Decimal("0.00")
            elif self.purchase_type == "box":
                if self.product_variation.box_size and self.product_variation.box_size != 0:
                    return price * (Decimal(self.quantity) / Decimal(self.product_variation.box_size))
                else:
                    return Decimal("0.00")
            else:
                return price * Decimal(self.quantity)
        else:
            return price * Decimal(self.quantity)

    def total_price(self):
        """Total price after discounts."""
        price = self.unit_price()
        if self.product_variation:
            if self.purchase_type == "bag":
                if self.product_variation.bag_size and self.product_variation.bag_size != 0:
                    return price * (Decimal(self.quantity) / Decimal(self.product_variation.bag_size))
                else:
                    return Decimal("0.00")
            elif self.purchase_type == "box":
                if self.product_variation.box_size and self.product_variation.box_size != 0:
                    return price * (Decimal(self.quantity) / Decimal(self.product_variation.box_size))
                else:
                    return Decimal("0.00")
            else:
                return price * Decimal(self.quantity)
        else:
            return price * Decimal(self.quantity)

    def total_discount(self):
        """Total discount for this CartItem."""
        return self.total_original_price() - self.total_price()

    def __str__(self):
        if self.product_variation:
            return f"{self.product_variation.product.name} [{self.purchase_type} x {self.quantity}]"
        elif self.product:
            return f"{self.product.name} [No Variation, x {self.quantity}]"
        else:
            return "CartItem with no product/variation"
