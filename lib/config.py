#!/usr/bin/env python3
class readConfig():
	def keyvaluepair(self, entries):
		if entries[1] == "" and len(self.lines) > self.index:
			self.triggers["  -"] = entries[0]
		else:
			key, value = entries
			self.config[key.strip()] = value.strip()
		
	def items(self, key, value):
		itemList = []
		if key in self.config:
			itemList = self.config[key]
		itemList.append(value.strip())
		self.config[key] = itemList
	
	def __init__(self, inp):
		"""
		not thread-safe
		"""
		self.config = {}
		self.triggers = {}
		
		self.lines = inp.split("\n")
		
		for index, line in enumerate(self.lines):
			self.index = index
			if line.find(":") > -1:
				self.keyvaluepair(line.split(":", 1))
			elif line.startswith("  -"):
				self.items(self.triggers["  -"], line.replace("  -", "", 1))
