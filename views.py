from flask import Flask, render_template, redirect, request, g, session, flash, url_for
import model
from model import session as db_session
# from flask.ext.bootstrap import Bootstrap
from random import choice, randrange
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

@app.route("/logout")
def logout():
    session.pop("id")
    return "Logged out"

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
        return redirect("/")
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


@app.route("/save_project", methods=["POST"])
def add_project():

    form = forms.AddProjectForm()
    if form.validate_on_submit():
        register_project = model.Project(id = None, project_name = form.name.data, project_password = form.password.data, base_text = form.base_text.data, keywords = form.keywords.data)
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
        # session["membership"] = place_membership.id
        # session["project"] = register_project.id
        project = register_project.id
        st_project = str(project)
        # session["kwords"] = register_project.keywords
        
        # flash("You have successfully created a new project.")

        return redirect("/my_project/" + st_project)
        # return redirect("/new_idea")
    return render_template("/mypage")

# @app.route("/new_idea")
# def add_idea():
# # def add_idea(project):

#     project = session.get("project")
#     # kwords = session.get("kword")

#     # split_kwords = split(kwords)
#     # print "HERE ARE MY KWORDS:" 
#     # print kwords

#     project_generator = []

#     for my_text in model.session.query(model.Project).filter_by(id=project):
#         project_generator.append(my_text)


#     # for my_text in model.session.query(model.Project).filter_by(id=project):
#     #     keyword_generator.append(my_text)

#     form = forms.AddIdeaForm()

#     # my_words = urlopen('http://api.wordnik.com/v4)
#     # response = my_words.read()

#     word_list = []

#     wordsApi = WordsApi.WordsApi(client)
#     random_word = wordsApi.getRandomWord()
#     word_list.append(random_word)

#     like_list = []


#     wordApi = WordApi.WordApi(client)


#     # query for correct project in project table
#     for kword_search in model.session.query(model.Project).filter_by(id=project):
#         # retrieve keywords that match project
#         fromlist = kword_search.keywords
#         # split keywords into individual elements in a list
#         splitlist = fromlist.split()
#         # randomly select an element/keyword from list and assign it to a variable
#         random_index = randrange(0,len(splitlist))
#         random_keyword = splitlist[random_index]

#     #     # access API client
#     #     # apply random keyword to word, select synonym and one each
#         synonym = wordApi.getRelatedWords(word = random_keyword, relationshipTypes='synonym', limitPerRelationshipType=1)
#     #     # append to list to be displayed in HTML page
#         like_list.append(synonym)

#     # return render_template("/new_idea.html", form=form, word_list = word_list)
#     return render_template("/new_idea.html", form=form, word_list = word_list, project_generator = project_generator, like_list = like_list)

# @app.route("/save_idea", methods=["GET", "POST"])
# def save_idea():

#     project = session.get("project")

#     form = forms.AddIdeaForm()

#     if form.validate_on_submit():
#         register_idea = model.Idea(id = None, idea = form.idea.data, project_id = project, creator_id = g.user.id)
#         model.session.add(register_idea)
#         model.session.commit()
#         # model.session.refresh(register_idea)
#         session["idea"] = register_idea.id

#     return redirect("/rate_idea")

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
            register_member = model.Membership(user_id = g.user.id, project_id = form.project_id.data)
        model.session.add(register_member)
        model.session.commit()
        # session["existing_project"] = id

        # THIS PROBABLY NEEDS TO BE WORKED ON
        # IT SHOULD PROBABLY BE REDIRECT INSTEAD OF JUST RENDER_TEMPLATE BUT IT CURRENTLY DOES NOT WORK AS REDIRECT WAY VERY WELL
        return render_template("/my_project.html", id=form.project_id.data)
    else:
        return redirect("/mypage")

@app.route("/my_project/<int:id>", methods=["GET"])
# def my_project(id, idea):
def my_project(id):

    # session["existing_project"] = id
    # existing_project = session.get("existing_project")
    return render_template("/my_project.html", id=id)

@app.route("/update_idea/<int:id>")
def update_idea(id):

    # NOTE: IF WE SEARCH PROJECT AND AUTHENTICATE OURSELVES, WE ARE DIRECTED TO PROJECT BUT HAVE WRONG BASE TEXT!!
    # existing_project = session.get("existing_project")

    project_generator = []

    for my_text in model.session.query(model.Project).filter_by(id=id):
        project_generator.append(my_text)

    form = forms.AddIdeaForm()

    # my_words = urlopen('http://api.wordnik.com/v4)
    # response = my_words.read()

    word_list = []
    # like_list = []

    wordsApi = WordsApi.WordsApi(client)
    random_word = wordsApi.getRandomWord()
    word_list.append(random_word)

    like_list = []

    wordApi = WordApi.WordApi(client)

    # # query for correct project in project table
    for kword_search in model.session.query(model.Project).filter_by(id=id):
        # retrieve keywords that match project
        fromlist = kword_search.keywords
        # split keywords into individual elements in a list
        splitlist = fromlist.split()
        # apply randrange function to list, thereby allowing a random selection to be assigned to an integer
        random_index = randrange(0,len(splitlist))
        # take it out of randrange integer state
        # to do this, we select the random_index element from the list
        random_keyword = splitlist[random_index]

    #     # access API client
    #     # apply random keyword to word, select synonym and one each
        synonym = wordApi.getRelatedWords(word = random_keyword, relationshipTypes='synonym', limitPerRelationshipType=1)
    #     # append to list to be displayed in HTML page
        like_list.append(synonym)

    return render_template("/update_idea.html", form=form, word_list = word_list, like_list = like_list, project_generator=project_generator)

@app.route("/save_updated_idea", methods=["GET", "POST"])
def save_updated_idea():

    # existing_project = session.get("existing_project")

    form = forms.AddIdeaForm()

    if form.validate_on_submit():
        # register_idea = model.Idea(id = None, idea = form.idea.data, creator_id = g.user.id, project_id = existing_project)
        register_idea = model.Idea(id = None, idea = form.idea.data, creator_id = g.user.id)
        # NEED TO ADD IN ID
        model.session.add(register_idea)
        model.session.commit()
        model.session.refresh(register_idea)
        # session["idea"] = register_idea.id

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

# @app.route("/view_ratings", methods=["GET", "POST"])
# def view_ratings():

#     idea = session.get("idea")
#     # project = session.get("project")

#     idea_ratings = []

#     for viewer in model.session.query(model.Rating).filter_by(idea_id = idea):
#         idea_ratings.append(viewer.idea)
#         # idea_ratings.append(viewer.rating)
#         # idea_ratings.append(viewer.rater)

#     # return render_template("mypage.html", recent_work = recent_work)
#     return render_template("view_ratings.html", idea_ratings = idea_ratings)

@app.route("/project_ideas", methods=['GET'])
def project_ideas():

    existing_project = session.get("existing_project")

    idea = session.get("idea")

    # create an empty list to append recent projects to
    all_ideas = []

    all_ratings = []

    # Query for all projects that match user in membership table (project user = global user)
    for each_idea in model.session.query(model.Idea).filter_by(project_id=existing_project):
        all_ideas.append(each_idea)

    # YOU HAVE TO GET THE PROPER IDEA ID SO YOU CAN PROPERLY FILTER TO WHICH IDEAS YOU WANT DISPLAYED HERE
    for each_rating in model.session.query(model.Rating):
        # indiv_rating = each_rating.rating
        # each_rating = indiv_rating.sort
        # each_rating = indiv_rating.sort()
        all_ratings.append(each_rating)

    # return render_template("mypage.html", recent_work = recent_work)
    return render_template("project_ideas.html", all_ideas = all_ideas, all_ratings = all_ratings)

@app.route("/about", methods=['GET'])
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug = True)