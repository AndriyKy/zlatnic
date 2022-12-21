from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    phone_number = PhoneNumberField(blank=True)


class Currency(models.Model):
    name = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=5)
    sign = models.CharField(max_length=5)

    def __str__(self) -> str:
        return f"{self.name} ({self.abbreviation})"


class Card(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cards"
    )
    bank_name = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    balance = models.FloatField(default=0.0)
    currency = models.ForeignKey(
        Currency,
        on_delete=models.RESTRICT,
        related_name="cards"
    )

    def save(self, *args, **kwargs):
        self.balance = round(self.balance, 2)
        return super(Card, self).save(*args, **kwargs)

    class Meta:
        ordering = ["bank_name"]
        constraints = [
            models.UniqueConstraint(
                fields=("user", "bank_name", "type",),
                name="unique_user_cards"
            ),
            models.CheckConstraint(
                check=(Q(balance__gte=0)),
                name="positive_card_balance"
            )
        ]

    def __str__(self):
        return f"Card: {self.bank_name} - {self.type} - "\
               f"{self.balance} {self.currency.sign}"


class Cash(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cash"
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.RESTRICT,
        related_name="cash"
    )
    balance = models.FloatField(default=0.0)

    def save(self, *args, **kwargs):
        self.balance = round(self.balance, 2)
        return super(Cash, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "cash"
        verbose_name_plural = "cash"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "currency",),
                name="unique_user_cash"
            ),
            models.CheckConstraint(
                check=(Q(balance__gte=0)),
                name="positive_cash_balance"
            )
        ]

    def __str__(self) -> str:
        return f"Cash - {self.balance} {self.currency.sign} "\
               f"({self.currency.abbreviation})"


class Cryptocurrency(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cryptocurrencies"
    )
    name = models.CharField(max_length=50)
    balance = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=Decimal(0.0)
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=("user", "name",),
                name="unique_user_cryptocurrencies"
            ),
            models.CheckConstraint(
                check=(Q(balance__gte=0)),
                name="positive_cryptocurrency_balance"
            )
        ]

    def __str__(self) -> str:
        return f"Cryptocurrency: {self.name} - {self.balance}"


class Accountancy(models.Model):
    INCOME = "I"
    OUTCOME = "O"
    IN_OUT_COME = [
        (INCOME, "Income"),
        (OUTCOME, "Outcome"),
    ]
    RELATED_NAME = "accountancy"

    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name=RELATED_NAME,
        null=True,
        blank=True
    )
    cash = models.ForeignKey(
        Cash,
        on_delete=models.CASCADE,
        related_name=RELATED_NAME,
        null=True,
        blank=True
    )
    cryptocurrency = models.ForeignKey(
        Cryptocurrency,
        on_delete=models.CASCADE,
        related_name=RELATED_NAME,
        null=True,
        blank=True
    )
    IO = models.CharField(
        max_length=1,
        choices=IN_OUT_COME,
        default=OUTCOME
    )
    IO_type = models.CharField(max_length=50)
    amount = models.FloatField()
    datetime = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.card and self.cash and self.cryptocurrency:
            raise ValidationError("Only one of the wallet fields can be set.")
        if self.amount < 0:
            raise ValidationError("Amount can't be negative.")

    class Meta:
        ordering = ["-datetime"]
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(card__isnull=False) &
                    Q(cash__isnull=True) &
                    Q(cryptocurrency__isnull=True)
                ) | (
                    Q(card__isnull=True) &
                    Q(cash__isnull=False) &
                    Q(cryptocurrency__isnull=True)
                ) | (
                    Q(card__isnull=True) &
                    Q(cash__isnull=True) &
                    Q(cryptocurrency__isnull=False)
                ),
                name="only_one_wallet"
            ),
            models.CheckConstraint(
                check=(Q(amount__gte=0)),
                name="positive_amount"
            )
        ]
