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
            let blob = new Blob(chunks, { 'type' : 'audio/webm;codecs=opus' });
            chunks = [];
            let formData = new FormData();
            formData.append('audio', blob, 'audio.flac');
            fetch('http://localhost:5000/upload', { method: 'POST', body: formData })
                .then(response => response.json())
                .then(data => {
                    let audio = {
                        content: data.audio
                    };
                    let config = {
                        encoding: 'FLAC',
                        sampleRateHertz: 16000,
                        languageCode: 'en-US',
                    };
                    let request = {
                        audio: audio,
                        config: config
                    };
                    return fetch('https://speech.googleapis.com/v1/speech:recognize', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer ' + YOUR_GOOGLE_CLOUD_API_KEY
                        },
                        body: JSON.stringify(request)
                    });
                })
                .then(response => response.json())
                .then(data => console.log(data));
        };
        
        //mediaRecorder.onstop = function(e) {
        //    let blob = new Blob(chunks, { 'type' : 'audio/webm;codecs=pcm' });
        //    let url = URL.createObjectURL(blob);
        //    let a = document.createElement('a');
        //    a.style.display = 'none';
        //    a.href = url;
        //    a.download = 'test.webm';  // use .webm file extension
        //    //document.body.appendChild(a);
        //    //a.click();
        //    //let blob = new Blob(chunks, { 'type' : 'audio/webm; codecs=pcm' });
        //    chunks = [];
        //    let formData = new FormData();
        //    formData.append('audio', blob);
        //    fetch('http://localhost:5000/upload', { method: 'POST', body: formData });
        //    //fetch('https://34.134.1.128:5000/upload', { method: 'POST', body: formData })
        //    //.then(response => {
        //    //    if (!response.ok) {
        //    //        throw new Error('Network response was not ok');
        //    //    }
        //    //    // Handle the response...
        //    //    console.log('Success:', response);
        //    //})
        //    //.catch(error => {
        //    //    console.error('There has been a problem with your fetch operation:', error);
        //    //});
        //};
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
