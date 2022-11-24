from rest_framework import serializers
from .models import File, AcceptedToken, Quote, Storage, PaymentMethod, Payment, PAYMENT_STATUS, UPLOAD_CODE

class TokensSerializer(serializers.ModelSerializer):
  def to_representation(self, instance):
    representation = super().to_representation(instance)

    # print("Instance detail ?", instance)
    # if (instance.is_created)
    if (instance):
      representation[instance.title] = instance.value

    return representation
  
  class Meta:
    model = AcceptedToken
    fields=[]
  
  def create(self, validated_data):
    print("From token creation", validated_data)

class PaymentMethodSerializer(serializers.ModelSerializer):
  acceptedTokens = TokensSerializer(many=True)
  class Meta:
    model = PaymentMethod
    fields=['chainId', 'acceptedTokens']

class StorageSerializer(serializers.ModelSerializer):
  paymentMethods = PaymentMethodSerializer(many=True)
  class Meta:
    model = Storage
    fields = ['type', 'description', 'url', 'paymentMethods']

  def create(self, validated_data):
    # print(validated_data)
    payment_method_data = validated_data.pop('paymentMethods')
    print(payment_method_data[0].pop('acceptedTokens'))
    # print(payment_method_data)
    storage = Storage.objects.create(**validated_data)

    for method in payment_method_data:
        # print('Payment method data', method)
        accepted_tokens_data = method.pop('acceptedTokens')

        # print('Accepted tokens data', accepted_tokens_data)
        payment_method = PaymentMethod.objects.create(storage=storage, **method)
        for accepted_token in accepted_tokens_data:
          print(accepted_token)
          tokenCreated = AcceptedToken.objects.create(paymentMethod=payment_method, **accepted_token)
          print('Created token', tokenCreated, tokenCreated.title, tokenCreated.value)

    return storage

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
  # payment = PaymentSerializer()
  files = FileSerializer(many=True)
  class Meta:
    model = Quote
    fields = ['storage', 'tokenAmount', 'quoteId', 'duration', 'tokenAddress', 'approveAddress', 'status', 'files']

  def create(self, validated_data):
    # payment_data = validated_data.pop('payment')
    files_data = validated_data.pop('files')
    quote = Quote.objects.create(**validated_data)

    # For payment method, check if it exits already. If so, associate it with the payment object instead of
    # payment_method = payment_data['paymentMethod']
    # method = PaymentMethod.objects.create(storage=validated_data['storage'], **payment_method)

    # payment_data['paymentMethod'] = method
    # Payment.objects.create(quote=quote, **payment_data)

    # Manage files save
    for file in files_data:
      File.objects.create(quote=quote, **file)

    return quote