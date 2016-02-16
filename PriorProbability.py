#! /usr/bin/env python
import sys
from scipy.stats import poisson
import numpy as np

class COIProbability:
	def __init__(self, max_coi):
		self.max_coi = int(max_coi)
		self.cois = {}
		
	def setProbabilities(self):
		mycoi = 1
		myprob = 1.0/float(self.max_coi)
		[self.setPriors(x,myprob) for x in range(1,self.max_coi+1)]
		
	def setPriors(self, coi, prob):
		self.cois[coi] = prob
		
	def getPrior(self, coi):
		return self.cois[coi]
		
	def validatePriors(self):
		coi = self.cois.keys()
		c_sum = 0.0
		for c in coi:
			if c<1 or c>self.max_coi:
				print "Specified COI must be [1,MAX_COI]"
				return 0
			c_sum += self.cois[c]
		c_sum = np.round(c_sum)
		if not c_sum == 1.0:
			print "Prior Probabilities must sum to 1.0"
			return 0
		if not len(coi) == self.max_coi:
			print "Prior probabilities do not match MAX_COI"
			return 0
		return 1

class Poisson(COIProbability):
	def setProbabilities(self, p_lambda):
		raw_cois = [poisson.pmf(x,p_lambda) for x in range(1,self.max_coi+1)]
		raw_sum = np.sum(raw_cois)
		counter = 1
		for rc in raw_cois:
			self.setPriors(counter, np.round((rc/raw_sum),4))
			counter +=1
	
class FromFile(COIProbability):
	def setProbabilities(self, prior_file):
		priors = open(prior_file,'r').readlines()
		for p in priors:
			p = p.rstrip()
			if p.find("#")>-1:
				continue
			l = p.split()
			self.setPriors(int(l[0]), float(l[1]))
		
	