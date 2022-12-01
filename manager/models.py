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
    name = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=5, unique=True)
    sign = models.CharField(max_length=2, unique=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.abbreviation} - {self.sign})"


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
    bank_name = models.CharField(max_length=50)
    type = models.CharField(max_length=50, null=True)
    balance = models.DecimalField(
        max_digits=10_000_000,
        decimal_places=2,
        default=Decimal(0.0)
    )

    class Meta:
        ordering = ["bank_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["bank_name", "type"],
                name="unique_cards"
            )
        ]


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
        constraints = [
            models.UniqueConstraint(
                fields=["users", "currancy"],
                name="unique_cash"
            )
        ]

    def __str__(self) -> str:
        return f"User: {self.users} | Currancy: {self.currancy}"\
               f" | Balance: {self.balance}"


class Cryptocurrency(models.Model):
    users = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cryptocurrencies"
    )
    name = models.CharField(max_length=50)
    balance = models.DecimalField(
        max_digits=1_000_000,
        decimal_places=8,
        default=Decimal(0.0)
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["users", "name"],
                name="unique_crypto"
            )
        ]

    def __str__(self) -> str:
        return f"Name: {self.name} | Balance: {self.balance}"


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
    wallet_id = models.PositiveIntegerField()
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
    io_type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=1_000_000, decimal_places=2)
    datetime = models.DateTimeField(auto_now_add=True)
