import os
import os.path

def clean():
	if not os.path.exists(os.path.realpath('./img')):
		os.mkdir(os.path.realpath('./img'))
	else:
		del_file(os.path.realpath('./img'))
	if os.path.isfile('ffmpeg.log'):
		os.remove('ffmpeg.log')
	if os.path.isfile('video.mp3'):
		os.remove('video.mp3')
	if os.path.isfile('videos.gz'):
		os.remove('videos.gz')
	if os.path.isfile('videos_layout.bmp'):
		os.remove('videos_layout.bmp')
	if os.path.isfile('temp.zip'):
		os.remove('temp.zip')

def  del_file(path):
	for i in os.listdir(path):
		path_file = os.path.join(path,i)
		if os.path.isfile(path_file):
			os.remove(path_file)
		else:
			del_file(path_file)
