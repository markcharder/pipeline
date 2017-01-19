#!/usr/bin/env python

import subprocess
import sys
import os
import glob

def cmd_exists(cmd):
    return subprocess.call("type " + cmd, shell=True, 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def bowtie_index(genome, output=""):
    if not cmd_exists("bowtie-build") == True:
        "\nPlease make sure Bowtie is installed and available in system path.\n"
        sys.exit()
    if output != "":
        args = ("bowtie-build", genome, output)
    else:
        args = ("bowtie-build", genome, genome)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (err, out) = proc.communicate()
    return err, out

def bowtie_map(params, genome_base, reads, output):
    if not cmd_exists("bowtie") == True:
        "\nPlease make sure Bowtie is installed and available in system path.\n"
        sys.exit()
    args = ("bowtie", params, genome_base, reads, output)
    proc = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    (err, out) = proc.communicate()
    
def convert_sam_to_bam(reference, sam, outfile):
    args = ("samtools", "view", "-bT", reference, sam)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (err, out) = proc.communicate()
    f = open(outfile, "w")
    f.write(err)
    return err, out

def bam_to_fastq(bam, outfile):
    args = ("bedtools", "bamtofastq", "-i", bam, "-fq", outfile)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (err,out) = proc.communicate()
    return err, out

def get_files(path):
    files = glob.glob(path+"*")
    return files
