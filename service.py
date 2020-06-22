#!/usr/bin/env python3
from urllib.parse import parse_qs
from lib.oauth import verification
from lib.database import helper as dbhelper
from lib.region import regiocodehelper

import cherrypy, os, importlib

oauthProviders = {}
APIconf = {}

class mentor(verification):
	def __init__(self, secretserverkey):
		self.secretserverkey = secretserverkey
		self.resourceOwners = {}
	
	@cherrypy.expose
	def login(self, loginProvider):
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
			usertoken = str(plugin.providerName()) + "_" + str(plugin.getUserIdentifier(oauthSession, config)) + " " + str("/".join(self.createExpireTime()))
			usertoken_hash = self.generateToken(usertoken)
			cookie = usertoken + "|" + usertoken_hash
			
			cherrypy.response.cookie["sessionId"] = cookie # http://localhost:9090
			cherrypy.response.cookie["sessionId"]["Path"] = "/"
			self.__redirect("redirectToAfterLogin")
	
	def __removeCookie(self, name):
		if name in cherrypy.request.cookie:
			cherrypy.response.cookie[name] = cherrypy.request.cookie[name]
			cherrypy.response.cookie[name]["expires"] = 0
	
	def __redirect(self, name):
		if name in cherrypy.request.cookie:
			cherrypy.response.status = "303"
			cherrypy.response.headers["Location"] = cherrypy.request.cookie[name]
			self.__removeCookie(name)
		elif name in APIconf:
			cherrypy.response.status = "303"
			cherrypy.response.headers["Location"] = APIconf[name]
	
	@cherrypy.expose
	def logout(self):
		if self.isAuthorized(cherrypy.request.cookie["sessionId"].value):
			self.__removeCookie("sessionId")
			self.__redirect("redirectToAfterLogout")
			return "logged out"
		else:
			return "not logged in"
	
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
	sfile = open("mentorapi.yml", "r")
	filebuffer = sfile.read()
	sfile.close()
	for entry in filebuffer.split("\n"):
		if entry.find(":") > -1:
			key, value = entry.split(":", 1)
			APIconf[key] = value
	
	print("Starting cherrypy server...")
	cherrypy.quickstart(mentor(secretserverkey), "/", "mentorserver.cfg")
if __name__ == "__main__":
	main() 
