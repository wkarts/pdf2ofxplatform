(() => {
    const input = document.getElementById('statement');
    const dropzone = document.getElementById('dropzone');
    const selected = document.getElementById('selected-file');
    const form = document.getElementById('upload-form');
    const submit = document.getElementById('submit-button');

    if (!input || !dropzone) return;

    const showFile = () => {
        selected.textContent = input.files?.[0]?.name ?? '';
    };

    input.addEventListener('change', showFile);
    ['dragenter', 'dragover'].forEach((eventName) => {
        dropzone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropzone.classList.add('dragging');
        });
    });
    ['dragleave', 'drop'].forEach((eventName) => {
        dropzone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropzone.classList.remove('dragging');
        });
    });
    dropzone.addEventListener('drop', (event) => {
        const files = event.dataTransfer?.files;
        if (!files?.length) return;
        const transfer = new DataTransfer();
        transfer.items.add(files[0]);
        input.files = transfer.files;
        showFile();
    });
    form?.addEventListener('submit', () => {
        if (submit) {
            submit.disabled = true;
            submit.textContent = 'Enviando e preparando...';
        }
    });
})();
