class WSHandler {
    constructor(webrtcHandler){
        this.ws = new WebSocket("wss://" + IP_ADDRESS + ":" + WS_PORT + "/camera");
        this.webrtcHandler = webrtcHandler;
        this.setupListeners()
    }

    setupListeners(){
        this.ws.onmessage = (message)=>{
            const temp = JSON.parse(message.data);
            const topic = temp.topic;
            const data = temp.data;
            switch(topic) {
                case 'answer':
                    this.webrtcHandler.handleAnswer(data)
                    break; 
            }
        }
    }
 
    send(data){
        this.ws.send(data)
    }
}
