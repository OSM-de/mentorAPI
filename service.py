#!/usr/bin/env python3
from urllib.parse import parse_qs
from lib.oauth import verification
from lib.database import helper as dbhelper
from lib.region import regiocodehelper
from lib.config import readConfig

import cherrypy, os, importlib, copy

oauthProviders = {}
APIconf = {}

class mentor(verification):
	def __init__(self, secretserverkey):
		self.secretserverkey = secretserverkey
		self.dbapi = dbhelper(APIconf)
		self.regiocodehelper = regiocodehelper()
	
	@cherrypy.expose
	def login(self, loginProvider):
		self.__crossOrigin()
		if loginProvider in oauthProviders:
			if "sessionId" in cherrypy.request.cookie:
				self.logout()
			plugin = oauthProviders[loginProvider]["plugin"]
			config = oauthProviders[loginProvider]["config"]
			key = self.oauthLogin(plugin.getOAuthInstance(), config["requestTokenURL"], config["customerKey"], config["customerSecret"])
			return config["loginPage"] + "?oauth_token=" + str(key)
	
	@cherrypy.expose
	def callback(self, callbackProvider, oauth_token, oauth_verifier=""):
		if callbackProvider in oauthProviders:
			plugin = oauthProviders[callbackProvider]["plugin"]
			config = oauthProviders[callbackProvider]["config"]
			oauthSession = self.oauthCallback(plugin.getOAuthInstance(), config["accessTokenURL"], config["customerKey"], config["customerSecret"], oauth_token, oauth_verifier)
			
			#receive user identifier (provider dependent), provider name (provider dependent), generate user token and set it as cookie
			usertoken = str(plugin.providerName()) + "_" + str(plugin.getUserIdentifier(oauthSession, config)) + "|" + str("/".join(self.createExpireTime()))
			usertoken_hash = self.generateToken(usertoken)
			cookie = usertoken + "|" + usertoken_hash
			
			cherrypy.response.headers["Set-Cookie"] = "sessionId=" + cookie + "; Max-Age=" + str(60*60) + "; Path=/; HttpOnly"
			"""cherrypy.response.cookie["sessionId"] = cookie # http://localhost:9090
			cherrypy.response.cookie["sessionId"]["Path"] = "/"
			cherrypy.response.cookie["sessionId"]["HttpOnly"] = True
			cherrypy.response.cookie["sessionId"]["expires"] = 60*60*1000
			cherrypy.response.cookie["sessionId"]["sameSite"] = "Lax"""
			
			self.__redirect("redirectToAfterLogin")
	
	def __removeCookie(self, name):
		if name in cherrypy.request.cookie:
			cherrypy.response.cookie[name] = cherrypy.request.cookie[name]
			cherrypy.response.cookie[name]["expires"] = 0
			cherrypy.response.cookie[name]["Max-Age"] = 0
	
	def __redirect(self, name):
		if name in cherrypy.request.cookie:
			cherrypy.response.status = "303"
			cherrypy.response.headers["Location"] = cherrypy.request.cookie[name]
			self.__removeCookie(name)
		elif name in APIconf:
			cherrypy.response.status = "303"
			cherrypy.response.headers["Location"] = APIconf[name]
	
	def __crossOrigin(self):
		if "Origin" in cherrypy.request.headers:
			cherrypy.response.headers["Access-Control-Allow-Origin"] = cherrypy.request.headers["Origin"]
		elif "Host" in cherrypy.request.headers:
			cherrypy.response.headers["Access-Control-Allow-Origin"] = cherrypy.request.headers["Host"]
	
	@cherrypy.expose
	def logout(self):
		self.__crossOrigin()
		if "sessionId" in cherrypy.request.cookie and self.isAuthorized(cherrypy.request.cookie["sessionId"].value):
			self.__removeCookie("sessionId");
			self.__redirect("redirectToAfterLogout");
			return "logged out"
		else:
			return "not logged in"
	
	@cherrypy.expose
	def profileExists(self):
		self.__crossOrigin()
		if "sessionId" in cherrypy.request.cookie and self.isAuthorized(cherrypy.request.cookie["sessionId"].value):
			userid = cherrypy.request.cookie["sessionId"].value.split("|")[0]
			if self.dbapi.userExists(userid, "profiles") and self.dbapi.userExists(userid, "contact"):
				return "true"
			return "false"
		return "not logged in"
	
	@cherrypy.expose
	def createprofile(self):
		self.__crossOrigin()
		if "sessionId" in cherrypy.request.cookie and self.isAuthorized(cherrypy.request.cookie["sessionId"].value):
			userid = cherrypy.request.cookie["sessionId"].value.split("|")[0]
			if not self.dbapi.userExists(userid, "profiles"):
				self.dbapi.sendToPostgres(APIconf["createprofile"], (userid,))
			if not self.dbapi.userExists(userid, "contact"):
				self.dbapi.sendToPostgres(APIconf["createcontact"], (userid,))
			return "OK"
		return "not logged in"
	
	@cherrypy.expose
	def removeprofile(self):
		self.__crossOrigin()
		if "sessionId" in cherrypy.request.cookie and self.isAuthorized(cherrypy.request.cookie["sessionId"].value):
			userid = cherrypy.request.cookie["sessionId"].value.split("|")[0]
			if self.dbapi.userExists(userid, "profiles"):
				self.dbapi.sendToPostgres(APIconf["removeprofile"], (userid,))
			if self.dbapi.userExists(userid, "contact"):
				self.dbapi.sendToPostgres(APIconf["removecontact"], (userid,))
			return "OK"
		return "not logged in"
	
	@cherrypy.expose
	@cherrypy.tools.json_in()
	def changeprofile(self):
		self.__crossOrigin()
		if "sessionId" in cherrypy.request.cookie and self.isAuthorized(cherrypy.request.cookie["sessionId"].value):
			userid = cherrypy.request.cookie["sessionId"].value.split("|")[0]
			args = cherrypy.request.json
			query = []
			if not self.dbapi.userExists(userid, "profiles"):
				return "profile not existing"
			if "id" in args:
				return "'id' not allowed"
			if "location" in args and args["location"].find(",") > -1 and not args["location"] == "":
				args["location"], settings = self.regiocodehelper.resolve(args["location"].split(","))
				args["location"] = ",".join(args["location"])
			for item in args:
				name = "update_" + item
				query.append(self.dbapi.modifyUser(userid, name, args[item]))
			self.dbapi.sendToPostgres("\n".join(query))
			return "OK"
		return "not logged in"
	
	@cherrypy.expose
	@cherrypy.tools.json_out()
	def showprofile(self):
		self.__crossOrigin()
		if "sessionId" in cherrypy.request.cookie and self.isAuthorized(cherrypy.request.cookie["sessionId"].value):
			userid = cherrypy.request.cookie["sessionId"].value.split("|")[0]
			return self.dbapi.sendToPostgres(APIconf["showprofile"], (userid,))
		return {"error": "not logged in"}
	
	@cherrypy.expose
	def contactmethods(self):
		self.__crossOrigin()
		return ",".join(self.dbapi.tableSchema("contact"))
	
	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	def searchpeople(self):
		self.__crossOrigin()
		if "sessionId" in cherrypy.request.cookie and self.isAuthorized(cherrypy.request.cookie["sessionId"].value):
			output = {}
			args = cherrypy.request.json
			if not "location" in args:
				return {"error": "'location' requirred"}
			
			defaults = {"available": "true"}
			params = copy.deepcopy(args)
			params["location"], settings = self.regiocodehelper.resolve(args["location"].split(","))
			output["region_resolved"] = ",".join(params["location"])
			params["location"] = ",".join(params["location"]) + "%"
			
			for item in params:
				defaults[item] = params[item]
			
			query = self.dbapi.searchpeople(defaults)
			output["resultset"] = self.dbapi.sendToPostgres(query)
			output["request_params"] = args
			output["resolve_settings"] = settings
			
			return output
		else:
			return {"error": "not logged in"}
	
	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	def autocompleteRegion(self):
		self.__crossOrigin()
		searchresult = {}
		if not "json" in dir(cherrypy.request):
			return 0
		regiocodes = cherrypy.request.json
		
		for search in regiocodes:
			searchresult[search] = self.regiocodehelper.search(regiocodes[search], search)
		
		return searchresult
	
	def _cp_dispatch(self, vpath):
		if vpath[0] == "login":
			vpath.pop(0)
			cherrypy.request.params["loginProvider"] = vpath.pop(0)
			return self
		if vpath[0] == "callback":
			vpath.pop(0)
			cherrypy.request.params["callbackProvider"] = vpath.pop(0)
			cherrypy.request.params["oauthToken"] = vpath.pop(0)
			cherrypy.request.params["oauthVerifier"] = vpath.pop(0)
			return self
		
def main():
	global APIconf
	print("Generating secret server key just this instance knows...")
	secretserverkey = os.urandom(16)
	
	print("Loading oauth provider plugins...")
	for content in os.listdir("oauthproviders"):
		if os.path.isdir(os.path.join("oauthproviders", content)):
			print("  - " + content)
			oauthProviders[content] = {}
			oauthProviders[content]["plugin"] = importlib.import_module("oauthproviders." + content).provider()
			sfile = open(os.path.join("oauthproviders", content, "config.yml"), "r")
			filebuffer = sfile.read()
			sfile.close()
			config = {}
			for entry in filebuffer.split("\n"):
				if entry.find(":") > -1:
					key, value = entry.split(":", 1)
					config[key.strip()] = str(value.strip())
			oauthProviders[content]["config"] = config
	
	print("Loading mentorAPI configuration...")
	APIconf = readConfig(os.path.join(os.getcwd(), "mentorapi.yml")).config
	
	print("Starting cherrypy server...")
	cherrypy.quickstart(mentor(secretserverkey), "/", "mentorserver.cfg")
if __name__ == "__main__":
	main() 
