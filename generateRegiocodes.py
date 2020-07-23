#!/usr/bin/env python3
import os, sys, json, copy
communityindexDir = "communityindex"
regionIndexFile = os.path.join("regions", "index.json")
combineGeojson = {}
regionIndex = {}
regiocodes = {}

def loadRegiocodes(code):
	global communityIndexFile
	
	filebuffer = ""
	file = os.path.join(os.path.dirname(communityIndexFile), code + ".json")
	
	if os.path.exists(file):
		sfile = open(os.path.join(file, "r")
		filebuffer = sfile.read()
		sfile.close()
	regiocodes[code] = filebuffer

def saveRegiocodes():
	global regiocodes
	
	sfile = open(os.path.join(os.path.dirname(communityIndexFile), code + ".json"), "w")
	sfile.write(json.dumps(regioncodes, indent=4))
	sfile.close()

def checkExistenceInRegion(regiocode):
	if not regiocode in regiocodes:
		regiocodes[regiocode] = {}

def checkExistenceInRegioIndex(key, value=""):
	global regionIndex
	if key in regionIndex:
		if regionIndex[key] == "":
			regionIndex[key] = value
	else:
		regionIndex[key] = ""

def generate(fromFile, curDir):
	global combineGeojson, regiocodes
	
	country = os.path.basename(curDir)
	filename = os.path.basename(fromFile).split(".", 1)[0]
	countrycode, region = filename.split("-", 1)
	region = region.replace("-", " ")
	
	if not countrycode in regiocodes and len(regiocodes) == 1:
		saveRegiocodes()
	
	checkExistenceInRegioIndex(country, countrycode)

	sfile = open(fromFile)
	geojson = json.loads(sfile.read())
	sfile.close()
	
	combineGeojson[countrycode + "," + region] = geojson["geometry"]["coordinates"]
	if not countrycode in regiocodes:
		loadRegiocodes(countrycode)
	
	checkExistenceInRegion(region)
	
	
def crawl(curdir): # recursive programming
	global regionIndex
	
	for content in os.listdir(curdir):
		if os.path.isdir(os.path.join(curdir, content)):
			checkExistenceInRegioIndex(content)
			crawl(curdir)
		elif os.path.isfile(os.path.join(curdir, content)):
			generate(os.path.join(curdir, content), curdir)

def init():
	global communityindexDir, regionIndexFile, regionIndex
	
	args = sys.argv
	del args[0];
	
	for i in args:
		if i.find("=") > -1:
			key, value = i.split("=", 1)
			if key == "communityindex":
				communityindexDir = value
	
	sfile = open(regionIndexFile, "r")
	regionIndex = json.loads(sfile.read())
	sfile.close()
	
	crawl(communityindexDir)
	
	sfile = open(os.path.join(os.path.dirname(regionIndexFile), "georeferences.json"), "w")
	sfile.write(json.dumps(combineGeojson, indent=4))
	sfile.close()
	
	sfile = open(regionIndexFile, "w")
	sfile.write(json.dumps(regionIndex, indent=4))
	sfile.close()

if __name__ == "__main__":
	init()
