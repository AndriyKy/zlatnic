from django.contrib import admin
from django.contrib.admin import ModelAdmin
from manager.models import (
    Currency,
    Card,
    Cash,
    Cryptocurrency,
    Accountancy,
)

admin.site.register(Currency, ModelAdmin)


@admin.register(Card)
class CardAdmin(ModelAdmin):
    list_display = (
        "user",
        "bank_name",
        "type",
        "balance",
        "currency",
    )


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
