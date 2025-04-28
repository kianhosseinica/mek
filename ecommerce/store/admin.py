from django.contrib import admin
from django.utils.html import format_html
from .models import *
from mptt.admin import MPTTModelAdmin
from .models import Category, SubCategory

from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import MPTTModelAdmin
from .models import Category


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    """Category Admin with a tree view, displaying subcategories properly."""
    list_display = ('name', 'parent', 'image_preview', 'slug')
    list_filter = ('parent',)
    search_fields = ('name', 'parent__name')
    prepopulated_fields = {'slug': ('name',)}
    mptt_level_indent = 20  # ✅ Indents subcategories in the admin panel

    def image_preview(self, obj):
        """✅ Show category image preview in admin, handling missing images."""
        if obj.image:
            return format_html('<img src="{}" width="50" style="border-radius:5px;" />', obj.image.url)
        return "No Image"

    image_preview.short_description = 'Image Preview'

    def get_queryset(self, request):
        """✅ Ensure proper ordering of categories and subcategories."""
        return super().get_queryset(request).order_by('parent', 'name')



### ✅ SUBCATEGORY ADMIN ###
@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    """Admin for handling nested subcategories."""
    list_display = ('name', 'category', 'parent', 'image_thumbnail')
    list_filter = ('category', 'parent')
    search_fields = ('name', 'slug', 'category__name', 'parent__name')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'parent', 'image')
        }),
    )

    def get_queryset(self, request):
        """Ensure proper ordering for nested subcategories."""
        return super().get_queryset(request).order_by('category', 'parent', 'name')

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 50px; max-height: 50px;" />', obj.image.url)
        return "-"
    image_thumbnail.short_description = 'Image'


### ✅ BRAND ADMIN ###
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_preview', 'is_new')
    list_filter = ('is_new',)
    search_fields = ('name',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" style="border-radius:5px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Brand Logo'


### ✅ VENDOR ADMIN ###
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_info')
    search_fields = ('name', 'contact_info')


from django.contrib import admin
from django.utils.html import format_html
from .models import Product, ProductVariation, BoxSize

class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1  # Allows adding new variations inline


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model."""
    list_display = (
        'name', 'category', 'subcategory', 'brand', 'vendor', 'price',
        'online_price', 'default_cost', 'get_stock', 'rating',
        'system_id', 'publish_to_ecommerce', 'image_preview'
    )
    list_filter = ('category', 'subcategory', 'brand', 'vendor', 'rating', 'publish_to_ecommerce')
    search_fields = ('name', 'custom_sku', 'system_id', 'ean', 'upc')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariationInline]
    readonly_fields = ('system_id', 'quantity_history')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'subcategory', 'brand', 'vendor', 'description', 'image')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price', 'default_cost', 'online_price')
        }),
        ('Stock & Tracking', {
            'fields': ('quantity', 'quantity_history')
        }),
        ('Identifiers', {
            'fields': ('system_id', 'ean', 'upc', 'custom_sku')
        }),
        ('E-commerce Visibility', {
            'fields': ('publish_to_ecommerce', 'options')
        }),
        ('Flags', {
            'fields': ('trending', 'best_selling', 'most_popular', 'just_arrived')
        }),
        ('Physical Properties (Default - Single)', {
            'fields': ('weight', 'length', 'width', 'height')
        }),
    )

    def get_stock(self, obj):
        """Calculate total stock from all variations based solely on stock_single."""
        if obj.variations.exists():
            return sum(obj.variations.values_list('stock_single', flat=True))
        return obj.quantity  # Fallback if no variations exist
    get_stock.short_description = "Total Stock"
    get_stock.admin_order_field = 'quantity'

    def image_preview(self, obj):
        """Show product image preview in admin."""
        if obj.image:
            return format_html('<img src="{}" width="50" style="border-radius:5px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Product Image'


@admin.register(ProductVariation)
class ProductVariationAdmin(admin.ModelAdmin):
    list_display = (
        'product', 'size', 'color', 'price_single', 'stock_single', 'variation_id',
        'bag_size', 'price_bag', 'box_size', 'price_box',
        'custom_sku', 'upc', 'ean'
    )
    list_filter = ('size', 'color')
    search_fields = (
        'product__name', 'size__name', 'color',
        'manufacturer_sku', 'custom_sku', 'upc', 'ean'
    )

    readonly_fields = ('variation_id',)  # This allows it to be displayed, not edited.

    fieldsets = (
        ('Basic Information', {
            'fields': ('product', 'size', 'color', 'image', 'variation_id')
        }),
        ('Pricing & Stock', {
            'fields': ('price_single', 'stock_single', 'discount_price')
        }),
        ('Packaging Conversion Factors', {
            'fields': ('bag_size', 'price_bag', 'box_size', 'price_box')
        }),
        ('Identifiers', {
            'fields': ('manufacturer_sku', 'custom_sku', 'upc', 'ean')
        }),
        ('Physical Properties (Single)', {
            'fields': ('weight', 'length', 'width', 'height')
        }),
        ('Physical Properties (Bag)', {
            'fields': ('bag_weight', 'bag_length', 'bag_width', 'bag_height')
        }),
        ('Physical Properties (Box)', {
            'fields': ('box_weight', 'box_length', 'box_width', 'box_height')
        }),
        ('Refund', {
            'fields': ('is_refundable',)
        }),
    )


@admin.register(BoxSize)
class BoxSizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_weight', 'length', 'width', 'height', 'volume')
    search_fields = ('name',)
    list_filter = ('max_weight',)

    def volume(self, obj):
        """Calculate and display the internal volume of the box."""
        return obj.length * obj.width * obj.height
    volume.short_description = "Volume"



### ✅ SIZE ADMIN ###
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


### ✅ PRICE LIST & PRICE RULE ADMIN ###
from .models import PriceList, PriceRule
from store.models import ProductVariation

class PriceListAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('products', 'product_variations')

admin.site.register(PriceList, PriceListAdmin)

from django.contrib import admin
from store.models import PriceRule

from django.contrib import admin
from store.models import PriceRule

@admin.register(PriceRule)
class PriceRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer_type', 'discount_percentage')
    list_filter = ('customer_type',)
    search_fields = ('name',)

    # Ensure all your ManyToMany fields appear here:
    filter_horizontal = (
        'apply_to_categories',
        'apply_to_subcategories',  # <--- This is for subcategories
        'apply_to_products',       # <--- This is for products
        'apply_to_variations',
        'exclude_products',
        'exclude_variations',
    )




# admin.py

from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'subject', 'message')
    ordering = ('-created_at',)
