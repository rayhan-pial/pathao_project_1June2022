from django.contrib import admin
from .models import CategoryModel, ProductModel, ShortageOfProduct, Cart, Order, BillingAddress

# Register your models here.
admin.site.register(CategoryModel)
admin.site.register(ProductModel)
admin.site.register(ShortageOfProduct)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(BillingAddress)

