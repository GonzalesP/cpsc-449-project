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
# Use project-manager database
db = client['project-manager']
# Create collections
employees_collection = db['employees']
projects_collection = db['projects']
tasks_collection = db['tasks']

# Create Redis cache
redis_cache = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Test your connection to MongoDB
@app.route('/v1/project-manager/test', methods=['GET'])
def check_dbs():
	print(client.list_database_names())
	return jsonify({'message': 'hi'}), 200



# EMPLOYEES METHODS

# TODO: create new employee (POST)

# get list of all employees
@app.route('/v1/project-manager/employees', methods=['GET'])
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
			emp_data['projects'] = json.loads(emp_data['projects'])
			# save the document in list of employees
			employees.append(emp_data)
		
		# print("from the cache!")
		return jsonify(employees), 200  # return all employees (from cache)

	# Cache miss, query the MongoDB database
	documents = list(employees_collection.find())
	# list of employee documents to return
	employees = []
	for document in documents:
		# make each document JSON serializable (stringify objects/lists)
		document['_id'] = str(document['_id'])
		document['skills'] = json.dumps(document['skills'])
		document['projects'] = json.dumps(document['projects'])
		# save each employee ID
		emp_id = document['employee_ID']
		# cache each employee in a hash map and store their IDs in a set
		# first, stringify lists for redis cache
		redis_cache.hset(f"employee:{emp_id}", mapping=document)
		redis_cache.sadd("employee_ids", emp_id)

		# then, revert the document's lists to JSON (to return to user)
		# note: Redis needs to save lists as strings, but user should get lists as JSON
		document['skills'] = json.loads(document['skills'])
		document['projects'] = json.loads(document['projects'])

		# finally, save each employee document
		employees.append(document)
		
	# return all employees
	# print("from the database!")
	return jsonify(employees), 200  # return all employees (from MongoDB Atlas)

# get an employee by their employee ID
@app.route('/v1/project-manager/employees/<int:emp_id>')
def get_employee(emp_id):
	employee = employees_collection.find_one({'employee_ID': emp_id})
	if employee:
		employee['_id'] = str(employee['_id'])
		return jsonify(employee), 200
	else:
		return jsonify({'message': 'Employee not found'}), 404

# get an employee's projects by their employee ID
@app.route('/v1/project-manager/employees/<int:emp_id>/projects')
def get_employee_projects(emp_id):
	employee = employees_collection.find_one({'employee_ID': emp_id})
	if employee:
		# TODO: aggregation - show name of project
		return jsonify(employee['projects']), 200
	else:
		return jsonify({'message': 'Employee not found'}), 404

# get an employee's skills by their employee ID
@app.route('/v1/project-manager/employees/<int:emp_id>/skills')
def get_employee_skills(emp_id):
	employee = employees_collection.find_one({'employee_ID': emp_id})
	if employee:
		return jsonify(employee['skills']), 200
	else:
		return jsonify({'message': 'Employee not found'}), 404

# TODO: get employees with a certain skill (GET)

# TODO: update an employee using their ID (PUT)

# TODO: delete an employee using their ID (DELETE)



# PROJECTS METHODS

# TODO: create new project (POST)

# get list of all projects
@app.route('/v1/project-manager/projects', methods=['GET'])
def get_projects():
	projects = list(projects_collection.find())
	for project in projects:
		project['_id'] = str(project['_id'])
	return jsonify(projects), 200

# get project by its project ID
@app.route('/v1/project-manager/projects/<int:pro_id>')
def get_project(pro_id):
	project = projects_collection.find_one({'project_ID': pro_id})
	if project:
		project['_id'] = str(project['_id'])
		return jsonify(project), 200
	else:
		return jsonify({'message': 'Project not found'}), 404

# TODO: get employees names from project (using their IDs - aggregation)

# TODO: get manager name from project (using their ID - aggregation)

# TODO: update a project using its ID (PUT)

# TODO: delete a project using its ID (DELETE)



# TASKS METHODS

# TODO: create new task (POST)

# get list of all tasks
@app.route('/v1/project-manager/tasks', methods=['GET'])
def get_tasks():
	tasks = list(tasks_collection.find())
	for task in tasks:
		task['_id'] = str(task['_id'])
	return jsonify(tasks), 200

# get list of tasks for a project (using projecct ID)
@app.route('/v1/project-manager/projects/<int:pro_id>/tasks')
def get_project_tasks(pro_id):
	tasks = list(tasks_collection.find({'project_ID': pro_id}))
	for task in tasks:
		task['_id'] = str(task['_id'])
	# TODO: say "no tasks" if list empty
	return jsonify(tasks), 200

# get list of tasks for an employee (using employee ID)
@app.route('/v1/project-manager/employees/<int:emp_id>/tasks')
def get_employee_tasks(emp_id):
	tasks = list(tasks_collection.find({'employee_ID': emp_id}))
	for task in tasks:
		task['_id'] = str(task['_id'])
	# TODO: say "no tasks" if list empty
	return jsonify(tasks), 200

# TODO: update a task using its object ID ? hm.

# TODO: delete a task ?

if __name__ == '__main__':
	app.run(degbug=True)