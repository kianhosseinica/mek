from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid
from mptt.models import MPTTModel, TreeForeignKey
from orders.models import Order, OrderItem
from django.db import models
from decimal import Decimal
import uuid
from django.utils.text import slugify
class Size(models.Model):
    """Custom sizes defined dynamically in the admin panel."""
    name = models.CharField(max_length=50, unique=True)  # Example: 1/2", 3/4", 1"

    def __str__(self):
        return self.name


class Vendor(models.Model):
    """Stores vendor information."""
    name = models.CharField(max_length=255, unique=True)
    contact_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


from django.db import models
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey

class Category(MPTTModel):
    """Hierarchical Category Model using MPTT for nested categories."""
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.parent.name} > {self.name}" if self.parent else self.name

    @property
    def top_level_subcategories(self):
        """
        Returns only the subcategories that are not nested (i.e. their parent is None).
        This is used to display only the main subcategories for the category.
        """
        return self.subcategory_set.filter(parent__isnull=True)


class TopLevelSubCategoryManager(models.Manager):
    """
    Custom manager that returns only subcategories whose 'parent' is null.
    """
    def get_queryset(self):
        return super().get_queryset().filter(parent__isnull=True)


class SubCategory(models.Model):
    """Subcategories with nested relationships."""
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    image = models.ImageField(upload_to='subcategories/', blank=True, null=True)  # <-- New image field

    # Default manager returns all subcategories.
    objects = models.Manager()
    # This manager returns only top-level subcategories (where parent is None)
    top_level = TopLevelSubCategoryManager()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.parent.name} > {self.name}" if self.parent else self.name




class Brand(models.Model):
    """Product brands."""
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='brands/', blank=True, null=True)
    is_new = models.BooleanField(default=False)  # To highlight new brands

    def __str__(self):
        return self.name


# store/models.py

import uuid
from decimal import Decimal
from django.db import models
from django.utils.text import slugify
from django.conf import settings

# Import related models (adjust paths as needed)
from .models import Category, SubCategory, Brand, Vendor
from store.models import Size  # adjust if necessary

def generate_variation_id():
    """Generate a unique identifier for a ProductVariation."""
    return "VAR" + uuid.uuid4().hex[:10].upper()

class Product(models.Model):
    """Optimized Product model for better performance and unique system_id generation."""
    SYSTEM_ID_PREFIX = "ITEM"

    # General Info
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey('SubCategory', on_delete=models.SET_NULL, null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    default_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    online_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Stock & Tracking
    quantity = models.PositiveIntegerField(default=0)
    quantity_history = models.JSONField(default=list, blank=True)
    system_id = models.CharField(max_length=20, unique=True, editable=False, blank=True)

    # Identifiers
    ean = models.CharField(max_length=13, unique=True, blank=True, null=True)
    upc = models.CharField(max_length=12, unique=True, blank=True, null=True)
    custom_sku = models.CharField(max_length=50, unique=True, blank=True, null=True)

    # E-commerce Visibility
    publish_to_ecommerce = models.BooleanField(default=False)

    # Options (Variations)
    options = models.JSONField(default=dict, blank=True)

    # Popularity Flags
    rating = models.FloatField(default=0)
    trending = models.BooleanField(default=False)
    best_selling = models.BooleanField(default=False)
    most_popular = models.BooleanField(default=False)
    just_arrived = models.BooleanField(default=False)

    is_refundable = models.BooleanField(default=True, help_text="Mark if this product can be refunded.")

    weight = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("1.0"),
        help_text="Default weight per unit (lbs)"
    )
    length = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("12.0"),
        help_text="Default length in inches"
    )
    width = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("9.0"),
        help_text="Default width in inches"
    )
    height = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("4.0"),
        help_text="Default height in inches"
    )

    def save(self, *args, **kwargs):
        # Generate unique system_id if not set.
        if not self.system_id:
            self.system_id = f"{self.SYSTEM_ID_PREFIX}{uuid.uuid4().hex[:10].upper()}"
        # Auto-generate slug if missing.
        if not self.slug:
            self.slug = slugify(self.name)
        # Track quantity changes.
        if self.pk:
            old_quantity = Product.objects.filter(pk=self.pk).values_list('quantity', flat=True).first()
            if old_quantity is not None and old_quantity != self.quantity:
                self.quantity_history.append({"old": old_quantity, "new": self.quantity})
        super().save(*args, **kwargs)

    def get_all_sizes(self):
        """Return all sizes available for this product."""
        return list(self.variations.values_list("size__name", flat=True).distinct())

    def __str__(self):
        return f"{self.name} ({self.system_id})"


class ProductVariation(models.Model):
    """Variations of a product (size, color, using only single item stock)."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variations")
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    color = models.CharField(max_length=50, blank=True, null=True)

    # New unique identifier for each variation.
    variation_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        blank=True,
        default=generate_variation_id  # Use the helper function as default
    )

    # Identifiers for this variation
    manufacturer_sku = models.CharField(max_length=50, blank=True, null=True, help_text="Manufacturer SKU")
    custom_sku = models.CharField(max_length=50, blank=True, null=True, help_text="Custom SKU")
    upc = models.CharField(max_length=12, blank=True, null=True, help_text="UPC code")
    ean = models.CharField(max_length=13, blank=True, null=True, help_text="EAN code")

    # Single Item Pricing & Stock
    price_single = models.DecimalField(max_digits=10, decimal_places=2)
    stock_single = models.IntegerField(default=0)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Bag System (conversion factors only)
    bag_size = models.IntegerField(default=1)  # Items per bag
    price_bag = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Box System (conversion factors only)
    box_size = models.IntegerField(default=1)  # Bags per box
    price_box = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    image = models.ImageField(upload_to='product_variations/', blank=True, null=True)
    is_refundable = models.BooleanField(default=True, help_text="Mark if this product can be refunded.")
    weight = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("1.0"),
                                 help_text="Weight per unit (lbs)")
    length = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("12.0"),
                                 help_text="Length in inches")
    width = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("9.0"),
                                help_text="Width in inches")
    height = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("4.0"),
                                 help_text="Height in inches")

    # Packaging details for bag (if applicable)
    bag_weight = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.0"),
                                     help_text="Weight per bag (lbs) for this variation")
    bag_length = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.0"),
                                     help_text="Bag length in inches for this variation")
    bag_width = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.0"),
                                    help_text="Bag width in inches for this variation")
    bag_height = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.0"),
                                     help_text="Bag height in inches for this variation")

    # Packaging details for box (if applicable)
    box_weight = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.0"),
                                     help_text="Weight per box (lbs) for this variation")
    box_length = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.0"),
                                     help_text="Box length in inches for this variation")
    box_width = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.0"),
                                    help_text="Box width in inches for this variation")
    box_height = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.0"),
                                     help_text="Box height in inches for this variation")

    def save(self, *args, **kwargs):
        # Ensure variation_id is always set to a unique value.
        if not self.variation_id or self.variation_id.strip() == "":
            self.variation_id = generate_variation_id()
        super().save(*args, **kwargs)

    def total_weight(self, quantity, packaging="single"):
        if packaging == "bag" and self.bag_weight > 0:
            return self.bag_weight * quantity
        elif packaging == "box" and self.box_weight > 0:
            return self.box_weight * quantity
        return self.weight * quantity

    def __str__(self):
        return f"{self.product.name} - {self.size.name} - {self.color if self.color else 'No Color'}"








from django.db import models
from decimal import Decimal
from store.models import Product, ProductVariation, Category, SubCategory


class PriceList(models.Model):
    """Defines a custom price list containing specific products and variations."""
    name = models.CharField(max_length=255, unique=True)
    products = models.ManyToManyField(
        Product,
        related_name="price_lists",
        blank=True  # Allow empty lists
    )
    product_variations = models.ManyToManyField(
        ProductVariation,
        related_name="price_lists",
        blank=True  # Support variations
    )

    def __str__(self):
        return self.name


class PriceRule(models.Model):
    """Defines discount rules for different user types."""
    CUSTOMER_TYPES = [
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('platinum', 'Platinum'),
    ]

    name = models.CharField(max_length=255, unique=True)
    customer_type = models.CharField(max_length=10, choices=CUSTOMER_TYPES)
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Discount percentage (e.g. 20 for 20%)"
    )

    # Apply rule to specific categories, subcategories, products, price lists, or variations
    apply_to_categories = models.ManyToManyField(
        Category,
        blank=True,
        help_text="Apply to these categories"
    )
    apply_to_subcategories = models.ManyToManyField(
        SubCategory,
        blank=True,
        help_text="Apply to these subcategories"
    )
    apply_to_products = models.ManyToManyField(
        Product,
        blank=True,
        related_name="applied_price_rules",
        help_text="Apply to these products"
    )
    apply_to_price_list = models.ForeignKey(
        PriceList,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Apply to a specific price list"
    )
    apply_to_variations = models.ManyToManyField(
        ProductVariation,
        blank=True,
        related_name="applied_price_rules",
        help_text="Apply to specific product variations"
    )

    # Allow specific product & variation exclusions
    exclude_products = models.ManyToManyField(
        Product,
        blank=True,
        related_name="excluded_from_discount"
    )
    exclude_variations = models.ManyToManyField(
        ProductVariation,
        blank=True,
        related_name="excluded_from_discount"
    )

    def __str__(self):
        return f"{self.name} - {self.get_customer_type_display()} ({self.discount_percentage}%)"

    def get_discounted_price(self, product_or_variation):
        """
        Calculate the discounted price for a product or variation.
        For a ProductVariation, the discount is applied to its single item price.
        For a Product, the discount is applied to its base price.
        Returns None if no discount applies.
        """
        # If it's a ProductVariation
        if isinstance(product_or_variation, ProductVariation):
            if product_or_variation in self.exclude_variations.all():
                return None  # No discount if excluded
            if (
                product_or_variation.product.category in self.apply_to_categories.all() or
                product_or_variation.product.subcategory in self.apply_to_subcategories.all() or
                (self.apply_to_price_list and product_or_variation in self.apply_to_price_list.product_variations.all()) or
                product_or_variation in self.apply_to_variations.all() or
                product_or_variation.product in self.apply_to_products.all()
            ):
                discount_factor = Decimal(self.discount_percentage) / Decimal(100)
                discounted_price = product_or_variation.price_single - (product_or_variation.price_single * discount_factor)
                return round(discounted_price, 2)
        # If it's a Product
        elif isinstance(product_or_variation, Product):
            if product_or_variation in self.exclude_products.all():
                return None  # No discount if excluded
            if (
                product_or_variation.category in self.apply_to_categories.all() or
                product_or_variation.subcategory in self.apply_to_subcategories.all() or
                (self.apply_to_price_list and product_or_variation in self.apply_to_price_list.products.all()) or
                product_or_variation in self.apply_to_products.all()
            ):
                discount_factor = Decimal(self.discount_percentage) / Decimal(100)
                discounted_price = product_or_variation.price - (product_or_variation.price * discount_factor)
                return round(discounted_price, 2)
        return None  # No discount if not applicable



from django.db import models
from decimal import Decimal

class BoxSize(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="A unique name for the box type (e.g., Small, Medium, Large)."
    )
    max_weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Maximum weight capacity for this box in lbs."
    )
    length = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Internal length of the box in inches."
    )
    width = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Internal width of the box in inches."
    )
    height = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Internal height of the box in inches."
    )

    def volume(self):
        """Calculate the internal volume of the box."""
        return self.length * self.width * self.height

    def __str__(self):
        return self.name
