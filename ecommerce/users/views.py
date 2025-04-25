from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import CustomUser

import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm

logger = logging.getLogger(__name__)


import logging
import random
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import CustomUser
from store.emails import send_verification_code_email  # ✅ Import the email function

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

import logging
import random
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import CustomUser

logger = logging.getLogger(__name__)

def signup(request):
    logger.info("Signup view accessed. Request method: %s. User: %s", request.method, request.user)

    # ✅ If already logged in
    if request.user.is_authenticated:
        logger.info("User %s is already authenticated. Redirecting to profile.", request.user)
        messages.info(request, "You are already logged in.")
        return redirect("users:profile")

    if request.method == "POST":
        logger.info("Received POST request for signup.")
        form = CustomUserCreationForm(request.POST)

        # ✅ Normalize phone and email
        raw_phone = request.POST.get("phone_number", "")
        phone = raw_phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        email = request.POST.get("email", "").lower()

        # ✅ Check for existing email or phone number (case-insensitive)
        if CustomUser.objects.filter(phone_number__iexact=phone).exists():
            logger.warning("Signup failed: phone number already exists: %s", phone)
            messages.error(request, "❌ This phone number is already registered.")
        elif CustomUser.objects.filter(email__iexact=email).exists():
            logger.warning("Signup failed: email already exists: %s", email)
            messages.error(request, "❌ This email address is already registered.")
        elif form.is_valid():
            logger.info("Signup form is valid.")
            user = form.save(commit=False)

            # ✅ Assign cleaned values
            user.phone_number = phone
            user.email = email

            # ✅ Generate 4-digit code
            pin_code = f"{random.randint(1000, 9999)}"
            user.verification_code = pin_code
            user.save()

            # ✅ Send PIN code to email
            try:
                send_verification_code_email(user)
                logger.info("Verification email sent to %s", user.email)
            except Exception as e:
                logger.error("❌ Failed to send verification email: %s", str(e))

            # ✅ Optional: Clear previous PIN from session
            if 'verification_code' in request.session:
                del request.session['verification_code']

            messages.success(request, "✅ Your account has been created! Check your email for your 4-digit code.")
            return redirect("users:login")
        else:
            logger.warning("Signup form is invalid. Errors: %s", form.errors)
            messages.error(request, "❌ Please correct the errors below.")
    else:
        logger.info("Received GET request for signup.")
        form = CustomUserCreationForm()

    return render(request, "users/signup.html", {"form": form})


from django.http import JsonResponse
from .models import CustomUser
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import CustomUser
import random
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import CustomUser
from store.emails import send_verification_code_email
import random
import logging

logger = logging.getLogger(__name__)

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import CustomUser
from store.emails import send_verification_code_email
import random
import logging

logger = logging.getLogger(__name__)

@require_GET
def ajax_send_pin(request):
    phone = request.GET.get("phone", "").replace("(", "").replace(")", "").replace("-", "").replace(" ", "").strip()
    email = request.GET.get("email", "").strip().lower()

    logger.info(f"📩 [AJAX] PIN request started - Phone: {phone}, Email: {email}")

    # ✅ Basic validation
    if not phone or not email:
        logger.warning("❌ Missing phone or email in request.")
        return JsonResponse({"success": False, "message": "Missing phone or email."})

    # ✅ Check for existing user (case-insensitive)
    if CustomUser.objects.filter(phone_number__iexact=phone).exists():
        logger.warning(f"❌ Phone already registered: {phone}")
        return JsonResponse({"exists": True, "field": "phone"})

    if CustomUser.objects.filter(email__iexact=email).exists():
        logger.warning(f"❌ Email already registered: {email}")
        return JsonResponse({"exists": True, "field": "email"})

    # ✅ Generate and store PIN in session
    pin = f"{random.randint(1000, 9999)}"
    request.session.flush()  # Optional: clears old session values for clean state
    request.session["signup_pin"] = pin
    request.session["signup_email"] = email

    # ✅ Send the email
    try:
        send_verification_code_email(email=email, code=pin)
        logger.info(f"✅ Verification PIN {pin} sent to {email}")
        return JsonResponse({
            "success": True,
            "message": "PIN sent successfully."
            # "debug_pin": pin  # Uncomment for dev/testing
        })
    except Exception as e:
        logger.error(f"❌ Email failed for {email}: {e}")
        return JsonResponse({"success": False, "message": "Failed to send verification email."})





from django.http import JsonResponse
from .models import CustomUser

def check_user_exists(request):
    phone = request.GET.get("phone", "").replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    email = request.GET.get("email", "").lower()  # Normalize email for case-insensitive comparison

    response = {"exists": False, "field": ""}

    if CustomUser.objects.filter(phone_number__iexact=phone).exists():  # ✅ Case-insensitive phone
        response["exists"] = True
        response["field"] = "phone"
    elif CustomUser.objects.filter(email__iexact=email).exists():  # ✅ Case-insensitive email
        response["exists"] = True
        response["field"] = "email"

    return JsonResponse(response)



# views.py
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
import re



# users/views.py
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def custom_login(request):
    # ✅ Redirect logged-in users straight to their profile
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('users:profile')

    if request.method == "POST":
        username_or_phone = request.POST.get("username_or_phone", "").strip()
        password = request.POST.get("password", "").strip()

        user = None

        # ✅ Check if it's a Canadian-style phone number
        phone_regex = re.compile(r'^\(\d{3}\) \d{3}-\d{4}$')
        if phone_regex.match(username_or_phone):
            normalized_phone = re.sub(r'\D', '', username_or_phone)
            user_obj = CustomUser.objects.filter(phone_number__regex=rf'\D*{normalized_phone}$').first()
            if user_obj:
                user = authenticate(request, username=user_obj.phone_number, password=password)
        else:
            user = authenticate(request, username=username_or_phone, password=password)

        if user:
            login(request, user)
            return redirect('users:profile')  # ✅ Redirect to profile after login
        else:
            messages.error(request, "Invalid username/phone number or password.")

    return render(request, "store/account.html")



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from orders.models import Order  # Import Order model
from store.models import Product
from users.models import Wishlist

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django import forms
from .models import CustomUser, Wishlist
from orders.models import Order
import logging

# Configure logging
logger = logging.getLogger(__name__)



@login_required
def profile(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    total_orders = orders.count()
    wishlist = Wishlist.objects.filter(user=user)

    logger.debug(f"Profile view - User: {user.phone_number}, Orders: {total_orders}, Wishlist items: {wishlist.count()}")

    context = {
        'user': user,
        'orders': orders,
        'total_orders': total_orders,
        'wishlist': wishlist,
    }
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == "POST":
        logger.debug(f"Edit profile POST request received for user: {request.user.phone_number}")
        logger.debug(f"POST data: {request.POST}")
        logger.debug(f"FILES data: {request.FILES}")

        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            logger.debug(f"Updated user data: {user.__dict__}")
            # Check if the request is AJAX
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Profile updated successfully"})
            else:
                return redirect('users:profile')
        else:
            logger.error(f"Form validation failed: {form.errors}")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "errors": form.errors})
            else:
                # For non-AJAX requests, you might want to handle errors by rendering the form again with error messages.
                return redirect('users:profile')
    else:
        return redirect('users:profile')




from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Wishlist

@login_required
def remove_wishlist_item(request, product_id):
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product_id=product_id)
    wishlist_item.delete()
    return redirect('users:profile')  # Ensure 'users:profile' exists in your `users/urls.py`


@login_required
def wishlist_view(request):
    """Display the user's wishlist."""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')

    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'users/wishlist.html', context)


@login_required
def add_to_wishlist(request, product_id):
    """Add a product to the user's wishlist."""
    product = get_object_or_404(Product, id=product_id)

    # Check if product is already in the wishlist
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if created:
        messages.success(request, "Product added to your wishlist!")
    else:
        messages.info(request, "This product is already in your wishlist.")

    return redirect('users:wishlist_view')


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import RefundRequest, RefundMedia

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import RefundRequest, RefundMedia
from django.db.models import Sum


@login_required
def refund_list(request):
    user = request.user

    # Retrieve refunds with prefetch on related media
    refunds = RefundRequest.objects.prefetch_related('media').order_by('-requested_at')
    pending_count = RefundRequest.objects.filter(status='pending').count()
    processed_today = RefundRequest.objects.filter(updated_at__date=request.user.date_joined).count()
    total_refunded_amount = RefundRequest.objects.filter(status='approved').aggregate(Sum('refund_amount'))['refund_amount__sum'] or 0

    # For each refund, determine a primary photo and video (if any)
    for refund in refunds:
        refund.photo = None
        refund.video = None
        for media in refund.media.all():
            # Lowercase the file URL for easier extension checking
            file_url = media.media_file.url.lower()
            if not refund.photo and (file_url.endswith('.jpg') or file_url.endswith('.jpeg') or file_url.endswith('.png') or file_url.endswith('.gif')):
                refund.photo = media
            elif not refund.video and file_url.endswith('.mp4'):
                refund.video = media

    # Optionally, if you still want to pass a separate queryset of refund media:
    refund_media = RefundMedia.objects.filter(refund_request__in=refunds)

    return render(request, 'users/admin_refund_profile.html', {
        'user': user,
        'refunds': refunds,
        'refund_media': refund_media,  # This remains if needed elsewhere in the template
        'pending_count': pending_count,
        'processed_today': processed_today,
        'total_refunded_amount': total_refunded_amount,
    })



@login_required
def refund_detail(request, refund_id):
    """View to display details of a specific refund request."""
    refund = get_object_or_404(RefundRequest, id=refund_id)
    refund_media = RefundMedia.objects.filter(refund_request=refund)
    return render(request, 'refunds/refund_detail.html', {'refund': refund, 'refund_media': refund_media})


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import RefundRequest
from store.models import ProductVariation  # Import ProductVariation model

import logging
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import RefundRequest
from store.models import ProductVariation  # ✅ Import ProductVariation model

# ✅ Initialize logger
logger = logging.getLogger(__name__)


import logging
import paypalrestsdk
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings  # ✅ Import PayPal API settings
from .models import RefundRequest
from store.models import ProductVariation  # ✅ Import ProductVariation model

# ✅ Initialize logger
logger = logging.getLogger(__name__)

# ✅ Configure PayPal SDK using `.env` credentials
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # ✅ Uses "sandbox" or "live" from .env
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

import requests
import logging
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from decimal import Decimal
from orders.models import RefundRequest, OrderItem
from store.models import ProductVariation

logger = logging.getLogger(__name__)

@login_required
def approve_refund(request, refund_id):
    """Approves a refund request, updates stock, and processes PayPal refund if needed."""
    refund = get_object_or_404(RefundRequest, id=refund_id)
    order = refund.order
    order_item = refund.order_item

    # 1️⃣ Update Refund Status
    refund.status = "approved"
    refund.save()

    # 2️⃣ Return Items to Stock
    if order_item.product_variation:
        product_variation = order_item.product_variation
        product_variation.stock_single += refund.quantity  # ✅ Add refunded quantity back to stock
        product_variation.save()
        logger.info(f"✅ Stock Updated: {product_variation.product.name} - {refund.quantity} items returned.")
    elif order_item.product:  # Added branch for plain products without a variation
        product = order_item.product
        product.quantity += refund.quantity  # ✅ Add refunded quantity back to plain product stock
        product.save()
        logger.info(f"✅ Stock Updated: {product.name} - {refund.quantity} items returned.")

    # 3️⃣ Process PayPal Refund if applicable
    if order.payment_method == "paypal" and order.paypal_order_id:
        logger.info(f"🔄 Processing PayPal refund for Order: {order.paypal_order_id}")

        PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com" if settings.PAYPAL_MODE == "sandbox" else "https://api-m.paypal.com"
        PAYPAL_CLIENT_ID = settings.PAYPAL_CLIENT_ID
        PAYPAL_CLIENT_SECRET = settings.PAYPAL_CLIENT_SECRET

        # Authenticate with PayPal
        auth_response = requests.post(
            f"{PAYPAL_API_BASE}/v1/oauth2/token",
            headers={"Accept": "application/json", "Accept-Language": "en_US"},
            data={"grant_type": "client_credentials"},
            auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
        )

        if auth_response.status_code != 200:
            logger.error(f"🚨 PayPal Auth Error: {auth_response.text}")
            messages.error(request, "PayPal authentication failed.")
            return redirect("users:refund_list")

        access_token = auth_response.json().get("access_token")

        # Process the refund
        refund_payload = {
            "amount": {
                "value": str(refund.refund_amount),
                "currency_code": "CAD",
            }
        }

        refund_url = f"{PAYPAL_API_BASE}/v2/payments/captures/{order.paypal_capture_id}/refund"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        refund_response = requests.post(refund_url, headers=headers, json=refund_payload)

        if refund_response.status_code == 201:
            logger.info(f"✅ PayPal Refund Successful for Order: {order.paypal_order_id}")
            messages.success(request, "Refund approved and processed via PayPal.")
        else:
            logger.error(f"🚨 PayPal Refund Failed: {refund_response.json()}")
            messages.error(request, f"PayPal refund failed: {refund_response.json().get('message', 'Unknown error')}")

    else:
        messages.success(request, "Refund approved successfully.")

    return redirect("users:refund_list")






@login_required
def reject_refund(request, refund_id):
    """View to reject a refund request."""
    refund = get_object_or_404(RefundRequest, id=refund_id)
    refund.status = 'rejected'
    refund.save()
    messages.error(request, f'Refund request {refund.id} has been rejected.')
    return redirect('users:refund_list')


from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('users:login')  # 🔁 Change to 'index' if you want to send users to homepage




from django.shortcuts import render
from orders.models import Order  # Adjust the import path as needed

from django.shortcuts import render, get_object_or_404, redirect
from orders.models import Order  # adjust the import if necessary
from orders.forms import OrderStatusForm

# users/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Order


def order_list_view(request):
    qs = Order.objects.all().order_by('-created_at')

    status_q   = request.GET.get('status')
    method_q   = request.GET.get('method')
    search_q   = request.GET.get('search')

    if status_q and status_q != 'All':
        qs = qs.filter(status=status_q)

    if method_q and method_q != 'All':
        qs = qs.filter(fulfillment_method=method_q)

    if search_q:
        qs = qs.filter(
            Q(order_id__icontains=search_q) |
            Q(user__first_name__icontains=search_q) |
            Q(user__last_name__icontains=search_q) |
            Q(user__email__icontains=search_q)
        )

    context = {
        'orders': qs,
        'status_choices': [('All','All')] + Order.STATUS_CHOICES,
        'method_choices': [('All','All')] + Order.FULFILLMENT_OPTIONS,
        'current_status': status_q or 'All',
        'current_method': method_q or 'All',
        'search_query': search_q or '',
    }
    return render(request, 'users/order_list.html', context)


def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('orders:order_detail', order_id=order.id)
    else:
        form = OrderStatusForm(instance=order)

    return render(request, 'users/order_detail.html', {
        'order': order,
        'form': form,
    })




from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from orders.models import Order
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from orders.models import Order

@require_POST
def change_order_status_ajax(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get("order_status")
    allowed_statuses = ['Pending', 'Paid', 'Shipped', 'Delivered', 'Complete', 'Cancelled']
    if new_status in allowed_statuses:
        order.status = new_status
        order.save()
        return JsonResponse({"success": True, "new_status": order.status})
    else:
        return JsonResponse({"success": False, "error": "Invalid status selected."}, status=400)


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import ProfileUpdateForm


