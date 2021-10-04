from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    def __str__ (self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ Create a new profile object when a Django User is created."""
    if created:
        Profile.objects.create(user=instance)


class Portfolio(models.Model):
    owner = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
    )


class Trade(models.Model):
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
    )
    trade_date = models.DateField()
    symbol = models.CharField(max_length=12)
    units = models.FloatField()
    effective_price = models.FloatField()
    units = models.FloatField()
    brokerage_fee = models.FloatField()
    trade_type = models.CharField(max_length=1) # B or S

    def get_trade_value(self):
        return float((self.units * self.effective_price))