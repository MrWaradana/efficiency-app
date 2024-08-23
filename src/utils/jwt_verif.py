from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, make_response
import jwt
from flask import current_app
import requests

from utils import response
# from repositories import UserRepository

import config


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        if not token:
            return response(401, False, 'a valid token is missing')
        try:
            # Verify token using api /verify-token with resource(not yet)
            # payload = requests.get(AUTH_SERVICE_API + '/verify-token?resource=' + str(RESOURCE_ID),
            #                        headers={'Authorization': 'Bearer ' + token}).json()
            payload = requests.get(config.AUTH_SERVICE_API + '/verify-token',
                                   headers={'Authorization': 'Bearer ' + token})

            if not payload.ok:
                return response(401, False, 'token is invalid')
            
            user_id = payload.json()['data']['user_id']
            kwargs.update(user_id=user_id)

        except Exception as e:
            return response(500, False, str(e))

        return f(*args, **kwargs)
    return decorator


# def admin_required(f):


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
