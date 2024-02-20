let recordButton = document.getElementById('recordButton');
let chunks = [];
let mediaRecorder;

navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = function(e) {
            chunks.push(e.data);
        };

        mediaRecorder.onstop = function(e) {
            let blob = new Blob(chunks, { 'type' : 'audio/ogg; codecs=opus' });
            chunks = [];
            let formData = new FormData();
            formData.append('audio', blob);
            fetch('https://34.134.1.128:5000/upload', { method: 'POST', body: formData });
        };
    });

recordButton.onclick = function() {
    if (mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        recordButton.textContent = 'Start Recording';
    } else {
        mediaRecorder.start();
        recordButton.textContent = 'Stop Recording';
    }
};
