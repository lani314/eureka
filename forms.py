from flask.ext.wtf import Form
from wtforms import TextField, validators as v

class AddUserForm(Form):
	email = TextField("email", validators=[v.required()])
	username = TextField("username", validators=[v.required()])
	password = TextField("password", validators=[v.required()])

class LoginUserForm(Form):
	email = TextField("email", validators=[v.required()])
	username = TextField("username", validators=[v.required()])
	password = TextField("password", validators=[v.required()])

class AddProjectForm(Form):
	name = TextField("name", validators=[v.required()])
	password = TextField("password", validators=[v.required()])
	base_text = TextField("base_text", validators=[v.required()])
	keywords = TextField("keywords", validators=[v.required()])

class AddIdeaForm(Form):
	idea = TextField("idea", validators=[v.required()])

class RateIdeaForm(Form):
	rating = TextField("rating", validators=[v.required()])
	rating_notes = TextField("rating_notes", validators=[v.required()])

class JoinProjectForm(Form):
	project_id = TextField("project_id", validators=[v.required()])
	project_name = TextField("project_name", validators=[v.required()])
	project_password = TextField("project_password", validators=[v.required()])

class KeywordForm(Form):
	keyword = TextField("keyword", validators=[v.required()])