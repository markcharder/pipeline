#!/usr/bin/env python

import subprocess

def convert_sam_to_bam(sam, outfile):
    args = ("samtools", "-bT", sam, ">", outfile)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    (err, out) = proc.communicate()
    return err, out

    
