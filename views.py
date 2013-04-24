from flask import Flask, render_template, redirect, request, g, session, flash, url_for
import model
from model import session as db_session
import forms
from urllib2 import Request, urlopen, URLError

from wordnik import *
apiUrl = 'http://api.wordnik.com/v4'
apiKey = '3a764609677c7b0b4000408a0a905c1febd664dfa62363aaf'
client = swagger.ApiClient(apiKey, apiUrl)


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

    # Query for all projects that match user in membership table (project user = global user)
    for my_membership in model.session.query(model.Membership).filter_by(user_id=g.user.id):
        recent_work.append(my_membership.project)

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
        session["membership"] = place_membership.id
        session["project"] = register_project.id
        # WHY IS THE FLASH NOT WORKING?
        flash("You have successfully created a new project.")
        return redirect("/new_idea")
    return render_template("/mypage")

@app.route("/new_idea")
def add_idea():

    # THIS HAS SOME ISSUES. NOT COMPLETELY CORRECT.
    # BASE TEXT IS MOST RECENT. IT IS NOT PROPERLY ATTACHED TO THE PROPER PROJECT.

    project = session.get("project")

    basetext_generator = []

    for my_text in model.session.query(model.Project).filter_by(id=project):
        basetext_generator.append(my_text)

    form = forms.AddIdeaForm()

    # my_words = urlopen('http://api.wordnik.com/v4)
    # response = my_words.read()

    word_list = []
    # like_list = []

    wordsApi = WordsApi.WordsApi(client)
    random_word = wordsApi.getRandomWord()
    word_list.append(random_word)

    # wordApi = WordApi.WordApi(client)
    # synonym = wordApi.WordApi("WORD HERE")
    # like_list.append(synonym)

    # return render_template("/new_idea.html", form=form, word_list = word_list)
    return render_template("/new_idea.html", form=form, word_list = word_list, basetext_generator=basetext_generator)

@app.route("/save_idea", methods=["GET", "POST"])
def save_idea():

    project = session.get("project")

    form = forms.AddIdeaForm()

    if form.validate_on_submit():
        register_idea = model.Idea(id = None, idea = form.idea.data, project_id = project, creator_id = g.user.id)
        model.session.add(register_idea)
        model.session.commit()
        # model.session.refresh(register_idea)
        session["idea"] = register_idea.id

    return redirect("/rate_idea")


@app.route("/search_project", methods=["GET"])
def display_search():
    return render_template("search_project.html")

@app.route("/search", methods=["POST"])
def search():
    query = request.form['query']
    projects = model.session.query(model.Project).\
            filter(model.Project.project_name.ilike("%" + query + "%")).all()

    form = forms.JoinProjectForm()

    return render_template("project_searchresults.html", projects=projects, form=form)

@app.route("/authenticate_member", methods=["POST"])
def member_authenticate():

    form = forms.JoinProjectForm()
    if form.validate_on_submit():
        group_project = model.session.query(model.Project).filter_by(id=form.project_id.data, project_name=form.project_name.data, project_password=form.project_password.data)
        if group_project:
            # ENSURE THAT PERSON IS NOT ALREADY REGISTERED TO THIS PROJECT!
            register_member = model.Membership(user_id = g.user.id, project_id = form.project_id.data)
        model.session.add(register_member)
        model.session.commit()
        # THIS PROBABLY NEEDS TO BE WORKED ON
        # IT SHOULD PROBABLY BE REDIRECT INSTEAD OF JUST RENDER_TEMPLATE BUT IT CURRENTLY DOES NOT WORK AS REDIRECT WAY VERY WELL
        return render_template("/my_project.html")
    else:
        return redirect("/mypage")

@app.route("/my_project/<int:id>", methods=["GET"])
def my_project(id):

    session["existing_project"] = id
    return render_template("/my_project.html", id=id)

@app.route("/update_idea/<int:id>")
def update_idea(id):

    # project = session.get("project")
    existing_project = session.get("existing_project")

    basetext_generator = []

    for my_text in model.session.query(model.Project).filter_by(id=existing_project):
        basetext_generator.append(my_text)

    form = forms.AddIdeaForm()

    # my_words = urlopen('http://api.wordnik.com/v4)
    # response = my_words.read()

    word_list = []
    # like_list = []

    wordsApi = WordsApi.WordsApi(client)
    random_word = wordsApi.getRandomWord()
    word_list.append(random_word)


    return render_template("/update_idea.html", form=form, word_list = word_list, basetext_generator=basetext_generator)

@app.route("/save_updated_idea/", methods=["GET", "POST"])
def save_updated_idea():

    existing_project = session.get("existing_project")

    form = forms.AddIdeaForm()

    if form.validate_on_submit():
        register_idea = model.Idea(id = None, idea = form.idea.data, creator_id = g.user.id, project_id = existing_project)
        model.session.add(register_idea)
        model.session.commit()
        # model.session.refresh(register_idea)
        session["idea"] = register_idea.id

    return redirect("/rate_idea")

@app.route("/rate_idea")
def add_rating():

    form = forms.RateIdeaForm()
    return render_template("/rate_idea.html", form=form)

@app.route("/save_rating", methods=["GET", "POST"])
def save_rating():

    idea = session.get("idea")

    form = forms.RateIdeaForm()

    if form.validate_on_submit():
        register_rating = model.Rating(id = None, idea_id = idea, rater_id = g.user.id, rating = form.rating.data, rating_notes = form.rating_notes.data)
        model.session.add(register_rating)
        model.session.commit()

        # commit this addition
    model.session.commit()

    return redirect("/mypage")

@app.route("/view_ratings", methods=["GET", "POST"])
def view_ratings():

    idea = session.get("idea")
    # project = session.get("project")

    idea_ratings = []

    for viewer in model.session.query(model.Rating).filter_by(idea_id = idea):
        idea_ratings.append(viewer.idea)
        # idea_ratings.append(viewer.rating)
        # idea_ratings.append(viewer.rater)

    # return render_template("mypage.html", recent_work = recent_work)
    return render_template("view_ratings.html", idea_ratings = idea_ratings)


if __name__ == "__main__":
    app.run(debug = True)