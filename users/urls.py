from django.urls import path

from users.views import (
    register_request,
    user_account,
)


urlpatterns = [
    path("register/", register_request, name="register"),
    path("account/", user_account, name="account"),
]

app_name = "users"
