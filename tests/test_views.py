from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.test import TestCase
from django.urls import reverse

from manager.models import (
    Currency,
    Card,
    Cash,
    Cryptocurrency,
    Accountancy,
)


WALLETS_URL = reverse("manager:wallets")
INDEX_URL = reverse("manager:index")
ACCOUNT_URL = reverse("manager:account")
ACCOUNTANCY_URL = reverse("manager:monthly-accountancy-list")
MONTHLY_ACCOUNTANCY_URL = reverse(
    "manager:monthly-accountancy",
    kwargs={
        "wallet": "card",
        "wallet_id": 1,
        "month": 11,
        "year": 2022
    }
)


class PublicViewsTests(TestCase):
    def test_wallets_login_required(self):
        response = self.client.get(WALLETS_URL)
        self.assertNotEqual(response.status_code, 200)

    def test_index_login_required(self):
        response = self.client.get(INDEX_URL)
        self.assertNotEqual(response.status_code, 200)

    def test_account_login_required(self):
        response = self.client.get(ACCOUNT_URL)
        self.assertNotEqual(response.status_code, 200)

    def test_accountancy_login_required(self):
        response = self.client.get(ACCOUNTANCY_URL)
        self.assertNotEqual(response.status_code, 200)


class PrivateViewsTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(  # type: ignore
            username="test",
            password="test1234"
        )
        self.client.force_login(self.user)

        currency = Currency.objects.create(
            name="U. S. Dollar",
            abbreviation="USD",
            sign="$"
        )
        payment_card = Card.objects.create(
            user=self.user,
            bank_name="Mono",
            type="Payment card",
            currency=currency
        )
        Card.objects.create(
            user=self.user,
            bank_name="Mono",
            type="Storage card",
            currency=currency
        )
        Cash.objects.create(user=self.user, currency=currency)
        bitcoin = Cryptocurrency.objects.create(
            user=self.user,
            name="BitCoin"
        )
        Cryptocurrency.objects.create(
            user=self.user,
            name="Dogecoin"
        )
        Accountancy.objects.create(
            card=payment_card,
            IO="I",
            IO_type="Salary",
            amount="25000",
            datetime=datetime(2022, 11, 1)
        )
        Accountancy.objects.create(
            cryptocurrency=bitcoin,
            IO="I",
            IO_type="Salary",
            amount="0.00020001",
            datetime=datetime(2022, 12, 1)
        )

    def test_retrieve_wallets(self):

        response = self.client.get(WALLETS_URL)
        cards = Card.objects.all()
        cash = Cash.objects.all()
        crypto = Cryptocurrency.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["cards_list"]),
            list(cards)
        )
        self.assertEqual(
            list(response.context["cash_list"]),
            list(cash)
        )
        self.assertEqual(
            list(response.context["crypto_list"]),
            list(crypto)
        )
        self.assertTemplateUsed(response, "manager/wallets.html")

    def test_retrieve_monthly_financial_turnover(self):
        response = self.client.get(ACCOUNTANCY_URL)
        accountancy = Accountancy.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(
            list(response.context["accountancy_list"]),
            list(accountancy)
        )
        self.assertTemplateUsed(
            response, "manager/monthly_accountancy_list.html"
        )

    def test_retrieve_wallets_financial_turnover(self):
        response = self.client.get(MONTHLY_ACCOUNTANCY_URL)
        accountancy = Accountancy.objects.filter(
            Q(datetime__month=11)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["accountancy_list"]),
            list(accountancy)
        )
        self.assertTemplateUsed(
            response, "manager/monthly_accountancy.html"
        )
