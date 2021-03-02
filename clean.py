import os
import os.path

def clean():
	if not os.path.exists(os.path.realpath('./img')):
		os.mkdir(os.path.realpath('./img'))
	else:
		del_file(os.path.realpath('./img'))
	try_remove('ffmpeg.log')
	try_remove('video.mp3')
	try_remove('videos.gz')
	try_remove('videos_layout.bmp')
	try_remove('temp.zip')
	try_remove('videos_layout_decode.gz')
	try_remove('videos_layout_decode.jpg')

def del_file(path):
	for i in os.listdir(path):
		path_file = os.path.join(path,i)
		if os.path.isfile(path_file):
			os.remove(path_file)
		else:
			del_file(path_file)

def try_remove(name:str):
	if os.path.isfile(name):
		os.remove(name)
