#! /usr/bin/env python
import sys
import numpy as np
import MAF, PriorProbability

class Barcode:
	def __init__(self, id, sequence):
		self.id = id
		self.seq = sequence
		self.rough_coi = 0
		
	def getLength(self):
		return len(self.seq)
		
	def getSeqChars(self):
		charset = set([])
		for s in self.seq:
			charset.add(s)
		return charset
		
	def setRoughCOI(self):
		n_count = self.seq.count('N')
		if n_count <= 0:
			self.rough_coi = 1
		elif n_count == 1:
			self.rough_coi = 2
		else:
			self.rough_coi = 3
			
	def getPosition(self, pos): ##pos is base 0
		return self.seq[pos:pos+1]
		
	def getPositionForMAF(self, pos): ##pos is base 0
		base = self.seq[pos:pos+1]
		#right now, no N seqs are returned so this if statement is never used
		if base == 'N':
			base = 'N'*self.coi
		return base
		
	def predictCOI(self,myMAF,max_coi, threshold, my_priors):
		#get list of tuples with base call and position
		junk_positions = [(x,y) for y in range(len(self.seq)) for x in self.seq]
		positions = []
		for i in junk_positions[0::len(self.seq)+1]:
			positions.append(i)
			
		#Where the COI magic really happens!
		coi = 1
		rawCOIs = []
		while coi <= max_coi:
			#get list of posterior probabilities for each position in barcode
			pos_probs = [myMAF.getProbability(pos,coi) for pos in positions]
			
			#multiply product of posterior probabilities by prior prob
			#append to rawCOIs
			rawCOIs.append(np.prod(pos_probs)*my_priors.getPrior(coi))
			coi+=1

		coi_sum = np.sum(rawCOIs)
		COIs = [x/coi_sum for x in rawCOIs]
		most_likely_coi = np.amax(COIs)
		coi_index = COIs.index(most_likely_coi)
		ci = self.getCredibleInterval(COIs, coi_index, max_coi, threshold)
		print self.id, self.seq, coi_index+1, ci[0], ci[1], np.round(most_likely_coi,4)

		
	def getCredibleInterval(self, cois, coi_index, max_coi, threshold):
		low = coi_index
		high = coi_index
		sum = cois[coi_index]
		
		while sum < threshold:
			if low == 0:
				high+=1
				sum += cois[high]
			elif high == max_coi-1:
				low -=1
				sum += cois[low]
			elif cois[low-1] >= cois[high+1]:
				low -=1
				sum += cois[low]
			else:
				high +=1
				sum += cois[high]
		return (low+1, high+1)

class SetOfBarcodes:
	def __init__(self):
		self.barcodes = []  #list of Barcode objects
		
	def readBarcodeFile(self, file):
		bc_lines = open(file, 'r').readlines()
		print "Reading barcodes"
	
		for bcl in bc_lines:
			if bcl.find("#") == 0:
				continue
			bcl = bcl.rstrip()
			line = bcl.split()
			id = line[0]
			myBC = Barcode(id, line[1])
			myBC.setRoughCOI()
			self.barcodes.append(myBC)
			
	def validateBarcodes(self, validCharSet):
		first_len = self.barcodes[0].getLength()
		for b in self.barcodes:
			#check for length
			if not b.getLength()==first_len:
				ret_str = b.id+" length is not the same as first barcode length"
				return (0, ret_str)
			bchar = b.getSeqChars()
			#check for invalid characters
			if not bchar.issubset(validCharSet):
				ret_str = "Invalid character in barcode: "+b.id
				return (0, ret_str)
			if b.seq.count('X') > (first_len/2):
				print "WARNING: "+b.id+" has poor data quality. Consider excluding from analysis"
		return (1, "Barcodes OK")
		
		
	def computeMAFFromBarcodes(self,padding):
		###does not count barcode if there are any N values
		###Missing data (X) is not added to count for position
		myMAF = MAF.MAF()
		bLen = self.barcodes[0].getLength()
		i=0
		while i < bLen:
			myPos = MAF.MAFPosition(i)
			for b in self.barcodes:
				if b.rough_coi>1:
					continue
				myPos.addChar(b.getPositionForMAF(i))
			myPos.getMAFFromChars()
			myPos.setAlleleProbability(padding)
			#~ if myPos.isPositionInformative():
				#~ myMAF.addPosition(myPos)
			myMAF.addPosition(myPos)  #add position regardless of informative-ness
			i+=1
		return myMAF
			
	def validateMAF(self, myMAF):
		##check number of MAF positions
		if not len(myMAF.pos)==self.barcodes[0].getLength():
			print len(myMAF.pos), self.barcodes[0].getLength()
			ret_str = "Different number of positions between file and barcodes."
			return (0,ret_str)
		for pos in myMAF.pos:
			if pos.minor_freq < 0.0 or pos.minor_freq > 0.5:
				ret_str = "Invalid minor allele frequency"
				return (0,ret_str)
			if len(pos.getChars()) > 3:
				ret_str = "Only bi-allelic assays are supported."
				return (0,ret_str)
		return (1, "MAF is OK!")
			
	def predictBarcodeCOIs(self,myMAF,max_coi, threshold, my_priors):
		print "Sample", "Barcode", "COI", "CI-", "CI+", "Posterior Probability"
		for b in self.barcodes:
			b.predictCOI(myMAF,max_coi,threshold, my_priors)
