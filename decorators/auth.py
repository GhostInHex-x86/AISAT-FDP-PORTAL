from functools import wraps

from flask_login import current_user
from flask import abort


def admin_required(view):

    @wraps(view)
    def wrapped_view(*args, **kwargs):

        if current_user.role != "admin":
            abort(403)

        return view(*args, **kwargs)

    return wrapped_view


def faculty_required(view):

    @wraps(view)
    def wrapped_view(*args, **kwargs):

        if current_user.role != "faculty":
            abort(403)

        return view(*args, **kwargs)

    return wrapped_view
