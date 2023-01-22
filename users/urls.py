from django.urls import path

from users.views import register_request, UserUpdateView

urlpatterns = [
    path("register/", register_request, name="register"),
    path("account/<int:pk>/", UserUpdateView.as_view(), name="account"),
]

app_name = "users"
