import factory
from factory.django import DjangoModelFactory

from apps.mailings.models import Mailing


class MailingFactory(DjangoModelFactory):
    class Meta:
        model = Mailing

    external_id = factory.Sequence(lambda n: f"ext_{n}")
    user_id = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    subject = factory.Faker("sentence", nb_words=4)
    message = factory.Faker("paragraph")
