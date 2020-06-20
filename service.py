#!/usr/bin/env python3
from urllib.parse import parse_qs
import cherrypy, psycopg2, os, importlib, requests, time, hmac
oauthProviders = {}
APIconf = {}
class utils():
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
class verification():
	def isAuthorized(self, token):
		if type(token) is bytes:
			token = token.decode("utf-8")
		clientToken, clientHash = token.split("|")
		timestamp = clientToken.split(" ")[1]
		if hmac.compare_digest(self.generateToken(clientToken), clientHash):
			if time.strptime(timestamp, "%Y/%m/%d/%H/%M") >= time.localtime():
				return True
		return False
	def generateToken(self, msg):
		return hmac.new(self.secretserverkey, bytes(msg, "utf-8"), "sha3_224").hexdigest()
	def getCurTime(self):
		curTime = time.localtime()
		curTime = time.strftime("%Y/%m/%d/%H/%M", curTime).split("/")
		return [int(curTime[0]), int(curTime[1]), int(curTime[2]), int(curTime[3]), int(curTime[4])]
	def createExpireTime(self):
		curTime = self.getCurTime()
		curTime[3] += 1
		for i in range(0, len(curTime)):
			curTime[i] = str(curTime[i])
		return curTime
	def oauthCallback(self, OAuth, accessTokenURL, client_key, client_secret, oauthToken, oauthVerifier):
		if oauthVerifier == "":
			oauthSession = OAuth(client_key, client_secret=client_secret, resource_owner_key=oauthToken, resource_owner_secret=self.resourceOwners[oauthToken], signature_type="auth_header") #3
		else:
			oauthSession = OAuth(client_key, client_secret=client_secret, resource_owner_key=oauthToken, verifier=oauthVerifier, resource_owner_secret=self.resourceOwners[oauthToken], signature_type="auth_header") #3
		r = requests.post(url=accessTokenURL, auth=oauthSession)
		creds = parse_qs(r.text)
		access_key = creds.get("oauth_token")
		access_secret = creds.get("oauth_token_secret")
		
		return OAuth(client_key, client_secret=client_secret, resource_owner_key=access_key[0], resource_owner_secret=access_secret[0], signature_type="auth_header")
	
	def oauthLogin(self, OAuth, requestTokenURL, client_key, client_secret): #0
		oauthSession = OAuth(client_key, client_secret=client_secret, signature_type="auth_header") #1
		r = requests.post(url=requestTokenURL, auth=oauthSession)
		creds = parse_qs(r.text)
		user_key = creds.get("oauth_token")
		user_secret = creds.get("oauth_token_secret")
		self.resourceOwners[str(user_key[0])] = str(user_secret[0])
		
		return str(user_key[0])
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
