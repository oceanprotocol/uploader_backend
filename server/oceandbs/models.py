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
  (0, 'No such quote'),
  (1, 'Waiting for files to be uploaded'),
  (100, 'Processing payment'),
  (200, 'Processing payment failure modes'),
  (300, 'Uploading file to storage'),
  (400, 'Upload done'),
  (401, 'Upload failure modes'),
]

# Create your models here.
class Storage(models.Model):
  created = models.DateTimeField(default=timezone.now)
  type = models.CharField(max_length=256, verbose_name=_("Storage type"))
  description= models.TextField(verbose_name = _("Storage description"), null=True, blank=True)
  url = models.URLField(max_length=2048, default="https://example.com")
  is_active = models.BooleanField(default=True)

  def __str__(self):
    print("Storage __str__ method called")
    return self.type + " - " + self.description

  class Meta:
    ordering = ['created']

class PaymentMethod(models.Model):
  chainId = models.CharField(max_length=256)
  storage = models.ForeignKey(Storage, null=True, on_delete=models.CASCADE, related_name="payment")
  rpcEndpointUrl = models.URLField(max_length=2048, default="https://rpc-mumbai.maticvigil.com/")

  def __str__(self):
    print("PaymentMethod __str__ method called")
    return self.chainId + " - " + str(self.storage)


class AcceptedToken(models.Model):
  title = models.CharField(max_length=256)
  value = models.CharField(max_length=256)
  paymentMethod = models.ForeignKey(PaymentMethod, null=True, on_delete=models.CASCADE, related_name="acceptedTokens")

  def __str__(self):
    print("AcceptedToken __str__ method called")
    return str(self.paymentMethod) + " - " + self.title + " - " + self.value


class Payment(models.Model):
  status = models.CharField(choices = PAYMENT_STATUS, default=PAYMENT_STATUS[0], max_length = 256)
  tokenAddress = models.CharField(max_length=256, null = True)
  userAddress = models.CharField(max_length=256, null = True)
  paymentMethod = models.ForeignKey(PaymentMethod, null=True, on_delete=models.CASCADE, related_name="payments")

def nonce_computation():
    print("Payment nonce_computation method called")
    return timezone.now() - timezone.timedelta(days=7)

class Quote(models.Model):
  created = models.DateTimeField(default=timezone.now)
  quoteId = models.CharField(max_length=256, null=True)
  storage = models.ForeignKey(Storage, null=True, on_delete=models.SET_NULL, related_name="quotes")
  duration = models.BigIntegerField()
  payment = models.OneToOneField(Payment, null=True, blank=True, related_name="quote", on_delete=models.CASCADE)
  tokenAddress = models.CharField(max_length=256, null=True)
  approveAddress = models.CharField(max_length=256, null=True)
  tokenAmount = models.CharField(max_length=256, null=True)
  status = models.CharField(choices=UPLOAD_CODE, default=UPLOAD_CODE[1], null=True, blank=True, max_length=3)
  nonce = models.DateTimeField(default=nonce_computation())

  def __str__(self):
    print("Quote __str__ method called")
    return str(self.storage) + " - " + self.tokenAddress

  class Meta:
    ordering = ['created']

class File(models.Model):
  title = models.CharField(max_length=256, null=True)
  public_url = models.CharField(max_length=2048, null=True)
  cid = models.CharField(max_length=2048, null=True)
  quote = models.ForeignKey(Quote, null=True, on_delete=models.SET_NULL, related_name="files")
  length = models.BigIntegerField(default=0)

  def __str__(self):
    print("File __str__ method called")
    return str(self.quote) + " - " + str(self.length)
