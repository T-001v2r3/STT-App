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
        

                    //// Get the decided filename from the server
                    //fetch('https://34.134.1.128:5000/decide-filename')  // Replace with your server's URL
                    //    .then(response => response.json())
                    //    .then(data => {
                    //        let filename = data.filename;
            
                            // Upload file to Google Cloud Bucket
                            let formData = new FormData();
                            filename = "bananas.wav"
                            formData.append('audio', blob, filename);
                            fetch(`https://storage.googleapis.com/upload/storage/v1/b/ba-report-bucket/o?uploadType=media&name=${filename}`, {
                                method: 'POST', 
                                body: formData,
                                headers: {
                                    Authorization: `Bearer`
                                }
                            })
                            .then(response => {
                                if (!response.ok) {
                                    throw new Error('Failed to upload file to Google Cloud Storage');
                                }
                                // Call next step
                                fetch('https://34.134.1.128:5000/request-transcribe', {
                                    method: 'POST', 
                                    body: JSON.stringify({ filename: filename }),
                                    headers: { 'Content-Type': 'application/json' }
                                })
                            })
                            .catch(error => console.error(error));
                        //})
                        //.catch(error => console.error(error));
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
