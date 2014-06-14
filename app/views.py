from flask import render_template as renderer, abort, redirect, request, jsonify
from app import app
from db import *
from bcrypt import hashpw, gensalt
from forms import *
from helpers import *
from json import loads
from functools import wraps

class NoUpdate:
	pass


db = DB("app/main.db")
fake = DB("app/fake.db")

gsalt = app.config["GLOBAL_SALT"]

SUPER_USER = "GOODLIKE"
SUPER_VISOR= "JUST BELIEVE THAT U SEE"


signed_dict = {
	SUPER_USER:  False,
	SUPER_VISOR: False,
	"":          True
}


"""admin = raw_input("Input superuser password:")
visor = raw_input("Input supervisor password:")
salts = gensalt(), gensalt()
db.insert("_users", ["root", hashpw(admin+gsalt, salts[1]), salts[1], "", "GOODLIKE", ""], "REPLACE")
db.insert("_users", ["neo",  hashpw(visor+gsalt, salts[1]), salts[1], "", "JUST BELIEVE THAT U SEE", ""], "REPLACE")"""

def first_use(func):
	@wraps(func)
	def use(*args, **kwargs):
		if len(db["_users"]) <= 1:
			return redirect("/set_up")
		return func(*args, **kwargs)
	return use


def signed(func):
	@wraps(func)
	def check(*args, **kwargs):
		ip = request.remote_addr
		select = db.select("_users", where="ip = '%s'" % ip)
		if len(select) > 1 and signed_dict[select[1].spec]:
			kwargs["rights"] = select[1].rights
			return func(*args, **kwargs)
		return redirect("/auth")
	return check


@app.route("/set_up")
def show_setup():
	pswds = gensalt(), gensalt()
	return renderer("set_up.html", pswds=pswds, len=1)


@app.route("/set_up/post", methods=["POST"])
def get_sets():
	for vals in request.form: data = loads(vals)
	FIRST_USE = False
	salts  = gensalt(), gensalt()
	pswds  = data["admin"]["pass"], data["security"]["pass"]
	gkeys = data["admin"]["gpass"], data["security"]["gpass"]
	db.insert("_users", ["root", hashpw(pswds[0]+gsalt, salts[1]), salts[1], "", "GOODLIKE", ""], "REPLACE")
	db.insert("_users", ["neo",  hashpw(pswds[1]+gsalt, salts[1]), salts[1], "", "JUST BELIEVE THAT U SEE", ""], "REPLACE")
	db.insert("_gkey", ["root", gkeys[0]], "REPLACE")
	db.insert("_gkey", ["neo",  gkeys[1]], "REPLACE")
	return jsonify({"data": "ok", "redirect": "/auth"})


@app.route("/auth", methods=["GET", "POST"])
@first_use
def auth():
	form = IdentificateForm()
	if form.validate_on_submit():
		name, pswd = form.name.data, form.pswd.data
		try:
			user = db.select("_users", where="name = '%s'" % name)[1]
			hash = hashpw(pswd+gsalt, user.salt)
			if hash == user.hash:
				db.update("_users", "ip = '%s'" % request.remote_addr, "name = '%s'" % name)
				return redirect(["/", "/graphic/%s" % name][user.spec != ""])
		except Exception, e:
			print e
	return renderer("auth.html", form=form)


@app.route("/graphic/<name>")
@first_use
def graphic(name):
	return renderer("graphkey.html", len=1)


@app.route("/graphic/<name>/auth", methods=["POST"])
@first_use
def graphic_auth(name):
	for vals in request.form: data = vals
	select = db.select("_gkey", where="name = '%s'" % name)[1]
	print select
	print loads(vals), loads(select.gkey)
	ins = [ [1, 0][v in select.gkey] for v in vals ]
	if sum(ins) == 0:
		signed_dict[[SUPER_USER, SUPER_VISOR][name == "neo"]] = True
		return jsonify({"data": "ok", "redirect": "/"});
	return jsonify({"data": "failed"});


@app.route("/new_user", methods=["GET", "POST"])
@signed
def new_user(rights=None):
	form = IdentificateForm()
	if form.validate_on_submit():
		name, pswd, rights, salt = form.name.data, form.pswd.data, form.rght.data, gensalt()
		db.insert("_users", [name, hashpw(pswd+gsalt, salt), salt, rights, "", ""], "ROLLBACK")
	return renderer("new_user.html", form=form)


@app.route("/logs")
@signed
def logs(rights=None):
	pass


@app.route("/")
@signed
def index(rights=None):
	return renderer("index.html",
		title="Fuck this challenge",
		tables=db.list_tables(),
		fake_table=fake.list_tables())


@app.route("/table/<table>")
@signed
def table(table, rights=None):
	return renderer("table.html",
		title="See this worst table",
		name=table)


@app.route("/json/<table>")
@signed
def send_json(table, rights=None):
	try:
		table = db[table]
	except Exception, e:
		raise e
		abort(404)
	return jsonify({"data":table})

@app.route("/json/<table>")
@signed
def send_fake(table, rights=None):
	try:
		table = fake[table]
	except Exception, e:
		raise e
		abort(404)
	return jsonify({"data":table})

@app.route("/json/<table>", methods=["POST"])
@signed
def recieve_json(table, rights=None):
	for vals in request.form: data = vals
	db.full_update(table, [[]] + loads(data)[:-1])
	return jsonify({"data": "ok"})
	
@app.route("/fake/<table>", methods=["POST"])
@signed
def recieve_fake(table, rights=None):
	for vals in request.form: data = vals
	fake.full_update(table, [[]] + loads(data)[:-1])
	return jsonify({"data": "ok"})