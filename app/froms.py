from flask.ext.wtf import Form
from wtforms import TextField

class TableForm(Form):
	rows = []
	
	def new_row(self, vals):
		self.rows.append([])
		for v in vals:
			self.rows[-1].append(TextField(v))
		return self.rows[-1]
		
class AuthForm(Form):
	name = TextField("name")
	pswd = TextField("pswd")