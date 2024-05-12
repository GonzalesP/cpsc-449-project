# CPSC 449 Project - Scalable Backend System with Secure Authentication

## Project Description
This project is a company manager API. Using this API, users can perform MongoDB CRUD operations on collections of employees, projects, and project tasks.

# Setup
## First, please install the following apps and Python libraries
1. [Mongosh](https://www.mongodb.com/docs/mongodb-shell/install/)
2. Redis (follow steps below)
    - On Mac:
        - Make sure you have Homebrew installed using `brew --version`  
        - In your terminal, run `brew install redis`
    - On Windows/Linux:
        - Enable WSL2 or Install using `wsl --install` in administrator mode on PS or CMD
        - Once you're running Ubuntu on windows, paste the following into the terminal:
```bash
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg  

echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list  

sudo apt-get update  
sudo apt-get install redis  
```

3. `pip install -r requirements.txt`

## Then, initialize the MongoDB
- Open a new terminal tab and enter the mongosh command given to you by Atlas
- Navigate to the [mongodb-initialization.txt](https://github.com/GonzalesP/cpsc-449-project/blob/main/mongodb-initialization.txt) file.
- In the terminal, run `use company-manager`
- Copy and paste each `insertMany` statement into the terminal as they appear in [mongodb-initialization.txt](https://github.com/GonzalesP/cpsc-449-project/blob/main/mongodb-initialization.txt). They look like this:
```bash
db.collection.insertMany([
{
    "...": ...,
    "...": ...
},
{
    "...": ...,
    "...": ...
},
])
``` 

## Next, start the Redis server and company-manager microservices
1. Start your Redis server at port 6379
    - On Mac, run `redis-server`
    - On Windows, in WSL2, run `sudo service redis-server start`
2. `python3 account-manager.py`
3. `python3 employee-manager.py`
4. `python3 project-manager.py`
5. `python3 task-manager.py`

## Finally, open a client (e.g. Postman) to use the APIs
1. account-manager runs on port 31001
    - **POST** `http://127.0.0.1:31001/v1/account-manager/signup`
    - **POST** `http://127.0.0.1:31001/v1/account-manager/login`
    - **GET** `http://127.0.0.1:31001/v1/account-manager/users/<username>`
    - **PUT** `http://127.0.0.1:31001/v1/account-manager/users/<username>`
2. employee-manager runs on port 31002
    - **POST** `http://127.0.0.1:31002/v1/employee-manager/employees`
    - **GET** `http://127.0.0.1:31002/v1/employee-manager/employees`
    - **GET** `http://127.0.0.1:31002/v1/employee-manager/employees/<int:emp_id>`
    - **PUT** `http://127.0.0.1:31002/v1/employee-manager/employees/<int:emp_id>`
    - **DELETE** `http://127.0.0.1:31002/v1/employee-manager/employees/<int:emp_id>`
3. project-manager runs on port 31003
    - **POST** `http://127.0.0.1:31003/v1/project-manager/projects`
    - **GET** `http://127.0.0.1:31003/v1/project-manager/projects`
    - **GET** `http://127.0.0.1:31003/v1/project-manager/projects/<int:pro_id>`
    - **PUT** `http://127.0.0.1:31003/v1/project-manager/projects/<int:pro_id>`
    - **DELETE** `http://127.0.0.1:31003/v1/project-manager/projects/<int:pro_id>`
4. task-manager runs on port 31004
    - **POST** `http://127.0.0.1:31004/v1/task-manager/tasks`
    - **GET** `http://127.0.0.1:31004/v1/task-manager/tasks`
    - **GET** `http://127.0.0.1:31004/v1/task-manager/projects/<int:pro_id>`
    - **GET** `http://127.0.0.1:31004/v1/task-manager/employees/<int:emp_id>`
    - **PUT** `http://127.0.0.1:31004/v1/task-manager/tasks/<id>`
    - **DELETE** `http://127.0.0.1:31004/v1/task-manager/tasks/<id>`
5. note: 
    - For POST and PUT operations, you will need a raw JSON body
    - For Authentication, you need to navigate to the `Headers` tab and input `Key= Authorization` and `Value= Bearer <token-here>`

# Github Repository
Click [here](https://github.com/GonzalesP/cpsc-449-project) to view the github repository

# Team Members
- Pascual Gonzales
- Tarek Chaalan
- Bryan De Los Santos

# Contributions
- ### Pascual Gonzales
    - Planned microservices architecture
    - Redis cache implementation
- ### Tarek Chaalan
    - JWT implementation
- ### Bryan De Los Santos
    - bcrypt implementation
- ### Everyone
    - API development
    - API testing

# Scalable Strategies & Significant Design Decisions
- ### Caching
    - We implemented caching to store frequently accessed queries in memory.
    - To implement the cache, we used Redis
- ### Microservices Architecture
    - We broke down our application into four smaller, independently deployable services.
        - 1. Account Manager: Sign-Up/Log-In and JWT token creation
        - 2. Employee Manager: CRUD operations for the db.employees collection
        - 3. Project Manager: CRUD operations for the db.projects collection
        - 4. Task manager: CRUD operations for the db.tasks collection
- ### Secure User Authentication
    - In order to make our APIs secure, users are required to obtain a JWT token. This is done through the Account Manager service's Log-In feature.
- ### Encrypted Password Storage
    - To store encrypted user passwords, we used the bcrypt library.
