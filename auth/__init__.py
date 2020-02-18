import hashlib
import auth

from flask import request, abort, request, g
from functools import wraps


def hash_password(password, salt):
    return hashlib.sha512(str.encode(password + salt)).hexdigest()


def login_required(perms):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            if 'auth' not in data:
                abort(401, "Missing authorization")
            g.auth = auth.jwt.check_jwt(data['auth'])
            return func(*args, **kwargs)
        return wrapper
    return decorator
