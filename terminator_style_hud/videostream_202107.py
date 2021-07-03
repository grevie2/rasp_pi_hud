import picamera
import io
import cv2
import numpy as np

from threading import Thread
import time

"""
with picamera.PiCamera() as camera:
    stream = picamera.streams.PiCameraCircularIO(camera, seconds=10)
    
    camera.resolution = (800, 800)
    camera.hflip = True
    camera.vflip = True
    #camera.start_preview()
    camera.start_recording(stream, format='mjpeg')
    #camera.wait_recording(10)
    
    
    for i in range(0,100): #however long it takes to loop around 100 times
        image_stream = io.BytesIO()
        camera.capture(image_stream, use_video_port=True, format='jpeg')
        data = np.frombuffer(image_stream.getvalue(), dtype=np.uint8)    
        # "Decode" the image from the array, preserving colour
        image = cv2.imdecode(data, 1)
        # OpenCV returns an array with data in BGR order. If you want RGB instead
        # use the following...
        #image = image[:, :, ::-1]
        cv2.imshow('Object detector', image)
        cv2.waitKey(1) #show the image onscreen for 1 ms
    
    #camera.wait_recording(10)
    camera.stop_recording()
"""    

class VideoStream:
    """Camera object that controls video streaming from the Picamera"""
    @staticmethod     
    def __init__(image_queue, resolution=(800,800), framerate=30):
        VideoStream.keep_going = False
        
        VideoStream.camera = picamera.PiCamera()
        VideoStream.stream = picamera.streams.PiCameraCircularIO(VideoStream.camera, seconds=5)
        VideoStream.camera.resolution = resolution
        VideoStream.camera.hflip = True
        VideoStream.camera.vflip = True
        VideoStream.camera.framerate = 30
        VideoStream.image_queue = image_queue
    
        #grab the first frame so we are always ready to return something
        data = io.BytesIO()
        # Create a blank 300x300 black image
        data = np.zeros((800, 800, 3), np.uint8)
        # Fill image with red color(set each pixel to red)
        data[:] = (0, 0, 255)
        VideoStream.frame = data

    @staticmethod     
    def start():
        if VideoStream.keep_going == False:
            VideoStream.keep_going = True
            VideoStream.t = Thread(target=VideoStream.update,args=())
            VideoStream.t.start()
    
    @staticmethod     
    def update():
        
        VideoStream.camera.start_recording(VideoStream.stream, format='h264')
            
        while VideoStream.keep_going:
            #grab the next frame from the stream
            image_stream = io.BytesIO()
            VideoStream.camera.capture(image_stream, use_video_port=True, format='jpeg')
            data = np.frombuffer(image_stream.getvalue(), dtype=np.uint8)    
            # "Decode" the image from the array, preserving colour
            image = cv2.imdecode(data, 1)
            VideoStream.frame = image
            
            #put frame on queue
            while VideoStream.image_queue.qsize() > 0:
                pass
                
            VideoStream.image_queue.put(VideoStream.frame)
            
            time.sleep(0.05)
              
        VideoStream.camera.stop_recording()
            
    @staticmethod                 
    def read():
        # Return the most recent frame
        return VideoStream.frame
        
    @staticmethod         
    def stop():
        if VideoStream.keep_going == True:
            VideoStream.keep_going = False
            
            #VideoStream.image_queue.queue.clear()
            while VideoStream.t.isAlive():
                pass
            cv2.destroyAllWindows()
