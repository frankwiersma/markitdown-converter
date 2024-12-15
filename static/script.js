document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const selectFileBtn = document.getElementById('select-file');
    const urlInput = document.getElementById('url-input');
    const convertUrlBtn = document.getElementById('convert-url');
    const result = document.getElementById('result');
    const markdownResult = document.getElementById('markdown-result');

    // Gestion du drag & drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        const file = e.dataTransfer.files[0];
        handleFile(file);
    });

    // Gestion du bouton de sélection de fichier
    selectFileBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        handleFile(file);
    });

    // Gestion de la conversion par URL
    convertUrlBtn.addEventListener('click', () => {
        const url = urlInput.value.trim();
        if (url) {
            convertUrl(url);
        }
    });

    function handleFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch('/convert', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(handleResponse)
        .catch(handleError);
    }

    function convertUrl(url) {
        const formData = new FormData();
        formData.append('url', url);

        fetch('/convert', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(handleResponse)
        .catch(handleError);
    }

    function handleResponse(data) {
        if (data.success) {
            result.hidden = false;
            markdownResult.textContent = data.markdown;
        } else {
            alert('Erreur: ' + data.error);
        }
    }

    function handleError(error) {
        alert('Erreur: ' + error.message);
    }

    function copyToClipboard() {
        const markdownText = document.getElementById('markdown-result').textContent;
        navigator.clipboard.writeText(markdownText)
            .then(() => {
                const copyButton = document.querySelector('.copy-button i');
                // Change l'icône temporairement pour donner un feedback visuel
                copyButton.classList.replace('fa-copy', 'fa-check');
                setTimeout(() => {
                    copyButton.classList.replace('fa-check', 'fa-copy');
                }, 2000);
            })
            .catch(err => {
                console.error('Erreur lors de la copie :', err);
                alert('Erreur lors de la copie dans le presse-papiers');
            });
    }
}); 