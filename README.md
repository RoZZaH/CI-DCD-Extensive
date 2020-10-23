## DEPLOYMENT


### CLONE THE GIT REPOSITORY

1. Clone the Git Repo<br>
    if using [VSCode](https://code.visualstudio.com/) Ctrl+Shift+P (Win) or Cmd+Shift+P (Mac) type 'Clone' (Git:Clone)<br>
    * Paste in this Git URI -> https://github.com/RoZZaH/CI-DCD-Extensive.git

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

6.  `pip install -r requirements.txt` or alternatively `pipenv install requirements.txt`

7. **N.B.** If deploying to Heroku rther than testing on localhost you should probably delete or move the Pipfile and Pipfile.lock into a 'misc' folder this is set to be ignored by .gitignore (this interferes with Heroku deployment)

8. VSCode will probably ask to install python extension and linter for the python language

9. Before we run the app we need to connect to a Mongo Atlas DB - follow steps below

10. Alternatively if Mongo is installed locally create a database called 'bandz' with a single collection 'user'; the flask app should see there's not band data and import some JSON (in 'setup' folder) automagically!



### MONGO_SETTINGS

Presuming no localhost MongoDB available simplest set up is create a free Database/Cluster on MongoDB Database-as-a-service offering MongoDB Atlas.

1. Login/Sign up for [MongoDB Atlas](https://account.mongodb.com/account/login)
2. Create a new Project first, by clicking the folder icon - as you are limited to one free cluster per project
3. Create a free AWS Cluster - there should be one available in Dublin just make sure M0, Free Forever Tier, is available.
    * ![](/docs/create-cluser.png)
    * ![](/docs/cluster-name.png)
    * should end up with something like this:<br> ![](/docs/cluster-created.png)
4. While you are waiting for the cluster to be provisioned - you can create a database user by clicking **Database Access** in the left navigation
    * create a database user with read/write access
    * ![](/docs/create-db-user.png)
    * use a password with uppercase and lowercase letters and numbers but without special characters like hyphens as this aids simple connections using a mongodb_uri
    * You will need to note this username and password down as the connection string will need to be edited to include these credientals
    * ![](/docs/create-db-user2.png)
5. The database user should have read/write access 
    *    ![](/docs/database-access.png)
6. You will probably still be waiting on the cluster, so change **Network Access** (again in the left hand-side navbar)
    * Set all IP addresses are whitelisted; this can be made more secure if deploying to production like Heroku.
    * ![](/docs/network-access.png)
    * ![](/docs/ip-access.png)
7. The Cluster should now be provisioned and you can add a new database
    * click **Collections** under the Cluster name 
    * in the collection area click **Add My Own Data** to open a pop-up
    * create a database called 'bandz' and a initial collection called 'user'
    * ![](/docs/create-db.png)
    * ![](/docs/user-collection.png)
    * other collections will be created during the setup phase on launching the flask app 
8. Finally copy the mongodb_uri/srv connection string; either click the Command Line Tools tab over to the extreme right of the Collections or Overview tabs or go up one level in the breadcrumb trail to the project name from here click **Connect** under the Cluster Name choose *Connect your application* change the driver to python, version 3.6 or later
    * click copy
    * ![](/docs/mongo-uri.png)
9.
    1. Paste / add this connection string into [config.py object](https://flask.palletsprojects.com/en/1.1.x/config/) 
       * Ammend the string the the correct database name and database user's password 
       * Add `SECRET_KEY` and set `PICTURES_FOLDER="media"`
       * Here is a [sample](/sample_config.py)
       * For more on this Julian Nash has a [good video](https://www.youtube.com/watch?v=GW_2O9CrnSU) on using the config object 
    2. Alternatively you can use Environmental Variables
       * rename the current __init__.py file to __init__.bak
       * rename the __init__.env sample file to __init__.py
       * set Environmental Variables for:
         * `SECRET_KEY`
         * `MONGO_CONNECTION_URI` (containing the appropriate db details)
         * use `export MONGO_CONNECTION="<paste-connection-edit-with-database-and-password>"` - on Mac/Unix, ammend before saving / hitting Enter 
         * `$env:MONGO_CONNECTION="<paste-connection-edit-with-database-and-password>"` is the equivalent Windows Powershell command


## FIRST FLASK RUN
1. You should see this page
    * ![](/docs/setup.png)
    * this will take a little while
2. Back in Mongo Atlas the database should have grown to include Towns and Bands (and the initial User credientals)
    * ![](/docs/db-tables-post-import.png)
3. On first run it only returns one genre so you need to shutdown and restart the server (may require pushing again to heroku ) the next time it reads the genres
