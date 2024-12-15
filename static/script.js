document.addEventListener('DOMContentLoaded', () => {
    // Elements DOM
    const elements = {
        dropZone: document.getElementById('drop-zone'),
        fileInput: document.getElementById('file-input'),
        selectFileBtn: document.getElementById('select-file'),
        urlInput: document.getElementById('url-input'),
        convertUrlBtn: document.getElementById('convert-url'),
        result: document.getElementById('result'),
        markdownResult: document.getElementById('markdown-result'),
        apiKeyInput: document.getElementById('api-key'),
        copyButton: document.getElementById('copy-button'),
        loading: document.getElementById('loading'),
        resultWrapper: document.querySelector('.result-wrapper')
    };

    // Gestionnaires de fichiers
    function handleFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        if (isImageFile(file) && elements.apiKeyInput) {
            const apiKey = elements.apiKeyInput.value.trim();
            if (!apiKey) {
                alert('Please provide an OpenAI API key for image analysis');
                return;
            }
            formData.append('api_key', apiKey);
        }

        convertContent('/convert', formData);
    }

    function isImageFile(file) {
        return file && file.type.startsWith('image/');
    }

    // Conversion et affichage
    function convertContent(url, formData) {
        showLoading();
        
        fetch(url, { method: 'POST', body: formData })
            .then(response => response.json())
            .then(handleResponse)
            .catch(error => {
                alert('Error: ' + error.message);
                hideLoading();
            });
    }

    function handleResponse(data) {
        if (!data.success) {
            alert('Error: ' + data.error);
            hideLoading();
            return;
        }

        const formattedText = formatMarkdown(data.markdown);
        elements.markdownResult.textContent = formattedText;
        elements.result.hidden = false;
        hideLoading();
    }

    function formatMarkdown(text) {
        return text
            .replace(/\n\n/g, '\u200B\n\n')
            .replace(/([^\n])\n([^\n])/g, '$1 $2')
            .replace(/\u200B/g, '')
            .trim();
    }

    // Copie dans le presse-papiers
    function showCopySuccess() {
        const copyIcon = elements.copyButton.querySelector('i');
        copyIcon.classList.replace('fa-copy', 'fa-check');
        setTimeout(() => copyIcon.classList.replace('fa-check', 'fa-copy'), 2000);
    }

    function copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text)
                .then(showCopySuccess)
                .catch(() => fallbackCopy(text));
        } else {
            fallbackCopy(text);
        }
    }

    function fallbackCopy(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        
        try {
            document.execCommand('copy');
            showCopySuccess();
        } catch (err) {
            console.error('Fallback: Copy error', err);
            alert('Error copying to clipboard');
        }
        
        document.body.removeChild(textArea);
    }

    // Event Listeners
    document.addEventListener('dragover', e => e.preventDefault());
    document.addEventListener('drop', e => e.preventDefault());

    elements.dropZone.addEventListener('dragover', e => {
        e.preventDefault();
        e.stopPropagation();
        elements.dropZone.classList.add('drag-over');
    });

    elements.dropZone.addEventListener('dragleave', e => {
        e.preventDefault();
        e.stopPropagation();
        elements.dropZone.classList.remove('drag-over');
    });

    elements.dropZone.addEventListener('drop', e => {
        e.preventDefault();
        e.stopPropagation();
        elements.dropZone.classList.remove('drag-over');
        const file = e.dataTransfer.files[0];
        if (file) handleFile(file);
    });

    elements.selectFileBtn.addEventListener('click', () => elements.fileInput.click());
    elements.fileInput.addEventListener('change', e => handleFile(e.target.files[0]));

    elements.convertUrlBtn.addEventListener('click', () => {
        const url = elements.urlInput.value.trim();
        if (url) {
            const formData = new FormData();
            formData.append('url', url);
            convertContent('/convert', formData);
        }
    });

    elements.copyButton.addEventListener('click', () => {
        const text = elements.markdownResult.textContent;
        if (text) {
            copyToClipboard(text);
        }
    });

    function showLoading() {
        elements.result.hidden = false;
        elements.loading.hidden = false;
        elements.resultWrapper.hidden = true;
        elements.markdownResult.textContent = '';
    }

    function hideLoading() {
        elements.loading.hidden = true;
        elements.resultWrapper.hidden = false;
    }
}); 
