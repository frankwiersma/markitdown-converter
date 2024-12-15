document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const selectFileBtn = document.getElementById('select-file');
    const urlInput = document.getElementById('url-input');
    const convertUrlBtn = document.getElementById('convert-url');
    const result = document.getElementById('result');
    const markdownResult = document.getElementById('markdown-result');

    // Drag & drop handling
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

    // File selection button handling
    selectFileBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        handleFile(file);
    });

    // URL conversion handling
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
            // Formater le texte en préservant uniquement les doubles sauts de ligne
            const formattedText = data.markdown
                .replace(/([^\n])\n([^\n])/g, '$1 $2')  // Remplace les sauts de ligne simples par des espaces
                .replace(/\n\n/g, '\n\n')               // Préserve les doubles sauts de ligne
                .trim();                                // Enlève les espaces inutiles au début et à la fin
            
            markdownResult.textContent = formattedText;
        } else {
            alert('Error: ' + data.error);
        }
    }

    function handleError(error) {
        alert('Error: ' + error.message);
    }

    function copyToClipboard() {
        const markdownText = markdownResult.textContent;
        navigator.clipboard.writeText(markdownText)
            .then(() => {
                const copyButton = document.querySelector('.copy-button i');
                copyButton.classList.replace('fa-copy', 'fa-check');
                setTimeout(() => {
                    copyButton.classList.replace('fa-check', 'fa-copy');
                }, 2000);
            })
            .catch(err => {
                console.error('Error copying to clipboard:', err);
                alert('Error copying to clipboard');
            });
    }
}); 