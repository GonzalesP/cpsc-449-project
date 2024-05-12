from flask import Flask, jsonify, request
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from JWT import generate_token

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'cpsc-449-jwt-secret-key'
jwt = JWTManager(app)

bcrypt = Bcrypt(app)

uri = "mongodb+srv://tchaalan23:Tutuch2003-@cluster0.uo27hwg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['company-manager']
accounts_collection = db['accounts']

@app.route('/v1/account-manager/signup', methods=['POST'])
def signup():
    account = request.json
    password = account['password']
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    account['password'] = pw_hash
    result = accounts_collection.insert_one(account)
    if result.acknowledged:
        print(f"Account created successfully with id {result.inserted_id}")
        print("Hello")
        return jsonify({'message': 'Account created successfully'}), 201
    else:
        print("Failed to create account")
        return jsonify({'message': 'Failed to create account'}), 500


@app.route('/v1/account-manager/login', methods=['POST'])
def login():
    account_details = request.json
    username = account_details['username']
    password = account_details['password']
    account = accounts_collection.find_one({'username': username})
    if account and bcrypt.check_password_hash(account['password'], password):
        # Password is correct, generate and return a JWT
        token = create_access_token(identity=username)
        return jsonify({'token': token}), 200
    else:
        # Username or password is incorrect
        return jsonify({'message': 'Invalid username or password'}), 401


@app.route('/v1/account-manager/users/<username>', methods=['GET'])
@jwt_required()
def get_user(username):
    user = accounts_collection.find_one({'username': username})
    if user:
        user['_id'] = str(user['_id'])
        del user['password']  # Never return the password
        return jsonify(user), 200
    else:
        return jsonify({'message': 'User not found'}), 404


@app.route('/v1/account-manager/users/<username>', methods=['PUT'])
def update_user(username):
    updated_data = request.json
    result = accounts_collection.update_one({'username': username}, {'$set': updated_data})
    if result.matched_count:
        return jsonify({'message': 'User updated successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, port=31001)  # use a different port for each service
