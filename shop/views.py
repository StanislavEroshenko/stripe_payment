import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from .models import Item, Order

# Вообще вроде работает, но по хорошему надо протестить ещё раз. Я много чего менял пока делал доп. задания, что то где то могло слететь.

def get_stripe_keys(currency):
    if currency == 'usd':
        return settings.STRIPE_SECRET_KEY_USD, settings.STRIPE_PUBLIC_KEY_USD
    return settings.STRIPE_SECRET_KEY_EUR, settings.STRIPE_PUBLIC_KEY_EUR


def item_view(request, id):
    item = get_object_or_404(Item, id=id)
    _, public_key = get_stripe_keys(item.currency)
    return render(request, 'item.html', {'item': item, 'public_key': public_key})


def buy_item(request, id):
    item = get_object_or_404(Item, id=id)
    secret_key, public_key = get_stripe_keys(item.currency)
    stripe.api_key = secret_key
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': item.currency.lower(),
                'product_data': {'name': item.name},
                'unit_amount': item.price,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://127.0.0.1:8000',
        cancel_url='http://127.0.0.1:8000/item/{}/'.format(item.id),
    )
    return JsonResponse({'id': session.id})


def menu_view(request): 
    items = Item.objects.all()
    orders = Order.objects.all()
    return render(request, 'menu.html', {'items': items, 'orders': orders})


def buy_order(request, id):
    order = get_object_or_404(Order, id=id)
    items = order.items.all()
    currency = items.first().currency
    secret_key, _ = get_stripe_keys(currency)
    stripe.api_key = secret_key
    line_items = []
    for item in items:
        line_items.append({
            'price_data': {
                'currency': currency,
                'product_data': {
                    'name': item.name,
                },
                'unit_amount': item.price,
            },
            'quantity': 1,
        })
    discounts = []
    for d in order.discounts.all():
        coupon = stripe.Coupon.create(
            percent_off=d.percent,
            duration='once',
            name=d.name
        )
        discounts.append({'coupon': coupon.id})
    tax_rates = []
    for t in order.taxes.all():
        tax_rate = stripe.TaxRate.create(
            display_name=t.name,
            percentage=t.percent,
            inclusive=False
        )
        tax_rates.append(tax_rate.id)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                **li,
                'tax_rates': tax_rates
            } for li in line_items
        ],
        discounts=discounts,
        mode='payment',
        success_url='http://127.0.0.1:8000',
        cancel_url='http://127.0.0.1:8000', # Вообще не данном этапе этот момент меня смущает, но раз работает то оставляем.
    )

    return JsonResponse({'id': session.id})


def order_view(request, id):
    order = get_object_or_404(Order, id=id)
    items = order.items.all()
    total = sum(item.price for item in items)
    for d in order.discounts.all():
        total -= total * d.percent // 100
    for t in order.taxes.all():
        total += total * t.percent // 100
    _, public_key = get_stripe_keys(items.first().currency)
    return render(
        request,
        'order.html',
        {
            'order': order,
            'items': items,
            'total': total,
            'public_key': public_key,
        }
    )


def buy_item_intent(request, id):
    item = get_object_or_404(Item, id=id)
    secret_key, _ = get_stripe_keys(item.currency)
    stripe.api_key = secret_key

    intent = stripe.PaymentIntent.create(
        amount=item.price,
        currency=item.currency,
        automatic_payment_methods={'enabled': True}
    )

    return JsonResponse({'client_secret': intent.client_secret})