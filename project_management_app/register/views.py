from django.http import JsonResponse
from django.views.generic import FormView
from .forms import RegisterFrom
from django.urls import reverse_lazy


class RegisterView(FormView):
    """
    Class-based view to handle user registration.

    This view handles both GET and POST requests for user registration.
    Upon a valid POST submission, it saves the user to the database.
    If the form submission is invalid, it returns a JSON response with errors.

    Attributes:
    - template_name (str): Specifies the path to the template for rendering the registration form.
    - form_class (Form): The form class used for user registration.
    - success_url (str): URL to redirect to upon successful form submission.
    """

    template_name = 'register/register.html'  # Path to the registration form template
    form_class = RegisterFrom  # Custom registration form class
    success_url = reverse_lazy('login')  # URL to redirect to after successful registration

    def form_valid(self, form):
        """
        Handle valid form submission.

        If the form is valid, this method saves the user data to the database
        and then redirects the user to the success URL (in this case, the login page).

        Args:
        - form (Form): The submitted form.

        Returns:
        - HttpResponse: A redirection to the success URL.
        """
        form.save()  # Save the user data to the database
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Handle invalid form submission.

        If the form is invalid, this method returns a JSON response containing
        the form errors and a 400 status code.

        Args:
        - form (Form): The submitted form with errors.

        Returns:
        - JsonResponse: A JSON response with form errors and a 400 status code.
        """
        # Return a JSON response with the form errors
        return JsonResponse({"error": form.errors}, status=400)

