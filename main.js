let videoElement = document.getElementById('video');
let binaryImageElement = document.getElementById('binaryImage');
let detectedTextElement = document.getElementById('detected-text');
let stream = null;

// Check if the browser supports getUserMedia
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
  // Request access to the camera
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(function (stream) {
      // Set the video source and start playing the stream
      videoElement.srcObject = stream;
      videoElement.play();
    })
    .catch(function (error) {
      console.error('Error accessing the camera:', error);
    });
} else {
  console.error('getUserMedia is not supported by this browser.');
}

// Add event listener to capture the frame when the 's' key is pressed
document.addEventListener('keypress', function (event) {
  if (event.key === 's') {
    captureFrame();
  }
});

function captureFrame() {
  // Create a canvas element and draw the current frame from the video element
  let canvas = document.createElement('canvas');
  canvas.width = videoElement.videoWidth;
  canvas.height = videoElement.videoHeight;
  const context = canvas.getContext('2d');
  context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
  const imageDataURL = canvas.toDataURL('image/jpeg');

  // Send the data URL to the server for further processing
  sendImageToServer(imageDataURL);
}

function sendImageToServer(imageDataURL) {
  // Make a POST request to the server using Axios
  axios.post('/process_image', { image_data_url: imageDataURL })
    .then(function (response) {
      console.log('Image sent to server:', response.data);
      binaryImageElement.setAttribute('src', 'data:image/jpeg;base64,' + response.data.image_data);
      detectedTextElement.innerHTML = response.data.detected_text;
    })
    .catch(function (error) {
      console.error('Error sending image to server:', error);
    });
}