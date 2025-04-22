from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from orders.models import Order


@login_required
def user_orders(request):
    """Display all orders for the logged-in user with optimized queries and first image handling."""
    user = request.user

    # ✅ Optimized Query: Prefetch related items & products to minimize DB hits
    orders = (
        Order.objects.filter(user=user)
        .prefetch_related("items__product_variation__product", "items__product")
        .order_by("-created_at")
    )

    # ✅ Attach the first image dynamically to each order
    for order in orders:
        first_item = order.items.first()  # ✅ Get the first OrderItem

        if first_item:
            if first_item.product_variation and first_item.product_variation.image:
                order.first_image = first_item.product_variation.image.url
            elif first_item.product_variation and first_item.product_variation.product.image:
                order.first_image = first_item.product_variation.product.image.url
            elif first_item.product and first_item.product.image:  # ✅ Handle plain products
                order.first_image = first_item.product.image.url
            else:
                order.first_image = "/static/images/default-product.jpg"  # ✅ Fallback image
        else:
            order.first_image = "/static/images/default-product.jpg"  # ✅ Ensure an image is always available

    context = {
        "orders": orders,
        "total_orders": orders.count(),
    }
    return render(request, "orders/orders.html", context)



from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from orders.models import Order

@login_required
def order_detail(request, order_id):
    """Displays detailed information about a single order with optimized queries and safe product access."""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    # ✅ Optimized Query: Select related products to avoid redundant queries
    order_items = order.items.select_related("product_variation__product", "product")

    context = {
        'order': order,
        'order_items': order_items,  # ✅ Ensures safe looping in template
    }
    return render(request, 'store/order_detail.html', context)








from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import RefundRequest, Order, OrderItem
from .forms import RefundRequestForm

from django.shortcuts import render, redirect, get_object_or_404
from .models import RefundRequest, RefundMedia, Order, OrderItem
from .forms import RefundRequestForm
from django.contrib import messages

from django.shortcuts import render, redirect, get_object_or_404
from .models import RefundRequest, RefundMedia, Order, OrderItem
from .forms import RefundRequestForm, RefundMediaForm
from django.contrib import messages

from django.shortcuts import render, redirect
from .forms import RefundRequestForm, RefundMediaForm
from .models import RefundRequest

from django.shortcuts import render, redirect
from .forms import RefundRequestForm, RefundMediaForm

from django.shortcuts import render, redirect, get_object_or_404
from .forms import RefundRequestForm, RefundMediaForm


# from .models import Order  # Uncomment if you need to fetch the order

from django.shortcuts import render, get_object_or_404
from .models import RefundRequest, RefundMedia
from orders.models import Order, OrderItem
from .forms import RefundRequestForm, RefundMediaForm

import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import RefundRequest, RefundMedia
from orders.models import Order, OrderItem
from .forms import RefundRequestForm, RefundMediaForm

# Set up logging
logger = logging.getLogger(__name__)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Order, OrderItem, RefundRequest
from .forms import RefundRequestForm, RefundMediaForm

import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Order, OrderItem, RefundRequest, RefundMedia
from .forms import RefundRequestForm, RefundMediaForm

# Configure Logging
logger = logging.getLogger(__name__)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum
import logging
from decimal import Decimal
from .models import Order, OrderItem, RefundRequest
from .forms import RefundRequestForm, RefundMediaForm

logger = logging.getLogger(__name__)

@login_required
def refund_request_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all()  # Get all items in the order

    # ✅ Fetch Refund History for this Order
    refund_history = RefundRequest.objects.filter(order=order).order_by("-requested_at")

    if request.method == "POST":
        logger.info("🟢 Refund Request Started for Order ID: %s", order_id)
        refund_requests = []
        refund_form = RefundRequestForm(request.POST)
        media_form = RefundMediaForm(request.POST, request.FILES)

        for item in order_items:
            refund_item_key = f"refund_item_{item.id}"
            refund_quantity_key = f"refund_quantity_{item.id}"

            if refund_item_key in request.POST:  # Check if item is selected
                refund_quantity = int(request.POST.get(refund_quantity_key, 0))

                # ✅ Check already refunded quantity
                already_refunded = RefundRequest.objects.filter(order_item=item, status__in=['pending', 'approved']).aggregate(Sum('quantity'))['quantity__sum'] or 0
                remaining_quantity = item.quantity - already_refunded

                # Safely determine product name for logging and messaging
                if item.product_variation and item.product_variation.product:
                    product_name = item.product_variation.product.name
                elif item.product and item.product.name:
                    product_name = item.product.name
                else:
                    product_name = "Unknown Product"

                logger.info(f"🔍 Processing refund for {product_name} - Requested: {refund_quantity}, Already Refunded: {already_refunded}, Remaining: {remaining_quantity}")

                # **🚨 Prevent over-refunding**
                if refund_quantity > remaining_quantity:
                    messages.error(request, f"🚫 You cannot return more than {remaining_quantity} of {product_name}.")
                    return redirect("orders:request_refund", order_id=order.id)

                # **🚨 Enforce full quantity for bags and boxes**
                if item.purchase_type == "bag" and item.product_variation and refund_quantity != item.product_variation.bag_size:
                    messages.error(request, f"🚫 You must return the entire bag size ({item.product_variation.bag_size}).")
                    return redirect("orders:request_refund", order_id=order.id)

                if item.purchase_type == "box" and item.product_variation and refund_quantity != item.product_variation.box_size:
                    messages.error(request, f"🚫 You must return the entire box size ({item.product_variation.box_size}).")
                    return redirect("orders:request_refund", order_id=order.id)

                # **✅ Create Refund Request**
                refund_request = RefundRequest(
                    user=request.user,
                    order=order,
                    order_item=item,
                    quantity=refund_quantity,
                    refund_reason=request.POST.get("refund_reason", ""),
                    additional_comments=request.POST.get("additional_comments", ""),
                )
                refund_requests.append(refund_request)

        # **✅ Save Refund Requests and process file uploads**
        if refund_requests:
            for refund_request in refund_requests:
                refund_request.save()
                for file in request.FILES.getlist("media_files"):
                    RefundMedia.objects.create(
                        refund_request=refund_request,
                        media_file=file
                    )
            messages.success(request, "✅ Your refund request has been submitted successfully.")
            logger.info("🟢 Refund Request Submitted Successfully")
        else:
            messages.error(request, "🚫 No valid refund items selected.")
            logger.warning("⚠️ No valid refund items selected")

        return redirect("orders:request_refund", order_id=order.id)

    return render(request, "orders/refund.html", {
        "order": order,
        "order_items": order_items,
        "refund_form": RefundRequestForm(),
        "media_form": RefundMediaForm(),
        "refund_history": refund_history,  # ✅ Added refund history to the template
    })









@login_required
def refund_history(request):
    """Show the user their refund history."""
    refunds = RefundRequest.objects.filter(user=request.user)
    return render(request, "orders/refund_history.html", {"refunds": refunds})


@login_required
def refund_detail(request, refund_id):
    """Show details of a specific refund request."""
    refund = get_object_or_404(RefundRequest, id=refund_id, user=request.user)
    return render(request, "orders/refund_detail.html", {"refund": refund})


