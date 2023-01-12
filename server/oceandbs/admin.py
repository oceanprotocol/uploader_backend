from django.contrib import admin

from .models import AcceptedToken, Storage, Quote, PaymentMethod, Payment, File

class CustomModelAdmin(admin.ModelAdmin):    
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields if field.name != "id"]
        super(CustomModelAdmin, self).__init__(model, admin_site)

class AcceptedTokenAdmin(CustomModelAdmin):
    readonly_fields = ('id',)

class PaymentMethodAdmin(CustomModelAdmin):
    readonly_fields = ('id',)

class StorageAdmin(CustomModelAdmin):
    readonly_fields = ('id',)

class PaymentAdmin(CustomModelAdmin):
    readonly_fields = ('id',)

class QuoteAdmin(CustomModelAdmin):
    readonly_fields = ('id',)

class FileAdmin(CustomModelAdmin):
    readonly_fields = ('id',)

admin.site.register(AcceptedToken, AcceptedTokenAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(Storage, StorageAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(PaymentMethod, PaymentMethodAdmin)