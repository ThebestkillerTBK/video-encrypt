#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path
import sys
import argparse
import math
import subprocess
import base64
import zipfile
import gzip
import time
import chacha
import clean
import encdec
timestamp =  int(time.time())
size = '720'
fps = '24'

def addzip(output:str,files:str):
    f = zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED)
    for i in files:
        file = i.split('/')[-1]
        f.write(i, file)
    f.close()

def filesizeMV(filePath):
 
    fsize = os.path.getsize(filePath)
    fsize = fsize/float(1024 * 1024)
 
    return round(fsize, 2)

def gzipcom():
	f_in = open("video.mp3", "rb")

	f_out = gzip.open("videos.gz", "wb")

	f_out.writelines(f_in)

	f_out.close()

	f_in.close()

def findfile(base:str):
    for a , b , fs in os.walk(base):
        for f in fs:
            yield f

def findbmp(base:str):
	for a , b , fs in os.walk(base):
		for f in fs:
			if f.endswith('.bmp'):
				yield './img/'+f
	yield "videos_layout.bmp"

def args_parser():

	parser = argparse.ArgumentParser(
		description="A tool to encrypt your video  with a key and encoded audio and images.")
	parser.add_argument("-i", "--input", help="Needed. Input file.")
	parser.add_argument("-o", "--output", help="Needed. Output directory for encrypting and output file for decrypting.")	
	parser.add_argument("--force",action='store_true',help="Optional. Encrypt a video over 150 MB. Default disabled.",default=False)
	parser.add_argument("--fps", help="Optional. Encrypted video fps. Default is 24.",default='24')
	parser.add_argument("--size", help="Optional. Encrypted video height. Default is 720.",default='720')
	parser.add_argument("-d","--decrypt",action='store_true',help="Decrypt a video.",default=False)
	parser.add_argument("--key", help="Needed. Decrypt key.")

	args = parser.parse_args()

	if not (args.input and args.output):
		print('Missing arguments.')
		parser.print_help()
		sys.exit(1)
	return parser

def main():
	os.chdir(sys.path[0])
	
	if not args.decrypt:
		encv()
	else:
		decv()

def decv():
	input = args.input
	output = args.output
	keyfile = args.key
	print('Input: {}'.format(input),'\nOutput: {}'.format(output))
	if not args.key:
		print('Decryption key needed!!!')
		sys.exit(1)
	if not (os.path.isfile(output) or os.path.isfile(input)):
		print('File or directory does not exist!!!')
		sys.exit(1)
	print('Decrypting video data...')
	chacha.decrypt_chacha(input,keyfile,'temp.zip')
def encv():
	input = args.input
	output = args.output
	force = args.force
	fps = args.fps
	size = args.size
	clean.clean()
	print('Input: {}'.format(input),'\nOutput: {}'.format(output),'\nFps: {}'.format(fps),'\nHeight: {}'.format(size))
	if not (os.path.isfile(output) or os.path.exists(input)):
		print('File or directory does not exist!!!')
		sys.exit(1)
	if filesizeMV(input) > 150 and not force:
		print('Your file is too large. Force encrypt by option --force')
		sys.exit(1)
	print("Converting video to image and audio...")
	out_code = subprocess.call(['ffmpeg', '-i',
	input,'-vf','scale=-1:'+size,'-r',fps,
	os.path.realpath('./img/image-%08d.jpg')], stdout = open('ffmpeg.log','a'), stderr = subprocess.STDOUT)
	if not (out_code == 0):
		print("Error converting!")
		sys.exit(1)
	out_code = subprocess.call(['ffmpeg', '-i',
	input,'-f','mp3','-vn','video.mp3'], stdout = open('ffmpeg.log','a'), stderr = subprocess.STDOUT)
	if not (out_code == 0):
		print("Warning: This video may not have sound or an conversion error occured.")
		fd = open('video.mp3', mode="w", encoding="utf-8")
		fd.close()
	print('Finished.\nEncoding images and audio...')
	for i in findfile('./img'):
		encdec.encodevid('./img/'+i)
	print('Finished.\nCompressing images and audio...')
	gzipcom()
	encdec.encodevid('videos.gz')
	addzip('temp.zip',findbmp('./img'))
	print('Finished.\nEncrypting...')
	if not os.path.exists(os.path.realpath(output)):
		os.mkdir(os.path.realpath(output))
	else:
		clean.del_file(os.path.realpath(output))
	
	keypath = os.path.realpath(output+'/key-'+str(timestamp)+'.key')
	chacha.w_files(keypath,os.urandom(32)+os.urandom(12))
	chacha.encrypt_chacha('temp.zip',keypath,os.path.realpath(output+'/'+os.path.basename(input)+'.encvid'))
	
	print('Encryption completed.\nCleaning...')
	clean.clean()
	print('Finished!')


	

if __name__ == "__main__":
	parser = args_parser()
	args = parser.parse_args()
	main()
	print("Press enter to exit ...")
	input()