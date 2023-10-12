from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve, Resolver404


class LoginRequiredMiddleware:
    """
    Middleware to enforce login requirement.

    This middleware checks if the user is authenticated for each incoming request.
    If the user is not authenticated and the requested path is not the login URL,
    it redirects the user to the login page.

    Attributes:
        get_response (function): The next middleware or view function in the chain.
    """

    def __init__(self, get_response):
        """
        Initialize the middleware.

        Args:
            get_response (function): The next middleware or view function in the chain.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process the incoming request.

        If the user is not authenticated and the requested path is not the login URL,
        redirect the user to the login page.

        Args:
            request (HttpRequest): The incoming request.

        Returns:
            HttpResponse: The response generated by the next middleware or view function.
        """
        # List of URL names that you want to exclude from authentication
        auth_exempt_urls = [
            'login',
            'logout',
            'password_reset',
            'password_reset_done',
            'password_reset_confirm',
            'password_reset_complete',
            'register',
            'register_success',
            'activate_account',
            # ... any other URL names related to authentication
        ]

        try:
            # Resolve the current path to its corresponding view function and pattern name
            normalised_path_info = request.path_info + '/' if request.path_info[-1] != '/' else request.path_info
            resolved_path = resolve(normalised_path_info)
            path_is_exempt = resolved_path.url_name in auth_exempt_urls
        except Resolver404:
            path_is_exempt = False

        # Check if the user is authenticated or if the path is exempt
        if request.user.is_authenticated or path_is_exempt:
            return self.get_response(request)
        else:
            return redirect(settings.LOGIN_URL)