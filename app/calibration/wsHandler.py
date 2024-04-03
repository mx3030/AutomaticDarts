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
        self.ws = websocket.WebSocketApp(f"wss://{ws_host}:{ws_port}/calibration", 
            on_message=self.on_message, 
            on_open=self.on_open 
        )
        ws_thread = threading.Thread(target=self.ws.run_forever)
        ws_thread.start()
        signal.signal(signal.SIGTERM, self.close) 
    
    def on_open(self, ws):
        data = { "pair_id": self.pair_id }
        message = {
            "topic": "start_calibration_offer",
            "data": data
        }
        self.ws.send(json.dumps(message))
 
    def on_message(self, ws, message):
        print(f"calibrationHandler: {message}")
        temp = json.loads(message)
        topic = temp.get("topic")
        data = temp.get("data")
        if topic == "pair_established":
            self.calibrationHandler.sendFrame()

    def close(self, signal_number, frame):
        data = { "pair_id": self.pair_id }
        message = {
            "topic": "stop_calibration_offer",
            "data": data
        }
        self.ws.send(json.dumps(message))
        self.ws.close()

    def send(self, message):
        """
        special send method for direct communication with pair
        """
        data = message.get("data")
        data["pair_id"] = self.pair_id
        data["target"] = "remote"
        self.ws.send(json.dumps(message))
