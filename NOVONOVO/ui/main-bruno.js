// Obtém uma referência para o elemento HTML com o ID 'recordButton'
let recordButton = document.getElementById('recordButton');

// Inicializa uma matriz vazia para armazenar os chunks de áudio
let chunks = [];

// Declaração da variável que será usada para controlar a gravação de áudio
let mediaRecorder;

/*
// Função para enviar o áudio para o servidor
function enviarAudioParaServidor(blob) {
    // Obtenha o nome do arquivo do servidor
    fetch('https://34.38.170.45:5000/decide-filename') // Substitua pelo URL do servidor
        .then(response => response.json())
        .then(data => {
            let filename = data.filename;

            // Crie um FormData com o arquivo de áudio
            let formData = new FormData();
            formData.append('audio', blob, filename);

            // Envie o FormData para o servidor
            fetch(`https://storage.googleapis.com/upload/storage/v1/b/ba-report-bucket/o?uploadType=media&name=${filename}`, {
                method: 'POST',
                body: formData,
                headers: {
                    'Authorization': `Bearer ${ya29.a0AfB_byDoMRrr_So6LsNr9HsBw54RP0gy9VVR1K7VlWJu - XqN8vofvtaYQWd6FV8yrGdd25bq7TNVs5tmE8Qg - zzXOWGv0vwYgyb82AsCR8xv28KB_fhifHEeAY2soH5Du17ZlEWJTQiJZz8uqZFa6ccGzrDKOqilp5zBaCgYKAQQSARESFQHGX2Mi26joEIm7lA3jYBT - Q7os2w0171}` // Substitua pelo token de acesso válido
                }
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Falha ao enviar o arquivo de áudio para o servidor');
                    }
                    // Se o envio for bem-sucedido, avance para a próxima etapa
                    fetch('https://34.38.170.45:5000/request-transcribe', {
                        method: 'POST',
                        body: JSON.stringify({ filename: filename }),
                        headers: { 'Content-Type': 'application/json' }
                    });
                })
                .catch(error => {
                    console.error('Erro durante o envio do arquivo de áudio:', error);
                });
        })
        .catch(error => {
            console.error('Erro ao obter o nome do arquivo do servidor:', error);
        });
}
*/
function enviarAudioParaServidor(blob) {

    // Send the audio blob to the Flask backend
    fetch('http://localhost:5000/upload-recorded', { // Update the URL to your Flask backend endpoint
        method: 'POST',
        body: blob
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
