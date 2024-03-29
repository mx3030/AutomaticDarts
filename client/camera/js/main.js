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
        this.pipeControl = document.getElementById('pipe-control')
        this.startPipeButton = document.getElementById('btn-pipe-start');
        this.stopPipeButton = document.getElementById('btn-pipe-stop');
      
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
        this.startPipeButton.addEventListener('click', ()=>{
            this.handleStartPipeEvent();
        })
        this.stopPipeButton.addEventListener('click', ()=>{
            this.handleStopPipeEvent();
        })
    }

    handleStartEvent(){
        let deviceIndex = this.videoMenu.selectedIndex;
        this.mediaHandler.startStream(this.mediaHandler.devices[deviceIndex]).then(async () => {
            this.startButton.disabled = true;
            this.stopButton.disabled = false; 
            this.mediaHandler.startVideo(); 
            await this.connectWebRTC();
            this.pipeControl.classList.remove('d-none')
            this.pipeControl.classList.add('d-flex')
            this.startPipeButton.disabled = false;
            this.stopPipeButton.disabled = true;
        })
    }

     async connectWebRTC(){
        this.webrtcHandler.addStream(this.mediaHandler.getStream())
        let message = await this.webrtcHandler.createOffer()
        if(message) {
            this.wsHandler.send(message)
        }
    }
 
    handleStopEvent(){
        this.startButton.disabled = false;
        this.stopButton.disabled = true;
        this.mediaHandler.stopVideo();
        this.pipeControl.classList.add('d-none')
        this.pipeControl.classList.remove('d-flex')
    } 

    handleStartPipeEvent(){ 
        this.startPipeButton.disabled = true;
        this.stopPipeButton.disabled = false;
        let message = { "topic": "start" } 
        this.wsHandler.send(message)
    }

    handleStopPipeEvent(){
        this.startPipeButton.disabled = false;
        this.stopPipeButton.disabled = true;
        let message = { "topic": "stop" }
        this.wsHandler.send(message)
    }

}

window.onload = function() {
    new Main();
};

