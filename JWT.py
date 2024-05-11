import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify

SECRET_KEY = 'cpsc-449-jwt-secret-key' # Secret Key for JWT

# Generate a token
def generate_token(user_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=1),  # Modify the number to change the expiration date of the token
        'iat': datetime.now(timezone.utc), # The time the token was generated
        'sub': user_id # Subject of the token
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256') # Encoded using Secret Key + Algorithm HS256

# Verify the token
def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256']) # Decode the token using the Secret Key and algorithm
        return payload['sub']  # Return the user_id (subject) of the token
    except jwt.ExpiredSignatureError:
        return None  # the token has expired
    except jwt.InvalidTokenError:
        return None  # the token is invalid

# Decorator for token verification
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization') # Get the token from the Authorization header (this is put in manually by the user/client)

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403 # Token not found in the Authorization header

        try:
            token = token.split(" ")[1] # Split the token by the space and get the second part (which is the token itself)
            user_id = verify_token(token) # Verify the token
            if not user_id: # Token is invalid or expired
                return jsonify({'message': 'Token is invalid or expired!'}), 401
        except IndexError:
            return jsonify({'message': 'Token format is invalid!'}), 400

        return f(*args, **kwargs)
    return decorated_function