#!/usr/bin/env python3
from psycopg2 import sql
import psycopg2
class helper():
	def __init__(self, dbconnstr):
		self.conn = psycopg2.connect(dbconnstr)
		self.lock = False
		self.canShutdown = True
		self.queries = {}
		self.queries["createprofile"] = ("insert into profiles values (%s,Null,Null,Null,Null,Null,Null,Null,Null);", [])
		self.queries["removeprofile"] = ("delete from profiles where id=%s;", [])
		self.queries["update_textdirection"] = ("update profiles set textdirection=%s where id=%s;", [])
		self.queries["update_location"] = ("update profiles set location=%s where id=%s;", [])
		self.queries["update_displayname"] = ("update profiles set displayname=%s where id=%s;", [])
		#self.queries["update_languages"] = ("update profiles set languages=%s where id=%s;", [])
		self.queries["update_contact"] = ("update contact set contact=%s where id=%s;", [])
		self.queries["update_keywords"] = ("update profiles set keywords=%s where id=%s;", [])
		self.queries["update_about"] = ("update profiles set about=%s where id=%s;", [])
		self.queries["update_available"] = ("update profiles set available=%s where id=%s;", [])
		self.queries["search"] = ("select * from userdetails where ", ["id", "textdirection", "location", "displayname", "languages", "contact", "keywords", "about", "available"])
		self.queries["search_location"] = ("location=%s", [])
		#self.queries["search_languages"] = ("%s ANY (languages)", [])
		self.queries["search_location"] = ("location LIKE %s%", [])
		self.queries["search_contact"] = ("contact ? %s", [])
		self.queries["search_keywords"] = ("%s ANY (keywords)", [])
		self.queries["search_available"] = ("available=%s", [])
	
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
	
	def queryHelper(self, name, params):
		query, columns = self.queries[name]
		if len(columns) > 0:
			return self.sendToPostgres((query, columns), params)
		else:
			return self.sendToPostgres((query, columns), params, noresult=True)

	def searchQueryHelper(self, filters):
		searchQuery, columns = self.queries["search"]
		filterQuery = []
		
		for fltr in filters:
			if fltr in columns and "search_" + fltr in self.queries and not fltr == "id":
				value = filters[fltr]
				if type(value) is list:
					for v in value:
						filterQuery.append((self.queries["search_" + fltr][0], v))
		
		query = []
		cur = self.conn.cursor()
		for q in filterQuery:
			q, arg = filterQuery[q]
			query.append(cur.mogrify(q, (arg,)))
		return self.sendToPostgres((searchQuery + "AND".join(query), columns))
	
	def sendToPostgres(self, query, params=(), noresult=False, limit=20):
		if self.lock == False:
			query, columns = query
			output = {}
			self.canShutdown = False
			
			with self.conn:
				with self.conn.cursor() as cursor:
					cursor.execute(query, params)
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
		self.conn.close()

class management():
	def __init__(self, dbconnstr):
		self.error = ""
		try:
			self.conn = psycopg2.connect(dbconnstr)
		except psycopg2.errors.OperationalError:
			self.error = "DOES NOT EXIST"

	def alterTable(self, name, desiredCols, beloud=True):
		query = []
		returnedCols = []
		desiredCols_simplified = []
		
		if not ("id", "text") in desiredCols:
			desiredCols = [("id", "text")] + desiredCols
		
		for i in desiredCols:
			desiredCols_simplified.append(i[0])
		
		with self.conn:
			with self.conn.cursor() as cursor:
				cursor.execute(sql.SQL("SELECT * FROM {} LIMIT 0").format(sql.Identifier(name)))
				for col in cursor.description:
					returnedCols.append(col.name)
		
		for n, i in enumerate(returnedCols):
			if i in returnedCols and not i in desiredCols_simplified:
				# remove from database table `name`
				if beloud:
					print("\033[1;31mwill remove\033[0;m {} from database table {}".format(i, name))
				query.append(sql.SQL("ALTER TABLE {} DROP COLUMN {}").format(sql.Identifier(name), sql.Identifier(i)))
		for n, i in enumerate(desiredCols):
			colname = i[0]
			if colname in desiredCols_simplified and not colname in returnedCols:
				# add to database table `name`
				if beloud:
					print("\033[1;32mwill add\033[0;m] {} to database table {}".format(i, name))
				query.append(sql.SQL("ALTER TABLE {} ADD {} {}").format(sql.Identifier(name), i, desiredCols[n][1]))
		
		if len(query) > 0:
			with self.conn:
				with self.conn.cursor() as cursor:
					print("executing query ('will' becomes 'do now')...")
					cursor.execute(";\n".join(query))
	
	def executeCMD(self, query, params=()):
		error = None
		with self.conn:
			with self.conn.cursor() as cursor:
				try:
					cursor.execute(query, params)
				except Exception as e:
					error = e
					cursor.rollback()
		return error
				
	def tableExists(self, name):
		exists = False
		with self.conn:
			with self.conn.cursor() as cursor:
				try:
					cursor.execute("SELECT * FROM " + name + " LIMIT 0")
					exists = True
				except psycopg2.errors.UndefinedTable:
					exists = False
		return exists
	
	def tearDown(self):
		self.conn.close()
