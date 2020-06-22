#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.getcwd())))
os.chdir(os.path.join(os.path.dirname(os.getcwd())))
from lib.region import regiocodehelper

helper = regiocodehelper()
testdata = [["germany", "schleswig-holstein", "henstedt-ulzburg", "goetzberg"], ["germany", "hamburg", "eppendorf"]]
print("resolving 'from' --> 'to' difference 'diff'")
for t in testdata:
	result = helper.resolveToResult(t)
	print(t, "-->", result, "difference", helper.diff(t))
	
print("\nshow search capabilities")
testdata = [(["germany", "schleswig-holstein", "henstedt-ulzburg"], "ulz"), (["germany", "hamburg"], "barmbek")]
for t in testdata:
	searchinto, searchinput = t
	print("search", searchinput, "in", searchinto, "-->", helper.search(searchinto, searchinput))
