from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from .models import User, Currancy, Card, Cash, Cryptocurrency, Accountancy


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (("Additional info", {"fields": ("phone_number",)}),)
    )  # type: ignore
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            (
                "Additional info",
                {
                    "fields": (
                        "first_name",
                        "last_name",
                        "phone_number",
                    ),
                },
            ),
        )
    )
    list_display = UserAdmin.list_display + ("phone_number",)  # type: ignore


admin.site.register(Currancy)


@admin.register(Card)
class CardAdmin(ModelAdmin):
    list_display = ("users", "currancy", "bank_name", "type", "balance",)


@admin.register(Cash)
class CashAdmin(ModelAdmin):
    list_display = ("users", "currancy", "balance",)


@admin.register(Cryptocurrency)
class CryptocurrencyAdmin(ModelAdmin):
    list_display = ("users", "name", "balance",)


@admin.register(Accountancy)
class AccountancyAdmin(ModelAdmin):
    list_display = (
        "users",
        "wallet_id",
        "wallet_type",
        "io",
        "io_type",
        "amount",
        "datetime",
    )
    search_fields = ("io_type",)
    list_filter = ("wallet_type", "io_type")
