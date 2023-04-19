# TaskManagerSimpleApp
This proyect are a simple app page made with python flask and Mysql, where you can use funtions like register/login/logout of users sessions,
add/edit/erase tasks, the proyect use a Mysql DataBase with two tables (at the moment) and exclusive user views that only can see by  a root user that are difined previus in the DataBase manager.

-First after you run the app you need to create a virutal enviroment, if you dont have installed it just use "pip install virtualenv"

-After installing the library for the virtual environments, you just need to create one while it is located in the project folder,
this may vary depending on what operating system you are on, so you can investigate how to do it.

-Now you just have to start the virtual environment again with the commands corresponding to your platform,
once started you should see the following at the beginning of the terminal address ("environment name") Address of the terminal, for example:
(.venv) PS C:\Users\Steam\OneDrive\Desktop\TaskManagerSimpleApp>

-Before executing the main file, it is necessary that the database is started, the database model is the .sql extension file, where there is simply the structure of the tables with their relationship and the addition of the root user,
for this you can use the hosting program you want, once done, at the top of the main code is the configuration of the connection to the database, change something if necessary.

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tmdb'


-now simply install the libraries that you will find in requirements.txt and start the main program as you usually run a python program "python3 ./main.py"

-When starting the main program in the console, it shows which port the app is hosted on

-now try the app :D
