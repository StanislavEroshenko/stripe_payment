from django.urls import path
from .views import item_view, buy_item, buy_order, menu_view, order_view, buy_item_intent

urlpatterns = [
    path('item/<int:id>/', item_view),
    path('buy/<int:id>/', buy_item), #Относится к item, не забыть
    path('order/<int:id>/', order_view),
    path('order/buy/<int:id>/', buy_order),
    path('', menu_view),
    path('buy-intent/<int:id>/', buy_item_intent),
]