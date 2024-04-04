class Main {
    constructor(){ 
        this.wsHandler = new WSHandler(this);

        this.calMenu = document.getElementById('select-cal-source'); 
        this.calReloadButton = document.getElementById('btn-cal-reload');
        this.calStartButton = document.getElementById('btn-cal-start');
        this.calStopButton = document.getElementById('btn-cal-stop');
        this.calStopButton.disabled = true;
        this.pair_id = null;

        this.setupEventListeners();
    }

    setupEventListeners(){
        this.calReloadButton.addEventListener('click', ()=>{
            this.handleReloadEvent();
        });
        this.calStartButton.addEventListener('click', ()=>{
            this.handleStartEvent();
        });
        this.calStopButton.addEventListener('click', ()=>{
            this.handleStopEvent();
        });

    }

    handleReloadEvent(){
        let message = { "topic": "get_calibration_offers" };
        this.wsHandler.send(message);
    }

    fillCalMenu(cal_offers){
        // gets called from message event in wsHandler
        this.calMenu.innerHTML = "";
        cal_offers.forEach((offer) => {
            let calItem = document.createElement("option");
            let parts = offer.split('/');
            calItem.innerText = parts[parts.length-1];
            calItem.value = offer;
            this.calMenu.appendChild(calItem);
        });
    }

    handleStartEvent(){
        let calIndex = this.calMenu.selectedIndex;
        let calOption = this.calMenu[calIndex];
        this.pair_id = calOption.value;
        if(this.pair_id){
            let data = {
                "pair_id": this.pair_id
            };
            let message = {
                "topic": "join_calibration_pair",
                "data": data
            };
            this.wsHandler.send(message);
        }
    }

    handlePairEstablished(){
        this.calStartButton.disabled = true;
        this.calMenu.disabled = true;
        this.calStopButton.disabled = false;
    }

    handleStopEvent(){
        let data = {
            "pair_id": this.pair_id,
        } 
        let message = {
            "topic": "disjoin_calibration_pair",
            "data": data
        }
        this.wsHandler.send(message);
        this.connectedPair = null;
        this.calStartButton.disabled = false;
        this.calMenu.disabled = false;
        this.calStopButton.disabled = true;
        this.handleReloadEvent();
    }

}

window.onload = function() {
    new Main();
};

