# BANDZ.ie
## Milestone Project Three: Data-Centric Design - Code Institute

This project is a speculative music website where artists and managers can create band bio and contact information. The was inspired by the wave of nostalgia for live events, favourite albums and bands that was a response to the current Covid-19 pandemic. Initially some inspiration drawn from [Discogs](https://www.discogs.com/) but I came across a fansite called [IrishMusicDB](http://www.irishmusicdb.com) that is obviously a labour of love, it's good to have a record of bands and music in Ireland, but the site is now showing its age. The idea would be for an Irish Music webiste for artists North and South, and then possibly extend to include artists from the Irish diaspora - so it would be a site celebrating music from artists past and present. The site could be extended to include Venues and Tour Dates (when they return!).

### Demo

A live demo can be found on [Heroku](http://bandz-ie.herokuapp.com/)
* Tester Credientals:
  * username: tester@testing.com
   * password: Tester

If deploying again, there are instructions below, please note that you can register as a new user but password reset is not implemented so..
please **Note Down your Password** - the reason to register is so that the dummy data is imported and associated with your account and you can edit / delete some live records.

## USER STORIES
There is a [wireframe PDF](/docs/bandz_wireframe.pdf) of the project showing the main CRUD functionality.

Users (Band Leaders and Managers) can:
* register to manage their own or multiple bands
* write a comprehensive band/artist bio including
  * uploading a band profile image (400 x 400 square). These may not remain on the Heroku app as files are wiped when it spins down.
  * an embed to a promo video on youtube or vimeo - see **A-House** listing for an example of this
  * contact details - including tel and email links
  * ROI/NI and International phone number using [Intl Tel Input](https://intl-tel-input.com/)
  * classify themselves or create new music genres

Fans can:
* Search the database
* Browse Bands by Location to a town or county
* Browse Bands by Genre
* Browse Bands alphabetically

## TECHNOLOGIES AND FEATURES
The site makes extensive use of a combination of CSS Grid and Flexbox to remain responsive at different resolutions.
I concentrated on a small-size (mobile) view and a wider desktop view.
As I could imagine a band or yound musician signing up and uploading their details on a phone, the create band feature is split over several pages/forms.
The site takes an All-Island approach to location, by calling it hometown and the towns are loaded into the towns dropdown as counties change.
Genres are unwound from band data (which is why the server needs a restart post deploy).
Locations are also unwound using a lookup, there is a slight lag on this page but I was challenging myself - there is 3,000+ bands and over 1,000 towns
Obviously if you were deploying this commerically you might use a chron script to create a quicker table or aggregate documents.
The navigation is generated largely programmatically using Flask-Nav and Flask-Breadcrumbs
The alphaebtical paging was quite challenging at involved using a combination of list/dict comprehensions and MongoDB Faceted search - it also works at small screen sizes.

## REFLECTIONS + DIRECTIONS
Mongoengine seemed like a good idea initially but I used Mongo aggregations / pipelines so much that I probably could have stuck with Pymongo.
The alphabetical paging was tough to work out and also meant a lot of logic now resides in the Jinja templates; I can see why these apps are seperated out into a backend API and a Javascript App. Also I can see the benefit of using Class-based views (possible but involved in Flask) over the Function-based views - that's probably where Django comes in. Search is rather naively implemented with equal weighting given across text-fields, obviously this needs further work you would want to weight a band name, or genres higher that words in a bio - but it is amazing how quickly mongo returned results.

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
    1. Paste / add the mongodb_uri/srv connection string into [config.py object](https://flask.palletsprojects.com/en/1.1.x/config/) 
       * Ammend the string the the correct database name and database user's password 
       * Add `SECRET_KEY` and set `PICTURES_FOLDER="media"`
       * Here is a [sample](/sample_config.py)
       * For more on this Julian Nash has a [good video](https://www.youtube.com/watch?v=GW_2O9CrnSU) on using the config object 
    2. Alternatively you can use Environmental Variables
       * rename the current __init__.py file to __init__.bak
       * rename the __init__.env sample file to __init__.py and move into the **bandz** folder 
       * set Environmental Variables for:
         * `SECRET_KEY`
         * `MONGO_CONNECTION_URI` (containing the appropriate db details)
         * use `export MONGO_CONNECTION="<paste-connection-edit-with-database-and-password>"` - on Mac/Unix, ammend before saving / hitting Enter 
         * `$env:MONGO_CONNECTION="<paste-connection-edit-with-database-and-password>"` is the equivalent Windows Powershell command


### FIRST FLASK RUN - LOCALLY
1. You should see this page
    * ![](/docs/setup.png)
    * this will take a little while
2. Back in Mongo Atlas the database should have grown to include Towns and Bands (and the initial User credientals)
    * ![](/docs/db-tables-post-import.png)
3. If you were to add a band straight away there would only be one **genre**, rock, available, so you need to shutdown and restart the server, the next time it correctly unwinds the newly imported records and defines available genres (you can also add your own by adding to a band - you can add more than one by using commas in bewteen)


### DEPLOYING TO HEROKU
If you did not uncomment the gunicorn line in the `requirements.txt` then gunicorn webserver has not been installed.
Heroku will need this or to know about it in the requirements file.
1. you need run `pip install gunicorn`
2. next run `pip freeze > requirements.txt` so that it becomes part of the requirements file that Heroku will use in its deployment of the app
3. the next file to create is a Procfile (capital P no extension) this file is a simple one line that tells Heroku you are deploying a web app and what is the starting file gunicorn will run in this case the run.py is the Flask [factory](https://flask.palletsprojects.com/en/1.1.x/patterns/appfactories/) the following code should suffice:
    * `web: gunicorn run:app`

4. apart from the **requirements.txt** you also need a **runtime.txt** specificying the version of python to use. The current version is python-3.6.12 on the heroku free tier
    * use `echo "python-3.6.12" > runtime.txt` to create this one line file
5.  Delete or Move the following **pipenv** files **Pipfile** and **Pipfile.lock** as these can confuse Heroku
    * a **misc** folder is a safe location as this is registered and ignore in .gitignore
6. Edit the current **.gitignore** - deploying to Heroku is similar to push a repo to Git but it needs to read .txt files
    * remove the line to ignore `*.txt` to make sure that the requirements.txt and runtime.txt are pushed
    * if using a configuration object remove the line `config.py` - see comments above
    * Alternatively use environmental variables but you will need to add these key:value pairs to [Heroku dashboard](https://devcenter.heroku.com/articles/config-vars)
    * for example:
        ```FLASK_ENV=production
           FLASK_RUN=run.py
           PICTURES_FOLDER=media
           SECRET_KEY=<some-secret-key>
           MONGO_CONNEX=<whatever-mongodb-uri>
           ```
    * ![](/docs/heroku-envvars.png)
7.  If using .flash-env for amaned 'production' - although Heroku probably reads from the Environmental Variables set above
8. the app may crash immediately after building but the heroku logs are verbose but useful (you will see a command for this on the webpage for your app). Environmental varibales are available via settings from the app dashboard


### Heroku Command Line
Presumes you have signed up for a free Heroku account. We will deploy using [Heroku Command Line Tools](https://devcenter.heroku.com/articles/heroku-cli) - this is basically setting up a remote git repository to push our local files too.

1. Initialise a local repo
    * `git init`
2. add everything
    * `git add .`
3. make an inital commit
    * `git commit -m"Initial Heroku Push"`
4. now use the following command to initialise the remote destination
   1. starting fresh:
    * `heroku create <project-name>`
    * VS Code will prompt you to open a web link and ask you to sign in to heroku
    * once it verifies your credientals it will create the remote destination
    * check that **heroku** is an available remote destination
    * ```
        git remote -v
        https://git.heroku.com/<project-name>/git
      ```
    * Finally push the local files (new master branch) to heroku
    * `git push heroku master`
    2. starting again:
        * `git remote add heroku https://git.heroku.com/<project-name>/git`
        * you may need to force push
        * `git push -f heroku master`

5. See Section on **FIRST FLASK RUN** above
6. As noted above genres not setup correctly on first running the server
    * use `heroku restart --app <project-name>` to restart the server, you should be able to see more than one genre category when adding a new band


## Notes on TESTING
I found Chrome and Edge a little flaky when testing the grid/responsive layouts - they appear to break but if you do a refresh there actually working.
Firefox Developer Edition has much better tools for this.
As I've tried to detail above, music genres need a restart to stick - I'm not sure whether it's a caching issue but the list_genres route doesn't work the first time, even though browse by Genre seems to have unwound the mongo records post import.
The dummy data was generating using band names taken from the [IrishMusicDB](http://www.irishmusicdb.com) and a combination of mockaroo and some generation using the Towns data (which is largely accurate taken from OS and Census data in ROI/NI). And the genres are out - again I was trying to get bands/results to spread across genre and location, Sharon Shannon is not a Belfast Funk Artist in real life! The band description could be longer but it would've made the csv/json document very difficult to wrangle the odd typo or extra space in front of band names.
As noted above you can register on Heroku, although password reset/user management is not fully implemented, it's best to use the credientals provided to have full control.

## Credits
Youtubers [Julian Nash](https://www.youtube.com/channel/UC5_oFcBFlawLcFCBmU7oNZA) and [Corey Schafer](https://www.youtube.com/watch?v=YYXdXT2l-Gg&list=PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU) do a brilliant job of getting people up and running with Flask.

Two other individuals who helped a great deal on going beyond the basics of MongoDB are John Dupuy AKA [Needless Process](https://www.youtube.com/c/needlessprocess) who has a great short playlist on [MongoEngine and the various fieldtypes](https://www.youtube.com/playlist?list=PL6RpFCvmb5SGUCLmzTc_wS6gvG0c3GIrS) and [Bogdan Stashchuk](https://www.youtube.com/channel/UCiyasqPIZz8zzbJp7-17dJw) has a very comprehensive playlist on the [Mongo Aggregation Framework](https://www.youtube.com/watch?v=A3jvoE0jGdE&list=PLWkguCWKqN9OwcbdYm4nUIXnA2IoXX0LI)

MongoDB University is also a great resource and offers [free courses and certification](https://university.mongodb.com)
