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
# Use tasks collection
tasks_collection = db['tasks']
# Connect to Redis cache
redis_cache = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Test your connection to MongoDB
@app.route('/v1/task-manager/test', methods=['GET'])
def check_dbs():
	print(client.list_database_names())
	return jsonify({'message': 'hi'}), 200



# TASKS METHODS

# TODO: create new task (POST)

# get list of all tasks
@app.route('/v1/task-manager/tasks', methods=['GET'])
def get_tasks():
	tasks = list(tasks_collection.find())
	for task in tasks:
		task['_id'] = str(task['_id'])
	return jsonify(tasks), 200

# get list of tasks for a project (using projecct ID)
@app.route('/v1/task-manager/projects/<int:pro_id>')
def get_project_tasks(pro_id):
	tasks = list(tasks_collection.find({'project_ID': pro_id}))
	for task in tasks:
		task['_id'] = str(task['_id'])
	# TODO: say "no tasks" if list empty
	return jsonify(tasks), 200

# get list of tasks for an employee (using employee ID)
@app.route('/v1/task-manager/employees/<int:emp_id>')
def get_employee_tasks(emp_id):
	tasks = list(tasks_collection.find({'employee_ID': emp_id}))
	for task in tasks:
		task['_id'] = str(task['_id'])
	# TODO: say "no tasks" if list empty
	return jsonify(tasks), 200

# TODO: update a task using its object ID ? hm.

# TODO: delete a task ?

if __name__ == '__main__':
	app.run(debug=True, port=31002)