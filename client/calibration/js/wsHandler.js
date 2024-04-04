class WSHandler {
    constructor(main){
        this.ws = new WebSocket("wss://" + IP_ADDRESS + ":" + WS_PORT + "/calibration");
            this.main = main;
            this.calibrationHandler = new CalibrationHandler(this);
            this.setupListeners()
    }

    setupListeners(){
        this.ws.onmessage = (message)=>{
            //console.log(message)
            const temp = JSON.parse(message.data);
            const topic = temp.topic;
            const data = temp.data;
            switch(topic) {
                // for basic setup
            case 'calibration_offers':
                this.main.fillCalMenu(data["calibration_offers"]);
                break;
            case 'pair_established':
                this.main.handlePairEstablished();
                break;
            case 'stop_calibration_offer':
                this.main.handleStopEvent();
                break;

                // for actual calibration
            case 'update_cal_img':
                this.calibrationHandler.update_cal_img(data["cal_img"]);
                break;
            case 'update_contour_number':
                this.calibrationHandler.update_contour_number(data["contour_number"]);
                break;
            }
        }
    }

    send(message){
        this.ws.send(JSON.stringify(message))
    }

    send2local(message) {
        if (!message.hasOwnProperty('data')) {
            message.data = {};
        }
        message.data["pair_id"] = this.main.pair_id;
        message.data["target"] = "local";
        this.send(message);
    }

}
