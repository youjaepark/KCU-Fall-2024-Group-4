

let stream = null;
const video = document.getElementById('main__img');
const canvas = document.getElementById('canvas');
const startCameraBtn = document.getElementById('startCameraBtn');
const captureBtn = document.getElementById('captureBtn');
const retakeBtn = document.getElementById('retakeBtn');
const confirmBtn = document.getElementById('confirmBtn');
const staticImg = document.getElementById('static__img');
const photoControls = document.querySelector('.photo-controls');
let imageData = null;  // Changed to let


async function startCamera() {
    try {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        video.style.display = 'block';
        staticImg.style.display = 'none';
        captureBtn.style.display = 'block';
        startCameraBtn.style.display = 'none';
    } catch (err) {
        console.error('Error accessing camera:', err);
    }
}


function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    video.srcObject = null;
}


function capturePhoto() {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
   
    imageData = canvas.toDataURL('image/png');  // Reassigns imageData here
    console.log('Base64 image:', imageData);


    localStorage.setItem('capturedImage', imageData);
   
    video.style.display = 'none';
    captureBtn.style.display = 'none';
    photoControls.style.display = 'block';
    canvas.style.display = 'block';
}


function retakePhoto() {
    canvas.style.display = 'none';
    photoControls.style.display = 'none';
    video.style.display = 'block';
    captureBtn.style.display = 'block';
}


function confirmPhoto() {
    imageData = localStorage.getItem('capturedImage');
   
    fetch('https://Madhacks.pythonanywhere.com/image_api', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image_data: imageData })
    })
    .then(response => response.json())
    .then(data => {
        const resultString = data.object_name;
        return fetch('https://Madhacks.pythonanywhere.com/llm_api', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ object_name: resultString })
        });
    })
    .then(response => response.json())
    .then(data => {
        const resultText = document.getElementById('resultText');
        resultText.value = data.info;
        resultText.style.display = 'block';
       
        photoControls.style.display = 'none';
        canvas.style.display = 'none';
        startCameraBtn.textContent = 'Take Another Photo';
        startCameraBtn.style.display = 'block';
       
        stopCamera();
       
        const points = 100;
        const currentPoints = parseInt(localStorage.getItem('ecoPoints') || '0');
        localStorage.setItem('ecoPoints', currentPoints + points);
       
        const currentItems = parseInt(localStorage.getItem('itemsRecycled') || '0');
        localStorage.setItem('itemsRecycled', currentItems + 1);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while processing the image');
    });
}


startCameraBtn.addEventListener('click', startCamera);
captureBtn.addEventListener('click', capturePhoto);
retakeBtn.addEventListener('click', retakePhoto);
confirmBtn.addEventListener('click', confirmPhoto);