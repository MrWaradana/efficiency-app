from typing import TypeVar, Union

from flask import jsonify, make_response
from flask.wrappers import Response

T = TypeVar("T")

# def response(data, status_code=200):
#     """ Response """
#     return make_response(jsonify(data), status_code)


def response(
    status_code: Union[str, int],
    status: bool,
    message: str = "",
    data: Union[str, dict[T, T], None] = None,
) -> Response:
    if data is None:
        return make_response(
            jsonify(
                {
                    "status": status,
                    "message": message,
                }
            ),
            status_code,
        )
    else:
        return make_response(
            jsonify({"status": status, "message": message, "data": data}), status_code
        )
