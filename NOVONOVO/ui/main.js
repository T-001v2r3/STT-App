// Obtém uma referência para o elemento HTML com o ID 'recordButton'
let recordButton = document.getElementById('recordButton');

// Inicializa uma matriz vazia para armazenar os chunks de áudio
let chunks = [];

// Declaração da variável que será usada para controlar a gravação de áudio
let mediaRecorder;

// Envia áudio gravado para o servidor
function enviarAudioParaServidor(blob) {
    
    let formData = new FormData();
    formData.append('audio', blob);
    let worker_number = document.getElementById('workerNumberInput').value;
    formData.append('worker_number', worker_number);

    fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to send audio file to the backend');
            }
            console.log('Audio file sent successfully to the backend');
        })
        .catch(error => {
            console.error('Error while sending audio file to the server:', error);
        });
}

// Manipulador do evento de clique do botão "recordButton"
recordButton.onclick = function () {
    if (mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        recordButton.textContent = 'Start Recording';
        recordButton.style.backgroundColor = "#3498db"; // Altera a cor do botão para azul
    } else {
        mediaRecorder.start();
        recordButton.textContent = 'Stop Recording';
        recordButton.style.backgroundColor = "red"; // Altera a cor do botão para vermelho
    }
};

// Configuração do MediaRecorder após a permissão do usuário
navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = function (e) {
            chunks.push(e.data);
        };

        mediaRecorder.onstop = function (e) {
            let blob = new Blob(chunks, { 'type': 'audio/webm;codecs=pcm' });
            chunks = [];

            // Envie o áudio para o servidor quando a gravação parar
            enviarAudioParaServidor(blob);
        };
    })
    .catch(error => {
        console.error('Erro ao acessar o microfone:', error);
    });

// Upload de ficheiro pelo form
document.getElementById('uploadForm').addEventListener('submit', function (event) {
    event.preventDefault();

    let fileInput = document.getElementById('audio');
    let file = fileInput.files[0];

    if (!file.type.startsWith('audio/')) {
        console.error('Uploaded file is not an audio file');
        return;
    }
    if (file.size === 0) {
        console.error('Cannot send empty audio file');
        return;
    }
    let formData = new FormData();
    formData.append('audio', file);

    let worker_number = document.getElementById('workerNumberInput').value;
    formData.append('worker_number', worker_number);

    fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to upload file to backend');
            }
            console.log('File uploaded successfully to backend');
        })
        .catch(error => {
            console.error(error);
        });
});