class MediaHandler {
    constructor() {
        this.stream = null;
        this.devices = [];
        this.videoArea = document.getElementById('video-area')
    }

    async getDevices(){
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
            let devices = await navigator.mediaDevices.enumerateDevices();
            devices.forEach((device,index)=>{
                if(device.deviceId != null && device.kind == 'videoinput'){
                    this.devices.push(device)
                }
            })
            return this.devices;
        } catch (error) {
            console.error('Error getting devices:', error);
            throw error;
        }
    }

    async startStream(device){ 
        let deviceId = device["deviceId"]
        let deviceName = device["label"]
        let options;
        if(this._isIOS()){
            options = {
                video: {
                    width: { ideal: 1920 },
                    height: { ideal: 1080 },
                    facingMode: deviceName == 'Frontkamera' ? 'user' : 'environment',
                },
                audio: false
            };
        } else {
            options = {
                video: { deviceId: deviceId ? { exact: deviceId } : undefined },
                audio: false
            };
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia(options);
            this.stream = stream;
        } catch (error) {
            console.error('Error getting stream:', error);
            throw error;
        }
    }

    _isIOS(){
        var isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        return isIOS;
    }

    startVideo(){
        this.videoArea.srcObject = this.stream; 
        this.videoArea.play();
    }

    stopVideo(){
        this.videoArea.srcObject = null;
    }
 
    getStream(){
        return this.stream
    }
}

