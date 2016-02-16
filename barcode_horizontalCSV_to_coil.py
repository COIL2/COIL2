#!/usr/bin/env python
import sys

def main(argv):
	barcode_file = argv[0]
	
	bc_lines = open(barcode_file,'r').readlines()
	
	samples = {}
	
	for bc in bc_lines:
		bc = bc.rstrip()
		if bc.find("#")>-1:
			continue
		bc = bc.replace("Target ","")
		l = bc.split(",")
		sample = l[0].replace(" ","_")
		barcode = "".join(l[1:])
		samples[sample] = barcode
		
	for s in samples:
		#~ if samples[s].count("N") <= 2 and samples[s].count("N")> 0:
		print s, samples[s]
		
		
		
		
		
		
	

if __name__ == "__main__":
	if len(sys.argv) == 1:
		sys.exit("run it right")
	else:
		main(sys.argv[1:])