# cart/context_processors.py
from .models import Cart

def cart_context(request):
    """
    Retrieves or creates a Cart for the current user or session,
    then returns it along with its items to be available in all templates.
    """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # Ensure there is a session_key; create one if not present.
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_id=session_key)

    # Return the cart and its items (or an empty list if cart is None)
    return {
        'cart': cart,
        'cart_items': cart.items.all() if cart else [],
    }
