from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, make_response
import jwt
from flask import current_app
import requests
from repositories import UserRepository

AUTH_SERVICE_API = 'http://localhost:5000'
RESOURCE_ID = 1


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        if not token:
            return make_response(jsonify({'message': 'a valid token is missing'}), 401)
        try:
            # Verify token using api /verify-token
            payload = requests.get(AUTH_SERVICE_API + '/verify-token?resource=' + str(RESOURCE_ID),
                                   headers={'Authorization': 'Bearer ' + token}).json()

            if not payload.status:
                return make_response(jsonify({'message': 'token is invalid'}), 401)

            kwargs.update(user_id=payload.data.user_id)

        except:
            return make_response(jsonify({'message': 'token is invalid'}), 401)

        return f(*args, **kwargs)
    return decorator


def admin_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'Authentication' in request.headers:
            token = request.headers['Authentication']

        if not token:
            return make_response(jsonify({'message': 'a valid token is missing'}), 401)
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            admin = UserRepository.get_by_id(payload['user_id'])

            if admin.type != 'seller':
                return make_response(jsonify({'message': 'you are not admin'}), 401)

            kwargs.update(user_id=payload['user_id'])
        except:
            return make_response(jsonify({'message': 'token is invalid'}), 401)

        return f(*args, **kwargs)
    return decorator

