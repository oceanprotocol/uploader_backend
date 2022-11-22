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
  ('201', 'Quote created'),
  ('202', 'Files uploaded'),
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
  chainId = models.CharField(max_length=256)
  storage = models.ForeignKey(Storage, null=True, on_delete=models.SET_NULL, related_name="paymentMethods")

  def __str__(self):
    return self.chainId + " - " + str(self.storage)


class AcceptedToken(models.Model):
  title = models.CharField(max_length=256)
  value = models.CharField(max_length=256)
  paymentMethod = models.ForeignKey(PaymentMethod, null=True, on_delete=models.SET_NULL, related_name="acceptedTokens")

  def __str__(self):
    return str(self.paymentMethod) + " - " + self.title + " - " + self.value


class Payment(models.Model):
  status = models.CharField(choices = PAYMENT_STATUS, default=PAYMENT_STATUS[0], max_length = 256)
  wallet_address = models.CharField(max_length=256, null = True)
  paymentMethod = models.ForeignKey(PaymentMethod, null=True, on_delete=models.SET_NULL, related_name="payments")


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
  public_url = models.CharField(max_length=255, null=True)
  quote = models.ForeignKey(Quote, null=True, on_delete=models.SET_NULL, related_name="files")
  length = models.BigIntegerField(default=0)
  file = models.FileField(null=True, blank=True)

  def __str__(self):
    return str(self.quote) + " - " + str(self.length)
