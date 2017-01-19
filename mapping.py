#!/usr/bin/env python

from optparse import OptionParser
from subprocess import call
from os.path import basename
import sys
import subprocess
import os

parser = OptionParser()

parser.add_option("-r", "--reads", dest="readsfile",
  		  help="Reads fastq or fasta file for mapping to GENOME.", metavar="READS")
parser.add_option("-g", "--genome", dest="genomefile",
  		  help="Reference genome file to which READS will be mapped.", metavar="GENOME")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
		  help="Prints status messages throughout script runtime.")
parser.add_option("-o", "--output-directory", dest="outdir",
		  help="Directory in which to store output. Defaults to current directory.", metavar="OUTDIR")
parser.add_option("-d", "--default", action="store_true", dest="default",
    		  help="Provide default settings to bowtie rather than all exact matches.")

(options, args) = parser.parse_args()

if not options.readsfile:
    parser.error("\nPlease specify READS\n")
if not options.readsfile:
    parser.error("\nPlease specify GENOME\n")
if not options.outdir:
    options.outdir = "./"

def cmd_exists(cmd):
    return subprocess.call("type " + cmd, shell=True, 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

if cmd_exists("bowtie") == False:
    print("\nPlease install bowtie and make it available in the $PATH variable.\n")
    sys.exit()

genomebase = basename(options.genomefile)
readsbase = basename(options.readsfile)
genomebase = os.path.splitext(genomebase)[0]
readsbase = os.path.splitext(readsbase)[0]

if not os.path.isdir(options.outdir):
    print "Specified output directory does not exist.\n"
    print "Creating", outdir
    subprocess.call(["mkdir", outdir])

args = "bowtie-build", options.genomefile, options.outdir + "/" + genomebase

proc = subprocess.Popen(args, stdout=subprocess.PIPE)
(out, err) = proc.communicate()

if options.verbose == True:
    print "Bowtie output:", out
    print "\nBowtie indexing of reference genome complete.\n"

if options.default == True:
    args = "bowtie", options.outdir + "/" + genomebase, options.readsfile, "--sam", options.outdir + "/" + readsbase + "." + genomebase  + ".map"
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    (out,err) = proc.communicate()
else:
    args = "bowtie", "-v", "0", "-a", options.outdir + "/" + genomebase, options.readsfile, "--sam", options.outdir + "/" + readsbase + "." + genomebase  + ".map"
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    (out,err) = proc.communicate()

if options.verbose == True:
    print "Bowtie output:", out
    print "\nBowtie mapping of reads complete.\n"
