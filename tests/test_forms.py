from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from manager.models import Currency, Card, Accountancy


class FormTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test.user",
            password="testpass1234"
        )
        self.client.force_login(self.user)

        self.currency = Currency.objects.create(
            name="U. S. Dollar",
            abbreviation="USD",
            sign="$"
        )
        self.card = Card.objects.create(
            user=self.user,
            bank_name="Mono",
            type="Payment card",
            balance=150,
            currency=self.currency
        )

    def test_outcome_accountancy_form_for_incomes(self):
        accountancy_I = Accountancy.objects.create(
            card=self.card,
            IO="I",
            IO_type="Salary",
            amount=100
        )

        form_data = {
            "wallet_choice": f"card - {accountancy_I.amount}",
            "amount": "50"
        }
        response = self.client.post(
            path=reverse(
                "manager:accountancy-update",
                kwargs={
                    "pk": 1
                }
            ),
            data=form_data
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Card.objects.get(id=1).balance, 100)
        self.assertEqual(Accountancy.objects.get(id=1).amount, 50)

    def test_outcome_accountancy_form_for_outcomes(self):
        accountancy_O = Accountancy.objects.create(
            card=self.card,
            IO="O",
            IO_type="Home",
            amount=100
        )

        form_data = {
            "wallet_choice": f"card - {accountancy_O.amount}",
            "amount": "50"
        }
        response = self.client.post(
            path=reverse(
                "manager:accountancy-update",
                kwargs={
                    "pk": 1
                }
            ),
            data=form_data
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Card.objects.get(id=1).balance, 200)
        self.assertEqual(Accountancy.objects.get(id=1).amount, 50)


class SearchFormTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test_username",
            password="testpass1234",
        )
        self.client.force_login(self.user)

        self.currency = Currency.objects.create(
            name="U. S. Dollar",
            abbreviation="USD",
            sign="$"
        )
        self.card = Card.objects.create(
            user=self.user,
            bank_name="Mono",
            type="Payment card",
            balance=150,
            currency=self.currency
        )
        Accountancy.objects.create(
            card=self.card,
            IO="O",
            IO_type="Home",
            amount=15,
            datetime=datetime(2022, 12, 1)
        )
        Accountancy.objects.create(
            card=self.card,
            IO="O",
            IO_type="Pets",
            amount=8,
            datetime=datetime(2022, 12, 1)
        )

    def test_monthly_accountancy_search_form(self):
        search_term = {"IO_type": "Home"}
        response = self.client.get(
            path=reverse(
                "manager:monthly-accountancy",
                kwargs={
                    "wallet": "card",
                    "wallet_id": 1,
                    "month": 12,
                    "year": 2022
                }
            ),
            data=search_term
        )

        self.assertNotContains(response, "Pets")
