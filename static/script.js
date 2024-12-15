document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const selectFileBtn = document.getElementById('select-file');
    const urlInput = document.getElementById('url-input');
    const convertUrlBtn = document.getElementById('convert-url');
    const result = document.getElementById('result');
    const markdownResult = document.getElementById('markdown-result');
    const llmConfig = document.getElementById('llm-config');
    const apiKeyInput = document.getElementById('api-key');
    const modelSelect = document.getElementById('model');
    const copyButton = document.getElementById('copy-button');

    // Empêcher le comportement par défaut du navigateur pour le drag & drop
    document.addEventListener('dragover', (e) => e.preventDefault());
    document.addEventListener('drop', (e) => e.preventDefault());

    // Drag & drop handling
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('drag-over');
        
        const file = e.dataTransfer.files[0];
        if (file) {
            handleFile(file);
        }
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

    function isImageFile(file) {
        return file && file.type.startsWith('image/');
    }

    function handleFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        // Si c'est une image et qu'il n'y a pas de clé API dans l'environnement
        if (isImageFile(file) && document.getElementById('api-key')) {
            const apiKey = apiKeyInput.value.trim();
            if (!apiKey) {
                alert('Please provide an OpenAI API key for image analysis');
                return;
            }
            formData.append('api_key', apiKey);
        }

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
            // Formater le texte en préservant la structure
            const formattedText = data.markdown
                .replace(/\n\n/g, '\u200B\n\n')  // Ajoute un caractère de largeur nulle avant les doubles sauts de ligne
                .replace(/([^\n])\n([^\n])/g, '$1 $2')  // Remplace les sauts de ligne simples par des espaces
                .replace(/\u200B/g, '')  // Retire les caractères de largeur nulle
                .trim();
            
            markdownResult.textContent = formattedText;
        } else {
            alert('Error: ' + data.error);
        }
    }

    function handleError(error) {
        alert('Error: ' + error.message);
    }

    // Gestionnaire pour le bouton de copie
    copyButton.addEventListener('click', () => {
        const markdownText = markdownResult.textContent;
        
        // Fonction de secours pour copier le texte
        const fallbackCopyToClipboard = (text) => {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                const copyIcon = copyButton.querySelector('i');
                copyIcon.classList.replace('fa-copy', 'fa-check');
                setTimeout(() => {
                    copyIcon.classList.replace('fa-check', 'fa-copy');
                }, 2000);
            } catch (err) {
                console.error('Fallback: Erreur lors de la copie', err);
                alert('Error copying to clipboard');
            }
            document.body.removeChild(textArea);
        };

        // Essayer d'abord l'API Clipboard moderne, sinon utiliser la méthode de secours
        if (navigator.clipboard) {
            navigator.clipboard.writeText(markdownText)
                .then(() => {
                    const copyIcon = copyButton.querySelector('i');
                    copyIcon.classList.replace('fa-copy', 'fa-check');
                    setTimeout(() => {
                        copyIcon.classList.replace('fa-check', 'fa-copy');
                    }, 2000);
                })
                .catch(() => {
                    fallbackCopyToClipboard(markdownText);
                });
        } else {
            fallbackCopyToClipboard(markdownText);
        }
    });
}); 