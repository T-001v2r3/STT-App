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
            let blob = new Blob(chunks, { 'type' : 'audio/webm;codecs=pcm' });
            chunks = [];
            
            // Upload file to Google Cloud Storage
            let formData = new FormData();
            formData.append('audio', blob, 'audio.webm');
        
            fetch('https://storage.googleapis.com/upload/storage/v1/b/ba-report-bucket/o?uploadType=media&name=audio.webm', {
                method: 'POST', 
                body: blob,
                headers: {Authorization: 'Bearer ya29.a0AfB_byAMREFSqyxfnXSkDYe9fiwzPHg9pbUOxF0rNBpitRVj_HJJHspIEV8OIPNAEFWvCEvRPl2m9JHwNMSKmSIw-2m9CH7Df1d6JnUmU11PLfJb3336TC71Vpk8lG5yL-1we7QhZwJf8GXTDZwCZuOn-5vZFFdH-tAhaCgYKAaQSARESFQHGX2MiAkKokx81kMQL9w0NfBZdew0171'}
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to upload file to Google Cloud Storage');
                }
                // File uploaded successfully, now make the call to Google Cloud Speech-to-Text API
                let audioUri = `gs://ba-report-bucket/audio.webm`;
                let audio = {
                    uri: audioUri
                };
                let config = {
                    encoding: 'LINEAR16',
                    sampleRateHertz: 16000,
                    languageCode: 'en-US',
                };
                let request = {
                    audio: audio,
                    config: config
                };
                return fetch('https://speech.googleapis.com/v1/speech:recognize?key=YOUR_GOOGLE_CLOUD_API_KEY', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(request)
                });
            })
            .then(response => response.json())
            .then(data => console.log(data))
            .catch(error => console.error(error));
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
