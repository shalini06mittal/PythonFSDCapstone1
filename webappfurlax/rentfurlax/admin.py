from django.contrib import admin
from rentfurlax.models import *
# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Furniture)
class FurnitureAdmin(admin.ModelAdmin):
    pass

@admin.register(RentalOptions)
class RentalOptionsAdmin(admin.ModelAdmin):
    pass

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    pass

@admin.register(LineItem)
class LineItemAdmin(admin.ModelAdmin):
    pass