import os
from shutil import copy
import re

class FileSequence ( object ):
	def __init__(self, path, basename,postname="", ext=""):
		self.basename = basename
		self.postname = postname
		self.path = path
		self.ext = ext
		self.pattern = "{0}{{0}}{1}{2}".format(basename,postname,ext)
		self.printpatt = ""
		self.first = 999999999
		self.last = 0
		self.pad = 0
		self.holes = []

	@property
	def patternffmpeg( self ):
		patt = self.basename + "%0{0}d".format(self.pad) + self.ext
		return patt

	def addFile(self, filenumber):
		iFileNum = int(filenumber)
		if iFileNum < self.first:
			self.first = iFileNum
		if iFileNum > self.last:
			self.last = iFileNum
		self.pad = len(filenumber)
		self.printpatt = self.pattern.format("{0:0>"+str(self.pad)+"}")

	def analyze( self ):
		openhole = False
		holestart = 0
		holeend = 0
		for frame in range(self.first,self.last+1):
			candidate = self.printpatt.format(frame)
			found = os.path.exists(os.path.join(self.path,candidate))
			if not found and not openhole:
				holestart = frame
				openhole = True
			if not found and openhole:
				holeend = frame
			if found and openhole:
				openhole = False
				self.holes.append((holestart,holeend))

__reSEQ = re.compile("^(.*?)([0-9]+)([^0-9]*)$")

def ls (path ):
	seqfound = {}
	for file in os.listdir(path):
		name,ext = os.path.splitext(file)
		remSEQ = __reSEQ.match(name)
		if remSEQ:
			basename,filenumber,postname = remSEQ.groups()
			pattern = "{0}{{0}}{1}{2}".format(basename,postname,ext)
			if not pattern in seqfound:
				newFS = FileSequence(path,basename,postname,ext)
				seqfound[pattern] = newFS
			seqfound[pattern].addFile(filenumber)

	list(map(lambda x : x.analyze(),seqfound.values()))

	return seqfound

if __name__=="__main__":
	dFSeq = ls("./testbed")
	for k,oFS in dFSeq.items():
		print (k,oFS.basename,oFS.postname,oFS.path,oFS.ext,oFS.pattern,oFS.first,oFS.last,oFS.pad,oFS.holes,oFS.patternffmpeg)
