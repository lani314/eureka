from flask import Flask, render_template, redirect, request, g, session, flash, url_for
import model
# from model import User, Project, Membership, Idea, Rating
from model import session as db_session
import forms

app = Flask(__name__)
app.secret_key = 'discovery'


@app.before_request
def before_request():

    # authenticate existence of session id within object
    user_id = session.get("id")

    if user_id:
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


@app.route("/mypage", methods=['GET'])
def my_page():

    # create an empty list to append recent projects to
    recent_work = []

    # query for projects from the Membership table
    # query for USER rather than ALL
    work_query = model.session.query(model.Membership).all()
    # test query -- an object should be printed out
    print work_query
    # iterate through all memberships from query

    for membership in work_query:
        # assign variable to user backreference of memberships
        recent_work.append(membership)


        # user_info = membership.user
        # # assign variable to project backreference of memberships
        # project_info = membership.project
        # # for a project in the backreference of the projects

        # print user_info
        # print project_info

        # for each_project in project_info:
        #     # append the project names to the recent_work list
        #     recent_work.append(project)

    # # # test to see recent_work list 
    # print recent_work

    # other reference point from past ratings project:
    # projects = model.session.query(model.Membership).get(1)
        # filter(model.Membership.project_id).\
        # limit(5).all()

    # return render_template("mypage.html", recent_work = recent_work)
    return render_template("mypage.html", recent_work = recent_work)


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
        register_project = model.Project(id = None, project_name = form.name.data, project_password = form.password.data, base_text = form.base_text.data)
        model.session.add(register_project)
        
        # query in Projects to get the id of the currently registered project's id
        # model.session.commit()
        # model.session.refresh(register_project)
        
        # insert id into memberships table position for project_id
        #project_id = register_project.id, user_id = g.user.id)

        # access membership table, set to variable
        place_membership = model.Membership()
        # access user from model, set that to global user from session
        place_membership.user = g.user
        # access the project part of membership, set that to the registered project
        place_membership.project = register_project
        # add this id, as represented as a variable
        model.session.add(place_membership)

        # commit this addition
        model.session.commit()
        session["project"] = register_project.id
        # WHY IS THE FLASH NOT WORKING?
        flash("You have successfully created a new project.")
        return redirect("/new_idea")
    return render_template("/mypage")

@app.route("/new_idea")
def add_idea():

    form = forms.AddIdeaForm()
    return render_template("/new_idea.html", form=form)

@app.route("/save_idea", methods=["GET", "POST"])
def save_idea():

    project = session.get("project")

    form = forms.AddIdeaForm()

    if form.validate_on_submit():
        register_idea = model.Idea(idea = form.idea.data, project_id = project)
        model.session.add(register_idea)
        model.session.commit()
        # session["idea"] = register_idea.id

        model.session.refresh(register_idea)

    # return redirect("/new_idea.html", form=form)
    return render_template("/new_idea.html", form=form)

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

# @app.route("/rate_idea")
# def add_rating():

#     form = forms.RateIdeaForm()
#     return render_template("/rate_idea.html", form=form)

# @app.route("/save_rating", methods=["GET", "POST"])
# def save_rating():

#     idea = session.get("idea")

#     form = forms.RateIdeaForm()

#     if form.validate_on_submit():
#         register_rating = model.Rating(idea_id = idea, rater_id = g.user, rating = form.rating.data, rating_notes = form.rating_notes.data)
#         model.session.add(register_rating)
#         model.session.commit()

if __name__ == "__main__":
    app.run(debug = True)
