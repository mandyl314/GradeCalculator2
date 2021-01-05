# YOUR PROJECT TITLE
#### Video Demo:  https://youtu.be/63H5Mzj3u0c
#### Description:
This is a web application that allows users to calculate their current grade or
grade needed to reach a desired grade. This uses HTML/CSS, SQL, Flask, & Python,
as well as Bootstrap to style the page.
Users can create their own account and add/delete grades and categories. The
grades are outputed in a table on the page.

Files:
layout.html: the basic layout, specifically the header depending on if the user
if logged in. It also has the buttons depending on wether the user is logged in
or not.
failure.html: produces error messages if the user inputs the wrong information
such as wrong username, password, clicking submit without the necessary fields,
etc.
index.html: contains the grade table and the options depending on if the
calculate current or calculate desired grade is clicked. It either has the
options to enter grades and categories or enter the information to calculate the
grade needed. It automatically updates when the user enters information.
login.html: login page, contains fields to enter username and password and submit
register.html: register page, contains fields to enter username and password to
create new account.
application.py: python code for the web application
    def index(): gets the information needed for the table. Also calculates the
    current grade. It gets the user's session id and gets the corresponding
    category and grae entered information from the SQL database.
    def choice(): Determines whether the user wants to calculate current grade
    or desired grade based on button clicked and reroutes accordingly.
    def needed(): Calculates the grade needed. It gets the user's session id and
    gets the corresponding category and grae entered information from the SQL
    database.
    def update_cat(): Adds or deletes a category from the SQL database
    def update_grade(): Adds or deletes a grade from the SQL database
    def login(): Gets the users input username and password and checks with the
    SQL database to see if it exists
    def register(): Gets the users input username and password and creates new
    account if username is not in user
    def logout(): logs the user out
grades.db: contains three tables to store data: users, categories, and gradebook
users (
'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
'username' TEXT NOT NULL,
'hash' TEXT NOT NULL
)
gradebook (
user_id INTEGER,
category VARCHAR(255),
points NUMERIC,
total NUMERIC
)
categories (
userid_cat INTEGER,
category VARCHAR(255),
percent NUMERIC
)
styles.css: styles the page, uses some components from Bootstrap
requirements.txt
README.md
