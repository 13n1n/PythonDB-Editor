#!/usr/bin/python

import pickle, os, sys, cgi, collections
from threading import Thread
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from db import *

import db

db = db.DB("main.db")

class GraphicKey:
	def __str__(self):
		return "<html><input type=button /></html>"
		
	@staticmethod
	def generate():
		return None

		
class User:
	permissions = dict()
	graphkey = None
	def __init__(self, name, pswd):
		self.name, self.pswd = name, pswd

	def __str__(self):
		return "%s:%s" % (self.name, self.pswd)

	def check_access(self, table_name):
		return permissions.get(table_name, "No")


class SuperUser(User):	#godlike access admin
	def __init__(self, pswd):
		User.__init__(self, "root", pswd)
		self.graphkey = GraphicKey.generate()
		
	def check_access(self, table_name):
		return "Full"


class SuperVisor(User):	#read-only access admin
	def __init__(self, pswd):
		User.__init__(self, "neo", pswd)
		self.graphkey = GraphicKey.generate()
		
	def check_access(self, table_name):
		return "Read"


class UserManager:
	def __init__(self, location):
		if os.path.isfile(location):
			self.file = open(location)
			self.users = pickle.load(self.file)
			self.file.close()
			self.file = open(location, "w")
		else:
			self.file = open(location, "a")
			root = raw_input("Superuser password: ")
			visor = raw_input("Supervisor password: ")
			self.users = [SuperUser(root), SuperVisor(visor)]

	def auth(self, name, pswd):
		print self.users
		for u in self.users:
			print u.name, "=", name, "|", u.pswd, "=", pswd
			if u.name == name and u.pswd == pswd:
				return u
		return None

	def dump(self):
		pickle.dump(self.users, self.file)

class Template:
	from quik import FileLoader
	html = FileLoader("html")

class Table(Template):
	curr = None

	def __init__(self, db, name):
		self.db = db
		self.name = name

	def __iter__(self):
		return self.db.fetch(self.name).__iter__()
	
	def names(self):
		return self.db.names(self.name)

	def __str__(self):
		print "RLY!?!?"
		return self.html.load_template("table.html").render({"author": "Deerenaros", "self": self}, loader=self.html).encode("utf-8")

	def update(self, handler, form):
		items = dict()
		for k in form.keys():
			items[k] = map(lambda x: x.value, form[k])
		self.db.update(map(lambda x: x[1], sorted(items.items())), self.name)


class Auth(Template):
	def __str__(self):
		return self.html.load_template("auth.html").render({"author": "Deerenaros"}, loader=self.html).encode("utf-8")
	def update(self, handler, form):
		user = handler.uman.auth(form[ "name" ].value, form[ "pswd" ].value)
		if user != None:
			handler.update_sess(Session(user, Main()))
		else:
			handler.update_sess(Session(None, Auth()))

		
class AccessDenied(Template):
	def __str__(self):
		return "<center style='color:red'>Access Denied!</center>"
		
class Main(Template):
	def __init__(self):
		pass

	def __str__(self):
		list = map(lambda el: "<a href='/%s'>%s</a>" % (el[0], el[0]), db.list())
		return "<br/>".join(list)

class Session:
	def __init__(self, user, current):
		self.user, self.current = user, current

class Handler(BaseHTTPRequestHandler):
	sessions = {}
	def send_page(self, string):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(string)

	def sess(self):
		return self.sessions.get(self.client_address[0], Session(None, Auth()))
	
	def update_sess(self, sess):
		self.sessions[self.client_address[0]] = sess

	def do_GET(self):
		path = self.path[1:]
		if path != "favicon.ico":
			if path == "":
				self.sess().current = Main()
				print "RLY!?!?!?!"
			elif self.sess().user != None:
				if self.sess().user.check_access(path) != "No":
					self.sess().current = db[path]
				else:
					self.sess().current = AccessDenied()
		self.send_page(self.sess().current)

	def form(self):
		return cgi.FieldStorage(fp=self.rfile,headers=self.headers,environ={'REQUEST_METHOD':'POST','CONTENT_TYPE':self.headers['Content-Type']})
	
	def do_POST(self):
		self.sess().current.update(self, self.form())
		self.send_page(self.sess().current)

	@classmethod
	def init(cls):
		cls.uman = UserManager("./users.pk")
		return cls

	@classmethod
	def down(cls):
		cls.uman.dump()

server = HTTPServer(("localhost",8080), Handler.init())
try:
	print "Server is started!"
	server.serve_forever()
except KeyboardInterrupt:
	print "Closing server..."
	Handler.down()
	sys.exit(0)