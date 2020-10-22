##DEPLOYMENT


###CLONE THE GIT REPOSITORY

1. Clone the Git Repo<br>
    if using [VSCode](https://code.visualstudio.com/) Ctrl+Shift+P (Win) or Cmd+Shift+P (Mac) type 'Clone' (Git:Clone)<br>
..* Paste in this Git URI -> https://github.com/RoZZaH/CI-DCD-Extensive.git

2. Create a Virtual Environment using venv or [pipenv](https://realpython.com/pipenv-guide/) or virtualenv

3.	Depending on your computer os change the commands as appropriate (Mac tends to have Python 2 also installed so you need to use pip3 or python3 in your commands)<br>
```python
    python3 -m venv ci_bandz
    source ci_bandz/bin/activate #to activate
``` 
or use `pipenv shell` if using pipenv

4.  usually the pip version is outdated install old version of pip
    `pip install --upgrade pip`

5.   use the requirements.txt to install dependicies <br>
N.B. if deploying to heroku uncomment the line for gunicorn

6.  pip install -r requirements.txt | pipenv install requirements.txt

7. N.B. If deploying to Heroku rther than testing on localhost you should probably delete or move the Pipfile and Pipfile.lock into a 'misc' folder this is set to be ignored by .gitignore (this interferes with Heroku deployment)

8. VSCode will probably ask to install python extension and linter for the python language

9. Before we run the app we need to connect to a Mongo Atlas DB - follow steps below

10. Alternatively if Mongo is installed locally create a database called 'bandz' with a single collection 'user'; the flask app should see there's not band data and import some JSON (in 'setup' folder) automagically!



###MONGO_SETTINGS

Presuming no localhost MongoDB available simplest set up is create a free Database/Cluster on MongoDB Database-as-a-service offering MongoDB Atlas.

1. Login/Sign up for [MongoDB Atlas](https://account.mongodb.com/account/login)
2. Create a Project if you like
3. Create a free AWS Cluster - there should be one available in Dublin just make sure M0, Free Forever Tier, is available.
    * ![](/docs/create-cluser.png)
    * ![](/docs/cluster-name.png)
    * should end up with something like this:<br> ![](/docs/cluster-created.png)
4. create a database called 'bandz' and a initial collection called 'user'
    * ![](/docs/create-db.png)
    * ![](/docs/user-collection.png)
    * other collections will be created during the setup phase on launching the flask app
5. create a database user with read/write access
    * ![](/docs/create-db-user.png)
    * use a password with uppercase and lowercase letters and numbers but without special characters like hyphens as this aids simple connections using a mongodb_uri
    * ![](/docs/create-db-user2.png)
6. The database user should have read/write access 
    *    ![](/docs/database-access.png)
7. Change Network access so that all IP addresses are whitelisted; this can be made more secure if deploying to production like Heroku.
    * ![](/docs/network-access.png)
    * ![](/docs/ip-access.png)
8. Finally copy the mongodb_uri/srv connection string; click the three ... little dots<br>
   beside collections
    * ![](/docs/mongo-uri.png)
9. Paste / add this connection string to the __init__.py or [config.py object](https://flask.palletsprojects.com/en/1.1.x/config/) depending on how you are deploying
10. Amend to include the 'bandz' (or whatever you called the database) and the database user's password
    * **N.B.** MongoEngine uses **MONGO_SETTINGS** Object as opposed to the usual MONGODB_URI with PyMongo
    * 
    ```python
    SECRET_KEY = <some secret string or env variable>
    MONGODB_SETTINGS = {
    "db" : "bandz", #this name takes precedence
    "host" : <uri/short-srv connection string>
    }
    ```



