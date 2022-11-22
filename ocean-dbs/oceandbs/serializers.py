from rest_framework import serializers
from .models import File, AcceptedToken, Quote, Storage, PaymentMethod, Payment, PAYMENT_STATUS, UPLOAD_CODE


class TokensSerializer(serializers.ModelSerializer):
  def to_representation(self, instance):
    representation = super().to_representation(instance)
    representation[instance.title] = instance.value
    return representation
  
  class Meta:
    model = AcceptedToken
    fields=[]

class PaymentMethodSerializer(serializers.ModelSerializer):
  acceptedTokens = TokensSerializer(many=True, read_only=True)
  class Meta:
    model = PaymentMethod
    fields=['chainId', 'acceptedTokens']

class StorageSerializer(serializers.ModelSerializer):
  paymentMethods = PaymentMethodSerializer(many=True, read_only=True)
  class Meta:
    model = Storage
    fields = ['type', 'description', 'paymentMethods']

class PaymentSerializer(serializers.ModelSerializer):
  paymentMethod = PaymentMethodSerializer()

  class Meta:
    model = Payment
    fields = ['paymentMethod', 'wallet_address']

  def create(self, validated_data):
    payment_method_data = validated_data.pop('payment')
    payment = Payment.objects.create(**validated_data)
    for method in payment_method_data:
        PaymentMethod.objects.create(payment=payment, **method)
    return payment


class FileSerializer(serializers.ModelSerializer):
  class Meta:
    model = File
    fields = ['length']


class QuoteSerializer(serializers.ModelSerializer):
  payment = PaymentSerializer()
  files = FileSerializer(many=True)
  class Meta:
    model = Quote
    fields = ['storage', 'tokenAmount', 'quoteId', 'duration', 'payment', 'tokenAddress', 'approveAddress', 'status', 'files']

  def create(self, validated_data):
    payment_data = validated_data.pop('payment')
    files_data = validated_data.pop('files')
    quote = Quote.objects.create(**validated_data)

    # For payment method, check if it exits already. If so, associate it with the payment object instead of
    payment_method = payment_data['paymentMethod']
    method = PaymentMethod.objects.create(storage=validated_data['storage'], **payment_method)

    payment_data['paymentMethod'] = method
    Payment.objects.create(quote=quote, **payment_data)

    # Manage files save
    for file in files_data:
      File.objects.create(quote=quote, **file)

    return quote