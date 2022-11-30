from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    phone_number = PhoneNumberField(blank=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Currancy(models.Model):
    name = models.CharField(max_length=150, unique=True)
    abbreviation = models.CharField(max_length=5, unique=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.abbreviation})"


class Card(models.Model):
    users = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cards"
    )
    currancy = models.ForeignKey(
        Currancy,
        on_delete=models.RESTRICT,
        related_name="cards"
    )
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, null=True)
    balance = models.DecimalField(
        max_digits=10_000_000,
        decimal_places=2,
        default=Decimal(0.0)
    )

    class Meta:
        ordering = ["name"]


class Cash(models.Model):
    users = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cash"
    )
    currancy = models.ForeignKey(
        Currancy,
        on_delete=models.RESTRICT,
        related_name="cash"
    )
    balance = models.DecimalField(
        max_digits=10_000_000,
        decimal_places=2,
        default=Decimal(0.0)
    )

    class Meta:
        verbose_name = "cash"
        verbose_name_plural = "cash"

    def __str__(self) -> str:
        return f"User: {self.users} | Currancy: {self.currancy}"\
               f" | Balance: {self.balance}"


class Cryptocurrency(models.Model):
    users = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cryptocurrencies"
    )
    name = models.CharField(max_length=255)
    balance = models.DecimalField(
        max_digits=1_000_000,
        decimal_places=8,
        default=Decimal(0.0)
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"User: {self.users} | Name: {self.name}"\
               f" | Balance: {self.balance}"


class Accountancy(models.Model):
    INCOME = "I"
    OUTCOME = "O"
    IO = [
        (INCOME, "Income"),
        (OUTCOME, "Outcome"),
    ]

    CARD = "CD"
    CASH = "CSH"
    CRYPTOCURRENCY = "CC"
    WALLET_TYPE = [
        (CARD, "Card"),
        (CASH, "Cash"),
        (CRYPTOCURRENCY, "Cryptocurrency"),
    ]

    users = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="accountancy"
    )
    wallet = models.IntegerField()
    wallet_type = models.CharField(
        max_length=3,
        choices=WALLET_TYPE,
        default=CASH
    )
    io = models.CharField(
        max_length=1,
        choices=IO,
        default=OUTCOME
    )
    io_type = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=1_000_000, decimal_places=2)
    datetime = models.DateTimeField(auto_now_add=True)
