#!/usr/bin/env python3
class readConfig():
	def keyvaluepair(self, entries):
		entries = line.split(":", 1)
		if len(entries) == 2:
			key, value = entries
			self.config[key.strip()] = value.strip()
		elif len(entries) == 1 and entries.endswith(":") and len(self.lines) > index:
			self.triggers["  -"] = entries[0][0:len(entries)-1]
	def items(self, key, value):
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
			if line.find(":") > -1:
				self.keyvaluepair(line.split(":", 1))
			elif line.startswith("  -"):
				self.items(self.triggers["  -"], line.replace("  -", "", 1))
		
		return self.config
