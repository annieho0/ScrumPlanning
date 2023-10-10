from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import FormView, View
from .forms import RegisterFrom, CreateHourGraphForm
from django.urls import reverse_lazy, reverse
from .models import CustomizedUser
from django.contrib.auth.mixins import UserPassesTestMixin


class RegisterView(FormView):
    """
    Class-based view to handle user registration.

    This view handles both GET and POST requests for user registration.
    Upon a valid POST submission, it saves the user to the database.
    If the form submission is invalid, it returns a JSON response with errors.

    Attributes:
        template_name (str): Specifies the path to the template for rendering the registration form.
        form_class (Form): The form class used for user registration.
        success_url (str): URL to redirect to upon successful form submission.
    """

    template_name = 'register/register.html'  # Path to the registration form template
    form_class = RegisterFrom  # Custom registration form class
    success_url = reverse_lazy('register_success')  # URL to redirect to after successful registration

    def form_valid(self, form):
        """
        Handle valid form submission.

        If the form is valid, this method saves the user data to the database
        and then redirects the user to the success URL (in this case, the login page).

        Args:
            form (Form): The submitted form.

        Returns:
            HttpResponse: A redirection to the success URL.
        """
        user = form.save(commit=False)  # Don't save to the database yet
        user.is_active = False  # Deactivate account until email confirmation
        user.save()  # Now save user to the database

        # Send confirmation email
        mail_subject = 'Activate your account'
        activation_link = self.request.build_absolute_uri(
            reverse('activate_account', kwargs={
                'activation_token': user.activation_token
            }))
        message = f'Click the link below to activate your account:\n{activation_link}'
        from_email = 'your_email@example.com'
        send_mail(mail_subject, message, from_email, [user.email])

        # Not redirecting as frontend ajax will do the redirecting
        return JsonResponse({"success": "Registered successfully!"})

    def form_invalid(self, form):
        """
        Handle invalid form submission.

        If the form is invalid, this method returns a JSON response containing
        the form errors and a 400 status code.

        Args:
            form (Form): The submitted form with errors.

        Returns:
            JsonResponse: A JSON response with form errors and a 400 status code.
        """
        # Return a JSON response with the form errors
        return JsonResponse({"error": form.errors}, status=400)


def activate_account(request, activation_token):
    """
    Activate the user account based on the activation token.

    This view function is called when the user clicks on the activation link in the email.
    It activates the user's account and sets the email confirmation flag.

    Args:
        request (HttpRequest): The HTTP request object.
        activation_token (str): The activation token extracted from the URL.

    Returns:
        HttpResponse: A redirection to the login page or another success page.
    """
    try:
        user = CustomizedUser.objects.get(activation_token=activation_token)
    except CustomizedUser.DoesNotExist:
        user = None

    if user and not user.is_email_confirmed:
        user.is_active = True
        user.is_email_confirmed = True
        user.save()
        return render(request, 'register/account_activation_valid.html')
    else:
        return render(request, 'register/account_activation_invalid.html')


class RegisterSuccessView(View):
    """
    Class-based view to handle successful user registration.

    This view handles GET requests for successful user registration.
    It simply renders the registration success template.

    Attributes:
        template_name (str): Specifies the path to the template for rendering the registration success page.
    """

    template_name = 'register/register_success.html'  # Path to the registration success template

    def get(self, request):
        """
        Handle GET request.

        Renders the registration success template.

        Args:
            request (HttpRequest): The GET request.

        Returns:
            HttpResponse: A response containing the rendered registration success template.
        """
        return render(request, self.template_name)


class AdminGraphView(UserPassesTestMixin, View):
    """
    Class-based view to handle rendering the admin graph page.

    This view handles GET requests for rendering the admin graph page.
    It simply renders the admin graph template.

    Attributes:
        template_name (str): Specifies the path to the template for rendering the admin graph page.
    """
    template_name = 'admin/hour_graph.html'

    def test_func(self):
        """
        Define the test function used by UserPassesTestMixin.

        This method should return True if the user passes the test (i.e., if the user is a superuser)
        and False otherwise.

        Returns:
            bool: True if user is a superuser, False otherwise.
        """
        return self.request.user.is_superuser

    def get(self, request):
        """
        Handle GET request.

        Renders the admin graph template.

        Args:
            request (HttpRequest): The GET request.

        Returns:
            HttpResponse: A response containing the rendered admin graph template.
        """
        context = {
            'has_permission': self.request.user.is_superuser,
            'is_nav_sidebar_enabled': True,
            'is_popup': False,
            'title': 'Admin Graph',
        }
        return render(request, self.template_name, context)


class LoginView(LoginView):
    """
    Class-based view to handle user login.

    This view handles both GET and POST requests for user login.
    Upon a valid POST submission, it logs the user in.
    If the user is a superuser, it redirects to the admin panel.
    Otherwise, it redirects to a specified page.

    Attributes:
        template_name (str): Specifies the path to the template for rendering the login form.
    """

    template_name = 'registration/login.html'  # Your login template

    def form_valid(self, form):
        """
        Handle valid form submission.

        If the form is valid, this method logs the user in.
        If the user is a superuser, it redirects to the admin panel.
        Otherwise, it redirects to a specified page.

        Args:
            form (Form): The submitted form.

        Returns:
            HttpResponse: A redirection to the admin panel or a specified page.
        """
        login(self.request, form.get_user())

        # Check if the user is a superuser. Redirect to the admin panel if they are.
        if self.request.user.is_superuser:
            return redirect(reverse_lazy('admin:index'))
        # Otherwise, redirect to your desired page
        else:
            return redirect(reverse_lazy('home'))
        
class CreateHourGraphView(View):
    template_name = 'admin/hour_graph.html'

    def create_graph(self, request):
        if request.method == "POST":
            form = CreateHourGraphForm(request.POST)
            if form.is_valid():
                person = form.cleaned_data['person']
                date = form.cleaned_data['data']

        else:
            form = CreateHourGraphForm()

        return render(request, self.template_name, {'create_graph_form': form})
