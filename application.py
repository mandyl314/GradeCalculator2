from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///grades.db")

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
@login_required
def index():
    gradebook = db.execute("SELECT * FROM categories JOIN gradebook ON categories.category = gradebook.category AND user_id_cat = user_id WHERE user_id_cat = ? ORDER BY percent DESC", session["user_id"])
    category_info = db.execute("SELECT * FROM categories WHERE user_id_cat = ?",session["user_id"])
    result = 0
    for category in category_info:
        subsection = db.execute("SELECT * FROM gradebook WHERE user_id = ? AND category= ?",session["user_id"], category["category"])
        earned = 0
        total = 0
        percent = category["percent"]
        if not subsection:
            continue
        else:
            for grade in subsection:
                earned += grade["points"]
                total += grade["total"]
            result += (earned / total) * (percent)

    return render_template("index.html", category_info=category_info, gradebook=gradebook, result=round(result,2), choice=1)

@app.route("/choice")
@login_required
def choice():
    choice = request.args.get("choice")
    if (choice == "calc_current"):
        return redirect("/")
    else:
        return redirect("/needed")

@app.route("/needed", methods=["GET", "POST"])
@login_required
def needed():
    gradebook = db.execute("SELECT * FROM categories JOIN gradebook ON categories.category = gradebook.category WHERE user_id_cat = ? ORDER BY percent DESC", session["user_id"])
    category_info = db.execute("SELECT * FROM categories WHERE user_id_cat = ?",session["user_id"])

    if request.method == "GET":
        return render_template("index.html", category_info=category_info, gradebook=gradebook, choice=2)
    else:
        if not request.form.get("grade_category"):
            return render_template("failure.html", message="must provide category")
        if not request.form.get("total"):
            return render_template("failure.html", message="must provide total")
        if not request.form.get("desired"):
            return render_template("failure.html", message="must provide desired grade")
        category_select = request.form.get("grade_category")
        total_add = int(request.form.get("total"))
        desired = int(request.form.get("desired"))
        if (total_add < 0 or desired < 0):
            return render_template("failure.html", message="must provide valid total")

        partial = 0
        select_total = 0
        select_earned = 0
        select_percent = 0
        for category in category_info:
            subsection = db.execute("SELECT * FROM gradebook WHERE user_id = ? AND category= ?",session["user_id"], category["category"])
            earned = 0
            total = 0
            percent = category["percent"]
            if not subsection:
                if (category["category"] == category_select):
                    select_percent = percent
                continue
            else:
                for grade in subsection:
                    earned += grade["points"]
                    total += grade["total"]
                if (category["category"] != category_select):
                    partial += (earned / total) * (percent)
                else:
                    select_total = total
                    select_earned = earned
                    select_percent = percent
        target = desired - partial
        needed = (target/select_percent) * (select_total + total_add) - select_earned
        return render_template("index.html", category_info=category_info, gradebook=gradebook,category=category_select, needed=round(needed,2) , total_add=total_add, choice=3, desired=desired)


@app.route("/update_cat", methods=["POST"])
@login_required
def update_cat():
    if not request.form.get("new_cat"):
        return render_template("failure.html", message="must provide category")
    if not request.form.get("percent"):
        return render_template("failure.html", message="must provide percent")
    category = request.form.get("new_cat")
    percent = int(request.form.get("percent"))

    if (percent <= 0):
        return render_template("failure.html", message="must provide valid percent")
    if(request.form.get("update") == "add"):
        db.execute("INSERT INTO categories (user_id_cat, category, percent) VALUES (?, ?, ?)", session["user_id"], category, percent)
    else:
        grades = db.execute("SELECT * FROM gradebook WHERE user_id = ? AND category = ?", session["user_id"], category)
        if not grades:
             db.execute("DELETE FROM categories WHERE user_id_cat = ? AND category = ?", session["user_id"], category)
        else:
            return render_template("failure.html", message="cannot remove, category not empty")
    return redirect("/")


@app.route("/update_grade", methods=["POST"])
@login_required
def update_grade():
    if not request.form.get("grade_category"):
        return render_template("failure.html", message="must provide category")
    if not request.form.get("points"):
        return render_template("failure.html", message="must provide points")
    if not request.form.get("total"):
        return render_template("failure.html", message="must provide total")
    category = request.form.get("grade_category")
    points = int(request.form.get("points"))
    total = int(request.form.get("total"))

    if (points < 0 or total < 0):
        return render_template("failure.html", message="must provide valid points and total")

    if(request.form.get("update") == "add"):
        category_info = db.execute("SELECT * FROM categories WHERE user_id_cat = ? AND category = ?",session["user_id"], category)
        if (category_info[0]["category"] == None):
            return render_template("failure.html", message="category does not exist")
        db.execute("INSERT INTO gradebook (user_id, category, points, total) VALUES (?, ?, ?, ?)", session["user_id"], category, points, total)
    else:
        grade = db.execute("SELECT * FROM gradebook WHERE user_id = ? AND category = ? AND points = ? AND total = ?", session["user_id"], category, points, total)
        if not grade:
            return render_template("failure.html", message="cannot find grade to delete")
        else:
            db.execute("DELETE FROM gradebook WHERE user_id = ? AND category = ? AND points = ? AND total = ? LIMIT 1", session["user_id"], category, points, total)
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("failure.html", message="must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("failure.html", message="must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("failure.html", message="not valid username or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("failure.html", message="must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("failure.html", message="must provide password")

        username = request.form.get("username")
        password = request.form.get("password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # check if username exists alread
        if len(rows) == 1:
            return render_template("failure.html", message="username already exists")

        # hash password
        pwhash = generate_password_hash(request.form.get("password"))

        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, pwhash)

        # Redirect user to home page
        return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")