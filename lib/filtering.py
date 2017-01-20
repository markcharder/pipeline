#!/usr/bin/env python

import subprocess
import sys
import os
import glob
import re

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

def bowtie_map(params, genome_base, reads, output, um="False", unmapped="unmapped.fq"):
    if not cmd_exists("bowtie") == True:
        "\nPlease make sure Bowtie is installed and available in system path.\n"
        sys.exit()
    bowtie = ("bowtie",)
    if um == True:
        args = bowtie + (params) + (unmapped, genome_base, reads, output)
    else:
	args = bowtie + (params) + (genome_base, reads, output)
    proc = subprocess.Popen(list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (err, out) = proc.communicate()
    return out, err

def create_output(filename):
    filebase = os.path.basename(filename)
    filebase = os.path.splitext(filebase)[0]
    return filebase

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

def get_files(path, ext=''):
    files = glob.glob(path+"*"+ext)
    return files

def map_wrap(file_list, params, reads, outd, um=True):
    filebase = create_output(file_list)
    readsbase = create_output(reads)
    if um == True:
        (out, err) = bowtie_map(params, file_list, reads, outd + "/" + readsbase + "." + filebase + ".sam", unmapped=outd + "/" + readsbase + "." + filebase + ".um.fq", um=True)
    else:
	(out, err) = bowtie_map(params, file_list, reads, outd + "/" + readsbase + "." + filebase + ".sam")
    print out, err
    return out, err
