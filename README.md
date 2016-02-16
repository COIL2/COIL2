# COIL2 Usage

python COIL.py [options] -b [barcode file]
	
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