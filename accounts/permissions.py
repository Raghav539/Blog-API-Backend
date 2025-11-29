from rest_framework.response import Response


def role_required(allowed_roles):
    """
    Decorator to restrict API access based on user role.
    """

    def decorator(view_func):
        def wrapper(self, request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                return Response({"error": "Authentication required"}, status=401)

            if user.role not in allowed_roles:
                return Response({"error": "Permission denied"}, status=403)

            return view_func(self, request, *args, **kwargs)

        return wrapper

    return decorator
