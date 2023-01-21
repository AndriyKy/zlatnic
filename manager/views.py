from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth, Round
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic

from manager.forms import (
    AccountancyForm,
    AccountancySearchForm,
)
from manager.models import Card, Cash, Cryptocurrency, Accountancy
from manager.wallet_operations import (
    wallet_choice,
    monthly_financial_turnover,
    wallet_data_parse,
    change_wallet_balance,
)


def wallet_objects(request):
    user = request.user
    cards = user.cards.select_related("currency")
    cash_types = user.cash.select_related("currency")
    crypto = user.cryptocurrencies.all()

    return cards, cash_types, crypto


@login_required
def wallets(request):
    cards, cash_types, crypto = wallet_objects(request)

    context = {
        "cards_list": cards,
        "cash_list": cash_types,
        "crypto_list": crypto,
    }
    return render(request, "manager/wallets.html", context)


class CardCreateView(LoginRequiredMixin, generic.CreateView):
    model = Card
    fields = (
        "user",
        "bank_name",
        "type",
        "balance",
        "currency",
    )
    success_url = reverse_lazy("manager:wallets")


class CardUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Card
    fields = (
        "user",
        "bank_name",
        "type",
        "currency",
    )
    success_url = reverse_lazy("manager:wallets")


class CardDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Card
    success_url = reverse_lazy("manager:wallets")


class CashCreateView(LoginRequiredMixin, generic.CreateView):
    model = Cash
    fields = (
        "user",
        "currency",
    )
    success_url = reverse_lazy("manager:wallets")


class CashUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Cash
    fields = (
        "user",
        "currency",
    )
    success_url = reverse_lazy("manager:wallets")


class CashDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Cash
    success_url = reverse_lazy("manager:wallets")


class CryptoCreateView(LoginRequiredMixin, generic.CreateView):
    model = Cryptocurrency
    fields = (
        "user",
        "name",
    )
    success_url = reverse_lazy("manager:wallets")


class CryptoUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Cryptocurrency
    fields = (
        "user",
        "name",
    )
    success_url = reverse_lazy("manager:wallets")


class CryptoDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Cryptocurrency
    success_url = reverse_lazy("manager:wallets")


@login_required
def index(request):
    """Function-based view for the base page of the site."""

    wallets_set = []
    error = False
    current_balance = income = outcome = 0
    accountancy = Accountancy.objects

    cards, cash_types, crypto = wallet_objects(request)

    if cards:
        for card in cards:
            wallets_set.append([f"card - {card.id}", card])

    if cash_types:
        for cash in cash_types:
            wallets_set.append([f"cash - {cash.id}", cash])

    if crypto:
        for crypto in crypto:
            wallets_set.append([f"crypto - {crypto.id}", crypto])

    # Check whether POST includes any wallet data to process
    if "wallet_choice" in request.POST and request.POST["wallet_choice"]:
        wallet_type, wallet_id = wallet_data_parse(request.POST)
        q_filter, wallet_obj = wallet_choice(wallet_type, wallet_id)

        if (
            "Outcome" in request.POST or request.POST["Income"] != "none"
        ) and request.POST["amount"]:

            amount = float(request.POST["amount"])
            expense = "Outcome" if "Outcome" in request.POST else "Income"

            try:
                wallet_obj = change_wallet_balance(expense, wallet_obj, amount)

                acc_data = {
                    "IO": expense[0],
                    "IO_type": request.POST[expense],
                    "amount": amount,
                }

                if wallet_type == "card":
                    accountancy.create(card=wallet_obj, **acc_data)
                elif wallet_type == "cash":
                    accountancy.create(cash=wallet_obj, **acc_data)
                elif wallet_type == "crypto":
                    accountancy.create(cryptocurrency=wallet_obj, **acc_data)
                wallet_obj.save()

            except ValidationError as ve:
                error = ve

        # Move selected wallet at the top
        for wallet_index, wallet in enumerate(wallets_set):
            if wallet[0] == request.POST["wallet_choice"]:
                wallets_set.insert(0, wallets_set.pop(wallet_index))
                wallets_set[0][1] = wallet_obj
                break

        current_balance = wallets_set[0][1].balance

        # Get monthly incomes and outcomes
        income = monthly_financial_turnover(q_filter, "I")
        outcome = monthly_financial_turnover(q_filter, "O")

    context = {
        "wallets": wallets_set,
        "current_balance": current_balance,
        "Income": income,
        "Outcome": outcome,
        "error": error,
    }

    return render(request, "manager/index.html", context=context)


class MonthlyAccountancyList(LoginRequiredMixin, generic.ListView):
    model = Accountancy
    template_name = "manager/monthly_accountancy_list.html"
    paginate_by = 10

    def get_queryset(self):
        user_id = self.request.user.id

        # Get month expenses
        self.queryset = (
            self.model.objects.filter(
                Q(card__user=user_id)
                | Q(cash__user=user_id)
                | Q(cryptocurrency__user=user_id)
            )
            .annotate(
                month=TruncMonth("datetime"),
            )
            .values("month")
            .annotate(
                amount_sum=Round(Sum("amount"), 8),
            )
            .values(
                "card_id",
                "card__bank_name",
                "card__type",
                "card__currency__sign",
                "cash_id",
                "cash__currency__name",
                "cryptocurrency_id",
                "cryptocurrency__name",
                "IO",
                "amount_sum",
                "month",
            )
            .order_by("-month")
        )  # type: ignore

        return self.queryset


class MonthlyAccountancy(LoginRequiredMixin, generic.ListView):
    model = Accountancy
    template_name = "manager/monthly_accountancy.html"
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MonthlyAccountancy, self).get_context_data(**kwargs)
        IO_type = self.request.GET.get("IO_type", "")
        context["search_form"] = AccountancySearchForm(initial={"IO_type": IO_type})

        return context

    def get_queryset(self):
        details = self.request.resolver_match.kwargs
        q_filter, wallet_obj = wallet_choice(details["wallet"], details["wallet_id"])

        # Get accountancy per specific month & year
        self.queryset = (
            self.model.objects.filter(
                q_filter
                & Q(datetime__month=details["month"])
                & Q(datetime__year=details["year"])
            )
            .order_by("-datetime")
            .values("id", "IO", "IO_type", "amount", "datetime")
        )

        form = AccountancySearchForm(self.request.GET)
        if form.is_valid():
            return self.queryset.filter(IO_type__icontains=form.cleaned_data["IO_type"])

        return self.queryset


class AccountancyUpdate(LoginRequiredMixin, generic.UpdateView):
    model = Accountancy
    form_class = AccountancyForm
    template_name = "manager/accountancy_form.html"
    success_url = reverse_lazy("manager:monthly-accountancy-list")


class AccountancyDelete(LoginRequiredMixin, generic.DeleteView):
    model = Accountancy
    success_url = reverse_lazy("manager:monthly-accountancy-list")
