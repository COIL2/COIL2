#! /usr/bin/env python

import sys, getopt
import Barcode, MAF, PriorProbability #, Tally, Likelihood, Probability

def usage_barcodeFormat():
	print """Formatting issue with barcode file.  
	
	Barcode format criteria:
	All sample lines must have the same number of columns.
	No field may have spaces.
	Valid barcode sequence characters are A,C,G,T,X,N.
	All barcode sequences must be the same length.
	Only bi-allelic assays are permitted.
	"""
	
def usage_MAFFile():
	print """Formatting issue with MAF file.
	
	MAF format criteria:
	# positions must be equal to # barcode positions.
	Minor allele frequency must be [0.0,0.5].
	"""
	
def usage_ErrorFile():
	print """Formatting issue with Error File.
	
	Format criteria:
	Lines with '#' will not be read.
	2 columns: [position] [error rate].
	Error rate must be [0.0,1.0).
	Each assay must have an error rate specified.
	"""

def usage():
	print """python COIL.py [options] -b [barcode file]
	
	Required:
	-b, --barcode [file]
		where [file] contains sample names and barcodes
	
	Optional:
	-m, --maf [file]
		where [file] contains minor allele frequencies for each assay
	-c, --max_coi [integer]
		where [integer] is the maximum allowable COI for analysis
		default = 5
	-s, --subset [file]
		where [file] is a list of samples contained in [barcode file]
	-e, --error [float]
		where [float] is a number [0.0,1.0)
		default = 0.05
	-E, --error_file [file]
		where [file] contains the error rate for each assay
	-i, --credible_interval [float]
		where [float] is a number (0.0,1.0]
		default = 0.95
	-f, --prior_file [file]
		where [file] contains the prior probabilities of each COI [1,max_coi]
		Probabilities must sum to 1.0.
	-p, --poisson [integer]
		where [integer] is expected value of Poisson distribution of prior probability
	"""


def main(argv):
	barcode_file = ""
	MAF_file = ""
	get_MAF_from_barcode = 1
	PADDING = 1
	ERROR = 0.05
	error_file = ""
	MAX_COI = 5
	CI_THRESHOLD = 0.95
	PRIOR_DISTRIBUTION = 'uniform'
	prior_file = ""
	poisson_lambda = 1
	
	validCharSet = set(['A','C','G','T','N','X'])
	
	try:
		opts, args = getopt.getopt(argv, "b:m:s:e:E:i:c:f:p:",["barcode=","maf=","subset=","error=","error_file=","credible_interval=","max_coi=","prior_file=","poisson="])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-b","--barcode"):
			barcode_file = arg
		elif opt in ("-m","--maf"):
			get_MAF_from_barcode = 0
			MAF_file = arg
		elif opt in ("-s","--subset"):
			subset_barcodes = 1
			subset_file = arg
		elif opt in ("-e","--error"):
			ERROR = float(arg)
			if ERROR < 0 or ERROR > 1:
				sys.exit("Error must be [0,1)")
		elif opt in ("-E", "--error_file"):
			ERROR = -1
			error_file = arg
		elif opt in ("-i","--credible_interval"):
			CI_THRESHOLD = float(arg)
			if CI_THRESHOLD<=0 or CI_THRESHOLD > 1:
				sys.exit("Credible Interval must be (0,1]")
		elif opt in ("-c","--max_coi"):
			MAX_COI = int(arg)
		elif opt in ("-f","--prior_file"):
			PRIOR_DISTRIBUTION = 'from_file'
			prior_file = arg
		elif opt in ("-p","--poisson"):
			PRIOR_DISTRIBUTION = "poisson"
			poisson_lambda = int(arg)
			
	
	###Read barcode file, create barcode set, validate barcodes
	barcodes = Barcode.SetOfBarcodes()
	barcodes.readBarcodeFile(barcode_file)
	print len(barcodes.barcodes), "barcodes read"
	bc_valid = barcodes.validateBarcodes(validCharSet)
	if bc_valid[0] == 0:
		print bc_valid[1]
		usage_barcodeFormat()
		sys.exit(2)
	
	###MAF Handling
	myMAF = MAF.MAF()
	if get_MAF_from_barcode == 0:
		myMAF.readMAFFile(MAF_file)
		maf_valid = barcodes.validateMAF(myMAF)
		if maf_valid[0]==0:
			print maf_valid[1]
			usage_MAFFile()
			sys.exit(2)
	else:
		myMAF = barcodes.computeMAFFromBarcodes(PADDING)
	print myMAF

	###Add genotyping error tolerance
	if ERROR>=0:
		myMAF.setErrorFromConstant(ERROR)
	else:
		ret = myMAF.setErrorFromErrorFile(error_file)
		if ret == 0:
			usage_ErrorFile()
			sys.exit(2)
	
	###Define Prior Probabilities
	myPriors = None
	if PRIOR_DISTRIBUTION == 'uniform':
		myPriors = PriorProbability.COIProbability(MAX_COI)
		myPriors.setProbabilities()
	elif PRIOR_DISTRIBUTION == 'from_file':
		myPriors = PriorProbability.FromFile(MAX_COI)
		myPriors.setProbabilities(prior_file)
	elif PRIOR_DISTRIBUTION == 'poisson':
		myPriors = PriorProbability.Poisson(MAX_COI)
		if poisson_lambda <1 or poisson_lambda > MAX_COI:
			print "Poisson lambda must be [1,MAX_COI]"
			usage()
			sys.exit(2)
		myPriors.setProbabilities(poisson_lambda)
			
	valid_prior = myPriors.validatePriors()
	print myPriors.cois
	if not valid_prior:
		usage()
		sys.exit(2)
		
	###Allele Computations
	barcodes.predictBarcodeCOIs(myMAF, MAX_COI, CI_THRESHOLD, myPriors)
	
	
if __name__ == "__main__":
	if len(sys.argv) == 1:
		sys.exit(usage())
	else:
		main(sys.argv[1:])