from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from users.forms import NewUserForm, UserAccountForm


def register_request(request):
    """User registration function-based view"""

    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("manager:wallets")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def user_account(request):
    """Function-based view for user data changing"""

    if request.method == "POST":
        form = UserAccountForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("manager:index")
        messages.error(request, "Invalid information.")
    form = UserAccountForm()
    return render(request, "users/account.html", {"form": form})
