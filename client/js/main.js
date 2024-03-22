// IP_ADDRESS and WS_PORT are added dynamically to index.html by server according to config.ini

class Main {
    constructor(){
        this.mediaHandler = new MediaHandler();
        this.webrtcHandler = new WebRTCHandler();
        
        this.wsHandler = new WSHandler(
            this.webrtcHandler,
        );
        
        // setup source selection
        this.videoMenu = document.getElementById('select-video-source');
        this.mediaHandler.getDevices().then(devices => {
            this.fillVideoMenu(devices);
        }); 
        
        // setup control elements
        this.startButton = document.getElementById('btn-stream-start');
        this.startButton.disabled = false;
        this.stopButton = document.getElementById('btn-stream-stop');
        this.stopButton.disabled = true;
        
        this.leftPosition = document.getElementById('btn-position-left');
        this.rightPosition = document.getElementById('btn-position-right');
        this.position = 'left'

        this.sendArea = document.getElementById('send-area')
        this.sendPhotoButton = document.getElementById('btn-send-photo');

        this.setupEventListeners();
    }
    
   
    fillVideoMenu(devices){
        devices.forEach((device, index) => {
            let videoItem = document.createElement("option");
            videoItem.innerText = device["label"];
            videoItem.value = index;
            this.videoMenu.appendChild(videoItem);
        });
    }

    setupEventListeners(){
        this.startButton.addEventListener('click', async ()=>{
            this.handleStartEvent();
        });
        this.stopButton.addEventListener('click', ()=>{
            this.handleStopEvent();
        });
        this.leftPosition.addEventListener('click', ()=>{
            this.handlePositionEvent();
        });
        this.rightPosition.addEventListener('click', ()=>{
            this.handlePositionEvent();
        });
        this.sendPhotoButton.addEventListener('click', ()=>{
            this.handleSendPhotoEvent();
        });
    }

    handleStartEvent(){
        let deviceIndex = this.videoMenu.selectedIndex;
        this.mediaHandler.startStream(this.mediaHandler.devices[deviceIndex]).then(async () => {
            // change view
            this.startButton.disabled = true;
            this.stopButton.disabled = false;
            this.leftPosition.disabled = true;
            this.rightPosition.disabled = true;
            this.sendArea.classList.remove("d-none");
            this.sendArea.classList.add("d-flex"); 
            this.mediaHandler.startVideo();
            
            // use ws connection 
            this.sendPosition();
            await this.connectWebRTC();
        })
    }

     async connectWebRTC(){
        this.webrtcHandler.addStream(this.mediaHandler.getStream())
        let message = await this.webrtcHandler.createOffer()
        if(message) {
            this.wsHandler.send(JSON.stringify(message))
        }
    }

    sendPosition(){
        let data = {
            "position" : this.position
        }
        let message = {
            "topic": "position",
            "data" : data
        }
        this.wsHandler.send(JSON.stringify(message));
    }

    handleStopEvent(){
        this.startButton.disabled = false;
        this.stopButton.disabled = true;
        this.mediaHandler.stopVideo();
        this.sendArea.classList.remove("d-flex")
        this.sendArea.classList.add("d-none")
    }

    handlePositionEvent(){
        if(this.leftPosition.checked) {
            this.position = 'left';
        } else {
            this.position = 'right';
        }
    }
     
    handleSendPhotoEvent(){ 
        let data = {
            "img" : this.mediaHandler.takePhoto(),
        };
        let message = {
            "topic": "photo",
            "data": data,
        };
        this.wsHandler.send(JSON.stringify(message));
    }

}

window.onload = function() {
    new Main();
};

