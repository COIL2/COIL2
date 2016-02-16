#!/usr/bin/env python
import sys

def main(argv):
	barcode_file = argv[0]
	targets = int(argv[1])
	
	
	bc_lines = open(barcode_file,'r').readlines()
	
	samples = {}
	
	for bc in bc_lines:
		bc = bc.rstrip()
		if bc.find("#")>-1:
			continue
		bc = bc.replace("Target ","")
		l = bc.split(",")
		sample = l[0].replace(" ","_")
		sample = sample.replace("sample","Sample")
		assay = int(l[1])
		call = l[2]
		if not sample in samples:
			samples[sample] = targets*['X']
		samples[sample][assay-1] = call
	
	samples_meta = {}
	if len(argv) > 2:
		metadata = open(argv[2],'r').readlines()
		for m in metadata:
			m = m.rstrip()
			if m.find("#")>-1:
				continue
			l = m.split(",")
			location = l[1].replace(" ","_")
			metadat = location+";"+l[2]
			samples_meta[l[0]] = metadat
	for s in samples:
		#~ if samples[s].count("N") <= 2 and samples[s].count("N")> 0:
		if samples[s].count("X") < 5:
			barcode = "".join(samples[s])
			location = ""
			if s in samples_meta:
				location = samples_meta[s]
			print s, barcode, location
		
		
		
		
		
		
	

if __name__ == "__main__":
	if len(sys.argv) == 1:
		sys.exit("python barcode_vertical_to_coil.py [vertical csv - no spaces in col1, col2=int] [num targets (int)]")
	else:
		main(sys.argv[1:])