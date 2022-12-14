from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import Card, Cash, Cryptocurrency, Accountancy


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
            "phone_number"
        )

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserAccountForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number"
        )

    def save(self, commit=True):
        user = super(UserAccountForm, self).save(commit=False)
        if commit:
            user.save()
        return user


class AccountancyForm(forms.ModelForm):

    class Meta:
        model = Accountancy
        fields = ()

    def clean(self):
        amount = float(self.data["amount"])
        if amount < 0:
            raise ValidationError("Amount can't be negative.")

        wallet_data = self.data["wallet_choice"].split(" - ")
        amount = amount - float(wallet_data[1]) if wallet_data[1] else 0

        if wallet_data[0] == "card":
            self.wallet_obj = Card.objects.get(id=self.instance.card_id)
        elif wallet_data[0] == "cash":
            self.wallet_obj = Cash.objects.get(id=self.instance.cash_id)
        elif wallet_data[0] == "crypto":
            self.wallet_obj = Cryptocurrency.objects.get(
                id=self.instance.cryptocurrency_id
            )

        if self.instance.IO == "O" and self.wallet_obj.balance < amount:
            raise ValidationError(
                "There's too small amount of money on the balance"
            )
        elif self.instance.IO == "O":
            self.wallet_obj.balance = float(self.wallet_obj.balance) - amount
        elif self.instance.IO == "I":
            self.wallet_obj.balance = float(self.wallet_obj.balance) + amount

        return super().clean()

    def save(self, commit=True):
        accountancy = super(AccountancyForm, self).save(commit=False)
        self.clean()
        if commit:
            accountancy.amount = float(self.data["amount"])
            accountancy.save()
            self.wallet_obj.save()
        return super().save(commit)


class AccountancySearchForm(forms.Form):
    IO_type = forms.CharField(
        max_length=50,
        required=False,
        label="",
        widget=forms.TextInput(attrs={
            "placeholder": "Search by type ...",
            "class": "small_plate _comforta_bold text_shadow"
        })
    )
