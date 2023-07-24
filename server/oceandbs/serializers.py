from rest_framework import serializers
from .models import File, AcceptedToken, Quote, Storage, PaymentMethod, Payment, PAYMENT_STATUS, UPLOAD_CODE


class AcceptedTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcceptedToken
        fields = ['title', 'value']


class PaymentMethodSerializer(serializers.ModelSerializer):
    acceptedTokens = AcceptedTokenSerializer(many=True, required=False)

    class Meta:
        model = PaymentMethod
        fields = ['chainId', 'acceptedTokens']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['acceptedTokens'] = [{"title": token.title, "value": token.value} for token in instance.acceptedTokens.all()]
        return representation

class PaymentSerializer(serializers.ModelSerializer):
    paymentMethod = PaymentMethodSerializer()

    class Meta:
        model = Payment
        fields = ['paymentMethod', 'userAddress', 'tokenAddress', 'status']


class FileSerializer(serializers.ModelSerializer):
  class Meta:
    model = File
    fields = ['length']


class StorageSerializer(serializers.ModelSerializer):
  payment = PaymentMethodSerializer(many=True)
  class Meta:
    model = Storage
    fields = ['type', 'description', 'payment']


class CreateStorageSerializer(serializers.ModelSerializer):
    payment = PaymentMethodSerializer(many=True)

    class Meta:
        model = Storage
        fields = ['type', 'description', 'url', 'payment']

    def create(self, validated_data):
        payment_method_data = validated_data.pop('payment')
        storage = Storage.objects.create(**validated_data)

        for method_data in payment_method_data:
            accepted_tokens_data = method_data.pop('acceptedTokens')
            method = PaymentMethod.objects.create(storage=storage, **method_data)
            for accepted_token_data in accepted_tokens_data:
                AcceptedToken.objects.create(paymentMethod=method, **accepted_token_data)

        return storage

class QuoteSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer()
    files = FileSerializer(many=True)

    class Meta:
        model = Quote
        fields = ['storage', 'tokenAmount', 'quoteId', 'duration', 'tokenAddress', 'approveAddress', 'status', 'files', 'payment']

    def create(self, validated_data):
        payment_data = validated_data.pop('payment')
        files_data = validated_data.pop('files')
        quote = Quote.objects.create(**validated_data)

        payment_method_data = payment_data.pop('paymentMethod')
        method = PaymentMethod.objects.filter(storage=validated_data['storage'], chainId=payment_method_data['chainId']).first()
        payment_data['paymentMethod'] = method
        payment = Payment.objects.create(quote=quote, **payment_data)

        quote.payment = payment
        quote.save()

        for file_data in files_data:
            File.objects.create(quote=quote, **file_data)

        return quote