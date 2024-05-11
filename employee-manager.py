from flask import Flask, jsonify, request  # Flask app methods
from pymongo import MongoClient  # MongoDB Atlas connection
from pymongo.server_api import ServerApi  # MongoDB Atlas connection
from bson.objectid import ObjectId  # Creating/processing ObjectIDs
import redis  # Redis cache
import json  # Stringify JSONs for Redis cache

# Replace this with your URI from MongoDB Atlas!
uri = "insert_URI_here"
app = Flask(__name__)

# Connect to MongoDB
client = MongoClient(uri, server_api=ServerApi('1'))
# Use company-manager database
db = client['company-manager']
# Use employees collection
employees_collection = db['employees']
# Connect to Redis cache
redis_cache = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Test your connection to the employee manager service
@app.route('/v1/employee-manager/test', methods=['GET'])
def check_dbs():
	print(client.list_database_names())
	return jsonify({'message': 'hi'}), 200



# create new employee
@app.route('/v1/employee-manager/employees', methods=['POST'])
def create_employee():
	employee = request.json
	employee['_id'] = ObjectId()
	employees_collection.insert_one(employee)
	return jsonify({'message': 'employee created successfully'}), 201

# get list of all employees
@app.route('/v1/employee-manager/employees', methods=['GET'])
def get_employees():
	# attempt to load all employee IDs from Redis cache
	employee_ids = redis_cache.smembers("employee_ids")

	# Cache hit, load each employee's details from hash map
	if employee_ids:
		# list of employee documents to return
		employees = []
		# for each employee in the Redis cache, parse their data
		for emp_id in employee_ids:
			# get employee's data
			emp_data = redis_cache.hgetall(f'employee:{emp_id}')
			# parse lists (saved as strings in Redis, but should be JSON when returned)
			emp_data['skills'] = json.loads(emp_data['skills'])
			# save the document in list of employees
			employees.append(emp_data)
		
		print("from the cache!")
		return jsonify(employees), 200  # return all employees (from cache)

	# Cache miss, query the MongoDB database
	documents = list(employees_collection.find())
	# list of employee documents to return
	employees = []
	for document in documents:
		# make each document JSON serializable (stringify objects/lists)
		document['_id'] = str(document['_id'])
		document['skills'] = json.dumps(document['skills'])
		# save each employee ID
		emp_id = document['employee_ID']
		# cache each employee in a hash map and store their IDs in a set
		# first, stringify lists for redis cache
		redis_cache.hset(f"employee:{emp_id}", mapping=document)
		redis_cache.sadd("employee_ids", emp_id)

		# then, revert the document's lists to JSON (to return to user)
		# note: Redis needs to save lists as strings, but user should get lists as JSON
		document['skills'] = json.loads(document['skills'])

		# finally, save each employee document
		employees.append(document)
		
	# return all employees
	print("from the database!")
	return jsonify(employees), 200  # return all employees (from MongoDB Atlas)

# get an employee by their employee ID
@app.route('/v1/employee-manager/employees/<int:emp_id>', methods=['GET'])
def get_employee(emp_id):
	employee = employees_collection.find_one({'employee_ID': emp_id})
	if employee:
		employee['_id'] = str(employee['_id'])
		return jsonify(employee), 200
	else:
		return jsonify({'message': 'employee not found'}), 404

# TODO: get employees with a certain skill (GET)

# update an employee using their employee_ID
@app.route('/v1/employee-manager/employees/<int:emp_id>', methods=['PUT'])
def update_employee(emp_id):
	updated_data = request.json
	result = employees_collection.update_one({'employee_ID': emp_id}, {'$set': updated_data})
	if result.matched_count:
		return jsonify({'message': 'employee updated successfully'}), 200
	else:
		return jsonify({'message': 'employee not found'}), 404

# delete an employee using their employee_ID
@app.route('/v1/employee-manager/employees/<int:emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
	result = employees_collection.delete_one({'employee_ID': emp_id})
	if result.deleted_count:
		return jsonify({'message': 'employee deleted successfully'}), 200
	else:
		return jsonify({'message': 'employee not found'}), 404

if __name__ == '__main__':
	app.run(debug=True, port=31002)