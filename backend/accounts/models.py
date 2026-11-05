from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower


class User(AbstractUser):
    email = models.EmailField(blank=False)

    class Meta(AbstractUser.Meta):
        constraints = [models.UniqueConstraint(Lower("email"), condition=~models.Q(email=""), name="unique_account_email_casefold")]

    @property
    def display_name(self):
        return self.get_full_name() or self.get_username()

    @property
    def initial(self):
        return self.display_name[:1].upper()
