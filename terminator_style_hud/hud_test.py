import cv2
import io
import numpy as np
from hud import *
from videostream_202107 import *
import time

import queue
import multiprocessing

image_queue = queue.Queue()

VideoStream(image_queue, resolution=(400,400))
VideoStream.start()

hud = HUD((400, 400))
#hud = HUD((400, 400), False) #or use this to avoid the jittery overlay effect
hr = HUDRunner(hud)
hr.start()


hud.scanner.add_scanner_point((25,25))
hud.scanner.add_scanner_point((75,75))

try:
    while 1:
        try:
            if image_queue.qsize() > 0:
                img = image_queue.get_nowait()
        except:
            pass

        hud.update_frame(img)
        filtered_img = hud.get_current_image()
        resized_img = cv2.resize(filtered_img,(800,800))
        
        cv2.imshow('Object detector2', resized_img)
        cv2.waitKey(1)
        time.sleep(0.01)
except KeyboardInterrupt:
    VideoStream.stop()
    print("stopping threads, this takes a moment...")
    hr.stop()
finally:
    pass
