#!/usr/bin/env python3
class helper():
	def _establishConnToDB(self, dbconnstr):
		#connect to database
		conn = psycopg2.connect(dbconnstr)
		cur = conn.cursor()
		return cur, conn
	
	def _closeConnToDB(self, cur, conn):
		#close connection to database
		cur.close()
		conn.close()
	
	def _sendToDB(self, query, dbconnstr):
		#connect to database, send query and fetch result, close connection (simple version)
		cur, conn = self._establishConnToDB(dbconnstr)
		cur.execute(query)
		conn.commit()
		print(query)
		try:
			result = cur.fetchall()
		except:
			result = None
		self._closeConnToDB(cur, conn)
		return result
