from permissions import rolePermission, isLoggedIn
from rest_framework.response import Response
from rest_framework import status
from functools import wraps
from django.utils.decorators import available_attrs

# This decorator is used to detect version of api and choose to apply authentication method
def compatible_jwt(*roleList):
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(self, request, *args, **kwargs):
            if request.version == '2.0':
                roleListStr = ','.join(roleList)
                if not rolePermission(request, roleList):
                    return Response({'error': 'roles needed: ' + roleListStr}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if not isLoggedIn(request):
                    return Response({'error': 'authentication failed'}, status=status.HTTP_400_BAD_REQUEST)
            return func(self, request, *args, **kwargs)
        return inner
    return decorator