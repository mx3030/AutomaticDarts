import pickle
import cv2 as cv
import base64
from calibration.wsHandler import WSHandler

class CalibrationHandler:
    def __init__(self, ws_host, ws_port, pipeHandler):
        self.pipeHandler = pipeHandler
        pair_id = self.pipeHandler.pipe_path
        self.wsHandler = WSHandler(self, ws_host, ws_port, pair_id)
        
        # calibration data
        self.start_image = None
        self.bin_image = None
        self.contours = []
        self.contour = None
    
    def start(self):
        self.start_image = self.pipeHandler.getFrame()
        self.send_image(self.start_image)
        
    def image2remote(self, frame):
        """
        send image to remote interface
        """
        ret, buf = cv.imencode('.jpg', frame)
        if not ret:
            print("Error: Failed to encode frame as JPEG")
            return
        base64_image = base64.b64encode(buf).decode('utf-8') 
        message = {
            "topic": "update_cal_img",
            "data": {
                "cal_img": base64_image
            }
        } 
        self.wsHandler.send2remote(message)

    def img_pre_processing(self, data):
        """
        use filters to get binary black and white image for further operations
        """
        blur_kernel = int(data.get("blur"))
        thresh_value = int(data.get("thresh"))
        morph_value = int(data.get("morph"))
 
        blur=cv.blur(self.start_image,(blur_kernel,blur_kernel))
        hsv = cv.cvtColor(blur,cv.COLOR_BGR2HSV)
        h,s,v = cv.split(hsv)
        _,thresh = cv.threshold(v,thresh_value,255,cv.THRESH_BINARY_INV)
        morph_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (2*morph_value + 1, 2*morph_value+1), (morph_value, morph_value))
        self.bin_image = cv.morphologyEx(thresh, cv.MORPH_CLOSE, morph_kernel)
        self.image2remote(self.bin_image)

    def get_contours(self):
        contours,_ = cv.findContours(self.bin_image,cv.RETR_LIST,cv.CHAIN_APPROX_SIMPLE)
        self.contours = sorted(contours, key=cv.contourArea)
        data = {
            "contour_number": len(self.contours)
        }
        message = {
            "topic": "update_contour_number",
            "data": data
        }
        self.wsHandler.send2remote(message) 

    def draw_contour(self, data):
        contour_index = int(data.get("contour_index"))
        copy = self.start_image.copy()
        cv.drawContours(copy,self.contours,contour_index,(0,255,0),2)
        self.contour = self.contours[contour_index]
        self.image2remote(copy)
