import websocket
import threading
import signal
import json

class WSHandler:
    """
    websocket client for calibration
    """
    def __init__(self, calibrationHandler, ws_host, ws_port, pair_id): 
        self.calibrationHandler = calibrationHandler
        self.pair_id = pair_id
        self.pair_established = False
        
        self.ws = websocket.WebSocketApp(f"wss://{ws_host}:{ws_port}/calibration", 
            on_message=self.on_message, 
            on_open=self.on_open 
        )
        ws_thread = threading.Thread(target=self.ws.run_forever)
        ws_thread.start()
        
        # handle subprocess termination from ws server
        signal.signal(signal.SIGTERM, self.close) 
    
    def on_open(self, ws):
        data = { "pair_id": self.pair_id }
        message = {
            "topic": "start_calibration_offer",
            "data": data
        }
        self.ws.send(json.dumps(message))
 
    def on_message(self, ws, message):
        temp = json.loads(message)
        topic = temp.get("topic")
        data = temp.get("data")
        
        print(f"calibrationHandler: {topic}")
        
        if topic == "pair_established":
            self.pair_established = True
            self.calibrationHandler.start()
        elif topic == "disjoin_calibration_pair":
            self.pair_established = False
        elif topic == "img_pre_processing":
            self.calibrationHandler.img_pre_processing(data)
        elif topic == "get_contours":
            self.calibrationHandler.get_contours()
        elif topic == "selected_contour":
            self.calibrationHandler.draw_contour(data)

    def close(self, signal_number, frame):
        data = { "pair_id": self.pair_id }
        message = {
            "topic": "stop_calibration_offer",
            "data": data
        }
        self.ws.send(json.dumps(message))
        self.ws.close()

    def send2remote(self, message):
        """
        special send method for direct communication with pair
        """
        if self.pair_established:
            data = message.get("data")
            data["pair_id"] = self.pair_id
            data["target"] = "remote"
            self.ws.send(json.dumps(message)) 
