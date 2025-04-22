from django.shortcuts import render
from .models import *
from django.shortcuts import render, get_object_or_404
from .models import Product, ProductVariation
import logging
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
# Homepage
from django.shortcuts import render
from .models import Brand, Category, Product
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from store.models import ProductVariation
from cart.models import *
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.conf import settings
from orders.models import Order
from cart.models import CartItem, Cart
import uuid
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
from .models import Order

def index(request):
    brands = Brand.objects.all()  # Fetch all brands
    new_brands = Brand.objects.filter(is_new=True)  # Fetch only new brands
    categories = Category.objects.all()  # Fetch all categories

    # Fetching product types
    trending_products = Product.objects.filter(trending=True)  # Fetch only trending products
    best_selling_products = Product.objects.filter(best_selling=True)
    most_popular_products = Product.objects.filter(most_popular=True)
    just_arrived_products = Product.objects.filter(just_arrived=True)

    context = {
        'brands': brands,
        'new_brands': new_brands,
        'categories': categories,
        'trending_products': trending_products,
        'best_selling_products': best_selling_products,
        'most_popular_products': most_popular_products,
        'just_arrived_products': just_arrived_products,
    }

    return render(request, 'store/index.html', context)


# Shop (Product Listing)
from django.shortcuts import render
from .models import Product, Category, Brand

from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Brand

def shop(request):
    # Start with all products
    products = Product.objects.all()
    categories = Category.objects.all()
    brands = Brand.objects.all()

    # Filter by category if a query parameter is provided.
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(
            Q(category__slug=category_slug) | Q(subcategory__slug=category_slug)
        )

    # High-level search:
    # This will search in the product name, description,
    # as well as in variation fields (size and color).
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(variations__size__name__icontains=query) |
            Q(variations__color__icontains=query)
        ).distinct()  # distinct to remove duplicate products if multiple variations match

    # Sorting logic
    sort_option = request.GET.get('sort')
    if sort_option == 'name_asc':
        products = products.order_by('name')
    elif sort_option == 'name_desc':
        products = products.order_by('-name')
    elif sort_option == 'price_asc':
        products = products.order_by('price')
    elif sort_option == 'price_desc':
        products = products.order_by('-price')
    elif sort_option == 'rating_desc':
        products = products.order_by('-rating')

    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
    }
    return render(request, 'store/shop.html', context)




# Single Product Page

from django.shortcuts import render, get_object_or_404
from .models import Product, ProductVariation


from django.shortcuts import render, get_object_or_404
from .models import Product, ProductVariation


from django.shortcuts import render, get_object_or_404
from .models import Product, ProductVariation

from django.shortcuts import render, get_object_or_404
from store.models import Product

from django.shortcuts import render, get_object_or_404
from decimal import Decimal
from store.models import Product, PriceRule


from django.shortcuts import render, get_object_or_404
from store.models import Product, PriceRule
from decimal import Decimal

from django.shortcuts import render, get_object_or_404
from store.models import Product, PriceRule, ProductVariation
from decimal import Decimal


from urllib.parse import unquote  # Import unquote at the top

from urllib.parse import unquote  # Import unquote at the top

def single_product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    logger = logging.getLogger(__name__)

    # Log product details
    logger.info("Displaying product: %s | System ID: %s", product.name, product.system_id)

    def apply_discount(price, discount):
        return price - ((price * discount) / 100) if price is not None else None

    # Get all available sizes and colors from variations
    available_sizes = list(product.variations.values_list('size__name', flat=True).distinct())
    available_colors = (
        list(product.variations.values_list('color', flat=True).distinct())
        if product.variations.exclude(color__isnull=True).exists() else []
    )
    logger.info("Initial available sizes: %s", available_sizes)
    logger.info("Initial available colors: %s", available_colors)

    # Retrieve and clean GET parameters
    selected_size = request.GET.get('size')
    logger.info("Raw selected_size from GET: %s", selected_size)
    if selected_size:
        # Decode percent-encoded data then strip whitespace and extraneous quotes (if any)
        selected_size = unquote(selected_size).strip()
        # Log the cleaned value before normalization
        logger.info("Cleaned selected_size before normalization: %s", selected_size)
        # If our available sizes always end with a double quote, then ensure it too:
        if not selected_size.endswith('"'):
            selected_size = selected_size + '"'
            logger.info("Normalized selected_size to: %s", selected_size)
    raw_color = request.GET.get('color')
    logger.info("Raw selected_color from GET: %s", raw_color)
    selected_color = raw_color if (raw_color and raw_color != "None") else None
    logger.info("Final selected_color: %s", selected_color)

    selected_variation = None
    variation_details = {}
    selected_variation_images = []

    if product.variations.exists():
        logger.info("Product %s has variations.", product.name)

        # Attempt to find a matching variation based on selected size and color
        if available_colors:
            logger.info("Looking for variation with size='%s' and color='%s'", selected_size, selected_color)
            selected_variation = product.variations.filter(size__name=selected_size, color=selected_color).first()
        else:
            logger.info("Looking for variation with size='%s'", selected_size)
            selected_variation = product.variations.filter(size__name=selected_size).first()

        # If no matching variation is found, try to default to the first variation for the selected size
        if not selected_variation:
            if selected_size:
                variations_with_size = product.variations.filter(size__name=selected_size)
                if variations_with_size.exists():
                    selected_variation = variations_with_size.first()
                    old_color = selected_color
                    selected_color = selected_variation.color
                    logger.info("No matching variation for size '%s' with color '%s'; defaulting color from '%s' to '%s'.",
                                selected_size, raw_color, old_color, selected_color)
                else:
                    selected_variation = product.variations.first()
                    selected_size = selected_variation.size.name
                    if available_colors:
                        selected_color = selected_variation.color
                    logger.info("Selected size '%s' not found; defaulting to first variation with size '%s'.",
                                selected_size, selected_variation.size.name)
            else:
                selected_variation = product.variations.first()
                if selected_variation:
                    selected_size = selected_variation.size.name
                    if available_colors:
                        selected_color = selected_variation.color
                logger.info("No size selected; defaulting to first variation.")

        if selected_variation:
            logger.info("Selected Variation: %s | Variation ID: %s | Size: %s | Color: %s",
                        selected_variation.product.name,
                        selected_variation.variation_id,
                        selected_variation.size.name,
                        selected_variation.color or "N/A")
        else:
            logger.warning("No variation selected for product %s", product.name)

        # Re-filter available colors based on the (normalized) selected size
        if selected_size:
            available_colors = list(
                product.variations.filter(size__name=selected_size)
                .values_list('color', flat=True)
                .distinct()
            )
            logger.info("Available colors after filtering by size '%s': %s", selected_size, available_colors)

        discount_percentage = 0
        if (request.user.is_authenticated and hasattr(request.user, 'customer_type')
                and request.user.customer_type != 'regular'):
            price_rule = PriceRule.objects.filter(customer_type=request.user.customer_type).first()
            if price_rule:
                eligible = (
                    product.category in price_rule.apply_to_categories.all() or
                    product.subcategory in price_rule.apply_to_subcategories.all() or
                    (price_rule.apply_to_price_list and product in price_rule.apply_to_price_list.products.all()) or
                    product in price_rule.apply_to_products.all()
                ) and product not in price_rule.exclude_products.all()
                if eligible:
                    discount_percentage = price_rule.discount_percentage
                    logger.info("Discount applicable: %s%%", discount_percentage)

        if selected_variation:
            price_single = selected_variation.price_single
            price_bag = selected_variation.price_bag
            price_box = selected_variation.price_box

            discounted_price_single = apply_discount(price_single, discount_percentage)
            discounted_price_bag = (apply_discount(price_bag, discount_percentage)
                                    if price_bag is not None else None)
            discounted_price_box = (apply_discount(price_box, discount_percentage)
                                    if price_box is not None else None)

            available_bags = (selected_variation.stock_single // selected_variation.bag_size) \
                if selected_variation.bag_size > 0 else 0
            available_boxes = (selected_variation.stock_single // selected_variation.box_size) \
                if selected_variation.box_size > 0 else 0

            variation_details = {
                'price_single': price_single,
                'discounted_price_single': discounted_price_single,
                'stock_single': selected_variation.stock_single,
                'price_bag': price_bag,
                'discounted_price_bag': discounted_price_bag,
                'bag_size': selected_variation.bag_size,
                'available_bags': available_bags,
                'price_box': price_box,
                'discounted_price_box': discounted_price_box,
                'box_size': selected_variation.box_size,
                'available_boxes': available_boxes,
                'image': (selected_variation.image.url
                          if selected_variation.image
                          else (product.image.url if product.image else None))
            }
            if variation_details.get('image'):
                selected_variation_images = [variation_details['image']]
    else:
        logger.info("Product %s has no variations; using product-level details.", product.name)
        available_sizes = []
        available_colors = []
        selected_size = None
        selected_color = None

        discount_percentage = 0
        if (request.user.is_authenticated and hasattr(request.user, 'customer_type')
                and request.user.customer_type != 'regular'):
            price_rule = PriceRule.objects.filter(customer_type=request.user.customer_type).first()
            if price_rule:
                eligible = (
                    product.category in price_rule.apply_to_categories.all() or
                    product.subcategory in price_rule.apply_to_subcategories.all() or
                    (price_rule.apply_to_price_list and product in price_rule.apply_to_price_list.products.all()) or
                    product in price_rule.apply_to_products.all()
                ) and product not in price_rule.exclude_products.all()
                if eligible:
                    discount_percentage = price_rule.discount_percentage
                    logger.info("Discount applicable for plain product: %s%%", discount_percentage)

        price_single = product.price
        discounted_price_single = apply_discount(price_single, discount_percentage)
        variation_details = {
            'price_single': price_single,
            'discounted_price_single': discounted_price_single,
            'stock_single': product.quantity,
            'price_bag': None,
            'discounted_price_bag': None,
            'bag_size': None,
            'available_bags': 0,
            'price_box': None,
            'discounted_price_box': None,
            'box_size': None,
            'available_boxes': 0,
            'image': product.image.url if product.image else None
        }
        if variation_details.get('image'):
            selected_variation_images = [variation_details['image']]
        logger.info("Using plain product details for %s | System ID: %s", product.name, product.system_id)

    context = {
        'product': product,
        'available_sizes': available_sizes,         # All sizes remain available
        'available_colors': available_colors,         # Filtered by selected size if provided
        'selected_variation': selected_variation,
        'selected_size': selected_size,
        'selected_color': selected_color,
        'variation_details': variation_details,
        'selected_variation_images': selected_variation_images,
    }
    logger.info("Final context: %s", context)
    return render(request, 'store/single-product.html', context)









# Cart Page
from django.shortcuts import render

from django.shortcuts import render
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

@login_required
def cart(request):
    """
    Display the user's cart, enforce bag/box increments, and calculate totals.
    Uses Decimal for currency calculations.
    Handles both items with variations and plain product items.
    """
    logger.info("🛍 [CART VIEW] Request received from user: %s",
                request.user if request.user.is_authenticated else "Guest")

    cart = None
    cart_items = []
    cart_total = Decimal("0.00")

    try:
        # Determine the correct cart based on authentication or session.
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
            logger.info("✅ Cart Retrieved for User: %s", request.user.username if cart else "No cart found for user")
        else:
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
                logger.info("✅ New session created: %s", session_id)
            cart = Cart.objects.filter(session_id=session_id).first()
            logger.info("✅ Cart Retrieved for Session: %s", session_id if cart else "No cart found for session")

        # Process cart items if a cart exists.
        if cart:
            cart_items = cart.items.all()
            logger.info("🛒 Cart Items Found: %d", cart_items.count())

            total_quantity = 0  # Total number of single units in cart.
            for item in cart_items:
                # Determine step size based on purchase type.
                if item.product_variation:
                    if item.purchase_type.lower() == "bag":
                        step = item.product_variation.bag_size
                    elif item.purchase_type.lower() == "box":
                        step = item.product_variation.box_size
                    else:
                        step = 1
                else:
                    # Plain product branch – step is 1.
                    step = 1

                # Ensure quantity is a multiple of the step value.
                if item.quantity % step != 0:
                    corrected_quantity = (item.quantity // step) * step
                    if item.product_variation:
                        product_name = item.product_variation.product.name
                    else:
                        product_name = item.product.name
                    logger.warning("⚠️ Quantity for %s adjusted from %d to %d (must be in multiples of %d)",
                                   product_name, item.quantity, corrected_quantity, step)
                    item.quantity = corrected_quantity
                    item.save()
                    messages.warning(request,
                        f"⚠️ Quantity for {product_name} adjusted to {corrected_quantity} (must be in multiples of {step}).")
                total_quantity += item.quantity

                # Log details using variation fields if available; otherwise, use plain product fields.
                if item.product_variation:
                    product_name = item.product_variation.product.name
                    variation_size = item.product_variation.size.name
                    variation_color = item.product_variation.color or "N/A"
                else:
                    product_name = item.product.name
                    variation_size = "N/A"
                    variation_color = "N/A"

                logger.info(
                    "📦 Product: %s | Variation: %s | Color: %s | Quantity: %d | Step: %d | Type: %s | Price: $%.2f",
                    product_name,
                    variation_size,
                    variation_color,
                    item.quantity,
                    step,
                    item.purchase_type,
                    item.total_price()
                )

            logger.info("🔢 Total number of single units in cart: %d", total_quantity)

            # Calculate cart total using Decimal arithmetic.
            cart_total = sum(item.total_price() for item in cart_items)
            logger.info("💰 Cart Total: $%.2f", cart_total)
        else:
            logger.info("🛒 No cart items found.")

    except Exception as e:
        logger.error("❌ [ERROR] Exception in cart view: %s", str(e), exc_info=True)
        messages.error(request, "An error occurred while fetching your cart.")
        cart_items = []
        cart_total = Decimal("0.00")

    return render(request, 'store/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'cart_total': cart_total,
    })





from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from decimal import Decimal
import uuid

# Checkout Page
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from decimal import Decimal
import uuid
from .models import *

import uuid
import json
import requests
from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse

PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com" if settings.PAYPAL_MODE == "sandbox" else "https://api-m.paypal.com"


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
import uuid
from decimal import Decimal
import json

from .models import Order, OrderItem


logger = logging.getLogger(__name__)  # <-- Use your preferred logger name


import uuid
import requests
from decimal import Decimal
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from orders.models import Order, OrderItem
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@login_required
def checkout(request):
    """Checkout View – Handles order creation & PayPal Smart Buttons.
       Uses front-end–submitted totals (subtotal, tax_amount, shipping_price, total) for order creation.
       Deducts stock_single based on the total cart quantity per product variation.
    """
    logger.info("==[CHECKOUT VIEW]== Start | Method: %s | User: %s", request.method, request.user)
    TAX_RATE = Decimal("0.13")  # (Not used if totals come from front end)

    # --- Stock validation ---
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect("store:cart")

    for item in cart.items.all():
        if item.product_variation:
            if item.quantity > item.product_variation.stock_single:
                messages.error(
                    request,
                    f"Insufficient stock for {item.product_variation.product.name} ({item.purchase_type}). "
                    f"Requested: {item.quantity}, Available: {item.product_variation.stock_single}."
                )
                return redirect("store:cart")
        else:
            if item.quantity > item.product.quantity:
                messages.error(
                    request,
                    f"Insufficient stock for {item.product.name}. "
                    f"Requested: {item.quantity}, Available: {item.product.quantity}."
                )
                return redirect("store:cart")

    # --- PayPal return branch ---
    paypal_order_id = request.GET.get("paymentId") or request.GET.get("paypal_order_id") or request.GET.get("token")
    payer_id = request.GET.get("PayerID")
    token    = request.GET.get("token")
    logger.info("PayPal return params -> paypal_order_id=%s, payer_id=%s, token=%s", paypal_order_id, payer_id, token)

    if paypal_order_id and payer_id and token:
        logger.info("Detected PayPal success parameters.")
        order = Order.objects.filter(paypal_order_id=paypal_order_id, user=request.user).first()

        if not order:
            logger.info("No existing order found. Using front-end totals from session checkout data.")
            checkout_data   = request.session.get("checkout_data", {})
            subtotal        = Decimal(checkout_data.get("subtotal",       "0.00"))
            tax_amount      = Decimal(checkout_data.get("tax_amount",     "0.00"))
            shipping_price  = Decimal(checkout_data.get("shipping_price", "0.00"))
            total           = Decimal(checkout_data.get("total",          "0.00"))
            logger.info("Front-end totals -> Subtotal=%.2f, Tax=%.2f, Shipping=%.2f, Total=%.2f",
                        subtotal, tax_amount, shipping_price, total)

            # billing details
            first_name  = checkout_data.get("firstname", request.user.first_name)
            last_name   = checkout_data.get("lastname",  request.user.last_name)
            company     = checkout_data.get("companyname", "")
            country     = checkout_data.get("country",    "Canada")
            address1    = checkout_data.get("address1",   "Not Provided")
            address2    = checkout_data.get("address2",   "")
            city        = checkout_data.get("city",       "Unknown")
            state       = checkout_data.get("state",      "Unknown")
            zip_code    = checkout_data.get("zip",        "00000")
            phone       = checkout_data.get("phone",      "000-000-0000")
            email       = checkout_data.get("email",      request.user.email)
            notes       = checkout_data.get("order_notes","")
            fulfillment = checkout_data.get("fulfillment_method", "pickup")

            # shipping details
            ship_fn = checkout_data.get("shipping_firstname", "")
            ship_ln = checkout_data.get("shipping_lastname",  "")
            ship_co = checkout_data.get("shipping_companyname", "")
            ship_a1 = checkout_data.get("shipping_address1","")
            ship_a2 = checkout_data.get("shipping_address2","")
            ship_city= checkout_data.get("shipping_city","")
            ship_st = checkout_data.get("shipping_state","")
            ship_zip= checkout_data.get("shipping_zip","")
            ship_ph= checkout_data.get("shipping_phone","")
            ship_em= checkout_data.get("shipping_email","")

            order = Order.objects.create(
                user=request.user,
                order_id=uuid.uuid4(),
                paypal_order_id=paypal_order_id,
                first_name=first_name,
                last_name=last_name,
                company_name=company,
                country=country,
                address1=address1,
                address2=address2,
                city=city,
                state=state,
                zip_code=zip_code,
                phone=phone,
                email=email,
                order_notes=notes,
                subtotal=subtotal,
                tax_amount=tax_amount,
                total_price=total,
                payment_method="paypal",
                fulfillment_method=fulfillment,
                status="Paid",
                shipping_cost=shipping_price,
                shipping_first_name=ship_fn,
                shipping_last_name=ship_ln,
                shipping_company=ship_co,
                shipping_address1=ship_a1,
                shipping_address2=ship_a2,
                shipping_city=ship_city,
                shipping_state=ship_st,
                shipping_zip_code=ship_zip,
                shipping_phone=ship_ph,
                shipping_email=ship_em,
            )
            logger.info("Order created successfully -> order_id=%s", order.order_id)

            # create items & deduct stock
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product_variation=item.product_variation,
                    product=item.product if item.product_variation is None else None,
                    purchase_type=item.purchase_type,
                    quantity=item.quantity,
                    price=item.unit_price(),
                    total_price=item.total_price(),
                    is_refundable=(
                        item.product_variation.is_refundable
                        if item.product_variation
                        else item.product.is_refundable
                    ),
                )
                if item.product_variation:
                    item.product_variation.stock_single -= item.quantity
                    item.product_variation.save()
                else:
                    item.product.quantity -= item.quantity
                    item.product.save()

            cart.items.all().delete()
            messages.success(request, "Your PayPal order has been placed successfully!")
        else:
            logger.info("Order with PayPal ID %s already exists.", paypal_order_id)

        # capture PayPal payment...
        try:
            # 1) Get an access token
            auth_resp = requests.post(
                f"{PAYPAL_API_BASE}/v1/oauth2/token",
                headers={"Accept": "application/json", "Accept-Language": "en_US"},
                data={"grant_type": "client_credentials"},
                auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
            )
            auth_resp.raise_for_status()
            access_token = auth_resp.json().get("access_token")

            # 2) Capture the order
            cap_resp = requests.post(
                f"{PAYPAL_API_BASE}/v2/checkout/orders/{paypal_order_id}/capture",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
            )
            cap_data = cap_resp.json()
            if cap_resp.status_code == 201 and cap_data.get("status") == "COMPLETED":
                capture_id = cap_data["purchase_units"][0]["payments"]["captures"][0]["id"]
                order.paypal_capture_id = capture_id
                order.save()
                logger.info("✅ PayPal capture succeeded: %s", capture_id)
            else:
                logger.error("🚨 PayPal capture failed: %s", cap_data)
        except Exception as e:
            logger.exception("Exception during PayPal capture: %s", str(e))

        return redirect(reverse("store:order_success", args=[str(order.order_id)]))

    # --- Standard POST branch (including PayPal session setup) ---
    if request.method == "POST":
        logger.info("Handling POST request for user %s", request.user)
        # billing
        first_name   = request.POST.get("firstname")
        last_name    = request.POST.get("lastname")
        company_name = request.POST.get("companyname", "")
        country      = request.POST.get("country", "Canada")
        address1     = request.POST.get("address1")
        address2     = request.POST.get("address2", "")
        city         = request.POST.get("city")
        state        = request.POST.get("state")
        zip_code     = request.POST.get("zip")
        phone        = request.POST.get("phone")
        email        = request.POST.get("email")
        notes        = request.POST.get("order_notes", "")
        payment_method = request.POST.get("payment_method")
        fulfillment    = request.POST.get("fulfillment_method", "pickup")

        # shipping (optional)
        ship_fn = request.POST.get("shipping_firstname", "")
        ship_ln = request.POST.get("shipping_lastname",  "")
        ship_co = request.POST.get("shipping_companyname","")
        ship_a1 = request.POST.get("shipping_address1","")
        ship_a2 = request.POST.get("shipping_address2","")
        ship_city= request.POST.get("shipping_city","")
        ship_st = request.POST.get("shipping_state","")
        ship_zip= request.POST.get("shipping_zip","")
        ship_ph= request.POST.get("shipping_phone","")
        ship_em= request.POST.get("shipping_email","")

        # ← pull the four hidden fields directly
        subtotal       = Decimal(request.POST["subtotal"])
        tax_amount     = Decimal(request.POST["tax_amount"])
        shipping_price = Decimal(request.POST["shipping_price"])
        total          = Decimal(request.POST["total"])
        logger.info("POST totals from front end -> Subtotal=%.2f, Tax=%.2f, Shipping=%.2f, Total=%.2f",
                    subtotal, tax_amount, shipping_price, total)

        # save for PayPal branch
        request.session["checkout_data"] = {
            "firstname":          first_name,
            "lastname":           last_name,
            "companyname":        company_name,
            "country":            country,
            "address1":           address1,
            "address2":           address2,
            "city":               city,
            "state":              state,
            "zip":                zip_code,
            "phone":              phone,
            "email":              email,
            "order_notes":        notes,
            "fulfillment_method": fulfillment,
            "shipping_firstname": ship_fn,
            "shipping_lastname":  ship_ln,
            "shipping_companyname": ship_co,
            "shipping_address1":  ship_a1,
            "shipping_address2":  ship_a2,
            "shipping_city":      ship_city,
            "shipping_state":     ship_st,
            "shipping_zip":       ship_zip,
            "shipping_phone":     ship_ph,
            "shipping_email":     ship_em,
            "subtotal":           str(subtotal),
            "tax_amount":         str(tax_amount),
            "shipping_price":     str(shipping_price),
            "total":              str(total),
        }
        logger.info("Stored checkout data in session: %s", request.session["checkout_data"])

        if payment_method == "paypal":
            return JsonResponse({"message": "session_stored"})

        # non-PayPal order creation
        order = Order.objects.create(
            user=request.user,
            order_id=uuid.uuid4(),
            first_name=first_name,
            last_name=last_name,
            company_name=company_name,
            country=country,
            address1=address1,
            address2=address2,
            city=city,
            state=state,
            zip_code=zip_code,
            phone=phone,
            email=email,
            order_notes=notes,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_price=total,
            payment_method=payment_method,
            fulfillment_method=fulfillment,
            status="Paid",
            shipping_cost=shipping_price,
            shipping_first_name=ship_fn,
            shipping_last_name=ship_ln,
            shipping_company=ship_co,
            shipping_address1=ship_a1,
            shipping_address2=ship_a2,
            shipping_city=ship_city,
            shipping_state=ship_st,
            shipping_zip_code=ship_zip,
            shipping_phone=ship_ph,
            shipping_email=ship_em,
        )
        logger.info("Created order immediately -> order_id=%s, user=%s", order.order_id, request.user)
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product_variation=item.product_variation,
                product=item.product if item.product_variation is None else None,
                purchase_type=item.purchase_type,
                quantity=item.quantity,
                price=item.unit_price(),
                total_price=item.total_price(),
                is_refundable=(
                    item.product_variation.is_refundable
                    if item.product_variation
                    else item.product.is_refundable
                ),
            )
            if item.product_variation:
                item.product_variation.stock_single -= item.quantity
                item.product_variation.save()
            else:
                item.product.quantity -= item.quantity
                item.product.save()
        cart.items.all().delete()

        messages.success(request, "Your order has been placed successfully!")
        return redirect(reverse("store:order_success", args=[str(order.order_id)]))

    # --- GET branch: initial render ---
    logger.info("Handling GET request -> user=%s", request.user)
    subtotal   = sum(item.total_price() for item in cart.items.all()) if cart.items.exists() else Decimal(0)
    tax_amount = (subtotal * TAX_RATE).quantize(Decimal("0.01"))
    total      = (subtotal + tax_amount).quantize(Decimal("0.01"))
    PAYPAL_CLIENT_ID = getattr(settings, "PAYPAL_CLIENT_ID", "sandbox_fallback_id_here")
    return render(request, "store/checkout.html", {
        "subtotal":     subtotal,
        "tax_amount":   tax_amount,
        "total":        total,
        "PAYPAL_CLIENT_ID": PAYPAL_CLIENT_ID,
    })
























import json
import json
import uuid
import paypalrestsdk
from django.http import JsonResponse
from django.conf import settings

import json
import paypalrestsdk
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

PAYPAL_API_BASE = (
    "https://api-m.sandbox.paypal.com"
    if settings.PAYPAL_MODE == "sandbox"
    else "https://api-m.paypal.com"
)



# ✅ Configure PayPal SDK
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # "sandbox" or "live"
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

logger = logging.getLogger(__name__)

import logging
import json
import paypalrestsdk

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

logger = logging.getLogger(__name__)


@csrf_exempt
def create_paypal_order(request):
    """Creates a PayPal Order via the v2 Orders API and returns the approval URL."""
    logger.info("==[CREATE_PAYPAL_ORDER]== Request Method: %s", request.method)

    if request.method != "POST":
        logger.warning("Invalid request method: %s", request.method)
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
        logger.info("Received JSON data: %s", data)

        total_price = float(data.get("total", 0.00))
        logger.info("Parsed total_price: %.2f", total_price)
        if total_price <= 0:
            logger.warning("Invalid total amount: %.2f", total_price)
            return JsonResponse({"error": "Invalid total amount"}, status=400)

        # Determine PayPal base URL from mode
        base = "https://api-m.sandbox.paypal.com" if settings.PAYPAL_MODE == "sandbox" else "https://api-m.paypal.com"

        # 1) Obtain OAuth2 access token from PayPal
        auth_response = requests.post(
            f"{base}/v1/oauth2/token",
            data={"grant_type": "client_credentials"},
            auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET)
        )
        auth_response.raise_for_status()
        access_token = auth_response.json()["access_token"]
        logger.info("Obtained access token from PayPal.")

        # 2) Create an order using the v2 Orders API
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": "CAD",
                    "value": f"{total_price:.2f}"
                },
                "description": "Order Payment"
            }],
            "application_context": {
                "return_url": request.build_absolute_uri(reverse("store:checkout")),
                "cancel_url": request.build_absolute_uri(reverse("store:checkout"))
            }
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        create_response = requests.post(f"{base}/v2/checkout/orders", headers=headers, json=payload)
        create_response.raise_for_status()
        response_data = create_response.json()
        logger.info("Create Order response data: %s", response_data)

        # 3) Extract order ID & approval URL
        order_id = response_data["id"]
        approval_url = next((link["href"] for link in response_data.get("links", []) if link.get("rel") == "approve"), None)
        logger.info("Order created successfully. ID: %s, Approval URL: %s", order_id, approval_url)

        return JsonResponse({"id": order_id, "approval_url": approval_url}, status=200)

    except requests.HTTPError as http_err:
        logger.exception("PayPal HTTP error: %s", http_err)
        return JsonResponse({"error": "PayPal API error"}, status=400)
    except json.JSONDecodeError as e:
        logger.exception("JSON decoding error: %s", e)
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        logger.exception("Unexpected exception: %s", e)
        return JsonResponse({"error": str(e)}, status=500)




import requests
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings

from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import requests
import json
import uuid
from decimal import Decimal
from django.urls import reverse
from django.conf import settings

from django.http import JsonResponse
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
import requests
from django.urls import reverse
import json
import uuid
from decimal import Decimal

@login_required
def capture_paypal_order(request):
    """Captures PayPal payment after approval and updates the Order with the capture ID."""
    logger.info("==[CAPTURE_PAYPAL_ORDER]== Request Method: %s", request.method)

    paypal_order_id = request.GET.get("paypal_order_id")
    if not paypal_order_id:
        logger.warning("Missing PayPal order ID in request")
        return JsonResponse({"error": "Missing PayPal order ID"}, status=400)

    # 1) Determine PayPal base URL
    base = "https://api-m.sandbox.paypal.com" if settings.PAYPAL_MODE == "sandbox" else "https://api-m.paypal.com"

    try:
        # 2) Fetch OAuth2 access token
        auth_resp = requests.post(
            f"{base}/v1/oauth2/token",
            data={"grant_type": "client_credentials"},
            auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
        )
        auth_resp.raise_for_status()
        access_token = auth_resp.json()["access_token"]
        logger.info("Obtained PayPal access token.")

        # 3) Capture the order
        capture_resp = requests.post(
            f"{base}/v2/checkout/orders/{paypal_order_id}/capture",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        )
        capture_resp.raise_for_status()
        data = capture_resp.json()
        logger.info("Capture response: %s", data)

        # 4) Verify completion and extract capture ID
        if data.get("status") == "COMPLETED":
            try:
                capture_id = data["purchase_units"][0]["payments"]["captures"][0]["id"]
            except (KeyError, IndexError) as e:
                logger.error("Failed to extract capture ID: %s", e)
                return JsonResponse({"error": "Failed to retrieve capture ID"}, status=400)

            # 5) Update our Order record
            order = Order.objects.filter(paypal_order_id=paypal_order_id, user=request.user).first()
            if order:
                order.paypal_capture_id = capture_id
                order.status = "Paid"
                order.save()
                logger.info("Order %s marked as Paid (capture ID %s).", order.order_id, capture_id)

            return JsonResponse({
                "message": "Payment successful. You may now return to your order summary."
            })
        else:
            logger.warning("Unexpected capture status: %s", data.get("status"))
            return JsonResponse({"error": "Payment not completed"}, status=400)

    except requests.HTTPError as e:
        # Log PayPal API failures with details
        logger.exception("PayPal API HTTP error: %s", e)
        return JsonResponse({"error": "PayPal API error", "details": str(e)}, status=502)

    except Exception as e:
        logger.exception("Exception during PayPal capture: %s", e)
        return JsonResponse({"error": "Internal server error", "details": str(e)}, status=500)








from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
import requests
import uuid
from decimal import Decimal
import json


@login_required
def payment_success(request):
    """Handles PayPal Payment Success without creating an order."""
    messages.success(request, "Your payment was successful! Please check your order details in your account.")
    return render(request, "store/payment_success.html")


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from orders.models import Order
from store.emails import send_receipt_email
@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    order_items = order.items.all()

    # Debug: confirm that we're about to send the email
    print(f"Sending receipt email for order #{order.order_id} to {order.user.email}")

    send_receipt_email(order)

    context = {
        "order": order,
        "order_items": order_items,
    }
    return render(request, "store/order_success.html", context)







# Account Page
def account(request):
    return render(request, 'store/account.html')

# Contact Page
def contact(request):
    return render(request, 'store/contact.html')

# About Page
def about(request):
    return render(request, 'store/about.html')

# 404 Error Page
def error_404(request, exception):
    return render(request, 'store/404.html', status=404)

# Thank You Page
def thank_you(request):
    return render(request, 'store/order_success.html')
from django.shortcuts import render
from .models import Category

from django.shortcuts import render
from .models import Category

from django.shortcuts import render
from .models import Category, SubCategory


from django.shortcuts import render
from .models import Category, SubCategory

from django.shortcuts import render
from .models import Category, SubCategory


from django.shortcuts import render
from .models import Category, SubCategory

from django.shortcuts import render
from .models import Category, SubCategory



import logging
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

# Initialize logger
logger = logging.getLogger(__name__)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from store.models import Product, ProductVariation, PriceRule
from cart.models import Cart, CartItem
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from store.models import Product, ProductVariation, PriceRule
from cart.models import Cart, CartItem
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

import logging
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from cart.models import Cart, CartItem
from store.models import Product, ProductVariation
from store.models import PriceRule  # assuming PriceRule is in store.models

import logging
from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from store.models import Product, ProductVariation, PriceRule
from cart.models import Cart, CartItem

logger = logging.getLogger(__name__)


import logging
from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from store.models import Product, ProductVariation, PriceRule
from cart.models import Cart, CartItem



import logging
from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from store.models import Product, ProductVariation
from cart.models import Cart, CartItem
from store.models import PriceRule  # Adjust if PriceRule is in a different app

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

import uuid
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_str  # <-- Imported force_str

logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

import logging
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils.encoding import force_str  # For Django 3.x+ use force_str
from django.contrib.auth.decorators import login_required


logger = logging.getLogger(__name__)

import logging
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils.encoding import force_str
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


@login_required
def add_to_cart(request, item_uid):
    """
    Add an item to the cart using a unique identifier.

    - If item_uid starts with "VAR", it’s treated as a ProductVariation (lookup via its variation_id).
    - If item_uid starts with "ITEM", it’s treated as a plain Product (lookup via its system_id).
    """
    # Ensure the item_uid is a string.
    item_uid = force_str(item_uid)
    logger.info("🛒 [ADD TO CART] Request received for item_uid: %s", item_uid)

    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    purchase_type = request.POST.get("purchase_type", "single").lower()
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except ValueError:
        messages.error(request, "Invalid quantity.")
        return redirect(request.META.get("HTTP_REFERER", "/"))
    logger.info("📌 Purchase Type: %s | Requested Quantity: %d", purchase_type, quantity)

    # Retrieve or create the cart.
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        logger.info("🛍 Cart Retrieved for User: %s | Created: %s", request.user.username, created)
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_id=session_id)
        logger.info("🛍 Cart Retrieved for Session: %s | Created: %s", session_id, created)

    try:
        if item_uid.startswith("VAR"):
            # Variation branch.
            variation = get_object_or_404(ProductVariation, variation_id=item_uid)
            logger.info("✅ Variation Found: %s | Variation ID: %s", variation.product.name, variation.variation_id)
            if purchase_type == "single":
                actual_quantity = quantity
            elif purchase_type == "bag":
                actual_quantity = quantity * variation.bag_size
            elif purchase_type == "box":
                actual_quantity = quantity * variation.box_size
            else:
                messages.error(request, "Invalid purchase type.")
                return redirect(request.META.get("HTTP_REFERER", "/"))
            logger.info("🔢 Adjusted Quantity (Actual Single Units): %d", actual_quantity)
            # Stock checks.
            if purchase_type == "single" and actual_quantity > variation.stock_single:
                messages.error(request, "Not enough stock for single items.")
                return redirect(request.META.get("HTTP_REFERER", "/"))
            if purchase_type == "bag":
                available_bags = variation.stock_single // variation.bag_size if variation.bag_size else 0
                if quantity > available_bags:
                    messages.error(request, "Not enough bags available.")
                    return redirect(request.META.get("HTTP_REFERER", "/"))
            if purchase_type == "box":
                available_boxes = variation.stock_single // variation.box_size if variation.box_size else 0
                if quantity > available_boxes:
                    messages.error(request, "Not enough boxes available.")
                    return redirect(request.META.get("HTTP_REFERER", "/"))
            # Create or update cart item for the variation.
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product_variation=variation,
                purchase_type=purchase_type
            )
            if not created:
                cart_item.quantity += actual_quantity
                cart_item.save()
                logger.info("🛒 Updated Variation Cart Item: %s | New Quantity: %d", variation.product.name,
                            cart_item.quantity)
            else:
                cart_item.quantity = actual_quantity
                cart_item.save()
                logger.info("✅ Created Variation Cart Item: %s | Quantity: %d", variation.product.name, actual_quantity)
        elif item_uid.startswith("ITEM"):
            # Plain Product branch.
            product = get_object_or_404(Product, system_id=item_uid)
            logger.info("✅ Plain Product Found: %s | System ID: %s", product.name, product.system_id)
            logger.info("Using plain product details for %s | System ID: %s", product.name, product.system_id)
            # Force plain products to use 'single' purchase type.
            if purchase_type not in ("single", "bag", "box"):
                messages.error(request, "Invalid purchase type for this product.")
                return redirect(request.META.get("HTTP_REFERER", "/"))
            if purchase_type in ("bag", "box"):
                logger.warning("Bag/Box selected for a product with no variations; treating as single.")
            actual_quantity = quantity
            if actual_quantity > product.quantity:
                messages.error(request, "Not enough stock available for this product.")
                return redirect(request.META.get("HTTP_REFERER", "/"))
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                product_variation=None,
                purchase_type="single"  # Always treat plain products as 'single'
            )
            if not created:
                cart_item.quantity += actual_quantity
                cart_item.save()
                logger.info("🛒 Updated Product Cart Item: %s | New Quantity: %d", product.name, cart_item.quantity)
            else:
                cart_item.quantity = actual_quantity
                cart_item.save()
                logger.info("✅ Created Product Cart Item: %s | Quantity: %d", product.name, actual_quantity)
        else:
            messages.error(request, "Invalid item identifier.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        messages.success(request, "Item added to cart successfully!")
        return redirect("store:cart")
    except Exception as e:
        logger.error("❌ [ERROR] add_to_cart exception: %s", str(e), exc_info=True)
        messages.error(request, "An error occurred while adding the item to the cart.")
        return redirect(request.META.get("HTTP_REFERER", "/"))


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages


def update_cart(request):
    """Update the quantity of items in the cart."""
    if request.method == "POST":
        item_ids = request.POST.getlist("item_id[]")  # Get multiple item IDs
        quantities = request.POST.getlist("quantity[]")  # Get corresponding quantities

        for item_id, quantity in zip(item_ids, quantities):
            try:
                cart_item = CartItem.objects.get(id=item_id)
                new_quantity = int(quantity)

                if new_quantity > 0:
                    cart_item.quantity = new_quantity
                    cart_item.save()
                else:
                    cart_item.delete()  # Remove item if quantity is 0
            except CartItem.DoesNotExist:
                messages.error(request, "Item not found in cart.")
                continue  # Skip and process the next item

        messages.success(request, "Cart updated successfully.")

    return redirect("store:cart")


def remove_from_cart(request, item_id):
    """Remove an item from the cart."""
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect("store:cart")


from django.shortcuts import render, get_object_or_404
from store.models import Category, SubCategory, Product

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from store.models import Category, SubCategory, Product

def category_list(request):
    """
    List all top-level categories (i.e. categories with no parent).
    """
    categories = Category.objects.filter(parent=None)
    return render(request, 'store/tcategory_list.html', {'categories': categories})

def category_detail(request, slug):
    """
    Display a category. If the category has top-level subcategories, show them;
    otherwise, redirect to the shop view (which will filter products by the category slug).
    """
    category = get_object_or_404(Category, slug=slug)
    subcategories = category.top_level_subcategories.all()
    if subcategories.exists():
        context = {
            'category': category,
            'subcategories': subcategories
        }
        return render(request, 'store/tcategory_detail.html', context)
    else:
        shop_url = reverse('store:shop')
        return redirect(f"{shop_url}?category={category.slug}")

def subcategory_detail(request, slug):
    """
    Display a subcategory. If the subcategory has further nested subcategories, show them;
    otherwise, redirect to the shop view to display products filtered by the subcategory slug.
    """
    subcategory = get_object_or_404(SubCategory, slug=slug)
    nested_subcategories = subcategory.subcategories.all()
    if nested_subcategories.exists():
        context = {
            'subcategory': subcategory,
            'subcategories': nested_subcategories
        }
        return render(request, 'store/tsubcategory_detail.html', context)
    else:
        shop_url = reverse('store:shop')
        return redirect(f"{shop_url}?category={subcategory.slug}")




def search(request):
    """
    Searches across products (name, description) and product variations (size, color)
    and returns a JSON response with matching results.
    """
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        # Search Products by name and description
        product_matches = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).distinct()

        # Search ProductVariations by size and color fields
        variation_matches = ProductVariation.objects.filter(
            Q(size__name__icontains=query) | Q(color__icontains=query)
        ).distinct()

        # Add product matches to results
        for product in product_matches:
            results.append({
                'name': product.name,
                'slug': product.slug,
                'image': product.image.url if product.image else '',
                'price': str(product.price),
                'type': 'product'
            })

        # Add variation matches (ensuring no duplicate product slugs)
        product_slugs = {item['slug'] for item in results}
        for variation in variation_matches:
            if variation.product.slug not in product_slugs:
                results.append({
                    'name': variation.product.name,
                    'slug': variation.product.slug,
                    'image': (variation.image.url if variation.image
                              else (variation.product.image.url if variation.product.image else '')),
                    'price': str(variation.price_single),
                    'size': variation.size.name,
                    'color': variation.color,
                    'type': 'variation'
                })
                product_slugs.add(variation.product.slug)

    return JsonResponse({'results': results})


def test(request):
    return render(request,'store/test.html')


from django.http import HttpResponse
from .emails import send_test_email
from django.contrib.auth.models import User

# views.py
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from .emails import send_test_email

def test_email_view(request):
    User = get_user_model()  # This will return your CustomUser model
    user = User.objects.first()  # Adjust this to pick a valid user for testing
    if user:
        send_test_email("kianhosseini423@gmail.com", user)  # Replace with your testing email address
        return HttpResponse("Test email sent!")
    else:
        return HttpResponse("No user found to send test email.")


import json
import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

import json
import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

import json
import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

import json
import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from decimal import Decimal
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

import json
import logging
from decimal import Decimal
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

logger = logging.getLogger(__name__)

import json
import logging
from decimal import Decimal
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

logger = logging.getLogger(__name__)

import json
import math
from decimal import Decimal
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from django.conf import settings
import json
import math
from decimal import Decimal
from django.http import HttpResponseBadRequest, JsonResponse
from decimal import Decimal
import json, math
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

import json, math
from decimal import Decimal
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import logging


@csrf_exempt
def get_rate(request):
    """
    Receives shipping details (to_address) and optional billing details (billing_address)
    from the front end via JSON. Uses a fixed sender (return_address) address,
    calls the Stallion Express Rates API, and returns the API response as JSON.

    If no items are provided, a default item is added.
    Insurance is optional (defaults to False if not provided).

    Before calling the API, if the submitted weight is higher than a threshold,
    the package dimensions are overridden with default dimensions known to work.
    """
    if request.method != "POST":
        logger.warning("Received non-POST request.")
        return HttpResponseBadRequest("Invalid request method; POST required.")

    try:
        data = json.loads(request.body)
        logger.info("Parsed JSON payload from request.")
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON from request body.")
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

    # Extract shipping details.
    to_address = {
        "name": data.get("name", "Recipient Name"),
        "company": data.get("company", "Recipient Company"),
        "address1": data.get("address1", "Default Address 1"),
        "address2": data.get("address2", ""),
        "city": data.get("city", "Concord"),
        "province_code": data.get("province_code", "ON"),
        "postal_code": data.get("postal_code", "L4K 0J7"),
        "country_code": data.get("country_code", "CA"),
        "phone": data.get("phone", "0000000000"),
        "email": data.get("email", "recipient@example.com"),
        "is_residential": data.get("is_residential", True)
    }
    logger.info("Using shipping details: %s", to_address)

    # Optional billing address.
    billing_address = {
        "name": data.get("billing_name", "Billing Name"),
        "company": data.get("billing_company", "Billing Company"),
        "address1": data.get("billing_address1", ""),
        "address2": data.get("billing_address2", ""),
        "city": data.get("billing_city", ""),
        "province_code": data.get("billing_province_code", ""),
        "postal_code": data.get("billing_postal_code", ""),
        "country_code": data.get("billing_country_code", "CA"),
        "phone": data.get("billing_phone", ""),
        "email": data.get("billing_email", ""),
        "is_residential": data.get("billing_is_residential", True)
    }
    logger.info("Captured billing details: %s", billing_address)

    # Fixed sender address.
    return_address = {
        "name": "Sender Name",
        "company": "Sender Company",
        "address1": "110 West Beaver Creek Rd Unit 16",
        "address2": "",
        "city": "Richmond Hill",
        "province_code": "ON",
        "postal_code": "L4B 1J9",
        "country_code": "CA",
        "phone": "0000000000",
        "email": "sender@example.com",
        "is_residential": True
    }
    logger.info("Using fixed sender address: %s", return_address)

    # Get items; if none, use a default item.
    items = data.get("items", [])
    if not items:
        items = [{
            "description": "Default Item",
            "sku": "DEFAULT",
            "quantity": 1,
            "value": 0.01,  # Minimal required value
            "currency": "CAD",
            "country_of_origin": "CA",
            "hs_code": "000000",
            "manufacturer_name": "Default Manufacturer",
            "manufacturer_address1": "Default Address",
            "manufacturer_city": "Default City",
            "manufacturer_province_code": "ON",
            "manufacturer_postal_code": "00000",
            "manufacturer_country_code": "CA"
        }]
        logger.info("No items provided; using default item: %s", items[0])
    else:
        logger.info("Received %d item(s) in payload.", len(items))

    # Try to get numeric values for weight and dimensions.
    try:
        weight = Decimal(str(data.get("weight", "1.0")))
        length = Decimal(str(data.get("length", "12")))
        width = Decimal(str(data.get("width", "9")))
        height = Decimal(str(data.get("height", "4")))
    except InvalidOperation as e:
        logger.error("Invalid numeric value for dimensions: %s", e)
        return JsonResponse({"error": "Invalid numeric value for weight or dimensions."}, status=400)

    # --- OPTIONAL: Adjust dimensions for heavy packages ---
    # For example, if weight > 10 lbs, override dimensions with default values that yield rates.
    heavy_threshold = Decimal("10")
    if weight > heavy_threshold:
        logger.info("Weight %s lbs exceeds threshold %s lbs; adjusting dimensions.", weight, heavy_threshold)
        # Set dimensions to default values from the API reference sample (or your chosen defaults)
        length = Decimal("9")
        width = Decimal("12")
        height = Decimal("1")
    else:
        # Otherwise, you might be computing scaled dimensions.
        # (If you have an algorithm to scale dimensions with weight, include it here.)
        pass

    logger.info("Received weight: %s lbs", weight)
    logger.info("Using dimensions: Length: %s cm, Width: %s cm, Height: %s cm", length, width, height)

    # Build the shipment payload.
    shipment_details = {
        "to_address": to_address,
        "return_address": return_address,
        "is_return": False,
        "weight_unit": "lbs",
        "weight": float(weight),  # Convert Decimal to float for JSON serialization
        "length": float(length),
        "width": float(width),
        "height": float(height),
        "size_unit": "cm",  # Using centimeters
        "items": items,
        "package_type": "Parcel",
        "postage_types": [],
        "signature_confirmation": data.get("signature_confirmation", True),
        "insured": data.get("insured", False),
        "region": data.get("region", None),
        "tax_identifier": data.get("tax_identifier", {
            "tax_type": "IOSS",
            "number": "IM1234567890",
            "issuing_authority": "GB"
        })
    }
    logger.info("Constructed shipment payload: %s", shipment_details)

    # Prepare the API call to the live shipping API (live environment).
    api_url = "https://ship.stallionexpress.ca/api/v4/rates"
    headers_api = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.STALLION_API_TOKEN}"
    }
    logger.info("Calling shipping API at %s", api_url)

    try:
        response = requests.post(api_url, headers=headers_api, json=shipment_details)
        response_data = response.json()
        logger.info("Shipping API response: %s", response_data)
    except Exception as e:
        logger.exception("Failed to call shipping API.")
        return JsonResponse({"error": "Error communicating with shipping API", "details": str(e)}, status=500)

    return JsonResponse({
        "shipping_api_response": response_data,
        "billing_address": billing_address
    })


import math
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
import logging
from cart.models import Cart  # Adjust the import path accordingly

logger = logging.getLogger(__name__)

import math
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
import logging
from cart.models import Cart  # Adjust the import to match your project structure

logger = logging.getLogger(__name__)

from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
import logging
from cart.models import Cart

logger = logging.getLogger(__name__)

from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
import logging
from cart.models import Cart

logger = logging.getLogger(__name__)


from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
import logging
from cart.models import Cart

logger = logging.getLogger(__name__)

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from django.http import JsonResponse
import logging
from cart.models import Cart

logger = logging.getLogger(__name__)

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from django.http import JsonResponse
import logging
from cart.models import Cart

logger = logging.getLogger(__name__)

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.http import JsonResponse
import logging
from cart.models import Cart

logger = logging.getLogger(__name__)


from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.http import JsonResponse
import logging
from cart.models import Cart

logger = logging.getLogger(__name__)

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.http import JsonResponse
import logging
from cart.models import Cart

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import math
import logging
from django.http import JsonResponse
from cart.models import Cart

logger = logging.getLogger(__name__)

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import logging
from django.http import JsonResponse
from cart.models import Cart

logger = logging.getLogger(__name__)

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import logging
from django.http import JsonResponse
from cart.models import Cart

logger = logging.getLogger(__name__)

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import logging
from django.http import JsonResponse
from cart.models import Cart

logger = logging.getLogger(__name__)

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import logging
from django.http import JsonResponse
from cart.models import Cart

logger = logging.getLogger(__name__)


from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.http import JsonResponse
import logging
from cart.models import Cart

logger = logging.getLogger(__name__)

def cart_total_weight(request):
    """
    Calculates the total weight of all items in the cart and aggregates the dimensions
    for pack items (bags or boxes) using values that are already in centimeters.

    For each cart item:
      - If using a product_variation:
          * For "bag" or "box" items:
              - effective_quantity = (item.quantity / pack_size)
              - subtotal weight = pack_weight * effective_quantity
              - The item dimensions are (pack_dimension * effective_quantity)
          * For "single" items:
              - subtotal weight = unit weight × quantity
              - item dimensions = variation dimensions × quantity
      - For plain products:
              - subtotal weight = unit weight × quantity
              - item dimensions = product dimensions × quantity

    Returns a JSON response including:
      - "cart_weight": overall total weight (lbs)
      - "cart_length": aggregated length (cm)
      - "cart_width": aggregated width (cm)
      - "cart_height": aggregated height (cm)
      - "details": per‑item breakdown.
    """
    total_weight = Decimal('0.0')
    agg_length = Decimal('0.0')
    agg_width = Decimal('0.0')
    agg_height = Decimal('0.0')
    item_details = []

    # Retrieve the cart based on user or session.
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        logger.info("User is authenticated: %s", request.user)
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        cart = Cart.objects.filter(session_id=session_id).first()
        logger.info("User is not authenticated, using session: %s", session_id)

    if not cart:
        logger.info("No cart found for user or session.")
        return JsonResponse({"cart_weight": 0.0, "details": "No cart items found."})

    logger.info("Found %d item(s) in cart.", cart.items.count())

    for item in cart.items.all():
        try:
            # Initialize per-item dimension variables.
            item_length = Decimal("0.00")
            item_width = Decimal("0.00")
            item_height = Decimal("0.00")
            purchase_type = "single"  # default

            # If the cart item uses a product variation…
            if hasattr(item, 'product_variation') and item.product_variation:
                weight_value = Decimal(item.product_variation.weight).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                product_name = item.product_variation.product.name
                source = "variation"
                purchase_type = item.purchase_type.lower()  # expected: "single", "bag", or "box"

                if purchase_type in ("bag", "box"):
                    # Field names depend on purchase type.
                    if purchase_type == "bag":
                        size_field = "bag_size"
                        weight_field = "bag_weight"
                        length_field = "bag_length"
                        width_field = "bag_width"
                        height_field = "bag_height"
                    else:
                        size_field = "box_size"
                        weight_field = "box_weight"
                        length_field = "box_length"
                        width_field = "box_width"
                        height_field = "box_height"

                    # Determine pack size (default to 1 if not set or invalid).
                    try:
                        pack_size = int(getattr(item.product_variation, size_field, 1))
                        if pack_size <= 0:
                            pack_size = 1
                    except (ValueError, TypeError):
                        pack_size = 1

                    # Get the pack weight (use a default of 1.0 if missing).
                    try:
                        pack_weight = Decimal(getattr(item.product_variation, weight_field, "1.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    except (InvalidOperation, TypeError):
                        pack_weight = Decimal("1.0")

                    # Get the pack dimensions (already stored in centimeters).
                    try:
                        length_raw = getattr(item.product_variation, length_field, None)
                        pack_length = Decimal(length_raw).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if length_raw is not None else None
                    except (InvalidOperation, TypeError):
                        pack_length = None
                    try:
                        width_raw = getattr(item.product_variation, width_field, None)
                        pack_width = Decimal(width_raw).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if width_raw is not None else None
                    except (InvalidOperation, TypeError):
                        pack_width = None
                    try:
                        height_raw = getattr(item.product_variation, height_field, None)
                        pack_height = Decimal(height_raw).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if height_raw is not None else None
                    except (InvalidOperation, TypeError):
                        pack_height = None

                    # Calculate effective number of packs.
                    effective_quantity = (Decimal(item.quantity) / Decimal(pack_size)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    subtotal_weight = (pack_weight * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                    # Calculate item dimensions for pack items.
                    item_length = (pack_length * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if pack_length is not None else Decimal("0.00")
                    item_width = (pack_width * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if pack_width is not None else Decimal("0.00")
                    item_height = (pack_height * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if pack_height is not None else Decimal("0.00")

                else:
                    # For "single" items in a variation.
                    effective_quantity = Decimal(item.quantity)
                    subtotal_weight = (weight_value * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    try:
                        var_length = Decimal(item.product_variation.length).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                        var_width = Decimal(item.product_variation.width).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                        var_height = Decimal(item.product_variation.height).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    except (InvalidOperation, TypeError):
                        var_length = var_width = var_height = Decimal("0.00")
                    item_length = (var_length * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    item_width = (var_width * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    item_height = (var_height * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            # For plain products.
            elif hasattr(item, 'product') and item.product:
                try:
                    weight_value = Decimal(item.product.weight).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                except (InvalidOperation, TypeError):
                    weight_value = Decimal("1.0")
                product_name = item.product.name
                source = "product"
                effective_quantity = Decimal(item.quantity)
                subtotal_weight = (weight_value * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                purchase_type = "single"
                try:
                    prod_length = Decimal(item.product.length).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    prod_width = Decimal(item.product.width).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    prod_height = Decimal(item.product.height).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                except (InvalidOperation, TypeError):
                    prod_length = prod_width = prod_height = Decimal("0.00")
                item_length = (prod_length * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                item_width = (prod_width * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                item_height = (prod_height * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            else:
                logger.warning("Cart item ID %s has no associated product or product_variation.", item.id)
                continue

            # Aggregate totals.
            total_weight += subtotal_weight
            agg_length += item_length
            agg_width += item_width
            agg_height += item_height

            # Build per-item log.
            item_log = {
                "cart_item_id": item.id,
                "product_name": product_name,
                "source": source,
                "weight_per_unit": str(weight_value),
                "quantity": item.quantity,
                "effective_quantity": str(effective_quantity),
                "subtotal_weight": str(subtotal_weight),
                "purchase_type": purchase_type,
                "item_length": str(item_length),
                "item_width": str(item_width),
                "item_height": str(item_height),
            }
            if purchase_type in ("bag", "box"):
                item_log["pack_weight"] = str(pack_weight) if pack_weight is not None else ""
                # Also include original pack dimensions (from model, already in cm)
                try:
                    original_length = Decimal(getattr(item.product_variation, length_field, None)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if getattr(item.product_variation, length_field, None) is not None else Decimal("0.00")
                except (InvalidOperation, TypeError):
                    original_length = Decimal("0.00")
                try:
                    original_width = Decimal(getattr(item.product_variation, width_field, None)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if getattr(item.product_variation, width_field, None) is not None else Decimal("0.00")
                except (InvalidOperation, TypeError):
                    original_width = Decimal("0.00")
                try:
                    original_height = Decimal(getattr(item.product_variation, height_field, None)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if getattr(item.product_variation, height_field, None) is not None else Decimal("0.00")
                except (InvalidOperation, TypeError):
                    original_height = Decimal("0.00")
                item_log["pack_length"] = str(original_length)
                item_log["pack_width"] = str(original_width)
                item_log["pack_height"] = str(original_height)
            item_details.append(item_log)
            logger.debug("Cart item calculated: %s", item_log)
        except Exception as e:
            logger.error("Error calculating weight for cart item ID %s: %s", item.id, e)

    logger.info("Total cart weight calculated: %s lbs", total_weight)
    logger.info("Aggregated dimensions: Length: %s cm, Width: %s cm, Height: %s cm",
                agg_length.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                agg_width.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                agg_height.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    return JsonResponse({
        "cart_weight": float(total_weight),
        "cart_length": str(agg_length.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "cart_width": str(agg_width.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "cart_height": str(agg_height.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "details": item_details
    })




import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .views import get_rate  # Import your existing get_rate view


@csrf_exempt
def test_get_rate(request):
    """
    A test view to simulate a POST request to get_rate with a fixed payload.
    """
    # Sample payload to test the shipping rate API.
    test_payload = {
        "to_address": {
            "name": "Recipient Name",
            "company": "Recipient Company",
            "address1": "950 Portage Pkwy",
            "address2": "",
            "city": "Concord",
            "province_code": "ON",
            "postal_code": "L4K 0J7",
            "country_code": "CA",
            "phone": "0000000000",
            "email": "recipient@example.com",
            "is_residential": True
        },
        "return_address": {
            "name": "Sender Name",
            "company": "Sender Company",
            "address1": "110 West Beaver Creek Rd Unit 16",
            "address2": "",
            "city": "Richmond Hill",
            "province_code": "ON",
            "postal_code": "L4B 1J9",
            "country_code": "CA",
            "phone": "0000000000",
            "email": "sender@example.com",
            "is_residential": True
        },
        "is_return": False,
        "weight_unit": "lbs",
        "weight": 2.5,
        "length": 10,
        "width": 10,
        "height": 10,
        "size_unit": "cm",
        "items": [
            {
                "description": "Two pair of socks",
                "sku": "SKU123",
                "quantity": 2,
                "value": 10,
                "currency": "CAD",
                "country_of_origin": "CN",
                "hs_code": "123456",
                "manufacturer_name": "Acme Clothing Inc.",
                "manufacturer_address1": "123 Manufacturing Blvd",
                "manufacturer_city": "Toronto",
                "manufacturer_province_code": "ON",
                "manufacturer_postal_code": "M5V 2H1",
                "manufacturer_country_code": "CA"
            }
        ],
        "package_type": "Parcel",
        "postage_types": [],
        "signature_confirmation": True,
        "insured": True,
        "region": None,
        "tax_identifier": {
            "tax_type": "IOSS",
            "number": "IM1234567890",
            "issuing_authority": "GB"
        }
    }

    # Since your get_rate view expects a POST with a JSON body, we simulate that:
    request.method = "POST"
    request._body = json.dumps(test_payload).encode("utf-8")

    # Call the existing get_rate view using the simulated request.
    return get_rate(request)



from django.http import JsonResponse
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from math import ceil
from cart.models import Cart
from .models import BoxSize  # Adjust the import if your BoxSize model is in a different app
import logging

logger = logging.getLogger(__name__)

from django.http import JsonResponse
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from math import ceil
from cart.models import Cart
from .models import BoxSize  # Adjust if BoxSize is in a different app
import logging

logger = logging.getLogger(__name__)


from django.http import JsonResponse
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from math import ceil
from cart.models import Cart
from .models import BoxSize  # Adjust if BoxSize is in a different app
import logging

logger = logging.getLogger(__name__)

def recommend_box(request):
    """
    Calculates the total weight and total volume of all items in the cart,
    aggregates their dimensions, and then iterates over all available BoxSize objects
    (converting each box’s dimensions from inches to centimeters) to determine how many boxes
    would be required to ship the cart contents.

    For each cart item:
      - If the item uses a product_variation:
          * For "bag" or "box" items:
              - effective_quantity = (item.quantity / pack_size)
              - subtotal weight = pack_weight * effective_quantity
              - Each pack’s dimensions (length, width, height) are multiplied by effective_quantity (dimensions are already in cm).
          * For "single" items:
              - subtotal weight = unit weight × quantity, and dimensions come directly from the variation.
      - For plain products, weight and dimensions come directly from the product.

    The view returns a JSON response including:
      - "cart_weight": overall total weight (lbs)
      - "total_volume": overall total volume (cm³)
      - "cart_length", "cart_width", "cart_height": aggregated dimensions (cm)
      - "box_recommendations": list of each box type with the calculated number of boxes required by weight and volume
      - "best_box": the box type with the lowest number of boxes needed
      - "details": per‑item breakdown.
    """
    total_weight = Decimal('0.0')
    agg_length = Decimal('0.0')
    agg_width = Decimal('0.0')
    agg_height = Decimal('0.0')
    total_volume = Decimal('0.0')
    item_details = []

    # Retrieve the cart based on user or session.
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        logger.info("User is authenticated: %s", request.user)
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        cart = Cart.objects.filter(session_id=session_id).first()
        logger.info("User is not authenticated, using session: %s", session_id)

    if not cart:
        logger.info("No cart found for user or session.")
        return JsonResponse({"error": "No cart items found."}, status=404)

    logger.info("Found %d item(s) in cart.", cart.items.count())

    # Loop through cart items and aggregate the weight, dimensions, and volume.
    for item in cart.items.all():
        try:
            # Initialize per-item dimensions.
            item_length = Decimal("0.00")
            item_width = Decimal("0.00")
            item_height = Decimal("0.00")
            purchase_type = "single"  # default

            if hasattr(item, 'product_variation') and item.product_variation:
                weight_value = Decimal(item.product_variation.weight).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                product_name = item.product_variation.product.name
                source = "variation"
                purchase_type = item.purchase_type.lower()  # "single", "bag", or "box"

                if purchase_type in ("bag", "box"):
                    # Choose appropriate field names.
                    if purchase_type == "bag":
                        size_field = "bag_size"
                        weight_field = "bag_weight"
                        length_field = "bag_length"
                        width_field = "bag_width"
                        height_field = "bag_height"
                    else:
                        size_field = "box_size"
                        weight_field = "box_weight"
                        length_field = "box_length"
                        width_field = "box_width"
                        height_field = "box_height"

                    # Determine pack size.
                    try:
                        pack_size = int(getattr(item.product_variation, size_field, 1))
                        if pack_size <= 0:
                            pack_size = 1
                    except (ValueError, TypeError):
                        pack_size = 1

                    try:
                        pack_weight = Decimal(getattr(item.product_variation, weight_field, "1.0")).quantize(
                            Decimal("0.01"), rounding=ROUND_HALF_UP)
                    except (InvalidOperation, TypeError):
                        pack_weight = Decimal("1.0")

                    try:
                        pack_length = Decimal(getattr(item.product_variation, length_field, None)).quantize(
                            Decimal("0.01"), rounding=ROUND_HALF_UP) if getattr(item.product_variation, length_field, None) is not None else None
                    except (InvalidOperation, TypeError):
                        pack_length = None
                    try:
                        pack_width = Decimal(getattr(item.product_variation, width_field, None)).quantize(
                            Decimal("0.01"), rounding=ROUND_HALF_UP) if getattr(item.product_variation, width_field, None) is not None else None
                    except (InvalidOperation, TypeError):
                        pack_width = None
                    try:
                        pack_height = Decimal(getattr(item.product_variation, height_field, None)).quantize(
                            Decimal("0.01"), rounding=ROUND_HALF_UP) if getattr(item.product_variation, height_field, None) is not None else None
                    except (InvalidOperation, TypeError):
                        pack_height = None

                    # Calculate effective number of packs.
                    effective_quantity = (Decimal(item.quantity) / Decimal(pack_size)).quantize(Decimal("0.01"),
                                                                                                rounding=ROUND_HALF_UP)
                    subtotal_weight = (pack_weight * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                    # For pack items, take dimensions directly (already in cm) and multiply by effective quantity.
                    item_length = (pack_length * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if pack_length is not None else Decimal("0.00")
                    item_width = (pack_width * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if pack_width is not None else Decimal("0.00")
                    item_height = (pack_height * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if pack_height is not None else Decimal("0.00")

                else:  # For "single" variation items.
                    effective_quantity = Decimal(item.quantity)
                    subtotal_weight = (weight_value * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    try:
                        var_length = Decimal(item.product_variation.length).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                        var_width = Decimal(item.product_variation.width).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                        var_height = Decimal(item.product_variation.height).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    except (InvalidOperation, TypeError):
                        var_length = var_width = var_height = Decimal("0.00")
                    item_length = (var_length * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    item_width = (var_width * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    item_height = (var_height * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            elif hasattr(item, 'product') and item.product:
                try:
                    weight_value = Decimal(item.product.weight).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                except (InvalidOperation, TypeError):
                    weight_value = Decimal("1.0")
                product_name = item.product.name
                source = "product"
                effective_quantity = Decimal(item.quantity)
                subtotal_weight = (weight_value * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                purchase_type = "single"
                try:
                    prod_length = Decimal(item.product.length).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    prod_width = Decimal(item.product.width).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    prod_height = Decimal(item.product.height).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                except (InvalidOperation, TypeError):
                    prod_length = prod_width = prod_height = Decimal("0.00")
                item_length = (prod_length * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                item_width = (prod_width * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                item_height = (prod_height * effective_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            else:
                logger.warning("Cart item ID %s has no associated product or product_variation.", item.id)
                continue

            total_weight += subtotal_weight
            # Calculate volume for the item (in cubic centimeters).
            item_volume = (item_length * item_width * item_height).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            total_volume = total_volume + item_volume
            agg_length += item_length
            agg_width += item_width
            agg_height += item_height

            # Build breakdown for each item.
            detail = {
                "cart_item_id": item.id,
                "product_name": product_name,
                "source": source,
                "weight_per_unit": str(weight_value),
                "quantity": item.quantity,
                "effective_quantity": str(effective_quantity),
                "subtotal_weight": str(subtotal_weight),
                "purchase_type": purchase_type,
                "item_length": str(item_length),
                "item_width": str(item_width),
                "item_height": str(item_height),
                "item_volume": str(item_volume)
            }
            if purchase_type in ("bag", "box"):
                detail["pack_weight"] = str(pack_weight) if pack_weight is not None else ""
                try:
                    original_length = Decimal(getattr(item.product_variation, length_field, None)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if getattr(item.product_variation, length_field, None) is not None else Decimal("0.00")
                except (InvalidOperation, TypeError):
                    original_length = Decimal("0.00")
                try:
                    original_width = Decimal(getattr(item.product_variation, width_field, None)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if getattr(item.product_variation, width_field, None) is not None else Decimal("0.00")
                except (InvalidOperation, TypeError):
                    original_width = Decimal("0.00")
                try:
                    original_height = Decimal(getattr(item.product_variation, height_field, None)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if getattr(item.product_variation, height_field, None) is not None else Decimal("0.00")
                except (InvalidOperation, TypeError):
                    original_height = Decimal("0.00")
                detail["pack_length"] = str(original_length)
                detail["pack_width"] = str(original_width)
                detail["pack_height"] = str(original_height)
            item_details.append(detail)
            logger.debug("Cart item calculated: %s", detail)
        except Exception as e:
            logger.error("Error calculating weight for cart item ID %s: %s", item.id, e)

    logger.info("Total cart weight calculated: %s lbs", total_weight)
    logger.info("Total aggregated volume: %s cubic cm", total_volume)
    logger.info("Aggregated dimensions: Length: %s cm, Width: %s cm, Height: %s cm",
                agg_length.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                agg_width.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                agg_height.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    # Now iterate over available BoxSize objects to produce recommendations.
    recommendations = []
    for box in BoxSize.objects.all():
        # Convert box dimensions from inches to centimeters.
        box_length_cm = (box.length * Decimal("2.54")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        box_width_cm = (box.width * Decimal("2.54")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        box_height_cm = (box.height * Decimal("2.54")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        box_volume = (box_length_cm * box_width_cm * box_height_cm).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        # Calculate boxes needed by weight and volume.
        try:
            boxes_by_weight = ceil(total_weight / box.max_weight)
        except (InvalidOperation, TypeError):
            boxes_by_weight = 9999
        boxes_by_volume = ceil(total_volume / box_volume) if box_volume > 0 else 9999
        boxes_needed = max(boxes_by_weight, boxes_by_volume)
        recommendations.append({
            "box_name": box.name,
            "max_weight": str(box.max_weight),
            "box_length_cm": str(box_length_cm),
            "box_width_cm": str(box_width_cm),
            "box_height_cm": str(box_height_cm),
            "box_volume": str(box_volume),
            "boxes_by_weight": boxes_by_weight,
            "boxes_by_volume": boxes_by_volume,
            "boxes_needed": boxes_needed
        })

    best = min(recommendations, key=lambda r: r["boxes_needed"]) if recommendations else {}

    logger.info("Box recommendations: %s", recommendations)
    logger.info("Best box recommendation: %s", best)

    return JsonResponse({
        "cart_weight": float(total_weight),
        "total_volume": str(total_volume),
        "cart_length": str(agg_length.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "cart_width": str(agg_width.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "cart_height": str(agg_height.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "box_recommendations": recommendations,
        "best_box": best,
        "details": item_details
    })


