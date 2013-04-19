from flask import Flask, render_template, redirect, request, g, session, flash, url_for
import model
# from model import User, Project, Membership, Idea, Rating
from model import session as db_session
import forms

app = Flask(__name__)
app.secret_key = 'discovery'


@app.before_request
def before_request():
    # authenticate - if id exists in the session object, then ...
    user_id = session.get("id")

    if user_id:
        print session
        g.user = model.session.query(model.User).get(user_id)
    else:
        g.user = None
    # else:
        # return redirect("/")


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
        user = model.session.query(model.User).filter_by(email=form.email.data,username=form.username.data, password=form.password.data).first()
        if user:
            session['id'] = user.id
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

        # userid_generator = model.session.query(model.User).get(register_user.id)

        # place_usermembership = model.Membership(user_id = register_user.id)

        # model.session.add(place_usermembership)
        # model.session.commit()


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

    # # create an empty list to append recent projects to
    # recent_work = []

    # # query for projects from the Membership table
    # # query for USER rather than ALL
    # work_query = model.session.query(model.Membership).all()
    # # test query -- an object should be printed out
    # print work_query
    # # iterate through all memberships from query
    # for membership in work_query:
    #     # assign variable to user backreference of memberships
    #     x = membership.user
    #     # assign variable to project backreference of memberships
    #     y = membership.project
    #     # for a project in the backreference of the projects
    #     for project in y:
    #         # append the project names to the recent_work list
    #         recent_work.append(project.name)

    # # test to see recent_work list 
    # print recent_work

    # other reference point from past ratings project:
    # projects = model.session.query(model.Membership).get(1)
        # filter(model.Membership.project_id).\
        # limit(5).all()

    # return render_template("mypage.html", recent_work = recent_work)
    return render_template("mypage.html")


@app.route("/new_project")
def new_project():
    # CHECK SESSION ID -- VALIDATE THAT IN SESSION IN ORDER TO HAVE PAGE RENDERED
    form = forms.AddProjectForm()
    return render_template("new_project.html", form=form)


@app.route("/logout")
def logout():
    session.pop("id")
    return "Logged out"

@app.route("/save_project", methods=["POST"])
def add_project():

    form = forms.AddProjectForm()
    if form.validate_on_submit():
        register_project = model.Project(project_name = form.name.data, project_password = form.password.data, base_text = form.base_text.data)
        model.session.add(register_project)
        
        # query in Projects to get the id of the currently registered project's id
        # model.session.commit()
        # model.session.refresh(register_project)
        
        # insert id into memberships table position for project_id
        place_membership = model.Membership() #project_id = register_project.id, user_id = g.user.id)
        place_membership.user = g.user
        place_membership.project = register_project
        # add this id, as represented as a variable
        model.session.add(place_membership)

        # commit this addition
        model.session.commit()

        # test -- shows id as object that cannot have int() method applied to it
        print g.user.id

        # WHY IS THE FLASH NOT WORKING?
        flash("You have successfully created a new project.")
        return render_template("/new_idea.html", form=form)
    return render_template("/my_page.html", form=form)

@app.route("/new_idea", methods=["GET"])
def new_idea():

    form = forms.AddIdeaForm()
    if form.validate_on_submit():
        register_idea = model.User(idea = form.idea.data)
        model.session.add(register_idea)
        model.session.commit()

    return render_template("new_idea.html", form=form)

@app.route("/search_project", methods=["GET"])
def display_search():
    return render_template("search_project.html")

@app.route("/search", methods=["POST"])
def search():
    query = request.form['query']
    projects = db_session.query(Project).\
            filter(Project.project_name.ilike("%" + query + "%")).\
            limit(20).all()

    return render_template("project_searchresults.html", projects=projects)

if __name__ == "__main__":
    app.run(debug = True)
