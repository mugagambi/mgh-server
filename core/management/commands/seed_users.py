from django.core.management.base import BaseCommand
from faker import Faker

from core.models import User

fake = Faker('en_US')


class Command(BaseCommand):
    help = 'generate 50 fake system users'

    def handle(self, *args, **options):
        for i in range(0, 50):
            username = 'username' + str(i)
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = fake.email()
            password = fake.password()
            User.objects.create_user(username=username, email=email, password=password, first_name=first_name,
                                     last_name=last_name)
            msg = f'added user {username}, {first_name}, {last_name}, {email}, {password}'
            print(msg)
