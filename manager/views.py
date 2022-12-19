from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth, Round
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from datetime import date

from manager.forms import (
    AccountancyForm,
    AccountancySearchForm,
    NewUserForm,
    UserAccountForm
)

from manager.models import (
    User,
    Currency,
    Card,
    Cash,
    Cryptocurrency,
    Accountancy
)


def wallet_choice(wallet: str, wallet_id: int):
    if wallet == "card":
        q_filter = Q(card=wallet_id)
        wallet_obj = Card.objects.get(id=wallet_id)
    elif wallet == "cash":
        q_filter = Q(cash=wallet_id)
        wallet_obj = Cash.objects.get(id=wallet_id)
    elif wallet == "crypto":
        q_filter = Q(cryptocurrency=wallet_id)
        wallet_obj = Cryptocurrency.objects.get(id=wallet_id)

    return q_filter, wallet_obj


def wallet_objects(request):
    user = User.objects.get(id=request.user.id)
    currency = Currency.objects.all()
    cards = user.cards.all()
    cash_types = user.cash.all()
    crypto = user.cryptocurrencies.all()

    return currency, cards, cash_types, crypto


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("manager:wallets")
        messages.error(
            request, "Unsuccessful registration. Invalid information."
        )
    form = NewUserForm()
    return render(
        request, "registration/register.html", {"form": form}
    )


@login_required
def user_account(request):
    if request.method == "POST":
        form = UserAccountForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("manager:index")
        messages.error(
            request, "Invalid information."
        )
    form = UserAccountForm()
    return render(
        request, "manager/account.html", {"form": form}
    )


@login_required
def wallets(request):
    _, cards, cash_types, crypto = wallet_objects(request)

    context = {
        "cards_list": cards,
        "cash_list": cash_types,
        "crypto_list": crypto,
    }
    return render(request, "manager/wallets.html", context)


class CardCreateView(LoginRequiredMixin, generic.CreateView):
    model = Card
    fields = ("user", "bank_name", "type", "balance", "currency",)
    success_url = reverse_lazy("manager:wallets")


class CardUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Card
    fields = ("user", "bank_name", "type", "currency",)
    success_url = reverse_lazy("manager:wallets")


class CardDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Card
    success_url = reverse_lazy("manager:wallets")


class CashCreateView(LoginRequiredMixin, generic.CreateView):
    model = Cash
    fields = ("user", "currency",)
    success_url = reverse_lazy("manager:wallets")


class CashUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Cash
    fields = ("user", "currency",)
    success_url = reverse_lazy("manager:wallets")


class CashDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Cash
    success_url = reverse_lazy("manager:wallets")


class CryptoCreateView(LoginRequiredMixin, generic.CreateView):
    model = Cryptocurrency
    fields = ("user", "name",)
    success_url = reverse_lazy("manager:wallets")


class CryptoUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Cryptocurrency
    fields = ("user", "name",)
    success_url = reverse_lazy("manager:wallets")


class CryptoDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Cryptocurrency
    success_url = reverse_lazy("manager:wallets")


@login_required
def index(request):
    """View function for the base page of the site."""

    wallets_set = []
    error = False
    current_balance = income = outcome = 0
    accountancy = Accountancy.objects

    _, cards, cash_types, crypto = wallet_objects(request)

    if cards:
        for card in cards:
            wallets_set.append([f"card - {card.id}", card])

    if cash_types:
        for cash in cash_types:
            wallets_set.append([f"cash - {cash.id}", cash])

    if crypto:
        for crypto in crypto:
            wallets_set.append([f"crypto - {crypto.id}", crypto])

    if "wallet_choice" in request.POST and request.POST["wallet_choice"]:
        wallet_data = request.POST["wallet_choice"].split(" - ")
        q_filter, wallet_obj = wallet_choice(wallet_data[0], wallet_data[1])

        if ("Outcome" in request.POST or request.POST["Income"] != "none")\
                and request.POST["amount"]:

            amount = float(request.POST["amount"])
            expense = "Outcome" if "Outcome" in request.POST else "Income"

            try:
                if expense == "Outcome" and wallet_obj.balance < amount:
                    raise ValidationError(
                        "There's too small amount of money on the balance"
                    )
                elif expense == "Outcome":
                    wallet_obj.balance = float(wallet_obj.balance) - amount
                elif expense == "Income":
                    wallet_obj.balance = float(wallet_obj.balance) + amount

                acc_data = {
                    "IO": expense[0],
                    "IO_type": request.POST[expense],
                    "amount": amount,
                }

                if wallet_data[0] == "card":
                    accountancy.create(card=wallet_obj, **acc_data)
                elif wallet_data[0] == "cash":
                    accountancy.create(cash=wallet_obj, **acc_data)
                elif wallet_data[0] == "crypto":
                    accountancy.create(
                        cryptocurrency=wallet_obj, **acc_data
                    )
                wallet_obj.save()
            except ValidationError:
                error = ValidationError(
                    "There's too small amount of money on the balance"
                )

        # Move selected wallet at the top
        for wallet_index, wallet in enumerate(wallets_set):
            if wallet[0] == request.POST["wallet_choice"]:
                wallets_set.insert(0, wallets_set.pop(wallet_index))
                wallets_set[0][1] = wallet_obj
                break
        current_balance = wallets_set[0][1].balance

        # Get monthly incomes and outcomes
        income = accountancy.filter(
            q_filter & Q(IO="I") & Q(datetime__month=date.today().month)
        ).aggregate(Sum("amount"))["amount__sum"]
        income = round(income, 8) if income else 0

        outcome = accountancy.filter(
            q_filter & Q(IO="O") & Q(datetime__month=date.today().month)
        ).aggregate(Sum("amount"))["amount__sum"]
        outcome = round(outcome, 8) if outcome else 0

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
        self.queryset = self.model.objects.filter(
            Q(card__user=user_id) |
            Q(cash__user=user_id) |
            Q(cryptocurrency__user=user_id)
        ).annotate(
            month=TruncMonth("datetime"),
        ).values("month").annotate(
            amount_sum=Round(Sum("amount"), 8),
        ).values(
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
            "month"
        ).order_by("-month")  # type: ignore

        return self.queryset


@login_required
def monthly_accountancy(request, wallet, wallet_id, month, year):
    q_filter, wallet_name = wallet_choice(wallet, wallet_id)

    queryset = Accountancy.objects.filter(
        q_filter &
        Q(datetime__month=month) &
        Q(datetime__year=year)
    ).order_by("-datetime").values(
        "id", "IO", "IO_type", "amount", "datetime"
    )

    # Search form
    IO_type = request.GET.get("IO_type", "")
    search_form = AccountancySearchForm(
        initial={
            "IO_type": IO_type
        }
    )

    form = AccountancySearchForm(request.GET)
    if form.is_valid():
        queryset = queryset.filter(
            IO_type__icontains=form.cleaned_data["IO_type"]
        )

    # Custom pagination
    paginate_by = 10
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, paginate_by)

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    if queryset.count() < paginate_by:
        is_paginated = False
    else:
        is_paginated = True

    context = {
        "monthly_accountancy": page_obj,
        "search_form": search_form,
        "paginator": paginator,
        "page_obj": page_obj,
        "wallet": wallet,
        "wallet_name": wallet_name,
        "is_paginated": is_paginated,
    }
    return render(request, "manager/monthly_accountancy.html", context=context)


class AccountancyUpdate(LoginRequiredMixin, generic.UpdateView):
    model = Accountancy
    form_class = AccountancyForm
    template_name = "manager/accountancy_form.html"
    success_url = reverse_lazy("manager:monthly-accountancy-list")


class AccountancyDelete(LoginRequiredMixin, generic.DeleteView):
    model = Accountancy
    success_url = reverse_lazy("manager:monthly-accountancy-list")
