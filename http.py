#!/usr/bin/python

#секьюрити админ имеет доступ на чтение всего
#админ царь и бог

import pickle, os, sys, cgi
from threading import Thread
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class DB:
	from sqlite3 import connect

	def __init__(self, dbpath):
		self.con = self.connect(dbpath)

	def __getitem__(self, name):
		return self.get(name)

	def get(self, name):
		return Table(self, name)

	def fetch(self, name):
		c = self.con.cursor()
		c.execute("SELECT * FROM %s" % name)
		return c.fetchall()


class Table:
	curr = None

	def __init__(self, db, name):
		self.db = db
		self.name = name

	def __iter__(self):
		return self.db.fetch(self.name).__iter__()

	def __str__(self):
		res = "<table>"
		res += "<tr>This is table</tr>"
		for r in self:
			res += "<tr>" + "".join(map(lambda s: "<td>%s</td>" % s, r)) + "</tr>"
		return res + "</table>"


class User:
	def __init__(self, name, pswd):
		self.name, self.pswd = name, pswd

	def __str__(self):
		return "%s:%s" % (self.name, self.pswd)


class SuperUser(User):
	def __init__(self):
		pass


class UserManager:
	def __init__(self, location):
		if os.path.isfile(location):
			self.file = open(location)
			self.users = pickle.load(self.file)
			self.file.close()
			self.file = open(location, "w")
		else:
			self.file = open(location, "a")
			self.users = [User("root", "qwerty")]

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


class Auth(Template):
	def __str__(self):
		return self.html.load_template("auth.html").render({"author": "Deerenaros"}, loader=self.html).encode("utf-8")


class Greet(Template):
	def __init__(self, name):
		self.name = name

	def __str__(self):
		return "Hello, %s" % self.name


class Main:
	def __init__(self, path):
		self.db = DB(path)

	def __str__(self):
		return str(self.db["main"])


class Handler(BaseHTTPRequestHandler):
	def send_page(self, string):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(string)

	def do_GET(self):
		self.send_page(Auth())

	def do_POST(self):
		form = cgi.FieldStorage(
			fp = self.rfile,
			headers = self.headers,
			environ = { 'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type'] }
		)
		user = self.uman.auth(form[ "name" ].value, form[ "pswd" ].value)
		if user != None:
			self.send_page(Main("main.db"))
		else:
			self.send_page(Auth())

	@classmethod
	def init(cls):
		cls.uman = UserManager("./users.pk")
		return cls

	@classmethod
	def down(cls):
		cls.uman.dump()

if __name__ == "__main__":
	server = HTTPServer(("localhost",8080), Handler.init())
	try:
		print "Server is started!"
		server.serve_forever()
	except KeyboardInterrupt:
		print "Closing server..."
		Handler.down ()
		sys.exit(0)