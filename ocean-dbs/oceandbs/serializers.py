from rest_framework import serializers
from .models import AcceptedToken, Quote, Storage, PaymentMethod, PAYMENT_STATUS, UPLOAD_CODE

class TokensSerializer(serializers.ModelSerializer):
  def to_representation(self, instance):
    representation = super().to_representation(instance)
    representation[instance.title] = instance.value
    return representation
  
  class Meta:
    model = AcceptedToken
    fields=[]

class PaymentMethodSerializer(serializers.ModelSerializer):
  accepted_tokens = TokensSerializer(many=True, read_only=True)
  class Meta:
    model = PaymentMethod
    fields=['chain_id', 'accepted_tokens']

class StorageSerializer(serializers.ModelSerializer):
  payment_methods = PaymentMethodSerializer(many=True, read_only=True)
  class Meta:
    model = Storage
    fields = ['type', 'description', 'payment_methods']


class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
      model = Quote
      fields = ['id', 'storage', 'duration', 'payment', 'wallet_address', 'upload_status']
