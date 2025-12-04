from typing import cast

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from sandwich.core.util.http import UserHttpRequest
from sandwich.users.models import User


class UserRequestFactory(RequestFactory):
    """A RequestFactory that creates requests with a user.

    Usage:
        def test_my_view(user: User, urf: UserRequestFactory):
            request = urf.get('/some-url/')  # Anonymous user by default
            response = my_view(request)
            # or
            request = urf(user).get('/some-url/')  # Authenticated as 'user'
            response = my_view(request)
    """

    def __init__(self, *args, **kwargs):
        self._init_args = args
        self._init_kwargs = kwargs
        self.user: User | AnonymousUser = kwargs.pop("user", AnonymousUser())
        super().__init__(*args, **kwargs)

    def __call__(self, user: User):
        """Return a new UserRequestFactory instance with the given user."""
        return UserRequestFactory(*self._init_args, user=user, **self._init_kwargs)

    def request(self, **request) -> UserHttpRequest:
        req = super().request(**request)
        req.user = self.user
        return cast("UserHttpRequest", req)
