from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField
import wtforms

#print help(wtforms.TextAreaField)

	
class IdentificateForm(Form):
	name = TextField("name")
	pswd = TextField("pswd")
	rght = TextField("rght")