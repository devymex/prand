#!/usr/bin/python3

import prand, cv2, numpy as np

dec = prand.Prand('rtsp://10.201.105.94/user=admin&password=&channel=1&stream=0.sdp', 1)
dec.start()
while True:
	frame_id, img1, jpeg = dec.get_frame(True)
	if frame_id > 0:
		jpeg = np.frombuffer(jpeg, dtype="uint8")
		img2 = cv2.imdecode(jpeg, cv2.IMREAD_COLOR)

		img1 = cv2.resize(img1, (960, 540))
		img2 = cv2.resize(img2, (960, 540))
		cv2.imshow("Downloaded from GPU", img1)
		cv2.imshow("Decode From JPEG", img2)
		key = cv2.waitKey(1) & 0xFF
		if key == 27:
			break
	#break
dec.stop()
