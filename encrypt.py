#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path
import sys
import argparse
import platform
import math
import subprocess
import base64
import zipfile
import gzip
import time
import chacha
import shutil
import clean
import encdec
timestamp =  int(time.time())
currdir = os.path.dirname(os.path.realpath(sys.argv[0]))
size = '720'
fps = '24'
ffmpegrun = ''

def unzip_file(zip_src, dst_dir):
	r = zipfile.is_zipfile(zip_src)
	if r:     
		fz = zipfile.ZipFile(zip_src, 'r')
		for file in fz.namelist():
			fz.extract(file, dst_dir)
	else:
		print('Error Compressing files!')
		sys.exit(1)

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

def gzipcom(input, output):
	f_in = open(input, "rb")

	f_out = gzip.open(output, "wb")

	f_out.writelines(f_in)

	f_out.close()

	f_in.close()

def gzipuncom(fn_in, fn_out):
    f_in = gzip.open(fn_in, 'rb')
    f_out = open(fn_out, 'wb')
    file_content = f_in.read()
    f_out.write(file_content)
    f_out.close()
    f_in.close()


def findfile(base:str):
    for a , b , fs in os.walk(base):
        for f in fs:
            yield f

def findbmp(base:str,extension:str):
	for a , b , fs in os.walk(base):
		for f in fs:
			if f.endswith(extension):
				yield './img/'+f
	yield "videos_layout.bmp"
	yield "./img/frame.txt"
	if os.path.isfile('./img/lossy'):
		yield './img/lossy'

def findext(base:str,extension:str):
	for a , b , fs in os.walk(base):
		for f in fs:
			if f.endswith(extension):
				yield f

def args_parser():

	parser = argparse.ArgumentParser(
		description="A tool to encrypt your video  with a key and encoded audio and images.")
	parser.add_argument("-i", "--input", help="Needed. Input file.")
	parser.add_argument("-o", "--output", help="Needed. Output directory for encrypting and output file for decrypting.")	
	parser.add_argument("--force",action='store_true',help="Optional. Encrypt a video over 150 MB. Default disabled.",default=False)
	parser.add_argument("--fps", help="Optional. Encrypted video fps. Default is 24.",default='24',type=int)
	parser.add_argument("--size", help="Optional. Encrypted video height. Default is 720.",default='720',type=int)
	parser.add_argument("-d","--decrypt",action='store_true',help="Decrypt a video.",default=False)
	parser.add_argument("--key", help="Needed. Decrypt key.")
	parser.add_argument("--ffmpeg", help="Optional. Ffmpeg directory.",default=currdir)
	parser.add_argument("--lossy",help='Optional. Use jpg files. Reduce output size.',action='store_true',default=False)
	args = parser.parse_args()
	if not (args.input and args.output):
		print('Missing arguments.')
		parser.print_help()
		sys.exit(1)
	return parser

def main():
	global ffmpegrun
	ffmpegd = args.ffmpeg
	os.chdir(currdir)
	print(os.path.realpath(ffmpegd+'/ffmpeg.exe'))
	ffmpegrun = os.path.realpath(ffmpegd+'/ffmpeg.exe')
	if platform.system()=='Windows':
		ffmpegrun = os.path.realpath(ffmpegd+'/ffmpeg.exe')
	else:
		ffmpegrun = os.path.realpath(ffmpegd+'/ffmpeg')
	if(platform.system()=='Windows' and not os.path.exists(ffmpegrun)):
		print('Please put ffmpeg binary to current directory and rename to \"ffmpeg\" or \"ffmpeg.exe\"!!!')
		sys.exit(1)
	elif not platform.system()=='Windows' and not os.path.exists(ffmpegrun):
		print('Please put ffmpeg binary to current directory and rename to \"ffmpeg\" or \"ffmpeg.exe\"!!!')
		sys.exit(1)
	if not args.decrypt:
		encv()
	else:
		decv()

def decv():
	input = args.input
	output = args.output

	keyfile = args.key
	
	clean.clean()
	print('Input: {}'.format(input),'\nOutput: {}'.format(output),'\nKey: {}'.format(keyfile))
	if not args.key:
		print('Decryption key needed!!!')
		sys.exit(1)
	if not os.path.isfile(keyfile):
		print('Decryption key not exist!!!')
		sys.exit(1)
	if not (os.path.isfile(output) or os.path.isfile(input)):
		print('File or directory does not exist!!!')
		sys.exit(1)
	print('Decrypting video data...')
	chacha.decrypt_chacha(input,keyfile,'temp.zip')
	print('Decryption complete.\nUncompressing...')
	unzip_file('temp.zip','./img')
	shutil.move('./img/videos_layout.bmp','.')
	encdec.decodevid('videos_layout.bmp','gz')
	gzipuncom('videos_layout_decode.gz','video.mp3')
	print('Uncompression complete.\nDecoding...')
	if os.path.isfile('./img/lossy'):
		imgformat = 'jpg'
	else:
		imgformat = 'png'

	for i in findext('./img','.bmp'):
		encdec.decodevid('./img/'+i,imgformat)
	
	fps = chacha.conint(chacha.read_files('./img/frame.txt'))
	print('Finished.\nConverting video...')
	sizes = os.path.getsize('video.mp3')
	if not output.endswith('.mp4'):
		output = '{}.mp4'.format('.'.join(output.split('.')[:-1]))
	if sizes == 0:
		out_code = subprocess.call([ffmpegrun, '-i',
		os.path.realpath('./img/image-%08d_layout_decode.'+imgformat),'-i','video.mp3','-acodec','aac',
		'-c:v','libx264','-r',str(fps),'-pix_fmt','yuv420p',output], stdout = open('ffmpeg.log','a'), stderr = subprocess.STDOUT)
	else:
		out_code = subprocess.call([ffmpegrun, '-i',
		os.path.realpath('./img/image-%08d_layout_decode.'+imgformat),'-i','video.mp3','-acodec','aac',
		'-c:v','libx264','-r',str(fps),'-pix_fmt','yuv420p',output], stdout = open('ffmpeg.log','a'), stderr = subprocess.STDOUT)
	if not (out_code == 0):
		print("Error converting!")
		sys.exit(1)
	print('Finished.\nCleaning...')
	clean.clean()
	print('Finished.\nDecryption complete.')
def encv():
	input = args.input
	output = args.output
	force = args.force
	fps = args.fps
	size = args.size
	if args.lossy:
		imgformat = 'jpg'
	else:
		imgformat = 'png'
	clean.clean()
	print('Input: {}'.format(input),'\nOutput: {}'.format(output),'\nFps: {}'.format(fps),'\nHeight: {}'.format(size))
	if int(fps) > 120 or int(fps) < 10:
		print('Error: Bad frame rate.')
		sys.exit(1)
	if int(size) > 4000 or int(size) < 10:
		print('Error: Bad video size.')
		sys.exit(1)
	if not (os.path.isfile(output) or os.path.exists(input)):
		print('File or directory does not exist!!!')
		sys.exit(1)
	if filesizeMV(input) > 150 and not force:
		print('Your file is too large. Force encrypt by option --force')
		sys.exit(1)
	print("Converting video to image and audio...")
	
	out_code = subprocess.call([ffmpegrun, '-i',
	input,'-vf','scale=-1:'+str(size),'-r',str(fps),
	os.path.realpath('./img/image-%08d.'+imgformat)], stdout = open('ffmpeg.log','a'), stderr = subprocess.STDOUT)
	if not (out_code == 0):
		print("Error converting!")
		sys.exit(1)
	out_code = subprocess.call([ffmpegrun, '-i',
	input,'-f','mp3','-vn','video.mp3'], stdout = open('ffmpeg.log','a'), stderr = subprocess.STDOUT)
	if not (out_code == 0):
		print("Warning: This video may not have sound or an conversion error occured.")
		fd = open('video.mp3', mode="w", encoding="utf-8")
		fd.close()
	print('Finished.\nEncoding images and audio...')
	for i in findfile('./img'):
		encdec.encodevid('./img/'+i)
	print('Finished.\nCompressing images and audio...')
	gzipcom('video.mp3','videos.gz')
	encdec.encodevid('videos.gz')	
	chacha.w_files('./img/frame.txt',chacha.conbyte(fps))
	if args.lossy:
		chacha.w_files('./img/lossy',b'')
	addzip('temp.zip',findbmp('./img','.bmp'))
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
	print('Finished.Encryption complete.')


	

if __name__ == "__main__":
	parser = args_parser()
	args = parser.parse_args()
	main()
	print("Press enter to exit ...")
	input()