from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from manager.models import (
    Currency,
    Card,
    Cash,
    Cryptocurrency,
    Accountancy,
)


@admin.register(get_user_model())
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


admin.site.register(Currency, ModelAdmin)


@admin.register(Card)
class CardAdmin(ModelAdmin):
    list_display = ("user", "bank_name", "type", "balance", "currency",)


admin.site.register(Cash, ModelAdmin)

admin.site.register(Cryptocurrency, ModelAdmin)


@admin.register(Accountancy)
class AccountancyAdmin(ModelAdmin):
    list_display = (
        "card",
        "cash",
        "cryptocurrency",
        "IO",
        "IO_type",
        "amount",
        "datetime",
    )
    search_fields = ("IO_type",)
    list_filter = ("IO_type",)
