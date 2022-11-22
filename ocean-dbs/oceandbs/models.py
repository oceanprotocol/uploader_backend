from tabnanny import verbose
from unittest.util import _MAX_LENGTH
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

PAYMENT_STATUS = [
  ['waiting', _('Waiting for transaction')],
  ['done', _('Payment done')],
  ['refunded', _('Payment refunded')]
]

UPLOAD_CODE = [
  ('200', 'Quote exists'),
  ('201', 'Quote created')
]

# Create your models here.
class Storage(models.Model):
  created = models.DateTimeField(default=timezone.now)
  type = models.CharField(max_length=256, verbose_name=_("Storage type"))
  description= models.TextField(verbose_name = _("Storage description"), null=True, blank=True)
  url = models.URLField(max_length=2048, default="https://example.com")

  def __str__(self):
    return self.type + " - " + self.description

  class Meta:
    ordering = ['created']

class PaymentMethod(models.Model):
  chain_id = models.CharField(max_length=256)
  storage = models.ForeignKey(Storage, null=True, on_delete=models.SET_NULL, related_name="payment_methods")

  def __str__(self):
    return self.chain_id + " - " + str(self.storage)


class AcceptedToken(models.Model):
  title = models.CharField(max_length=256)
  value = models.CharField(max_length=256)
  payment_method = models.ForeignKey(PaymentMethod, null=True, on_delete=models.SET_NULL, related_name="accepted_tokens")

  def __str__(self):
    return str(self.payment_method) + " - " + self.title + " - " + self.value


class Payment(models.Model):
  status = models.CharField(choices = PAYMENT_STATUS, max_length = 256, null = True)
  wallet_address = models.CharField(max_length=256, null = True)
  payment_method = models.ForeignKey(PaymentMethod, null=True, on_delete=models.SET_NULL, related_name="payments")


class Quote(models.Model):
  created = models.DateTimeField(default=timezone.now)
  quoteId = models.CharField(max_length=256, null = True)
  storage = models.ForeignKey(Storage, null = True, on_delete=models.SET_NULL, related_name ="quotes")
  duration = models.BigIntegerField()
  payment = models.OneToOneField(Payment, null=True, blank=True, related_name = "quote", on_delete=models.CASCADE)
  tokenAddress = models.CharField(max_length=256, null = True)
  approveAddress = models.CharField(max_length=256, null = True)
  tokenAmount = models.BigIntegerField(null = True)
  upload_status = models.CharField(choices=UPLOAD_CODE, null=True, blank=True, max_length=256)

  def __str__(self):
    return str(self.storage) + " - " + self.tokenAddress

  class Meta:
    ordering = ['created']


class File(models.Model):
    original_url = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255, default='None')
    stored_url = models.CharField(max_length=255, blank=True)
    object_content = models.BinaryField(blank=True)
    is_bytes = models.BooleanField(default=False)
    quote = models.ForeignKey(Quote, null=True, on_delete=models.SET_NULL, related_name="files")
    
    def __str__(self):
        return self.original_url