from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
from utils import response

from digital_twin_migration.models import db


def handle_exception(e):
    if isinstance(e, HTTPException):
        return response(e.code, False, e.description)

    if isinstance(e, SQLAlchemyError):
        db.session.rollback()
        return response(500, False, str(e))

    return (
        response(500, False, str(e))
        if current_app.debug
        else response(500, False, "Internal server error")
    )
