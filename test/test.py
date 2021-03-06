#!/usr/bin/python3
import sys, cv2
import prand, numpy as np
from time import sleep

assert(len(sys.argv) >= 2)
rtsp_url = sys.argv[1]
gpu_id = 0
if len(sys.argv) > 2:
	gpu_id = int(sys.argv[2])

max_size = 480
def size_fit_limit(size):
	if size[1] >= size[0] and size[1] > max_size:
		return (int((size[0] * max_size) / size[1]), max_size)
	if size[0] >= size[1] and size[0] > max_size:
		return (max_size, int((size[1] * max_size) / size[0]))
	return size

dec = prand.Prand(gpu_id)
dec.set_jpeg_quality(75)

ret, frame_size = dec.start(rtsp_url)
last_frame_id = 0
while True:
	frame_id, img1, jpeg = dec.get_frame(True)
	print('frame_id:', frame_id)
	if frame_id < 0:
		status = dec.get_current_status()
		dec.stop()
		if status == 0:
			break
		last_frame_id = 0
		sleep(0.1)
		ret, frame_size = dec.start(rtsp_url)
	elif frame_id > last_frame_id:
		last_frame_id = frame_id
		limited_size = size_fit_limit((frame_size[0], frame_size[1]))
		img1 = cv2.resize(img1, limited_size)
		jpeg = np.frombuffer(jpeg, dtype="uint8")
		img2 = cv2.imdecode(jpeg, cv2.IMREAD_COLOR)
		img2 = cv2.resize(img2, limited_size)
		if img1 is None:
			img1 = np.zeros((limited_size[1], limited_size[0], 3), np.uint8)
			img2 = np.zeros((limited_size[1], limited_size[0], 3), np.uint8)
		cv2.imshow("Downloaded from GPU", img1)
		cv2.imshow("Decode From JPEG", img2)
		key = cv2.waitKey(1) & 0xFF
		if key == 27:
			break
	else:
		sleep(0.001)

dec.stop()
