from django import forms
from django.core.exceptions import ValidationError

from manager.models import Accountancy
from manager.wallet_operations import wallet_choice, wallet_data_parse, change_wallet_balance


class AccountancyForm(forms.ModelForm):

    class Meta:
        model = Accountancy
        fields = ()

    def clean(self):
        amount = float(self.data["amount"])
        if amount < 0:
            raise ValidationError("Amount can't be negative.")

        wallet_type, previous_amount = wallet_data_parse(self.data)
        _, self.wallet_obj = wallet_choice(
            wallet_type,
            self.instance.card_id or self.instance.cash_id or self.instance.cryptocurrency_id
        )
        amount = amount - float(previous_amount) if previous_amount else 0

        self.wallet_obj = change_wallet_balance(
            self.instance.IO, self.wallet_obj, amount
        )

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
