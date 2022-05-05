
from flask import Flask, render_template, redirect, request, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, Users, Feedbacks
from form import Register, Login, Feedback
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = "bunnyrabbit"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///User'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()
bcrypt = Bcrypt()
logged_in = []

@app.route("/")
def home():
    return redirect("/register")

@app.route("/register")
def register():
    form = Register()
    users = Users.query.all()

    if len(logged_in) > 0:
        return redirect(f"/users/{logged_in[0]}")
    else: 
        return render_template("register.html", form=form, users=users)

@app.route("/register", methods=["POST"])
def register_post():
    form = Register()
    email = False

    emails = Users.query.all()
    for e in emails:
        if e.email == request.form["email"]:
            email = True

    if form.validate_on_submit():
        if Users.query.get(request.form["username"]) != None:
            flash("That username is already taken")
            return redirect(f"/register")
        elif email != False:
            flash("That email is already taken")
            return redirect(f"/register")
        else:
            username = request.form["username"]
            password = bcrypt.generate_password_hash(request.form["password"]).decode('utf-8')
            email = request.form["email"]
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]

            new_user = Users(
                username = username,
                password = password,
                email = email,
                first_name = first_name,
                last_name = last_name
            )
            db.session.add(new_user)
            db.session.commit()

            session["username"] = username
            logged_in.append(username)

            return redirect(f"/users/{username}")
    else: 
        return redirect("/register")

@app.route("/login")
def login():
    form = Login()

    if len(logged_in) > 0:
        return redirect(f"/users/{logged_in[0]}")
    else: 
        return render_template("login.html", form=form)

@app.route("/login", methods=["POST"])
def login_post():
    form = Login()

    if form.validate_on_submit():
        if Users.query.get(request.form["username"]) != None:
            user = Users.query.get(request.form["username"])

            if bcrypt.check_password_hash(user.password, request.form["password"]):
                session["username"] = user.username
                logged_in.append(user.username)
                return redirect(f"/users/{user.username}")
            else:
                flash("Incorrect username or password!")
                return redirect("/login")
        else:
            flash("Incorrect username or password!")
            return redirect("/login") 
    else:
        return redirect("/login")

@app.route("/secret")
def secret():
    if session["username"]:
        return "You made it!"
    else:
        flash("Please log in to continue!")
        return redirect("/login")

@app.route("/logout")
def logout():
    if session["username"] == None:
        flash("Please log in to continue!")
        return redirect("/login")
    else: 
        session.pop("username", None)
        logged_in.clear()
        return redirect("/login")

@app.route("/users/<username>")
def user(username):
    user = Users.query.get_or_404(username)
    users = Users.query.all()
    current_user = session.get("username")
    feedback = Feedbacks.query.all()

    return render_template(
        "user.html", 
        user = user, 
        users = users,
        current_user = current_user,
        feedback = feedback
    )

@app.route("/users/<username>/delete")
def user_delete(username):
    if session["username"] == None:
        flash("Please log in to continue!")
        return redirect("/login")
    else:
        session.pop("username", None)
        logged_in.clear()
        Users.query.filter_by(username=username).delete()
        db.session.commit()
        return redirect("/")

@app.route("/users/<username>/feedback/add")
def add_feedback(username):
    form = Feedback()
    current_user = session.get("username")

    if session["username"] == None:
        flash("Please log in to continue!")
        return redirect("/login")
    else:
        return render_template(
            "add_feedback.html", 
            current_user = current_user,
            form = form, 
            username = username
            )

@app.route("/users/<username>/feedback/add", methods=["POST"])
def add_feedback_post(username):
    form = Feedback()
    
    if form.validate_on_submit():
        title = request.form["title"]
        content = request.form["content"]

        new_feedback = Feedbacks(
            title = title, 
            content = content, 
            created_by = session["username"],
            posted_to = username
            )
        db.session.add(new_feedback)
        db.session.commit()

        return redirect(f"/users/{username}")
    else:
        return redirect(f"/users/{username}/feedback/add")

@app.route("/feedback/<int:feedbackid>/update")
def edit_feedback(feedbackid):
    form = Feedback()
    feedback = Feedbacks.query.get_or_404(feedbackid)
    current_user = session["username"]

    if session["username"] == None:
        flash("Please log in to continue!")
        return redirect("/login")
    elif feedback.created_by != current_user:
        flash("You cannot perform that action!")
        return redirect(f"/users/{current_user}")
    else:
        return render_template(
            "edit_feedback.html", 
            current_user = current_user,
            feedback = feedback,
            form = form
            )

@app.route("/feedback/<int:feedbackid>/update", methods=["POST"])
def edit_feedback_post(feedbackid):
    form = Feedback()
    feedback = Feedbacks.query.get_or_404(feedbackid)

    if form.validate_on_submit():
        title = request.form["title"]
        content = request.form["content"]

        feedback.title = title
        feedback.content = content

        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/users/{feedback.username}")
    else:
        return redirect(f"/feedback/{feedbackid}/update")

@app.route("/feedback/<int:feedbackid>/delete")
def delete_feedback(feedbackid):
    if session["username"] == None:
        flash("Please log in to continue!")
        return redirect("/login")
    else: 
        feedback = Feedbacks.query.get_or_404(feedbackid)
        Feedbacks.query.filter_by(id=feedbackid).delete()
        db.session.commit()
        return redirect(f"/users/{feedback.username}")
