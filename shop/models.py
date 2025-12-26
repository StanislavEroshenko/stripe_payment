from django.db import models

class Item(models.Model):
    CURRENCY_CHOICES = ( #поставить рубли? думаю пойдет
        ('usd', 'USD'),
        ('eur', 'EUR'),
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField()
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    def str(self):
        return self.name

class Discount(models.Model):
    name = models.CharField(max_length=100)
    percent = models.IntegerField()

class Tax(models.Model):
    name = models.CharField(max_length=100)
    percent = models.IntegerField()

class Order(models.Model): # Вообще странно что Tax и Discount работают к Order, но не к Item, но так было написано в ТЗ. Может потом расширю если руки дайдут. Хотя боюсь напортачить если честно.
    items = models.ManyToManyField(Item)
    discounts = models.ManyToManyField(Discount, blank=True)
    taxes = models.ManyToManyField(Tax, blank=True)