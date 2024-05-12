from flask import Flask, jsonify, request  # Flask app methods
from pymongo import MongoClient  # MongoDB Atlas connection
from pymongo.server_api import ServerApi  # MongoDB Atlas connection
from bson.objectid import ObjectId  # Creating/processing ObjectIDs
import redis  # Redis cache
import json  # Stringify JSONs for Redis cache
from JWT import token_required # Import JWT Decorator from JWT.py

# Replace this with your URI from MongoDB Atlas!
uri = "enter-uri-here"
app = Flask(__name__)

# Connect to MongoDB
client = MongoClient(uri, server_api=ServerApi('1'))
# Use company-manager database
db = client['company-manager']
# Use tasks collection
tasks_collection = db['tasks']
# Connect to Redis cache
redis_cache = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Test your connection to the task manager service
@app.route('/v1/task-manager/test', methods=['GET'])
def check_dbs():
	print(client.list_database_names())
	return jsonify({'message': 'hi'}), 200



# NOTE: if you run this program for the first time, please use /tasks first
# (get all tasks). running anything else for the first time ruins the cache!

# create new task
@app.route('/v1/task-manager/tasks', methods=['POST'])
@token_required
def create_task():
	# First, save the task data in db.tasks
	# get new task info
	task = request.json
	# create a new object id
	task['_id'] = ObjectId()
	# add the new task to db.tasks
	tasks_collection.insert_one(task)

	# Then, save the data in the Redis cache
	# stringify the task's object id (Redis friendly)
	task['_id'] = str(task['_id'])
	# save the new document in the cache
	redis_cache.hset(f"task:{task['_id']}", mapping=task)
	redis_cache.sadd("task_ids", task['_id'])

	# Finally, let the user know the task was created
	return jsonify({'message': 'task created successfully'}), 201

# get list of all tasks
@app.route('/v1/task-manager/tasks', methods=['GET'])
@token_required
def get_tasks():
	# attempt to load all task IDs from Redis cache
	task_ids = redis_cache.smembers("task_ids")

	# Cache hit, load each task's details from hash map
	if task_ids:
		# list of task documents to return
		tasks = []
		# for each task in the Redis cache, parse their data
		for task_id in task_ids:
			# get task's data
			task_data = redis_cache.hgetall(f'task:{task_id}')
			# parse tasks (some data saved as string in Redis, but should be int)
			task_data['project_ID'] = int(task_data['project_ID'])
			task_data['employee_ID'] = int(task_data['employee_ID'])
			# save the document in list of tasks
			tasks.append(task_data)

		print("from the cache!")
		return jsonify(tasks), 200  # return all tasks (from cache)

	# Cache miss, query the MongoDB database
	documents = list(tasks_collection.find())
	# list of task documents to return
	tasks = []
	for document in documents:
		# make each document JSON serializable (stringify objects/lists)
		document['_id'] = str(document['_id'])
		# cache each task in a hash map and store their IDs in a set
		redis_cache.hset(f"task:{document['_id']}", mapping=document)
		redis_cache.sadd("task_ids", document['_id'])

		# finally, save each task document
		tasks.append(document)

	# return all tasks
	print("from the database!")
	return jsonify(tasks), 200

# get list of tasks for a project (using project ID)
@app.route('/v1/task-manager/projects/<int:pro_id>', methods=['GET'])
@token_required
def get_project_tasks(pro_id):
	# get list of tasks
	tasks = list(tasks_collection.find({'project_ID': pro_id}))
	# if the list exists, convert _id into string (JSON friendly) and return
	if tasks:
		for task in tasks:
			task['_id'] = str(task['_id'])
		return jsonify(tasks), 200
	# otherwise, return an error
	else:
		return jsonify({'message': 'project not found'}), 404

# get list of tasks for an employee (using employee ID)
@app.route('/v1/task-manager/employees/<int:emp_id>', methods=['GET'])
@token_required
def get_employee_tasks(emp_id):
	# get list of tasks
	tasks = list(tasks_collection.find({'employee_ID': emp_id}))
	# if the list exists, convert _id into string (JSON friendly) and return
	if tasks:
		for task in tasks:
			task['_id'] = str(task['_id'])
		return jsonify(tasks), 200
	# otherwise, return an error
	else:
		return jsonify({'message': 'employee not found'}), 404

# update a task using its object ID
@app.route('/v1/task-manager/tasks/<id>', methods=['PUT'])
@token_required
def update_task(id):
	# get new task info
	updated_data = request.json
	# try to update the task with the given object ID
	result = tasks_collection.update_one({'_id': ObjectId(id)}, {'$set': updated_data})
	if result.matched_count:
		# after updatng the database, update the cache
		# stringify the data (Redis friendly)
		redis_cache.hset(f"task:{id}", mapping=updated_data)
		return jsonify({'message': 'task updated successfully'}), 200

	# otherwise, if it doesn't exist, return an error
	else:
		return jsonify({'message': 'task not found'}), 404

# delete a task using its object ID
@app.route('/v1/task-manager/tasks/<id>', methods=['DELETE'])
@token_required
def delete_task(id):
	# try to delete the task with the given object ID
	result = tasks_collection.delete_one({'_id': ObjectId(id)})
	if result.deleted_count:
		# after deleting the task from the database, remove it from the cache
		redis_cache.delete(f"task:{id}")
		redis_cache.srem("task_ids", id)
		return jsonify({'message': 'task deleted successfully'}), 200

	# if it doesn't exist, return an error
	else:
		return jsonify({'message': 'task not found'}), 404


if __name__ == '__main__':
	app.run(debug=True, port=31004)