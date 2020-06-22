#!/usr/bin/env python3
# code untested
import os, copy
import json as jsonLib

class regiocode():
	def __loadJSON(self, fb):
		return jsonLib.loads(fb, ensure_ascii=False)
	
	def normalize(self, regiocode)
		# normalize region code by converting to an array stripping the whitespaces at both start and end
		codeArray = regiocode.split(",")
		for code, i in enumerate(codeArray):
			codeArray[i] = code.strip()
		
		# normalize region code by deleting duplicates where their original one is a neighbour
		"""
		x,x,y --> x,y
		x,y,y --> x,y
		x,x,y,y --> x,y
		x,y,z,y --> x,y,z,y (stays the same)
		x,y,z,x --> x,y,z,x (stays the same)
		"""
		delIndex = []
		for code, i in enumerate(codeArray):
			if 0 >= i:
				continue
			oi = i-1
			if codeArray[oi] == codeArray[i]:
				delIndex.append(i)
		for i in delIndex:
			del codeArray[i]
			for u in delIndex:
				delIndex[i] -= 1
		
		return codeArray
		
	def getRegioDatabase(self, dbname):
		database = {}
		
		# get the index database itself
		if not "indexDB" in dir(self):
			sfile = open(os.path.join("regions", "index.json"), "r")
			self.indexDB = self.__loadJSON(sfile.read())
			sfile.close()
		if os.path.exists(os.path.join("regions", dbname + ".json")):
			self.indexDB[dbname] = dbname # add entry so it refers to itself
		if not dbname in self.indexDB:
			return "error 101 - no database resolve for {}".format(dbname)
		
		# get the local database
		dbname = self.indexDB[dbname] # resolve the local database name
		if "regiodbs" in dir(self):
			database = self.regiodbs[dbname]
		else:
			sfile = open(os.path.join("regions", dbname + ".json"), "r")
			database = self.__loadJSON(sfile.read())
			sfile.close()
		
		return dbname, database
	def ßßredirect(self, key, value, settings):
		if "redirectFrom" in settings and value == settings["redirectFrom"]:
			return "error 103 - no loop redirects from {} to {} and backwards".format(value, settings["redirectFrom"])
		settings["redirectFrom"] = key
		return value, settings # redirect to 'value' e.g. {"__redirect": "sh"} --> redirecting from 'address' to value 'sh'

	def resolveStorage(self, addresspiece, storage, resolved, settings):
		data = copy.deepcopy(storage)
		for key in resolved: # skipping resolve process of already resolved address pieces by switching to them directly in order
			data = data[key]
		
		if addresspiece in data: # check if the address piece exists in the local database
			data = data[addresspiece] # switch to it directly
			if type(data) is dict and len(data) > 0: # check if dictionary and has content
				for tag in data:
					if tag.startswith("@") and tag in dir(self): # checks wethever the key of the dictionary is a directive starting with '__'
						addresspiece, settings = self.__getattribute__(tag.replace("__", "ßß", 1))(addresspiece, data[tag], settings) # start the directive code and return the resolved 'addresspiece'. E.g.: 'hamburg' becomes 'hh'
			# else:
				# 'addresspiece' is already the correct one, so no need to resolve it
			return addresspiece, settings
		else:
			return "error 101 - no database resolve for {}".format(",".join(resolved) + "," + addresspiece), settings # print error because no entry of 'addresspiece' found
	
	def resolve(self, regiocode):
		resolvedregiocode = []
		
		regiocode = self.normalize(regiocode)
		countrycode, storage = self.getRegioDatabase(regiocode[0])
		del regiocode[0] # country name, do not needed in its local database
		
		settings = {}
		
		for key in regiocode:
			key, settings = self.resolveStorage(key, storage, resolvedregiocode, settings) # comply with rules and resolve intelligently
			if entry.startswith("error"):
				return entry
			resolvedregiocode.append(key) # add the resolved 'addresspiece' (here: 'key') to the list of resolved regiocodes so they won't be resolved again resulting in a never-ending execution loop
		return [countrycode] + resolvedregiocode, settings # return the resolved address
					
	
class regiocodehelper(regiocode):
	def resolveToResult(self, regiocode):
		"""
		It is a wrapper around the underlying resolve() method from class 'regiocode' from which the class is method is inside abstracts. Instead of the underlying method it calls, it only returns the resolved result itself and not the settings the underlying algorithm used for resolving.
		
		Parameters: regiocode (list of individual pieces which are together the regiocode)
		Returns: resolvedregiocode (list of resolved individual pieces which are together the regiocode)
		Example: resolveToResult(["germany", "schleswig-holstein", "henstedt-ulzburg"]) -->  ["de", "sh", "hu"]
		"""
		result, settings = self.resolve(regiocode)
		return result
	
	def exists(self, regiocode):
		"""
		checks if the 'regiocode' expressed as a python list of strings exists or not. It supports resolving e.g. `hamburg` to `hh` by using the underlying resolveToResult() method which calls the underlying resolve() method of the class `regiocode`.
		
		Parameters: regiocode (list of individual pieces which are together the regiocode)
		Returns: Boolean
		"""
		result = self.resolveToResult(regiocode)
		if type(result) is str:
			return False
		return True

	def extDiff(self, regiocode, resolvedregiocode, nosame=True):
		"""
		Compares two regiocode lists without resolving them and shows the difference. Ideally you compare the unresolved version with the resolved version to see how many were resolved.
		
		Parameters: regiocode (list of individual pieces which are together the regiocode), resolvedregiocode (list of individual resolved pieces which are together the regiocode), nosame=True (optional; if 'False' then it shows also the ones in the diff which are equal (were not resolved because not needed); default value: True)
		Returns: a python dictionary in the format {"<piece 1 of regiocode>": "<piece 1 of resolvedregiocode>", "<piece 2 of regiocode>": "<piece 2 of resolvedregiocode>", ...}
		Example: extDiff(["germany", "schleswig-holstein", "henstedt-ulzburg"], ["de", "sh", "hu"]) --> {"germany": "de", "schleswig-holstein": "sh", "henstedt-ulzburg": "hu"}
		"""
		for i, original in enumerate(regiocode):
			resolved = resolvedregiocode[i]
			if resolved == original and nosame == False:
				output[original] = original
			else:
				output[original] = resolved
		return output
	
	def diff(self, regiocode, nosame=True):
		"""
		Resolves 'regiocode', compares the old and new version and show the difference.
		diff(["germany", "schleswig-holstein", "henstedt-ulzburg"]) is equal to extDiff(["germany", "schleswig-holstein", "henstedt-ulzburg"], ["de", "sh", "hu"]). It calls the underlying extDiff() method and supplies the resolved version of 'regiocode'- and the 'nosame' parameter to it. It also calls the underlying resolveToResult() method which calls the underlying resolve() method of the class `regiocode` to resolve 'regiocode'.
		
		Parameters: regiocode (list of individual pieces which are together the regiocode), nosame=True (optional; if 'False' then it shows also the ones in the diff which are equal (were not resolved because not needed); default value: True)
		Returns: a python dictionary in the format {"<piece 1 of regiocode>": "<piece 1 of resolvedregiocode>", "<piece 2 of regiocode>": "<piece 2 of resolvedregiocode>", ...} or an error message as string from the underlying resolve algorithm
		Example: Diff(["germany", "schleswig-holstein", "henstedt-ulzburg"]) --> {"germany": "de", "schleswig-holstein": "sh", "henstedt-ulzburg": "hu"}
		"""
		result = self.resolveToResult(regiocode)
		if type(result) is str:
			return result
		return self.extDiff(regiocode, result, nosame)
	
	def search(self, regiocode, searchinput):
		"""
		Resolves 'regiocode' by calling the underlying resolveToResult() method, searches for 'searchinput' and returns a list of all matches found by python's builtin str.find() method.
		
		Parameters: regiocode (list of individual pieces which are together the regiocode to search in), searchinput (the piece of region name to search in the storage for 'regiocode' (only lower letters))
		Returns: A list of all matches found by python's builtin str.find() method.
		Example: search(["germany", "schleswig-holstein", "henstedt-ulzburg"], "ulz") --> ["ulzburg", "ulzburg-süd"]
		"""
		output = []
		resolved, settings = self.resolveToResult(regiocode)
		if type(resolved) is str:
			return resolved
		storage = self.getRegioDatabase(resolved[0])
		
		del resolved[0]
		
		for key in resolved:
			storage = storage[key]
			
		resultset = storage
		
		for key in resultset:
			if key.find(searchinput):
				output.append(key)
		return output
	
