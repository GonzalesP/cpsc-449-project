from flask import Flask, jsonify, request  # Flask app methods
from pymongo import MongoClient  # MongoDB Atlas connection
from pymongo.server_api import ServerApi  # MongoDB Atlas connection
from bson.objectid import ObjectId  # Creating/processing ObjectIDs
import redis  # Redis cache
import json  # Stringify JSONs for Redis cache
from JWT import token_required # Import JWT Decorator from JWT.py

# Replace this with your URI from MongoDB Atlas!
uri = "mongodb+srv://tchaalan23:Tutuch2003-@cluster0.uo27hwg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
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



# NOTE: if you run this program for the first time, please use /employees first
# (get all employees). running anything else for the first time ruins the cache!

# create new employee
@app.route('/v1/employee-manager/employees', methods=['POST'])
@token_required
def create_employee():
	# First, save the employee data in db.employees
	# get new employee info
	employee = request.json
	# create a new object id
	employee['_id'] = ObjectId()
	# add the new employee to db.employees
	employees_collection.insert_one(employee)

	# Then, save the data in the Redis cache
	# save the employee_ID of the new employee
	emp_id = employee['employee_ID']
	# make the document JSON serializable (stringify - Redis friendly)
	employee['_id'] = str(employee['_id'])
	employee['skills'] = json.dumps(employee['skills'])
	# save the new document in the cache
	redis_cache.hset(f"employee:{emp_id}", mapping=employee)
	redis_cache.sadd("employee_ids", emp_id)

	# Finally, let the user know the employee was created
	return jsonify({'message': 'employee created successfully'}), 201

# get list of all employees
@app.route('/v1/employee-manager/employees', methods=['GET'])
@token_required
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
			# parse data (saved as string in Redis, but should be JSON when returned)
			emp_data['skills'] = json.loads(emp_data['skills'])
			emp_data['employee_ID'] = int(emp_data['employee_ID'])
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
@token_required
def get_employee(emp_id):
	# attempt to load the employee from Redis cache
	emp_data = redis_cache.hgetall(f'employee:{emp_id}')

	# Cache hit, load the employee's details from hash map
	if emp_data:
		# parse data (saved as string in Redis, but should be JSON when returned)
		emp_data['skills'] = json.loads(emp_data['skills'])
		emp_data['employee_ID'] = int(emp_data['employee_ID'])

		print("from the cache!")
		return jsonify(emp_data), 200  # return the employee (from cache)

	# cache miss, query the MongoDB database
	employee = employees_collection.find_one({'employee_ID': emp_id})
	# if they exist, add the document to the cache and return it
	if employee:
		# make the employee document JSON serializable (Redis friendly)
		employee['_id'] = str(employee['_id'])
		employee['skills'] = json.dumps(employee['skills'])
		# save the employee ID
		emp_id = employee['employee_ID']
		# cache the employee in a hash map and store their ID in a set
		redis_cache.hset(f"employee:{emp_id}", mapping=employee)
		redis_cache.sadd("employee_ids", emp_id)

		# then, revert the document's lists to JSON (to return to user)
		# note: Redis needs to save lists as strings, but user should get lists as JSON
		employee['skills'] = json.loads(employee['skills'])

		# finally, return the employee
		print("from the database!")
		return jsonify(employee), 200

	# otherwise, if the employee doesn't exist, return an error
	else:
		return jsonify({'message': 'employee not found'}), 404

# update an employee using their employee_ID
@app.route('/v1/employee-manager/employees/<int:emp_id>', methods=['PUT'])
@token_required
def update_employee(emp_id):
	# get new employee info
	updated_data = request.json
	# try to update the employee with the given employee_ID
	result = employees_collection.update_one({'employee_ID': emp_id}, {'$set': updated_data})
	if result.matched_count:
		# after updatng the database, update the cache
		# stringify the data (Redis friendly)
		updated_data["skills"] = json.dumps(updated_data["skills"])
		redis_cache.hset(f"employee:{emp_id}", mapping=updated_data)
		return jsonify({'message': 'employee updated successfully'}), 200

	# otherwise, if they don't exist, return an error
	else:
		return jsonify({'message': 'employee not found'}), 404

# delete an employee using their employee_ID
@app.route('/v1/employee-manager/employees/<int:emp_id>', methods=['DELETE'])
@token_required
def delete_employee(emp_id):
	# try to delete an employee with the given employee_ID
	result = employees_collection.delete_one({'employee_ID': emp_id})
	if result.deleted_count:
		# after deleting the employee from the database, remove it from the cache
		redis_cache.delete(f"employee:{emp_id}")
		redis_cache.srem("employee_ids", emp_id)
		return jsonify({'message': 'employee deleted successfully'}), 200

	# if they don't exist, return an error
	else:
		return jsonify({'message': 'employee not found'}), 404



if __name__ == '__main__':
	app.run(debug=True, port=31002)