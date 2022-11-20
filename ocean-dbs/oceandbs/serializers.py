from rest_framework import serializers
from .models import AcceptedToken, Quote, Storage, PaymentMethod, Payment, PAYMENT_STATUS, UPLOAD_CODE

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

class PaymentSerializer(serializers.ModelSerializer):
  payment_method = PaymentMethodSerializer()

  class Meta:
    model = Payment
    fields = ['payment_method', 'wallet_address']

  def create(self, validated_data):
    payment_method_data = validated_data.pop('payment')
    payment = Payment.objects.create(**validated_data)
    for method in payment_method_data:
        PaymentMethod.objects.create(payment=payment, **method)
    return payment

class QuoteSerializer(serializers.ModelSerializer):
  payment = PaymentSerializer()
  class Meta:
    model = Quote
    fields = ['id', 'storage', 'duration', 'payment', 'wallet_address', 'upload_status']

  def create(self, validated_data):
    #TODO: make sure validated data or data contains type and files
    #TODO: from type, retrieve associated storage object
    # If not exists, raise error
    
    # From files, retrieve individual file size
    
    # For the given type of storage, make a call to the associated service API (mock first) to retrieve a cost associated with that
    # Save the cost/payment request
    
    # For payment method, check if it exits already. If so, associate it with the payment object instead of
    # creating the new payment with status still to execute
    print(validated_data)
    storage = Storage.objects.get(type=validated_data.pop('type'))
    print(storage)
    payment_data = validated_data.pop('payment')
    quote = Quote.objects.create(storage=storage, **validated_data)
    payment_method = payment_data['payment_method']
    method = PaymentMethod.objects.create(**payment_method)
    payment_data['payment_method'] = method
    Payment.objects.create(quote=quote, **payment_data)
    
    print(PaymentMethod.objects.all())
    print(Payment.objects.all())
    print(Quote.objects.all())
    return quote

