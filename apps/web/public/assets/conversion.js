(() => {
    const root = document.getElementById('conversion-app');
    if (!root) return;

    const csrf = document.querySelector('meta[name="csrf-token"]')?.content ?? '';
    const statusUrl = root.dataset.statusUrl;
    const updateTemplate = root.dataset.updateUrlTemplate;
    const processingPanel = document.getElementById('processing-panel');
    const processingTitle = document.getElementById('processing-title');
    const processingMessage = document.getElementById('processing-message');
    const errorPanel = document.getElementById('error-panel');
    const errorMessage = document.getElementById('error-message');
    const resultPanel = document.getElementById('result-panel');
    const body = document.getElementById('transactions-body');
    const template = document.getElementById('transaction-template');
    let pollTimer = null;
    const statusLabels = {
        queued: 'Na fila',
        processing: 'Processando',
        completed: 'Concluído',
        review_required: 'Revisão necessária',
        failed: 'Falhou'
    };

    const money = (value) => {
        if (value === null || value === undefined || value === '') return '—';
        return Number(value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    };

    const setText = (id, value, fallback = '—') => {
        const el = document.getElementById(id);
        if (el) el.textContent = value ?? fallback;
    };

    const showError = (message) => {
        processingPanel?.classList.add('hidden');
        resultPanel?.classList.add('hidden');
        errorPanel?.classList.remove('hidden');
        if (errorMessage) errorMessage.textContent = message || 'Falha não identificada.';
    };

    const request = async (url, options = {}) => {
        const response = await fetch(url, {
            headers: { 'Accept': 'application/json', 'X-CSRF-TOKEN': csrf, ...(options.headers || {}) },
            ...options
        });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok || payload.ok === false) {
            throw new Error(payload.message || payload.detail || 'Não foi possível concluir a solicitação.');
        }
        return payload;
    };

    const updateStatusBadge = (status, label) => {
        const badge = document.getElementById('status-badge');
        if (!badge) return;
        badge.className = `status status-${status}`;
        badge.textContent = label || status;
    };

    const renderWarnings = (warnings = []) => {
        const panel = document.getElementById('warnings-panel');
        const list = document.getElementById('warnings-list');
        if (!panel || !list) return;
        list.innerHTML = '';
        if (!warnings.length) {
            panel.classList.add('hidden');
            return;
        }
        warnings.forEach((warning) => {
            const li = document.createElement('li');
            li.textContent = typeof warning === 'string' ? warning : warning.message;
            list.appendChild(li);
        });
        panel.classList.remove('hidden');
    };

    const saveTransaction = async (index, row, deleted = false) => {
        const url = updateTemplate.replace('__INDEX__', String(index));
        const payload = {
            posted_at: row.querySelector('.transaction-date').value,
            description: row.querySelector('.transaction-description').value,
            document_number: row.querySelector('.transaction-document').value || null,
            amount: Number(row.querySelector('.transaction-amount').value),
            deleted
        };
        row.style.opacity = '.55';
        try {
            const response = await request(url, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            updateStatusBadge(
                response.payload.status,
                statusLabels[response.payload.status]
            );
            renderResult(response.payload);
        } catch (error) {
            alert(error.message);
        } finally {
            row.style.opacity = '';
        }
    };

    const renderTransactions = (transactions = []) => {
        if (!body || !template) return;
        body.innerHTML = '';
        transactions.forEach((transaction, index) => {
            const row = template.content.firstElementChild.cloneNode(true);
            row.dataset.index = index;
            if (transaction.deleted) row.classList.add('row-deleted');
            row.querySelector('.transaction-index').textContent = index + 1;
            row.querySelector('.transaction-date').value = transaction.posted_at;
            row.querySelector('.transaction-description').value = transaction.description;
            row.querySelector('.transaction-document').value = transaction.document_number ?? '';
            row.querySelector('.transaction-amount').value = Number(transaction.amount).toFixed(2);
            row.querySelector('.transaction-balance').textContent = money(transaction.balance);
            row.querySelector('.transaction-confidence').textContent =
                `${Math.round(Number(transaction.confidence ?? 0) * 100)}%`;
            row.querySelector('.save-transaction').addEventListener('click', () => saveTransaction(index, row, false));
            const deleteButton = row.querySelector('.delete-transaction');
            if (transaction.deleted) {
                deleteButton.textContent = '↺';
                deleteButton.title = 'Restaurar';
                deleteButton.addEventListener('click', () => saveTransaction(index, row, false));
            } else {
                deleteButton.addEventListener('click', () => {
                    if (confirm('Excluir esta transação do OFX?')) saveTransaction(index, row, true);
                });
            }
            body.appendChild(row);
        });
    };

    const renderResult = (payload) => {
        const result = payload.result || payload;
        processingPanel?.classList.add('hidden');
        errorPanel?.classList.add('hidden');
        resultPanel?.classList.remove('hidden');
        setText('bank-name', result.bank?.name);
        setText('branch-number', result.account?.branch);
        setText('account-number', result.account?.number);
        setText('transaction-count', result.transaction_count ?? result.transactions?.length ?? 0);
        setText('confidence', `${Math.round(Number(result.confidence ?? 0) * 100)}%`);
        setText('reconciliation-status', result.reconciliation?.balanced ? 'Conferido' : 'Revisar');
        const warnings = [
            ...(result.warnings || []),
            ...(result.reconciliation?.warnings || [])
        ].filter((warning, index, items) => items.indexOf(warning) === index);
        renderWarnings(warnings);
        renderTransactions(result.transactions || []);
    };

    const poll = async () => {
        try {
            const response = await request(statusUrl);
            const payload = response.payload;
            const status = payload.status;
            updateStatusBadge(status, response.conversion?.status_label);
            if (status === 'completed' || status === 'review_required') {
                clearTimeout(pollTimer);
                renderResult(payload);
                return;
            }
            if (status === 'failed') {
                clearTimeout(pollTimer);
                showError(payload.error?.message || response.conversion?.error_message);
                return;
            }
            processingTitle.textContent = status === 'processing' ? 'Interpretando o extrato...' : 'Aguardando processamento...';
            processingMessage.textContent = payload.progress?.message || 'A conversão será atualizada automaticamente.';
            pollTimer = setTimeout(poll, 1800);
        } catch (error) {
            processingMessage.textContent = error.message;
            pollTimer = setTimeout(poll, 4000);
        }
    };

    poll();
})();
