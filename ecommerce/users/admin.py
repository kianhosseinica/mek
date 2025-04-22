from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, Wishlist
from .forms import CustomUserCreationForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    model = CustomUser
    list_display = ('phone_number', 'email', 'first_name', 'last_name', 'customer_type', 'is_staff', 'is_active', 'is_pos', 'display_profile_image')
    list_filter = ('customer_type', 'is_staff', 'is_active', 'is_pos')

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal Info', {'fields': (
            'email', 'first_name', 'last_name', 'company', 'birth_date',
            'country', 'address', 'address2', 'city', 'province', 'postal_code',
            'customer_type', 'profile_image', 'verification_code'  # ✅ add here
        )}),
        ('POS Information', {'fields': ('is_pos', 'pos_pin')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone_number', 'email', 'first_name', 'last_name', 'password1', 'password2',
                'is_staff', 'is_active', 'is_pos', 'pos_pin', 'profile_image'
            )
        }),
    )

    search_fields = ('phone_number', 'email', 'first_name', 'last_name')
    ordering = ('phone_number',)

    def display_profile_image(self, obj):
        """Display profile image in the Django Admin panel."""
        if obj.profile_image:
            return format_html('<img src="{}" width="40" height="40" style="border-radius:50%;" />', obj.profile_image.url)
        return "No Image"

    display_profile_image.short_description = "Profile Image"

admin.site.register(CustomUser, CustomUserAdmin)



class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    search_fields = ('user__phone_number', 'product__name')

admin.site.register(Wishlist, WishlistAdmin)
