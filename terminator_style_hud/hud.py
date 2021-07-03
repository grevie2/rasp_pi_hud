import cv2
import io
import numpy as np
import threading
import time
from PIL import Image
from multiprocessing import Process
import multiprocessing
import random

class Widget():
    def __init__(self, resolution):
        self.empty_buffer = np.zeros((resolution[0], resolution[1], 4), np.uint8)
        self.empty_buffer[:] = (0, 0, 0, 0) #last param determines opaqueness
        
        self.overlay = np.zeros((resolution[0], resolution[1], 4), np.uint8)
        self.overlay[:] = (0, 0, 0, 0)
        
        self.resolution = resolution
        
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.fontColor = (255,255,255, 255)
        self.lineType = 2
        
    def draw(self):
        raise NotImplementedError
        
    def fade(self):
        raise NotImplementedError
        
    def reset_widget(self):
        # Create a blank black image
        self.overlay = np.zeros((self.resolution[0], self.resolution[1], 4), np.uint8)
        
    def leave_on_delay(self):
        return random.randint(0,4)
        
    def calc_point_x(self, x):
        return int(self.origin_x + self.widget_width/100 * x)
        
    def calc_point_y(self, y):
        return int(self.origin_y + self.widget_height/100 * y)

class LineBasedWidget(Widget):
    def __init__(self, resolution):
        super().__init__(resolution)
        
    def draw_line(self, layer, x1, y1, x2, y2, width=1, color=(255, 255, 255, 255)):
        cv2.line(layer, 
        (self.calc_point_x(x1), self.calc_point_y(y1)),
        (self.calc_point_x(x2), self.calc_point_y(y2)),
        color, width
        )
        
    def draw_point(self, layer, pt, radius=2, color=(255,255,255), width=-1):
        cv2.circle(layer,
        (self.calc_point_x(pt[0]), self.calc_point_y(pt[1])),
        radius,
        color,
        width
        )

class Scanner(LineBasedWidget):
    def __init__(self, resolution):
        super().__init__(resolution)
        
        self.num_x_points = 100
        self.num_y_points = 100

        self.grid = np.zeros((resolution[0], resolution[1], 4), np.uint8)
        self.grid[:] = (0, 0, 0, 0)
        
        self.is_init = False
        self.scanner_points = []
        self.point_radius = 10

    def draw_vertical_lines(self):
        for i in range(0, self.num_x_points, 10):
            self.draw_line(self.grid, i, 0, i, 100)
    
    def draw_horizontal_lines(self):
        for i in range(0, self.num_y_points, 10):
            self.draw_line(self.grid, 0, i, 100, i)
    
    def add_scanner_point(self, pt):
        self.scanner_points.append(pt)
        
    def draw_scanner_points(self):
        for pt in self.scanner_points:
            #cv2.circle(self.overlay, pt, self.point_radius, (255,255,255), -1) 
            self.draw_point(self.overlay, pt)
        
    def draw_grid(self):
        self.draw_grid_border()
        self.draw_vertical_lines()
        self.draw_horizontal_lines()

    def draw_grid_border(self):
        self.draw_line(self.grid, 0,0, 100,0, 2)
        self.draw_line(self.grid, 100,0, 100,100, 2)
        self.draw_line(self.grid, 100,100, 0,100, 2)
        self.draw_line(self.grid, 0,100, 0,0, 2)
        
    def draw(self):
        self.draw_grid()
        self.grid_buffer = self.grid 
        for j in range(0,2):
            self.complete_scan_cycle()
        self.fade()
        time.sleep(1)
    
    def fade(self):
        self.empty_buffer = np.zeros((self.resolution[0], self.resolution[1], 4), np.uint8) #new
        self.empty_buffer[:] = (0, 0, 0, 0)
            
        self.overlay = np.zeros((self.resolution[0], self.resolution[1], 4), np.uint8)
        for i in range(0, 8):
            self.grid = self.grid_buffer
            time.sleep(0.1)
            self.grid = self.empty_buffer
            time.sleep(0.1)
            
    def complete_scan_cycle(self):
        #cycle L2RT2B
        for i in range(0, 101, 4):
            self.reset_widget()
            self.draw_scanner_points()
            self.draw_line(self.overlay, i, 0, i, 100, 2)
            self.draw_line(self.overlay, 0, i, 100, i, 2)
            time.sleep(0.025)
        
        #cycle L2RT2B
        for i in range(101, 0, -4):
            self.reset_widget()
            self.draw_scanner_points()
            self.draw_line(self.overlay, i, 0, i, 100, 2)
            self.draw_line(self.overlay, 0, i, 100, i, 2)
            time.sleep(0.025)

class Compass(LineBasedWidget):
    def __init__(self, resolution):
        super().__init__(resolution)
        
    def draw(self, width):
        self.reset_widget()
        self.draw_line(self.overlay, 50, 50, 50, 0, width) #N
        time.sleep(0.2)
        
        self.draw_line(self.overlay, 50, 50, 90, 10, width) #NE
        time.sleep(0.2)
        
        self.draw_line(self.overlay, 50, 50, 100, 50, width) #E
        time.sleep(0.2)
       
        self.draw_line(self.overlay, 50, 50, 90, 90, width) #SE
        time.sleep(0.2)
       
        self.draw_line(self.overlay, 50, 50, 50, 100, width) #S
        time.sleep(0.2)
       
        self.draw_line(self.overlay, 50, 50, 10, 90, width) #SW
        time.sleep(0.2)
        
        self.draw_line(self.overlay, 50, 50, 0, 50, width) #W
        time.sleep(0.2)
        
        self.draw_line(self.overlay, 50, 50, 10, 10, width) #NW
        time.sleep(0.2)
        
        self.draw_compass_labels()
        
        time.sleep(self.leave_on_delay())
        self.fade()
        time.sleep(2) #delay until next compass
        
    def draw_compass_labels(self):
        cv2.putText(self.overlay, "N", (self.calc_point_x(45), self.calc_point_y(-10) ), self.font, 0.4, self.fontColor, 2)
        cv2.putText(self.overlay, "E", (self.calc_point_x(110), self.calc_point_y(55) ), self.font, 0.4, self.fontColor, 2)
        cv2.putText(self.overlay, "S", (self.calc_point_x(45), self.calc_point_y(120) ), self.font, 0.4, self.fontColor, 2)
        cv2.putText(self.overlay, "W", (self.calc_point_x(-20), self.calc_point_y(55) ), self.font, 0.4, self.fontColor, 2)
        
    def fade(self):
        self.overlay_buffer = self.overlay
        for i in range(0, 8):
            self.overlay = self.overlay_buffer
            time.sleep(0.1)
            self.overlay = self.empty_buffer
            time.sleep(0.1)

class Text(Widget):
    def __init__(self, text, resolution):
        super().__init__(resolution)
        self.text = text
        
    def draw(self, fontScale=0.3):
        lineType = 2
        x = self.origin_x
        y = self.origin_y
        
        self.reset_widget()
        time.sleep(1)

        for i, line in enumerate(self.text.split('\n')):
            y = y + 15
            cv2.putText(self.overlay, line, (x, y ), self.font, fontScale, self.fontColor, lineType)
            time.sleep(0.1)
            
        time.sleep(self.leave_on_delay())
        self.fade()
        time.sleep(1.5) #time till next text display
    
    def fade(self):
        self.overlay_buffer = self.overlay
        for i in range(0, 8):
            self.overlay = self.overlay_buffer
            time.sleep(0.1)
            self.overlay = self.empty_buffer
            time.sleep(0.1)
        
class PrintedText(Widget):
    def __init__(self, text, resolution):
        super().__init__(resolution)
        self.text = text

    def draw(self, fontScale=0.6):
        lineType = 2
        x = self.origin_x
        y = self.origin_y
        thickness = 3 #must be 3 else cursor does not look right
        
        time.sleep(1)

        text_width, text_height = cv2.getTextSize(self.text, self.font, fontScale, thickness)[0]
        x = int((self.resolution[0]/2) - (text_width/2))
        
        for i in range(0, len(self.text)):
            line = self.text[:i+1]
            
            #the cursor writes to overlay so we need to reset overlay
            self.reset_widget()
            cv2.putText(self.overlay, line, (x, y ), self.font, fontScale, self.fontColor, lineType)
            
            cursor_width, cursor_height = cv2.getTextSize("Z", self.font, fontScale, thickness)[0]
            text_width, text_height = cv2.getTextSize(line, self.font, fontScale, thickness)[0]
            cursor_x = x + text_width
            cursor_y = self.origin_y - text_height
            magic_number_two = 2 #it doesn't quite display right without this - don't know why yet
            
            cv2.rectangle(self.overlay, (cursor_x, cursor_y), (cursor_x + cursor_width, cursor_y + text_height + magic_number_two), (255,255,255,255), -1)
            time.sleep(0.02)

        time.sleep(0.5) #leave on delay
        self.fade()
        time.sleep(3) #how long to wait until we show the next printed text
            
    def fade(self):
        self.overlay_buffer = self.overlay
        for i in range(0, 8):
            self.overlay = self.overlay_buffer
            time.sleep(0.1)
            self.overlay = self.empty_buffer
            time.sleep(0.1)
        
class Runner():
    def __init__(self, widget):
        self.widget = widget
        self.keep_going = False
                
    def run(self):
        while self.keep_going == True:
            self.widget.draw()
        
    def start(self):
        if self.keep_going == False:
            self.keep_going = True
            self.t = threading.Thread(target=self.run, args=())
            self.t.start()
        
    def stop(self):
        if self.keep_going == True:
            self.keep_going = False
            while self.t.isAlive():
                pass

class CompassRunner(Runner):     
    def run(self):
        while self.keep_going:
            self.widget.draw(width=2)
        
class HUDRunner():
    def __init__(self, hud):
        self.hud = hud
        self.keep_going = False
        
    def start(self):
        if self.keep_going == False:
            self.keep_going = True
            self.hud.start_threads()
            self.t = threading.Thread(target=self.run, args=())
            self.t.start()
            
    def stop(self):
        if self.keep_going:
            self.hud.stop_threads() #stop everything started
            self.keep_going = False
            while self.t.isAlive():
                pass

    def run(self):
        while self.keep_going:
            self.hud.draw()

class HUD():
    def __init__(self, resolution, use_juddery_image=True):
        self.resolution = resolution
        self.scanner = Scanner(resolution)
        self.compass = Compass(resolution)                
        self.text = Text("OBJECT DETECTION RUNNING\nSEARCHING FOR OBJECT\nDROPPED OBJECTS: 0\nNUM OBJECTS DETECTED: TBC\nAVG OBJECT DST: TBC\nMAX BDR DST: TBC\nTOTAL OBJECTS DETECTED: TBC\n", resolution)
        self.text2 = Text("OBJECT DETECTION RUNNING\nSEARCHING FOR OBJECT\nDROPPED OBJECTS: 0\nNUM OBJECTS DETECTED: TBC\nAVG OBJECT DST: TBC\nMAX BDR DST: TBC\nTOTAL OBJECTS DETECTED: TBC\n", resolution)
        self.printed_text = PrintedText(" NO OBJECTS MATCHED", resolution)
                
        width = resolution[0]
        height = resolution[1]
        
        self.resolution = resolution
        
        #the hud dictates the size and position of the widgets
        self.scanner.widget_height = height * 0.2 
        self.scanner.widget_width = width * 0.2
        self.scanner.origin_x = int(width * 0.05)
        self.scanner.origin_y = int(height * 0.7)
       
        self.compass.widget_height = height * 0.2 
        self.compass.widget_width = width * 0.2
        self.compass.origin_x = int(width * 0.7)
        self.compass.origin_y = int(height * 0.1)
        
        self.text.origin_x = int(width * 0.05)
        self.text.origin_y = int(height * 0.05)
        
        self.text2.origin_x = int(width * 0.6)
        self.text2.origin_y = int(height * 0.65)
        
        self.printed_text.origin_x = int(width * 0.05)
        self.printed_text.origin_y = int(height * 0.5)
        
        #set default image to ensure system doesn't complain that it doesn't have one yet
        self.out_frame = np.zeros((width, height, 4), np.uint8)
        self.out_frame[:] = (0, 0, 255, 0)
        self.in_frame = np.zeros((width, height, 4), np.uint8)
        self.in_frame[:] = (0, 0, 255, 0)
        
        #set master layer image to ensure system doesn't complain that it doesn't have one yet
        self.master_layer = np.zeros((width, height, 4), np.uint8)
        self.master_layer[:] = (0, 0, 255, 0)
        
        #default filtered background
        self.filtered_background = np.zeros((width, height, 4), np.uint8) 
        self.filtered_background[:] = (0, 0, 255, 0)
        
        self.use_juddery_image = use_juddery_image
                    
    def start_threads(self):
        self.cr = CompassRunner(self.compass)
        self.cr.start()
        
        self.sr = Runner(self.scanner)
        self.sr.start()
        
        self.tr1 = Runner(self.text)
        self.tr1.start()
        
        self.tr2 = Runner(self.text2)
        self.tr2.start()
        
        self.ptr = Runner(self.printed_text)
        self.ptr.start()
                        
        time.sleep(0.5)
        
    def stop_threads(self):
        self.cr.stop()
        self.sr.stop()
        self.tr1.stop()
        self.tr2.stop()
        self.ptr.stop()
        
    def draw(self):                
        background = cv2.cvtColor(self.in_frame, cv2.COLOR_RGB2RGBA)                            
        self.filtered_background = self.add_red_filter(background)        
        temp = self.compass.overlay + self.scanner.overlay + self.scanner.grid + self.text.overlay + self.text2.overlay + self.printed_text.overlay
        
        if self.use_juddery_image:
            if random.randint(0,5) > 4:
                temp = self.apply_judder(temp, -1)
        
        self.master_layer = cv2.add(self.filtered_background, temp)

    def add_red_filter(self, frame):
        overlay = np.zeros((self.resolution[0], self.resolution[1], 4), np.uint8)
        overlay[:] = (0, 0, 255, 255)
        alpha = 0.5
        beta = ( 1.0 - alpha );
        output_image = cv2.addWeighted(overlay, alpha, frame, beta, 0.0)
        return output_image

    def apply_judder(self, frame, vertical_shift):
        num_rows, num_cols = frame.shape[:2]
        translation_matrix = np.float32([ [1,0,0], [0,1,vertical_shift] ])
        img_translation = cv2.warpAffine(frame, translation_matrix, (num_cols, num_rows))
        return img_translation
        
    def update_frame(self, frame):
        self.in_frame = frame
        
    def get_current_image(self):
        return self.master_layer
