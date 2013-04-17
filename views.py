from flask import Flask, render_template, redirect, request, g, session, flash, url_for
import model
from model import session as db_session
import forms

app = Flask(__name__)
app.secret_key = 'discovery'

@app.before_request
def before_request():
	g.id = session.get('id')

@app.route("/")
def login():
    form = forms.LoginUserForm()
    return render_template("login.html", form=form)

@app.route("/authenticate", methods=["POST"])
def authenticate():

    # old form of retrieving info, before wtforms:
    # email = request.form['email']
    # username = request.form['username']
    # password = request.form['password']

    form = forms.AddUserForm()
    if form.validate_on_submit():
        if model.session.query(model.User).filter_by(email=form.email.data,username=form.username.data, password=form.password.data).first():
            session['id'] = id
            return redirect("/mypage")
    else:
        return redirect("/")

@app.route("/new_user")
def new_user():
    form = forms.AddUserForm()
    return render_template("new_user.html", form=form)

# @app.route("/save_user", methods=["POST"])
@app.route("/save_user", methods=["GET", "POST"])
def add_user():

    form = forms.AddUserForm()
    if form.validate_on_submit():
        register_user = model.User(email = form.email.data, username = form.username.data, password = form.password.data)
        model.session.add(register_user)
        model.session.commit()

        # WHY IS THE FLASH NOT WORKING?
        flash("Thanks for registering. Please login now.")
        return render_template("/login.html")
    return render_template("/new_user.html", form=form)

    # OLD WAY BEFORE WTFORMS -- same structure for new projects, etc.:

    # email = request.form['email']
    # username = request.form['username']
    # password = request.form['password']	

    # add_user = model.User()

    # add_user.email = email

    # add_user.username = username

    # add_user.password = password

    # model.session.add(add_user)
    # model.session.commit()

    # return redirect("/")

@app.route("/mypage", methods=['GET'])
def my_page():

    recent_work = db_session.query(model.Membership).all()

    # other reference point from past ratings project:
    # projects = model.session.query(model.Membership).get(1)
        # filter(model.Membership.project_id).\
        # limit(5).all()

    session['id'] = id
    return render_template("mypage.html", recent_work = recent_work)

@app.route("/new_project")
def new_project():
    # CHECK SESSION ID -- VALIDATE THAT IN SESSION IN ORDER TO HAVE PAGE RENDERED
    form = forms.AddProjectForm()
    return render_template("new_project.html", form=form)

@app.route("/save_project", methods=["POST"])
def add_project():

    form = forms.AddProjectForm()
    if form.validate_on_submit():
        register_project = model.Project(project_name = form.name.data, project_password = form.password.data, base_text = form.base_text.data)
        # OLD WAY, BEFORE CORRECTIONS TO WFORMS -- THIS IS INCORRECT -- SHOW DIFFERENCES:
        # register_user = model.User(form.email.data, form.username.data, form.password.data)
        model.session.add(register_project)
        model.session.commit()

        # WHY IS THE FLASH NOT WORKING?
        flash("You have successfully created a new project.")
        return render_template("/mypage.html", form=form)
    return render_template("/new_idea.html", form=form)

@app.route("/search_project", methods=["GET"])
def display_search():
    return render_template("search_project.html")

@app.route("/search", methods=["POST"])
def search():
    query = request.form['query']
    projects = db_session.query(Project).\
            filter(Project.name.ilike("%" + query + "%")).\
            limit(20).all()

    return render_template("results.html", projects=projects)

if __name__ == "__main__":
    app.run(debug = True)
