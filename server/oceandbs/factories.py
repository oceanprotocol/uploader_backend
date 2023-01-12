from factory import Factory, Faker
from .models import Storage, Quote, PaymentMethod

class StorageFactory(Factory):
  class Meta:
    model = Storage
    abstract = False
  type = Faker("name")
  description = Faker("job")
  

class QuoteFactory(Factory):
  class Meta:
    model = Quote
    abstract = False
    
class PaymentMethodFactory(Factory):
  class Meta:
    model = PaymentMethod