#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.getcwd())))
os.chdir(os.path.join(os.path.dirname(os.getcwd())))
from lib.config import readConfig
from lib.database import management

APIconf = {}
queries = {"profiles": "createtable", "contact": "createtable"}
cmds = {"createdb", """psql -c "CREATE DATABASE {};" """, "exeSQL": "psql --dbname={} --file={}"}
sqls = {"createtable": "CREATE TABLE {} ({})", "createview": "CREATE OR REPLACE VIEW public.userdetails AS (SELECT {} FROM profiles FULL JOIN contact on profiles.id=contact.id where profiles.available IS TRUE);"}

def main():
	global APIconf, queries, cmds
	
	print("loading mentorAPI configuration...")
	sfile = open("../mentorapi.yml", "r")
	APIconf = readConfig(sfile.read())
	sfile.close()
	
	print("connecting to the database with the following dbconnstr:")
	print("  ", APIconf["dbconnstr"])
	dbhelper = management(APIconf["dbconnstr"])
	if type(dbhelper) is str:
		print("\033[1;mDatabase does not exist\033[0;m")
		
		print("creating database '{}'...".format(APIconf["dbname"]))
		os.system(cmds["createdb"].format(APIconf["dbname"]))
		
		print("restarting...")
		return main()
	else:
		print("\033[1;mDatabase does exist\033[0;m")
	
	print("checking existence of requirred tables...")
	for i in queries:
		if dbhelper.tableExists(i):
			print("\033[0;32m  '{}' exists...\033[0;m".format(i))
		else:
			print("\033[0;31m  '{}' does not exist\033[0;m".format(i))
			if "table_" + i in APIconf:
				print("  creating table '{}'...".format(i))
				dbhelper.executeCMD(sqls[queries[i]].format(i, ",\n".join(APIconf["table_" + i])))
			else:
				print("\033[0;31mtable scheme not specified in mentorapi.yml!\033[0;m")
			
	print("syncing columns (insert/remove)...")
	for i in queries:
		if "table_" + i in APIconf:
			cols = APIconf["table_" + i]
			for n, content in enumerate(cols):
				colname, coltype = content.split(" ")
				cols[n] = (colname, coltype)
			dbhelper.alterTable(i, cols)
	
	print("generating select statement for the view creation query...")
	select = []
	select2 = []
	for i in queries:
		confname = "table_" + i
		if confname in APIconf:
			for content in APIconf[confname]:
				content = content.split(" ")
				if not content[0] in select2:
					select.append(i + "." + content[0])
					select2.append(content[0])
	
	print("inserting generated select statement and execute query...")
	dbhelper.executeCMD(sqls["createview"].format(", ".join(select)))
	
	print("disconnecting from database...")
	dbhelper.tearDown()
