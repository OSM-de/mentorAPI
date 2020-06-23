#!/usr/bin/env python3
import psycopg2
_dbconnstr = "dbname=mentorapi"
class helper():
	def __toJSON(self, table, columns, curs):
		data = {}
		for row in table:
			col = {}
			ident = ""
			for i in range(0, len(columns)):
				if columns[i] == "identifier":
					ident = row[i]
				col[columns[i]] = row[i]
			data[ident] = col
		return data
	def __init__(self):
		self.conn = psycopg2.connect(_dbconnstr)
		self.lock = False
		self.canShutdown = True
		self.queries = {}
		self.queries["createprofile"] = ("insert into profiles values (%s,Null,Null,Null,Null,Null,Null,Null,Null);", [])
		self.queries["removeprofile"] = ("delete from profiles where id=%s;", [])
		self.queries["update_textdirection"] = ("update profiles set textdirection=%s where id=%s;", [])
		self.queries["update_location"] = ("update profiles set location=%s where id=%s;", [])
		self.queries["update_displayname"] = ("update profiles set displayname=%s where id=%s;", [])
		self.queries["update_language"] = ("update profiles set language=%s where id=%s;", [])
		self.queries["update_contact"] = ("update profiles set contact=%s where id=%s;", [])
		self.queries["update_keywords"] = ("update profiles set keywords=%s where id=%s;", [])
		self.queries["update_about"] = ("update profiles set about=%s where id=%s;", [])
		self.queries["update_available"] = ("update profiles set displayname=%s where id=%s;", [])
		return self
	def queryHelper(self, name, params):
		query, columns = self.queries[name]
		if len(columns) > 0:
			return self.sendToPostgres((query, columns), params)
		else:
			return self.sendToPostgres((query, columns), params, noresult=True)
	def sendToPostgres(self, query, params=(), noresult=False, limit=20):
		if self.lock == False:
			query, columns = query
			output = {}
			self.canShutdown = False
			
			with self.conn:
				with conn.cursor() as cursor:
					cursor.execute(query, params)
					cursor.commit()
					if noresult == False:
						output = self.__toJSON(cursor.fetchmany(limit), columns)
			
			self.canShutdown = True
			return output
			
		else:
			return "error - shutting down"
	def tearDown(self):
		self.lock = True
		while self.canShutdown == False:
			pass
		self.conn = close()
