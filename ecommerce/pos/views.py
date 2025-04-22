import re
import logging
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)
User = get_user_model()

def pos_login(request):
    """
    POS Login View:
    - Retrieves a user by email (if input contains '@') or by phone number.
    - For phone numbers, non-digit characters are removed.
    - Checks that the user has POS access (is_pos=True) and that the provided PIN matches the stored pos_pin.
    """
    if request.method == "POST":
        username_or_phone = request.POST.get("username_or_phone", "").strip()
        pin = request.POST.get("pin", "").strip()

        if not username_or_phone:
            logger.debug("No username or phone provided in POST data.")
            messages.error(request, "Please enter your phone number or email.")
            return render(request, "pos/login.html")

        user = None
        if "@" in username_or_phone:
            try:
                user = User.objects.get(email__iexact=username_or_phone)
            except User.DoesNotExist:
                user = None
                logger.debug("No user found with email: %s", username_or_phone)
        else:
            cleaned_phone = re.sub(r'\D', '', username_or_phone)
            logger.debug("Cleaned phone is: %s", cleaned_phone)
            if not cleaned_phone:
                logger.debug("Phone input after cleaning is empty.")
                messages.error(request, "Please enter a valid phone number.")
                return render(request, "pos/login.html")
            try:
                user = User.objects.get(phone_number=cleaned_phone)
            except User.DoesNotExist:
                user = None
                logger.debug("No user found with phone_number: %s", cleaned_phone)

        if user:
            if not user.is_pos:
                messages.error(request, "You do not have access to the POS system.")
                logger.debug("User exists but is not marked for POS access.")
            elif not user.is_active:
                messages.error(request, "Your account is inactive.")
                logger.debug("User is inactive.")
            else:
                if user.pos_pin and user.pos_pin == pin:
                    # Specify the backend explicitly when logging in.
                    login(request, user, backend='users.authentication.PhoneOrEmailBackend')
                    logger.debug("Login successful for user: %s", user)
                    return redirect("pos:dashboard")
                else:
                    logger.debug("Provided PIN '%s' does not match stored PIN '%s'", pin, user.pos_pin)
                    messages.error(request, "Invalid PIN.")
        else:
            messages.error(request, "Invalid login credentials. Please try again.")
    return render(request, "pos/login.html")

def dashboard(request):
    """
    POS Dashboard:
    Accessible only after a successful POS login.
    """
    return render(request, "pos/dashboard.html")



# pos/views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from users.models import CustomUser  # Adjust the import based on your project structure

@login_required
def pos_search_customers(request):
    query = request.GET.get("q", "")
    results = []
    if query:
        customers = CustomUser.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(email__icontains=query)
        )
        for customer in customers:
            results.append({
                "id": customer.id,
                "name": f"{customer.first_name} {customer.last_name}",
                "phone": customer.phone_number,
                "email": customer.email,
                "customer_type": getattr(customer, 'customer_type', 'regular')
            })
    return JsonResponse({"results": results})



# pos/views.py
from django.http import JsonResponse
from django.db.models import Q
from store.models import Product, ProductVariation


from django.db.models import Q
from django.http import JsonResponse


from django.db.models import Q
from django.http import JsonResponse
from store.models import Product, ProductVariation

from django.db.models import Q
from django.http import JsonResponse
from store.models import Product, ProductVariation, PriceRule


from django.db.models import Q
from django.http import JsonResponse
from store.models import Product, ProductVariation, PriceRule
from django.contrib.auth import get_user_model
User = get_user_model()

from django.db.models import Q
from django.http import JsonResponse
from store.models import Product, ProductVariation, PriceRule
from django.contrib.auth import get_user_model
User = get_user_model()

from django.db.models import Q
from django.http import JsonResponse
from store.models import Product, ProductVariation, PriceRule
from django.contrib.auth import get_user_model

User = get_user_model()

import logging
from django.http import JsonResponse
from django.db.models import Q
from store.models import Product, ProductVariation, PriceRule
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)

import re
import logging
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q
from store.models import Product, ProductVariation, PriceRule
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)

def pos_search_products(request):
    query = request.GET.get('q', '').strip()
    results = []
    logger.info("pos_search_products called with query: '%s'", query)

    # Helper function to calculate discounted price with logging.
    def calculate_discounted_price(base_price, discount_percentage):
        logger.info("Calculating discounted price: base_price=%s, discount_percentage=%s", base_price, discount_percentage)
        if discount_percentage and base_price is not None:
            discounted = base_price - (base_price * discount_percentage / 100)
            logger.info("Discounted price calculated: %s", discounted)
            return discounted
        return None

    # Retrieve the selected customer from GET parameters (if provided)
    selected_customer = None
    customer_id = request.GET.get('customer_id')
    if customer_id:
        try:
            selected_customer = User.objects.get(id=customer_id)
            logger.info("Selected customer: %s, customer_type: %s", selected_customer, getattr(selected_customer, 'customer_type', 'regular'))
        except User.DoesNotExist:
            logger.warning("Customer with id %s not found.", customer_id)
            selected_customer = None
    else:
        logger.info("No customer_id provided in the request.")

    # Look up the PriceRule for the selected customer (if any)
    discount_percentage = 0
    price_rule = None
    if (selected_customer and hasattr(selected_customer, 'customer_type')
            and selected_customer.customer_type != 'regular'):
        price_rule = PriceRule.objects.filter(customer_type=selected_customer.customer_type).first()
        if price_rule:
            discount_percentage = price_rule.discount_percentage
            logger.info("PriceRule found for customer_type '%s': %s, discount_percentage: %s",
                        selected_customer.customer_type, price_rule, discount_percentage)
        else:
            logger.info("No PriceRule found for customer_type: %s", selected_customer.customer_type)
    else:
        logger.info("Customer is either not selected or of type 'regular'; discount_percentage remains 0.")

    if query:
        # -------------------------------
        # 1) Search for plain Products (without variations)
        # -------------------------------
        product_matches = Product.objects.filter(
            Q(name__icontains=query) |
            Q(slug__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(subcategory__name__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(vendor__name__icontains=query) |
            Q(ean__icontains=query) |
            Q(upc__icontains=query) |
            Q(custom_sku__icontains=query) |
            Q(system_id__icontains=query)
        ).distinct().filter(variations__isnull=True)

        for product in product_matches:
            base_price = product.price
            # Determine eligibility as in your store app.
            eligible = False
            if discount_percentage and price_rule:
                eligible = (
                    (product.category in price_rule.apply_to_categories.all()) or
                    (product.subcategory in price_rule.apply_to_subcategories.all()) or
                    (price_rule.apply_to_price_list and product in price_rule.apply_to_price_list.products.all()) or
                    (product in price_rule.apply_to_products.all())
                ) and product not in price_rule.exclude_products.all()
            current_discount = discount_percentage if eligible else 0
            discounted = calculate_discounted_price(base_price, current_discount)
            logger.info("Product '%s': base_price=%s, eligible=%s, current_discount=%s, discounted=%s",
                        product.name, base_price, eligible, current_discount, discounted)
            results.append({
                "result_type": "product",
                "id": product.id,
                "name": product.name,
                "slug": product.slug,
                "description": product.description,
                "category": product.category.name if product.category else "",
                "subcategory": product.subcategory.name if product.subcategory else "",
                "brand": product.brand.name if product.brand else "",
                "vendor": product.vendor.name if product.vendor else "",
                "ean": product.ean,
                "upc": product.upc,
                "custom_sku": product.custom_sku,
                "system_id": product.system_id,
                "price": str(base_price),
                "discount_price": str(discounted) if discounted is not None else "",
                "image": product.image.url if product.image else "",
            })

        # -------------------------------
        # 2) Search for Variations.
        # -------------------------------
        variation_matches = ProductVariation.objects.filter(
            Q(color__icontains=query) |
            Q(size__name__icontains=query) |
            Q(manufacturer_sku__icontains=query) |
            Q(custom_sku__icontains=query) |
            Q(upc__icontains=query) |
            Q(ean__icontains=query) |
            Q(product__name__icontains=query)
        ).distinct()

        for variation in variation_matches:
            product = variation.product
            base_single = variation.price_single
            base_bag = variation.price_bag
            base_box = variation.price_box

            eligible = False
            if discount_percentage and price_rule:
                eligible = (
                    (product.category in price_rule.apply_to_categories.all()) or
                    (product.subcategory in price_rule.apply_to_subcategories.all()) or
                    (price_rule.apply_to_price_list and product in price_rule.apply_to_price_list.products.all()) or
                    (product in price_rule.apply_to_products.all())
                ) and product not in price_rule.exclude_products.all()
            current_discount = discount_percentage if eligible else 0

            discounted_single = calculate_discounted_price(base_single, current_discount)
            discounted_bag = calculate_discounted_price(base_bag, current_discount) if base_bag is not None else None
            discounted_box = calculate_discounted_price(base_box, current_discount) if base_box is not None else None

            logger.info("Variation for product '%s': base_single=%s, eligible=%s, current_discount=%s, discounted_single=%s",
                        product.name, base_single, eligible, current_discount, discounted_single)

            results.append({
                "result_type": "variation",
                "id": variation.id,
                "product": product.name,
                "manufacturer_sku": variation.manufacturer_sku,
                "custom_sku": variation.custom_sku,
                "upc": variation.upc,
                "ean": variation.ean,
                "price_single": str(base_single) if base_single is not None else "",
                "discounted_price_single": str(discounted_single) if discounted_single is not None else "",
                "stock_single": variation.stock_single,
                "bag_size": variation.bag_size,
                "price_bag": str(base_bag) if base_bag is not None else "",
                "discounted_price_bag": str(discounted_bag) if discounted_bag is not None else "",
                "box_size": variation.box_size,
                "price_box": str(base_box) if base_box is not None else "",
                "discounted_price_box": str(discounted_box) if discounted_box is not None else "",
                "image": variation.image.url if variation.image else "",
                "size": variation.size.name if variation.size else "",
                "color": variation.color if variation.color else ""
            })

    logger.info("pos_search_products returning %d results", len(results))
    return JsonResponse({"results": results})














