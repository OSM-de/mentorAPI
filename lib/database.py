#!/usr/bin/env python3
from psycopg2 import sql
import psycopg2
class helper():
	def __init__(self, conf):
		self.conf = conf
		self.conn = psycopg2.connect(conf["dbconnstr"])
		self.lock = False
		self.canShutdown = True
	
	def __toJSON(self, table, columns, curs):
		data = {}
		for row in table:
			col = {}
			ident = ""
			for i in range(0, len(columns)):
				if columns[i] == "id":
					ident = row[i]
				col[columns[i]] = row[i]
			data[ident] = col
		return data
	
	def modifyUser(self, userid, name, param):
		if name in query:
			query = self.conf[name]
			return sql.SQL(query).format(param, userid)
		else:
			return ""
	def removeUser(self, userid):
		query = []
		for name in ["removeprofile", "removecontact"]
			query = self.conf[name]
			query.append(sql.SQL(query).format(userid))
		return query
	def createUser(self, userid):
		query = []
		for name in ["createprofile", "createcontact"]
			query = self.conf[name]
			query.append(sql.SQL(query).format(userid))
	def searchpeople(self, filters):
		searchQuery = self.conf["search"]
		filterQuery = []
		
		for fltr in filters:
			if "search_" + fltr in self.conf and not fltr == "id":
				value = filters[fltr]
				if type(value) is list:
					for v in value:
						filterQuery.append((self.conf["search_" + fltr], v))
				else:
					filterQuery.append((self.conf["search_" + fltr], value))
		
		query = []
		cur = self.conn.cursor()
		for q in filterQuery:
			q, arg = filterQuery[q]
			query.append(cur.mogrify(q, (arg,)))
		return searchQuery + " " + "AND".join(query)
	
	def sendToPostgres(self, query, params=(), limit=20):
		if self.lock == False:
			output = {}
			self.canShutdown = False
			
			with self.conn:
				with self.conn.cursor() as cursor:
					cursor.execute(query, params)
					if not cursor.description == None:
						columns = []
						for col in cursor.description:
							cols.append(col.name)
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
