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
        print("to_representation called in PaymentMethodSerializer")
        try:
            representation = super().to_representation(instance)
            representation['acceptedTokens'] = [{"title": token.title, "value": token.value} for token in instance.acceptedTokens.all()]
            return representation
        except Exception as e:
            print(f"Error in PaymentMethodSerializer to_representation: {e}")
            raise e

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
        print("create called in CreateStorageSerializer")
        try:
            payment_method_data = validated_data.pop('payment')
            storage = Storage.objects.create(**validated_data)
            print(f"Storage created: {storage}")

            for method_data in payment_method_data:
                accepted_tokens_data = method_data.pop('acceptedTokens')
                method = PaymentMethod.objects.create(storage=storage, **method_data)
                print(f"PaymentMethod created: {method}")
                for accepted_token_data in accepted_tokens_data:
                    AcceptedToken.objects.create(paymentMethod=method, **accepted_token_data)
                    print(f"AcceptedToken created with data: {accepted_token_data}")

            return storage
        except Exception as e:
            print(f"Error in CreateStorageSerializer create: {e}")
            raise e

class QuoteSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer()
    files = FileSerializer(many=True)

    class Meta:
        model = Quote
        fields = ['storage', 'tokenAmount', 'quoteId', 'duration', 'tokenAddress', 'approveAddress', 'status', 'files', 'payment']

    def create(self, validated_data):
        print("create called in QuoteSerializer")
        try:
            payment_data = validated_data.pop('payment')
            files_data = validated_data.pop('files')
            quote = Quote.objects.create(**validated_data)
            print(f"Quote created: {quote}")

            payment_method_data = payment_data.pop('paymentMethod')
            method = PaymentMethod.objects.filter(storage=validated_data['storage'], chainId=payment_method_data['chainId']).first()
            if method:
                print(f"PaymentMethod found: {method}")
            else:
                print(f"No PaymentMethod found for chainId: {payment_method_data['chainId']}")

            payment_data['paymentMethod'] = method
            payment = Payment.objects.create(quote=quote, **payment_data)
            print(f"Payment created: {payment}")

            quote.payment = payment
            quote.save()

            for file_data in files_data:
                File.objects.create(quote=quote, **file_data)
                print(f"File created with data: {file_data}")

            return quote
        except Exception as e:
            print(f"Error in QuoteSerializer create: {e}")
            raise e
