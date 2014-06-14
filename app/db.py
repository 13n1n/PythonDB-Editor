import sqlite3 as lite
import multiprocessing as mp
from collections import namedtuple

def namedtuple_factory(cursor, row):
	fields = [col[0] for col in cursor.description]
	Row = namedtuple("Row", fields)
	return Row(*row)

class DB(lite.Connection):
	__doc__ = """
		Here is many bugs and security issues.
		So this database's wrapper implementation
		should not use in enterprise or production =)
		"""

	def __init__(self, path, logger=None):
		lite.Connection.__init__(self, path, check_same_thread=False)
		self.logger = logger
		self.row_factory = namedtuple_factory
		
	## have to rewrote it
	def titles(self, name):
		t, self.row_factory = self.row_factory, lite.Row
		c = self.cursor()
		c.execute('select * from %s' % name)
		r = c.fetchone()
		d = c.description
		self.row_factory = t
		return [ d[i][0] for i in xrange(0, len(d)) ]
	
	def __getitem__(self, name):
		cur = self.cursor()
		cur.execute("SELECT * FROM %s" % name)
		values = cur.fetchall()
		titles = self.titles(name)
		values.insert(0, titles)
		return values
	
	def select(self, name, where="1"):
		cur = self.cursor()
		cur.execute("SELECT * FROM %s WHERE %s" % (name, where))
		values = cur.fetchall()
		titles = self.titles(name)
		values.insert(0, titles)
		return values
		
	def full_update(self, name, values):
		with self:
			cur = self.cursor()
			cur.execute("DELETE FROM %s" % name)
			values = values[1:]
			for v in values:
				ins = "INSERT OR REPLACE INTO %s " % name
				vs  = ", ".join(map(lambda x: "'%s'" % str(x), v))
				cur.execute(ins + "VALUES(%s)" % vs)
	
	def update(self, name, expr, where="0"):
		with self:
			cur = self.cursor()
			cur.execute("UPDATE OR ROLLBACK %s SET %s WHERE %s" % (name, expr, where))
			
	def insert(self, name, values, on_collision="ROLLBACK"):
		with self:
			cur = self.cursor()
			values  = ", ".join(map(lambda x: "'%s'" % str(x), values))
			cur.execute("INSERT OR %s INTO %s VALUES (%s)" % (on_collision, name, values))

	def list_tables(self):
		c = self.cursor()
		c.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
		return map(lambda t: str(t[0]), c.fetchall())
		
if __name__ == "__main__":
	for table in DB("app/main.db").list_tables():
		print table