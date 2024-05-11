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
db = client['project-manager']
# Use projects collection
projects_collection = db['projects']
# Connect to Redis cache
redis_cache = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Test your connection to the project manager service
@app.route('/v1/project-manager/test', methods=['GET'])
def check_dbs():
	print(client.list_database_names())
	return jsonify({'message': 'hi'}), 200



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



if __name__ == '__main__':
	app.run(debug=True, port=31002)