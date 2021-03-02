from PIL import Image
import math
import base64
import sys

def decode(im):
	width, height = im.size
	lst = [ ]
	for y in range(height):
		for x in range(width):
			red, green, blue = im.getpixel((x, y))
			if (blue | green | red) == 0:
				break
			
			index = (green << 8) + blue
			lst.append( chr(index) )

	return ''.join(lst)

def decodevid(filename:str,extension:str):

	all_text = decode(Image.open(filename))
	all_text = base64.b64decode(all_text)
	with open("{}_decode.".format('.'.join(filename.split('.')[:-1]))+extension, "wb") as f:
		f.write(all_text)
def encode(text):
	str_len = len(text)
	width = math.ceil(str_len**0.5)
	im = Image.new("RGB", (width, width), 0x0)

	x, y = 0, 0
	for i in text:
		index = ord(i)
		rgb = ( 0,  (index & 0xFF00) >> 8,  index & 0xFF)
		im.putpixel( (x, y),  rgb )
		if x == width - 1:
			x = 0
			y += 1
		else:
			x += 1
	return im

def encodevid(filename: str):
	
    with open(filename, 'rb') as f:
        all_text = str(base64.b64encode(f.read()), encoding = 'utf-8')
        
    im = encode(all_text)
    im.save("{}_layout.bmp".format('.'.join(filename.split('.')[:-1])))
