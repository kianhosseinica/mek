from django.contrib import admin
from django.utils.html import format_html
from .models import *
from mptt.admin import MPTTModelAdmin
from .models import Category, SubCategory
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import MPTTModelAdmin
from .models import Category
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from django.contrib import admin
from django.utils.html import format_html
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from mptt.admin import MPTTModelAdmin
# Define these before you register them in admin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Product, Category, SubCategory, Brand, Vendor

from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.results import RowResult
from .models import Product, Category, SubCategory, Brand, Vendor

class ProductResource(resources.ModelResource):
    report_skipped = True
    skip_unchanged = True

    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'name')
    )
    subcategory = fields.Field(
        column_name='subcategory',
        attribute='subcategory',
        widget=ForeignKeyWidget(SubCategory, 'name')
    )
    brand = fields.Field(
        column_name='brand',
        attribute='brand',
        widget=ForeignKeyWidget(Brand, 'name')
    )
    vendor = fields.Field(
        column_name='vendor',
        attribute='vendor',
        widget=ForeignKeyWidget(Vendor, 'name')
    )

    class Meta:
        model = Product
        import_id_fields = ['system_id']
        skip_unchanged = True
        report_skipped = True
        fields = (
            'system_id', 'name', 'slug', 'category', 'subcategory', 'brand', 'vendor',
            'price', 'discount_price', 'default_cost', 'online_price', 'quantity',
            'ean', 'upc', 'custom_sku', 'publish_to_ecommerce', 'description',
            'additional_info', 'trending', 'best_selling', 'most_popular', 'just_arrived',
            'rating', 'is_refundable', 'weight', 'length', 'width', 'height'
        )

    def import_row(self, row, instance_loader, **kwargs):
        """
        Custom error handler to show clearer, more readable error messages.
        """
        try:
            return super().import_row(row, instance_loader, **kwargs)
        except Exception as e:
            row_result = RowResult()
            row_result.errors.append((
                "Import Error",
                f"Row failed: {dict(row)}\nReason: {str(e)}"
            ))
            return row_result




class ProductVariationResource(resources.ModelResource):
    product = fields.Field(
        column_name='product',
        attribute='product',
        widget=ForeignKeyWidget(Product, 'system_id')
    )
    size = fields.Field(
        column_name='size',
        attribute='size',
        widget=ForeignKeyWidget(Size, 'name')
    )

    class Meta:
        model = ProductVariation
        import_id_fields = ['variation_id']
        skip_unchanged = True
        report_skipped = True
        fields = (
            'variation_id', 'product', 'size', 'color', 'price_single', 'stock_single',
            'bag_size', 'price_bag', 'box_size', 'price_box',
            'manufacturer_sku', 'custom_sku', 'upc', 'ean',
        )


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    """Category Admin with a tree view, displaying subcategories properly."""
    list_display = ('name', 'parent', 'stock_threshold', 'image_preview', 'slug')
    list_filter = ('parent',)
    search_fields = ('name', 'parent__name')
    prepopulated_fields = {'slug': ('name',)}
    mptt_level_indent = 20  # Indents subcategories in the admin panel
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'parent', 'image')
        }),
        ('Stock Settings', {
            'fields': ('stock_threshold',)
        }),
    )

    def image_preview(self, obj):
        """Show category image preview in admin, handling missing images."""
        if obj.image:
            return format_html('<img src="{}" width="50" style="border-radius:5px;" />', obj.image.url)
        return "No Image"

    image_preview.short_description = 'Image Preview'

    def get_queryset(self, request):
        """Ensure proper ordering of categories and subcategories."""
        return super().get_queryset(request).order_by('parent', 'name')

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

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 50px; max-height: 50px;" />', obj.image.url)
        return "-"
    image_thumbnail.short_description = 'Image'

    def get_queryset(self, request):
        """Ensure proper ordering for nested subcategories."""
        return super().get_queryset(request).order_by('category', 'parent', 'name')

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

# ProductVariation Inline
# Updated ProductVariation Inline
class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1
    fields = (
        'size', 'color', 'price_single', 'default_cost', 'stock_single', 'discount_price',
        'bag_size', 'price_bag', 'box_size', 'price_box', 'image', 'variation_id'
    )
    readonly_fields = ('variation_id',)

# Updated Product Admin
@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = (
        'name', 'category', 'subcategory', 'brand', 'vendor', 'price',
        'online_price', 'default_cost', 'get_stock', 'rating',
        'system_id', 'publish_to_ecommerce', 'image_preview'
    )
    list_filter = (
        'category', 'subcategory', 'brand', 'vendor', 'publish_to_ecommerce',
        'trending', 'best_selling', 'most_popular', 'just_arrived'
    )
    search_fields = ('name', 'custom_sku', 'system_id', 'ean', 'upc', 'description', 'additional_info')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariationInline]
    readonly_fields = ('system_id', 'quantity_history')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'subcategory', 'brand', 'vendor', 'description', 'additional_info', 'image')
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
        ('Popularity Flags', {
            'fields': ('rating', 'trending', 'best_selling', 'most_popular', 'just_arrived')
        }),
        ('Physical Properties', {
            'fields': ('weight', 'length', 'width', 'height')
        }),
        ('Refund', {
            'fields': ('is_refundable',)
        }),
    )

    def get_stock(self, obj):
        if obj.variations.exists():
            return sum(v.stock_single for v in obj.variations.all())
        return obj.quantity
    get_stock.short_description = "Total Stock"
    get_stock.admin_order_field = 'quantity'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" style="border-radius:5px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Product Image'

# Updated ProductVariation Admin
@admin.register(ProductVariation)
class ProductVariationAdmin(ImportExportModelAdmin):
    resource_class = ProductVariationResource

    list_display = (
        'product', 'size', 'color', 'price_single', 'default_cost', 'stock_single',
        'variation_id', 'bag_size', 'price_bag', 'box_size', 'price_box', 'image_preview'
    )
    list_filter = ('size', 'color', 'product__category', 'product__brand')
    search_fields = (
        'product__name', 'size__name', 'color', 'variation_id',
        'manufacturer_sku', 'custom_sku', 'upc', 'ean'
    )
    readonly_fields = ('variation_id',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('product', 'size', 'color', 'image', 'variation_id')
        }),
        ('Pricing & Stock', {
            'fields': ('price_single', 'default_cost', 'stock_single', 'discount_price')
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

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" style="border-radius:5px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Variation Image'



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


