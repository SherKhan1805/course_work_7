from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.create(
            email='usaechv98@mail.ru',
            first_name='admin',
            last_name='admin',
            is_staff=True,
            is_superuser=True

        )

        user.set_password('alexia1456')
        user.save()
