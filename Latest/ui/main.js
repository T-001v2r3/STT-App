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
        
            // Get the decided filename from the server
            fetch('http://localhost:5000/decide-filename')  // Replace with your server's URL
                .then(response => response.json())
                .then(data => {
                    let filename = data.filename;
        
                    // Upload file to Google Cloud Bucket
                    let formData = new FormData();
                    formData.append('audio', blob, filename);
                    fetch(`https://storage.googleapis.com/upload/storage/v1/b/ba-report-bucket/o?uploadType=media&name=${filename}`, {
                        method: 'POST', 
                        body: blob,
                        headers: {Authorization: 'Bearer ya29.a0AfB_byCBXz_MO11Csru1iZYXNfKrPMyH9i1eJD2mBhOSBfRfLnK6VIciI3QlQTjhHzEBpX0kcc42r9hfOK2WSUvKOaxuAEa4dWsvkIy82X5T3jX-rjenDuc0Ky_TNzAVqSkKFd6v0rJ733om2hg7rSR4vbVFRNsW1zeraCgYKAWISARESFQHGX2MijSptFrv9PlMRFss1281g2w0171'}
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Failed to upload file to Google Cloud Storage');
                        }
                    // Call next step
                    fetch('http://localhost:5000/request-transcribe', {
                        method: 'POST', 
                        body: JSON.stringify({ filename: filename }),
                        headers: { 'Content-Type': 'application/json' }
                    })
                });
            })
            .catch(error => console.error(error));
        };        
    });

    recordButton.onclick = function() {
        if (mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            recordButton.textContent = 'Start Recording';
            recordButton.style.backgroundColor = "#3498db"; // Altera a cor do botão para vermelho
        } else {
            mediaRecorder.start();
            recordButton.textContent = 'Stop Recording';
            recordButton.style.backgroundColor = "red"; // Altera a cor do botão para vermelho
        }
};
