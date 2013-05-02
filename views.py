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
    form_add = forms.AddUserForm()
    return render_template("login.html", form=form, form_add=form_add)

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
def save_user():

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

        # user = g.user.id
        # str_newuser = str(user)
        return redirect("/")
        # return redirect("/")
    # return render_template("/new_user.html", form=form)
    return redirect("/")


@app.route("/mypage", methods=['GET'])
def my_page():

    # create an empty list to append recent projects to
    recent_work = []

    # Query for all projects that match user in membership table (project user = global user)
    for my_membership in model.session.query(model.Membership).filter_by(user_id=g.user.id):
        recent_work.append(my_membership)

    return render_template("mypage.html", recent_work = recent_work)

@app.route("/new_project")
def new_project():
    form = forms.AddProjectForm()
    return render_template("new_project.html", form=form)

@app.route("/save_project", methods=["POST"])
def add_project():

    form = forms.AddProjectForm()
    if form.validate_on_submit():
        register_project = model.Project(id = None, project_master = g.user.id, project_name = form.name.data, project_password = form.password.data, base_text = form.base_text.data, keywords = form.keywords.data)
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

        pro = form.project_id.data
        mem_project = str(form.project_id.data)
        return redirect("/my_project/" + mem_project)
        # return render_template("/my_project.html", id=form.project_id.data)
    else:
        return redirect("/mypage")

@app.route("/my_project/<int:id>", methods=["GET"])
def my_project(id):

    project_generator = []
    collaborators = []

    for my_text in model.session.query(model.Project).filter_by(id=id):
        project_generator.append(my_text)
        master = my_text.project_master
        for my_people in model.session.query(model.Membership).filter_by(project_id=id):
            if my_people.user_id != master:
                collaborators.append(my_people)

    return render_template("/my_project.html", id=id, project_generator=project_generator, collaborators=collaborators)

@app.route("/my_project/<int:id>/edit", methods =["POST", "GET"])
def edit_project(id):

    project_generator = []
    for project in model.session.query(model.Project).filter_by(id=id):
        project_generator.append(project)

    form = forms.AddProjectForm()

    current_user = g.user.id

    return render_template("edit.html", form=form, project_generator=project_generator, current_user=current_user)

# @app.route("/my_project/<int:id>/editor_authentication", methods=["POST"])
# def editor_authentication(id):

#     return_id = str(id)

#     form = forms.AddProjectForm()
#     if form.validate_on_submit():
#        for code in model.session.query(model.Project).filter_by(id=id):
#             for  code.project_master.password = form.editor_password.data:
#                 return redirect("my_project/" + return_id + "/save_project_edits")
#             else:
#                 return redirect("/my_project/" + return_id)
#                 flash("Sorry, you do not have permission to edit")

@app.route("/my_project/<int:id>/save_project_edits", methods=["POST", "GET"])
def save_project_edits(id):

    form = forms.AddProjectForm()

    pass_id = str(id)

    if form.validate_on_submit():
       for project in model.session.query(model.Project).filter_by(id=id):

            project_update = model.session.query(model.Project).get(id)
            if form.name.data:
                project_update.project_name = form.name.data
            if form.password.data:
                project_update.project_password = form.password.data
            if form.base_text.data:
                project_update.base_text = form.base_text.data
            if form.keywords.data:
                project_update.keywords = form.keywords.data
            model.session.commit()


    return redirect("/my_project/" + pass_id)

@app.route("/my_project/<int:id>/create_idea")
def create_idea(id):

    # existing_project = session.get("existing_project")

    project_generator = []

    for my_text in model.session.query(model.Project).filter_by(id=id):
        project_generator.append(my_text)

    form = forms.AddIdeaForm()

    # my_words = urlopen('http://api.wordnik.com/v4)
    # response = my_words.read()

    # word_list = []
    # like_list = []

    wordsApi = WordsApi.WordsApi(client)
    random_word = wordsApi.getRandomWord().word
    # word_list.append(random_word)

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
        if synonym:
            like_list.append(synonym[0].words[0])

    if like_list:
        random_combo = "%s %s"%(random_word, choice(like_list))
    else:
        random_combo = "No suggestions sad face :("
            
    return render_template("/update_idea.html", form=form, random_word = random_word, like_list = like_list, project_generator=project_generator, random_combo = random_combo)

@app.route("/my_project/<int:id>/save_idea", methods=["POST"])
def save_idea(id):

    # existing_project = session.get("existing_project")

    form = forms.AddIdeaForm()

    if form.validate_on_submit():
        # register_idea = model.Idea(id = None, idea = form.idea.data, creator_id = g.user.id, project_id = existing_project)
        register_idea = model.Idea(id = None, idea = form.idea.data, creator_id = g.user.id, project_id = id) 
        model.session.add(register_idea)
        model.session.commit()
        model.session.refresh(register_idea)

        new_idea = str(id)

        # session["idea"] = register_idea.id

    # return redirect("/rate_idea")

    return redirect("/my_project/" + new_idea + "/create_idea")

@app.route("/my_project/<int:id>/all_ideas", methods=["GET"])
def all_ideas(id):

    recent_ideas = []

    for work in model.session.query(model.Idea).filter_by(project_id=id):
        recent_ideas.append(work)
   
    return render_template("/all_ideas.html", recent_ideas=recent_ideas)

@app.route("/my_project/<int:id>/sorted_ideas", methods=["GET"])
def sorted_ideas(id):

    ideas_to_sort = []

    for each in model.session.query(model.Idea).filter_by(project_id=id):
        # sorted_version = sorted(each.average_rating)
        ideas_to_sort.append(each)
   
    return render_template("/sorted_ideas.html", ideas_to_sort=ideas_to_sort)


@app.route("/my_project/<int:id>/rate_idea/<int:idea>")
def rate_idea(id, idea):

    form = forms.RateIdeaForm()

    idea=idea
    id=id

    return render_template("/rate_idea.html", form=form, id=id, idea=idea)

@app.route("/my_project/<int:id>/rate_idea/<int:idea>/save_rating", methods=["POST"])
def save_rating(id, idea):

    # idea = session.get("idea")

    form = forms.RateIdeaForm()

    if form.validate_on_submit():
        register_rating = model.Rating(id = None, idea_id = idea, rater_id = g.user.id, rating = form.rating.data, rating_notes = form.rating_notes.data)
        model.session.add(register_rating)

    # IMPLEMENT AND INSERT COUNTER
    # query for appropriate idea row, according to matching id 
    for counter in model.session.query(model.Idea).filter_by(id=idea):
        # if the total_ratings table is None
        if counter.total_ratings == None:
            #  get the row for the idea
            current_idea = model.session.query(model.Idea).get(idea)
            # make total_ratings equal to 1
            current_idea.total_ratings = 1
        else:
            # get the row for the idea
            current_idea_update = model.session.query(model.Idea).get(idea)
            # retrieve current count from instance in table
            current_count = current_idea_update.total_ratings
            # add one to current count
            current_idea_update.total_ratings = current_count + 1

    # CALCULATE AND INSERT AVERAGE
    # query for appropriate idea row
    for average_counter in model.session.query(model.Idea).filter_by(id=idea):
        if average_counter.average_rating == None:
            current_average = model.session.query(model.Idea).get(idea)
            current_average.average_rating = form.rating.data
        else: 
            current_average_update = model.session.query(model.Idea).get(idea)
            average_base = current_average_update.average_rating
            total_count = current_average_update.total_ratings
            current_average_update.average_rating = (form.rating.data + average_base) / total_count
         
        model.session.commit()

    # project_rate = str(id)

    # idea_rate = str(idea)

    # input_rate = str(form.rating.data)

    # return redirect("/my_project/" + new_rating + "/all_ideas")
    # return redirect("/my_project/" + project_rate + "/rate_idea/" + idea_rate + "/rate_info_input/" + input_rate)

    return redirect("/mypage")

@app.route("/my_project/<int:id>/idea/<int:idea>")
def idea(id, idea):

    selected_idea = []

    # Query for idea in idea table to receive idea name, creator and ratings
    for selection in model.session.query(model.Idea).filter_by(id=idea):
        selected_idea.append(selection)

    all_ratings = []

    # Query for idea in idea table to receive idea name, creator and ratings
    for rating_info in model.session.query(model.Rating).filter_by(idea_id=idea):
        all_ratings.append(rating_info)

    return render_template("/idea.html", selected_idea = selected_idea, all_ratings = all_ratings)

@app.route("/about", methods=['GET'])
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug = True)