from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product

def bag_contents(request):
    # Initialize variables to store bag items, total, and product count
    bag_items = []
    total = 0
    product_count = 0

    # Retrieve the current bag from the session
    bag = request.session.get('bag', {})

    # Iterate through items in the bag
    for item_id, item_data in bag.items():
        # Check if the item_data is an integer (no size variations)
        if isinstance(item_data, int):
            # Get the product information from the database
            product = get_object_or_404(Product, pk=item_id)
            # Calculate total price for this item
            total += item_data * product.price
            # Increment the product count
            product_count += item_data
            # Add item details to bag_items list
            bag_items.append({
                'item_id': item_id,
                'quantity': item_data,
                'product': product,
            })
        else:
            # Handle products with size variations
            product = get_object_or_404(Product, pk=item_id)
            # Iterate through size and quantity in items_by_size dictionary
            for size, quantity in item_data['items_by_size'].items():
                # Calculate total price for this size and quantity
                total += quantity * product.price
                # Increment the product count
                product_count += quantity
                # Add item details to bag_items list
                bag_items.append({
                    'item_id': item_id,
                    'quantity': quantity,
                    'product': product,
                    'size': size,
                })

    # Calculate delivery cost and free delivery threshold delta
    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0
    
    # Calculate grand total
    grand_total = delivery + total
    
    # Create context dictionary with bag information
    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    # Return the context
    return context