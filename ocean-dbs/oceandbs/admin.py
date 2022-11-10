from django.contrib import admin

from .models import AcceptedToken, Storage, Quote, PaymentMethod, Payment, File

class AcceptedTokenAdmin(admin.ModelAdmin):
    fields = ['title', 'value', 'payment_method']
    readonly_fields = ('id',)

class PaymentMethodAdmin(admin.ModelAdmin):
    fields = ['chain_id', 'storage']
    readonly_fields = ('id',)

class StorageAdmin(admin.ModelAdmin):
    fields = ['type', 'description']
    readonly_fields = ('id',)

class PaymentAdmin(admin.ModelAdmin):
    fields = ['wallet_address', 'payment_method']
    readonly_fields = ('id',)

class QuoteAdmin(admin.ModelAdmin):
    fields = ['storage', 'duration', 'payment', 'wallet_address', 'upload_status']
    readonly_fields = ('id',)

class FileAdmin(admin.ModelAdmin):
    fields = ['original_url', 'content_type', 'stored_url', 'object_content', 'is_bytes', 'quote']
    readonly_fields = ('id',)

admin.site.register(AcceptedToken, AcceptedTokenAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(Storage, StorageAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(PaymentMethod, PaymentMethodAdmin)