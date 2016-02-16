INPUT FORMATS

1. Barcodes file

The barcodes file format is very flexible. It can contain any number of whitespace-separated columns where the last column contains your SNP barcode data. This is the only column that COIL is currently aware of. An example of appropriate input file format is given below. Right-click the file below and select 'Save Link As' to store the file locally on your computer.

Sample barcode data input file:

# Comment lines begin with a hash
# This file contains sample simulated barcodes.
# There are 99 barcodes with the COI roughly from a Poisson(1) distribution.
# Each barcode has 24 SNPs with MAF sampled from a Beta(1,1)=Uniform(0,1) distribution. 
#sample names CANNOT contain any spaces
# Put headers in comments
#ID	Barcode
sim1	GTCAGACTGACTTGTTTGGGATAC
sim2	GTCAGCTTGTCTTGTGTGAGTTAC
sim22	GACTGATXGTCTXGTTTTGATTCG
sim23	AXCAGATTCTCTTGTTTGGAATCC
sim24	GACAGATTCTCTTGTTTGGGTTAC
# Comments can go in the middle
sim25	ATCAAATTGTCTTGTTTGGAXTAG
sim26	GACXACTTGACTCCTTTGGATTAG

2. Allele frequencies file

These are optional because COIL can calculate the minor allele frequencies (MAF) for each assay from the barcodes. However, there are the following caveats:

You should include as many barcodes from one population as possible.
It is very important to include barcodes that do not not include heterogenomic calls. These are used to calibrate the MAFs.
Using a different set of barcodes will result in different output if the esimated MAFs for each assay change.
The MAFs file contains three columns. The first two are the two alleles possible for that assay of the barcode, the third column is the allele frequency of the allele in the first column.

#This file contains MAF information for a collection of assays.
#The first two columns indicate the two possible alleles for each assay.
#The third column indicates the MAF of the allele in the first column.
G	A	0.1
T	A	0.1
C	T	0.1
A	T	0.1
G	A	0.1
A	C	0.1
T	C	0.1
T	C	0.1 
C	G	0.1
T	A	0.1
C	G	0.1
T	C	0.1
T	C	0.1
C	G	0.1
T	G	0.1
T	G	0.1
T	A	0.1
G	T	0.1
G	A	0.1
G	A	0.1
A	T	0.1
T	C	0.1
A	C	0.1
C	G	0.1


OUTPUT FORMAT

Output is tab-delimited text, with columns providing the following information for each sample:

Sample barcode sequence
Estimated COI
COI credible interval
Posterior probability of the estimated COI value
The predictions are output in the same order as the input file. The estimated COI is the "maximal a posteriori" COI, the COI which has the greates probability in the constructed posterior distribution. This probability is provided in the last column.

The credible interval is the Bayesian analog of the confidence interval, and here specifies the COI bounds under which at least 95% of the posterior distribution lies. NOTE: if you see a "+" appended to the upper bound of your credible interval, that means that the upper bound is actually infinity. This behavior is due to the way COIL is implemented, and reflects the bounds specified during the construction of the prior distribution.
