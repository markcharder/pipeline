#!/usr/bin/env python

from optparse import OptionParser
from subprocess import call
from os.path import basename
import sys
import subprocess
import os

scriptpath = os.path.realpath(__file__)
sys.path.append(scriptpath + "/" + "lib")

import filtering

parser = OptionParser()

parser.add_option("-r", "--reads", dest="readsfile",
  		  help="Reads fastq or fasta file for mapping to GENOME.", metavar="READS")
parser.add_option("-g", "--genome", dest="genomefile",
  		  help="Reference genome file to which READS will be mapped.", metavar="GENOME")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
		  help="Prints status messages throughout script runtime.")
parser.add_option("-o", "--output-directory", dest="outdir",
		  help="Directory in which to store output. Defaults to current directory.", metavar="OUTDIR")
parser.add_option("-t", "--transfer-rnas", dest="trnas",
		  help="Fasta file containing transfer RNA database to screen reads against.\n", metavar="TRNABASE")

(options, args) = parser.parse_args()

def cmd_exists(cmd):
    return subprocess.call("type " + cmd, shell=True, 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

for var in "bowtie", "samtools":
    if cmd_exists(var) == False:
        print "\nPlease install", var, "and make it available in the $PATH variable.\n"
        sys.exit()

if not options.readsfile:
    parser.error("\nPlease specify READS.\n")
if not options.genomefile:
    parser.error("\nPlease specify GENOME.\n")
if not options.trnas:
    parser.error("\nPlease specify TRNABASE.\n")
if not options.outdir:
    options.outdir = "./"

genomebase = basename(options.genomefile)
readsbase = basename(options.readsfile)
genomebase = os.path.splitext(genomebase)[0]
readsbase = os.path.splitext(readsbase)[0]

if os.path.isdir(options.outdir):
    if not os.path.isdir(options.outdir + "/" + readsbase):
        subprocess.call(["mkdir", options.outdir + "/" + readsbase])
else:
    print "Specified output directory does not exist.\n"
    sys.exit()

args = "python", "mapping.py", "--reads=" + options.readsfile, "--genome=" + options.trnas, "--output-directory=" + options.outdir
proc = subprocess.Popen(args, stdout=subprocess.PIPE)
(out, err) = proc.communicate()

if options.verbose == True:
    print "Bowtie output:", out
    print "\nFinished mapping reads to trna database.\n"

args = "python", "mapping.py", "--reads=" + options.readsfile, "--genome=" + options.genomefile, "--output-directory=" + options.outdir
proc = subprocess.Popen(args, stdout=subprocess.PIPE)
(out, err) = proc.communicate()

if options.verbose == True:
    print "Bowtie output:", out
    print "\nFinished mapping reads to reference.\n"

filtering.convert_sam_to_bam(
