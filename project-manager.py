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
# Use projects collection
projects_collection = db['projects']
# Connect to Redis cache
redis_cache = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Test your connection to the project manager service
@app.route('/v1/project-manager/test', methods=['GET'])
def check_dbs():
	print(client.list_database_names())
	return jsonify({'message': 'hi'}), 200



# NOTE: if you run this program for the first time, please use /projects first
# (get all projects). running anything else for the first time ruins the cache!

# create new project
@app.route('/v1/project-manager/projects', methods=['POST'])
def create_project():
	# First, save the project data in db.projects
	# get new project info
	project = request.json
	# create a new object id
	project['_id'] = ObjectId()
	# add the new project to db.projects
	projects_collection.insert_one(project)

	# Then, save the data in the Redis cache
	# save the project_ID of the new project
	pro_id = project['project_ID']
	# make the document JSON serializable (stringify - Redis friendly)
	project['_id'] = str(project['_id'])
	project['employees'] = json.dumps(project['employees'])
	# save the new document in the cache
	redis_cache.hset(f"project:{pro_id}", mapping=project)
	redis_cache.sadd("project_ids", pro_id)

	# Finally, let the user know the project was created
	return jsonify({'message': 'project created successfully'}), 201

# get list of all projects
@app.route('/v1/project-manager/projects', methods=['GET'])
def get_projects():
	# attempt to load all employee IDs from Redis cache
	project_ids = redis_cache.smembers("project_ids")

	# Cache hit, load each project's details from hash map
	if project_ids:
		# list of project documents to return
		projects = []
		# for each project in the Redis cache, parse its data
		for pro_id in project_ids:
			# get projects's data
			pro_data = redis_cache.hgetall(f'project:{pro_id}')
			# parse employees (saved as string in Redis, but should be JSON when returned)
			pro_data['employees'] = json.loads(pro_data['employees'])
			pro_data['project_ID'] = int(pro_data['project_ID'])
			pro_data['manager'] = int(pro_data['manager'])
			# save the document in list of employees
			projects.append(pro_data)
		
		print("from the cache!")
		return jsonify(projects), 200  # return all projects (from cache)

	# Cache miss, query the MongoDB database
	documents = list(projects_collection.find())
	# list of project documents to return
	projects = []
	for document in documents:
		# make each document JSON serializable (stringify objects/lists)
		document['_id'] = str(document['_id'])
		document['employees'] = json.dumps(document['employees'])
		# save each project ID
		pro_id = document['project_ID']
		# cache each project in a hash map and store their IDs in a set
		redis_cache.hset(f"project:{pro_id}", mapping=document)
		redis_cache.sadd("project_ids", pro_id)

		# then, revert the document's lists to JSON (to return to user)
		# note: Redis needs to save lists as strings, but user should get lists as JSON
		document['employees'] = json.loads(document['employees'])

		# finally, save each project document
		projects.append(document)
	
	# return all projects
	print("from the database!")
	return jsonify(projects), 200

# get project by its project ID
@app.route('/v1/project-manager/projects/<int:pro_id>', methods=['GET'])
def get_project(pro_id):
	# attempt to load the project from Redis cache
	pro_data = redis_cache.hgetall(f'project:{pro_id}')

	# Cache hit, load the project's details from hash map
	if pro_data:
		# parse employees (saved as string in Redis, but should be JSON when returned)
		pro_data['employees'] = json.loads(pro_data['employees'])

		print("from the cache!")
		return jsonify(pro_data), 200  # return the employee (from cache)

	# cache miss, query the MongoDB database
	project = projects_collection.find_one({'project_ID': pro_id})
	# if they exist, add the document to the cache and return it
	if project:
		# make the project document JSON serializable (Redis friendly)
		project['_id'] = str(project['_id'])
		project['employees'] = json.dumps(project['employees'])
		# save the project ID
		pro_id = project['project_ID']
		# cache the project in a hash map and store their ID in a set
		redis_cache.hset(f"project:{pro_id}", mapping=project)
		redis_cache.sadd("project_ids", pro_id)

		# then, revert the document's lists to JSON (to return to user)
		# note: Redis needs to save lists as strings, but user should get lists as JSON
		project['employees'] = json.loads(project['employees'])

		# finally, return the project
		print("from the database!")
		return jsonify(project), 200
	
	# otherwise, if the project doesn't exist, return an error
	else:
		return jsonify({'message': 'Project not found'}), 404

# update a project using its project_ID
@app.route('/v1/project-manager/projects/<int:pro_id>', methods=['PUT'])
def update_project(pro_id):
	# get new project info
	updated_data = request.json
	# try to update the project with the given project_ID
	result = projects_collection.update_one({'project_ID': pro_id}, {'$set': updated_data})
	if result.matched_count:
		# after updatng the database, update the cache
		# stringify the data (Redis friendly)
		updated_data["employees"] = json.dumps(updated_data["employees"])
		redis_cache.hset(f"project:{pro_id}", mapping=updated_data)
		return jsonify({'message': 'project updated successfully'}), 200
	
	# otherwise, if it doesn't exist, return an error
	else:
		return jsonify({'message': 'project not found'}), 404

# delete a project using its project_ID
@app.route('/v1/project-manager/projects/<int:pro_id>', methods=['DELETE'])
def delete_project(pro_id):
	# try to delete a project with the given project_ID
	result = projects_collection.delete_one({'project_ID': pro_id})
	if result.deleted_count:
		# after deleting the project from the database, remove it from the cache
		redis_cache.delete(f"project:{pro_id}")
		redis_cache.srem("project_ids", pro_id)
		return jsonify({'message': 'project deleted successfully'}), 200
	
	# if it doesn't exist, return an error
	else:
		return jsonify({'message': 'employee not found'}), 404



if __name__ == '__main__':
	app.run(debug=True, port=31003)