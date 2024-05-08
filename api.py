from flask import Flask, jsonify, request  # Flask app methods
from pymongo import MongoClient  # MongoDB Atlas connection
from pymongo.server_api import ServerApi  # MongoDB Atlas connection
from bson.objectid import ObjectId  # Creating/processing ObjectIDs

uri = "insert_your_uri_here"
app = Flask(__name__)

# Connect to MongoDB and create collections
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['project-manager']  # use project-manager database
employees_collection = db['employees']
projects_collection = db['projects']
tasks_collection = db['tasks']

# test your connection to MongoDB
@app.route('/v1/project-manager/test', methods=['GET'])
def check_dbs():
	print(client.list_database_names())
	return jsonify({'message': 'hi'}), 201



# EMPLOYEES METHODS

# TODO: create new employee (POST)

# get list of all employees
@app.route('/v1/project-manager/employees', methods=['GET'])
def get_employees():
	employees = list(employees_collection.find())
	for employee in employees:
		employee['_id'] = str(employee['_id'])
	return jsonify(employees), 200

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