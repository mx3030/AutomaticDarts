class CalibrationHandler {
    constructor(wsHandler){
        this.wsHandler = wsHandler;
        
        this.calArea = document.getElementById("cal-area");
        this.calImg = document.getElementById("cal-img");
        
        this.imgProProcessingButton = document.getElementById("btn-img-pre-processing");

        // blur
        this.blurSlider = document.getElementById("blur-slider");
        this.blurLabel = document.getElementById("blur-label");
        this.blurValue = this.blurSlider.value;

        // thresh
        this.threshSlider = document.getElementById("thresh-slider");
        this.threshLabel = document.getElementById("thresh-label");
        this.threshValue = this.threshSlider.value;

        // morph
        this.morphSlider = document.getElementById("morph-slider");
        this.morphLabel = document.getElementById("morph-label");
        this.morphValue = this.morphSlider.value;
        
        this.searchBestContourButton = document.getElementById("btn-search-best-contour");

        // contour
        this.contourSlider = document.getElementById("contour-slider");
        this.contourLabel = document.getElementById("contour-label");
        this.contourValue = this.contourSlider.value;

        this.setupEventListeners()
    }

    setupEventListeners(){
        this.imgProProcessingButton.addEventListener("click", ()=>{
            this.send_img_pre_processing()
        })
        this.blurSlider.addEventListener("input", ()=>{
            this.blurValue = this.blurSlider.value
            this.blurLabel.innerHTML = this.blurValue
        });
        this.blurSlider.addEventListener("change", ()=>{
            this.send_img_pre_processing()
        });
        this.threshSlider.addEventListener("input", ()=>{
            this.threshValue = this.threshSlider.value
            this.threshLabel.innerHTML = this.threshValue
        });
        this.threshSlider.addEventListener("change", ()=>{
            this.send_img_pre_processing()
        });
        this.morphSlider.addEventListener("input", ()=>{
            this.morphValue = this.morphSlider.value
            this.morphLabel.innerHTML = this.morphValue
        });
        this.morphSlider.addEventListener("change", ()=>{
            this.send_img_pre_processing()
        });
        this.searchBestContourButton.addEventListener('click', ()=>{
            // notice local host to calculate contours
            this.wsHandler.send2local({ "topic": "get_contours" })
        });
        this.contourSlider.addEventListener("input", ()=>{
            this.contourValue = this.contourSlider.value
            this.contourLabel.innerHTML = this.contourValue
        });
        this.contourSlider.addEventListener("change", ()=>{
            this.send_selected_contour()
        });
    }

    update_cal_img(base64string){
        // update image received from local image processing
        let binaryString = atob(base64string); 
        let buffer = new ArrayBuffer(binaryString.length);
        let view = new Uint8Array(buffer);
        for (let i = 0; i < binaryString.length; i++) {
            view[i] = binaryString.charCodeAt(i);
        }   
        let blob = new Blob([view], { type: 'image/jpeg' }); 
        let imageUrl = URL.createObjectURL(blob);
        this.calImg.src = imageUrl;
    }

    send_img_pre_processing(){
        // send image processing data for binary image
        let data = {
            "blur": this.blurValue,
            "thresh": this.threshValue,
            "morph": this.morphValue,
        };
        let message = {
            "topic": "img_pre_processing",
            "data": data,
        };
        this.wsHandler.send2local(message)
    }
    
    update_contour_number(contour_number){
        this.contourSlider.max = parseInt(contour_number);
        this.contourSlider.value = parseInt(contour_number);
        this.contourLabel.innerHTML = contour_number;
    }

    send_selected_contour(){
        // send selected contour to local host
        let data = {
            "contour_index": this.contourValue,
        };
        let message = {
            "topic": "selected_contour",
            "data": data
        };
        this.wsHandler.send2local(message);
    }
 
}
