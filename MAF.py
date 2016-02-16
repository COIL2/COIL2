#!/usr/bin/env python
import sys, random
import Barcode

class MAF:
	def __init__(self):
		self.pos = []

	def readMAFFile(self,MAF_file):
		maf = open(MAF_file,'r').readlines()
		index = 0
		for m in maf:
			m = m.rstrip()
			if m.find("#")>-1:
				continue
			l = m.split()
			minor = l[0]
			major = l[1]
			minor_freq = float(l[2])
			myPos = MAFPosition(index)
			myPos.setMinor(minor)
			myPos.setMajor(major)
			myPos.setMinorFreq(minor_freq) ###also sets major freq
			myPos.setAlleleProbabilityNoCounts()
			self.addPosition(myPos)
			index+=1
			
	def setErrorFromErrorFile(self,error_file):
		file = open(error_file,'r').readlines()
		count = 0
		for ef in file:
			ef = ef.rstrip()
			if ef.find("#")>-1:
				continue
			count += 1
			l = ef.split()
			if len(l)>2:
				print "Error file format issue: too many columns."
				return 0
			rate = float(l[1])
			if rate < 0.0 or rate >= 1.0:
				print "Invalid error rate."
				return 0
			self.pos[int(l[0])+1].setErrorRate(float(l[1]))
		if not count == len(self.pos):
			print "Not enough lines in error file."
			return 0
		return 1
		
	def setErrorFromConstant(self, error_rate):
		for p in self.pos:
			p.setErrorRate(error_rate)
			
	def getProbability(self, position, coi):
		return self.pos[position[1]].getCallProbability(position[0], coi)
	
	def addPosition(self, MAFPos):
		self.pos.append(MAFPos)
		
	def __str__(self):
		retstr = []
		for p in self.pos:
			retstr.append(p.__str__())
		return "\n".join(retstr)
	
class MAFPosition:
	def __init__(self, pos):
		self.pos = pos
		self.chars = []
		self.minor = '-'
		self.major = '-'
		self.minor_count = 0
		self.major_count = 0
		self.het = 0
		self.missing = 0
		self.minor_freq = 0.0
		self.major_freq = 0.0
		self.missing_freq = 0.0
		self.het_freq = 0.0
		self.major_prob = 0.0
		self.minor_prob = 0.0
		self.error = 0.0
		
	def __str__(self):
		#~ retstr = "\t".join([str(self.pos),self.minor,self.major,str(self.minor_freq), str(self.major_freq)])
		#~ retstr = "\t".join([self.minor,self.major,str(self.minor_freq),str(self.minor_count),str(self.minor_count+self.major_count)])
		retstr = "\t".join([self.minor,self.major,str(self.minor_freq)])
		return retstr
		
	def setMinor(self, minor):
		self.minor = minor
		
	def setMajor(self, major):
		self.major = major
		
	def setMinorFreq(self, minor_freq):
		mf = float(minor_freq)
		###moved this error message to SetOfBarcodes.validateMAF()
		#~ if not mf>=0.0 and not mf<=0.5:
			#~ sys.exit("MAF:setMinorFreq - Minor frequency must be [0.0,0.5]")
		self.minor_freq = mf
		self.major_freq = 1.0-mf
		
	def setMinorProb(self, minor_prob):
		mp = float(minor_prob)
		self.minor_prob = mp
		self.major_prob = 1.0-mp
		
	def addChar(self, char):
		self.chars.append(char)
		
	def getChars(self):
		return set(self.chars)
		
		
	def getMAFFromChars(self):
		all_chars = set(self.chars)
		#~ if len(all_chars) > 6:  ##this is when rough COI is used in calculations
		if len(all_chars) > 3:
			print "Too many alleles at position", self.pos
			print all_chars
			#~ sys.exit("Only bi-allelic assays are supported.")
		max_count = 0
		max_char = ''
		other_chars = []
		coi2_hets = 0
		for ac in all_chars:
			if not ac == 'X' and not ac == 'N' and not ac=='NN' and not ac=='NNN':
				other_chars.append(ac)
			if ac=='X':
				self.missing = self.chars.count(ac)
			elif ac=='NN':
				coi2_hets = self.chars.count(ac)
			elif ac =='NNN':
				self.het = self.chars.count(ac)
			elif self.chars.count(ac)>max_count:
				max_count  = self.chars.count(ac)
				max_char = ac
		if len(other_chars)>0:
			self.major = max_char
			self.major_count = max_count + coi2_hets
			if len(other_chars)>1:
				other_chars.remove(max_char)
				self.minor = other_chars[0]
				self.minor_count = self.chars.count(self.minor) + coi2_hets
			min_maj = float(self.minor_count+self.major_count)
			self.minor_freq = float(self.minor_count)/min_maj
			self.major_freq = float(self.major_count)/min_maj
			self.missing_freq = float(self.missing)/float(len(self.chars))
			self.het_freq = float(coi2_hets+self.het)/float(len(self.chars))
		else:
			print "WARNING: There is no usable data for position", self.pos+1
		

		
	def setAlleleProbability(self, padding):	
		min_maj = float(self.minor_count+self.major_count+2*padding)
		self.minor_prob = float(self.minor_count+padding)/min_maj
		self.major_prob = float(self.major_count+padding)/min_maj
		
	def setAlleleProbabilityNoCounts(self):
		self.minor_prob = self.minor_freq
		self.major_prob = self.major_freq
		
	def setErrorRate(self,error_rate):
		self.error = error_rate
		
		
	#super naive way of describing informative
	#mostly a place holder
	def isPositionInformative(self):
		repBase = self.minor_count+self.major_count+self.het
		return 1
		if 3 > repBase:
			return 0
		elif self.major_freq == 1.0:
			return 0
		return 1
		
		
	def getCallProbability(self, call, coi):
		e0 = 1-self.error
		e1 = self.error/2
		
		major_error = e1
		minor_error = e1
		het_error = e1
		if call == self.major:
			major_error = e0
		elif call == self.minor:
			minor_error = e0
		elif call == 'N':
			het_error = e0
		
		major_prob = self.major_prob**coi
		minor_prob = self.minor_prob**coi
		het_prob = 1.0-minor_prob-major_prob
		
		probability = major_prob*major_error + minor_prob*minor_error + het_prob*het_error
		
		return probability
		