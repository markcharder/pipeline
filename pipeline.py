#!/usr/bin/env python

# Import general modules.
import subprocess
import sys
import os
import multiprocessing
import re
import optparse
import time
import itertools
import functools
import glob

# Import custom module from lib folder in current directory.
scriptpath = os.path.abspath(sys.argv[0])
scriptpath = os.path.dirname(scriptpath)
sys.path.append(scriptpath + "/" + "lib")

import filtering

# Get options.
time = time.strftime("%d/%m/%Y %H:%M:%S")

parser = optparse.OptionParser()

parser.add_option("-r", "--reads", dest = "readsfile",
		  help = "Reads file in fastq format.", metavar = "READS")
parser.add_option("-g", "--genome", dest = "genomefile",
		  help = "Reference genome file for mapping.", metavar = "GENOME")
parser.add_option("-f", "--filter", dest = "rnasfile",
		  help = "Database of known RNAs for filtering in fasta OR directory containing a database split across multiple fasta files.", metavar = "DATABASE")
parser.add_option("-b", "--big-db-threads", dest = "bdbthreads",
		  help = "Number of threads used for indexing multiple fasta files in a large RNA database (defaults to 1).", metavar = "BIG DATABASE THREADS")
parser.add_option("-v", "--verbose", action = "store_true", dest = "verbose",
		  help = "Print messages showing script progress.")
parser.add_option("-m", "--big-db-mapping-threads", dest = "bdbmapthreads",
		  help = "Number of threads used for mapping to multiple fasta files in large RNA database (defaults to 1).", metavar = "BIG DATABASE MAPPING THREADS")
parser.add_option("-d", "--bowtie-threads", dest = "btthreads",
		  help = "Number of mapping threads for Bowtie (defaults to 1).", metavar = "BOWTIE MAPPING THREADS")
parser.add_option("-o", "--output-dir", dest = "outdir",
		  help = "Output directory.", metavar = "OUTPUT DIRECTORY")

(options, args) = parser.parse_args()

if options.verbose == True:
    print "Script started at: " + time

# Throw errors if options not provided.
if not options.readsfile:
    parser.error("\nPlease specify READS.\n")
if not options.genomefile:
    parser.error("\nPlease specify GENOME.\n")
if not options.rnasfile:
    parser.error("\nPlease specify TRNABASE.\n")
if not options.outdir:
    options.outdir = "./"
if not options.bdbthreads:
    options.bdbthreads = 1
    if options.verbose == True:
        print "Setting big database threads to default which is 1."
if not options.bdbmapthreads:
    options.bdbmapthreads = 1
    if options.verbose == True:
        print "Setting big database mapping threads to default which is 1."
if not options.btthreads:
    options.btthreads = 1
    if options.verbose == True:
        print "Setting Bowtie mapping threads to default which is 1."

# Test if Bowtie index files exist in database directory.
files = filtering.get_files(options.rnasfile)
match = re.search("ebwt", ''.join(files))

# Test if database is a single file or a directory with multiple files. If former run index on single file, if latter run index on multiple files with specified threads.
if not match:
    if isinstance(files, basestring):
        if options.verbose == True:
            print "Indexing RNA database file with Bowtie started at:", time
        filtering.bowtie_index(options.rnasfile)
        if options.verbose == True:
            print "Indexing RNA database file with Bowtie finished at:", time
    else:
        if options.verbose == True:
           print "Indexing multiple RNA database files on", options.bdbthreads, "threads with Bowtie started at:", time
        process = multiprocessing.Pool(int(options.bdbthreads))
        process.map(filtering.bowtie_index, files)
        process.close()
        process.join()
        if options.verbose == True:
            print "Indexing multiple RNA database files on", options.bdbthreads, "threads with Bowtie finished at:", time
else:
    if not isinstance(files, basestring):    
        files = filtering.get_files(options.rnasfile,".fa")
        if not files:
            files = filtering.get_files(options.rnasfile,".fasta") #Change file list to just the fasta files if ebwt files are present.

readsbase = filtering.create_output(options.readsfile)
readsout = options.outdir + "/" + readsbase
genomebase = filtering.create_output(options.genomefile)
rnasbase = filtering.create_output(options.rnasfile)

params = ("--sam", "--threads", str(options.btthreads), "--un")

def wrap_map_wrap(wrapfiles):
    (out, err) = filtering.map_wrap(wrapfiles, params, options.readsfile, options.outdir, um=True)
    return out, err
    print out, err

# Test if database is a single file or a directory with multiple files. If former run mapping on single file, if latter run mapping on multiple files with specified threads.

if isinstance(files, basestring):
    if options.verbose == True:
        print "Mapping reads to RNA database with Bowtie started at:", time
    bowtie_map(params, rnasfile, readsfile, readsout + "." + rnasbase + ".sam", unmapped=readsout + "." + rnasbase + ".um.fq", um=True)
    if options.verbose == True:
        print "Mapping reads to RNA database with Bowtie finished at:", time
else:
    if options.verbose == True:
        print "Mapping reads to multiple RNA databases on", options.bdbmapthreads, "threads with Bowtie started at:", time
    process = multiprocessing.Pool(int(options.bdbmapthreads))
    process.map(wrap_map_wrap, files)
    process.close()
    process.join()
    if options.verbose == True:
        print "Mapping reads to multiple RNA databases on", options.bdbthreads, "threads with Bowtie finished at:", time

filt_reads = filtering.get_files(options.outdir, '.um.fq')
subprocess.call("cat " + ' '.join(filt_reads) + " > " + readsout + ".filt.fq", shell=True)
params = ("--sam", "-v", "0", "-a", "--threads", str(int(options.btthreads)))

# Map reads not mapped to rna database to genome.

if options.verbose == True:
    print "Indexing fasta reference file with Bowtie started at:", time
(err, out) = filtering.bowtie_index(options.genomefile)
if options.verbose == True:
    print "Indexing fasta reference file with Bowtie finished at:", time

if options.verbose == True:
    print "Mapping reads to Reference with Bowtie started at:", time
(out, err) = filtering.bowtie_map(params, options.genomefile, readsbase + ".filt.fq", readsout + "." + genomebase + ".sam")
if options.verbose == True:
    print "Mapping reads to reference with Bowtie finished at:", time
