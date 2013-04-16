from flask import Flask, render_template, redirect, request, g, session
import model

app = Flask(__name__)
app.secret_key = 'discovery'

@app.before_request
def before_request():
	g.id = session.get('id')

@app.route("/")
def login():
	return render_template("login.html")

@app.route("/authenticate", methods=["POST"])
def authenticate():

    email = request.form['email']
    username = request.form['username']
    password = request.form['password']

    user = model.session.query(model.User).filter_by(email=email,
		username=username, password=password).first()

    if not user:
        return redirect("/")
    else:
        session['id'] = id
        return redirect("/mypage")

@app.route("/new_user")
def new_user():
	# return template of login form
	return render_template("new_user.html")

@app.route("/save_user", methods=["POST"])
def add_user():
	
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']	

    add_user = model.User()

    add_user.email = email

    add_user.username = username

    add_user.password = password

    model.session.add(add_user)
    model.session.commit()

    return redirect("/")

@app.route("/mypage", methods=['GET'])
def my_page():
    projects = model.session.query(model.Membership).\
        filter(model.Membership.project_id).\
        limit(30).all()
    # return render_template("mypage.html")
    return render_template("mypage.html", projects=projects)

@app.route("/new_project")
def new_user():
    return render_template("new_project.html")

@app.route("/save_project", methods=["POST"])
def add_user():
    
    name = request.form['name']
    password = request.form['password']
    base_text = request.form['base_text'] 

    print base_text

    add_project = model.Project()

    add_project.project_name = name

    add_project.project_password = password

    add_project.base_text = base_text

    model.session.add(add_project)
    model.session.commit()

    return redirect("/mypage")

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
