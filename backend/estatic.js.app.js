document.addEventListener('DOMContentLoaded', function () {
    const youtubeShell = document.querySelector('.youtube-tab-shell');
    const youtubeToggle = document.querySelector('.youtube-tab-toggle');

    if (youtubeShell && youtubeToggle) {
        youtubeToggle.addEventListener('click', function () {
            youtubeShell.classList.toggle('active');
        });
    }

    function playClickSound() {
        const audio = new Audio('data:audio/wav;base64,UklGRlQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YTAAAAAAgICAf39/fwAAAP///wAA');
        audio.volume = 0.15;
        audio.play().catch(() => {});
    }

    function bindSoundClicks(scope = document) {
        const clickables = scope.querySelectorAll('.sound-click');
        clickables.forEach(function (element) {
            element.addEventListener('click', function () {
                playClickSound();
            });
        });
    }

    bindSoundClicks();

    const posRoot = document.getElementById('pos-root');
    if (!posRoot) return;

    const customerSearchInput = document.getElementById('customer-search-input');
    const customerSearchResults = document.getElementById('customer-search-results');
    const productSearchInput = document.getElementById('product-search-input');
    const productSearchResults = document.getElementById('product-search-results');
    const selectedCustomerDisplay = document.getElementById('selected-customer-display');
    const totalItemsEl = document.getElementById('pos-total-items');
    const totalAmountEl = document.getElementById('pos-total-amount');
    const itemsBody = document.getElementById('pos-items-body');

    const modeCustomerBtn = document.getElementById('mode-customer-btn');
    const modeVariosBtn = document.getElementById('mode-varios-btn');

    const clearDraftBtn = document.getElementById('pos-clear-draft-btn');
    const ticketBtn = document.getElementById('pos-ticket-btn');
    const ccfBtn = document.getElementById('pos-ccf-btn');
    const documentTypeLabel = document.getElementById('pos-document-type-label');

    const saveBtn = document.getElementById('pos-save-btn');
    const payBtn = document.getElementById('pos-pay-btn');
    const creditBtn = document.getElementById('pos-credit-btn');

    const openCashBtn = document.getElementById('pos-open-cash-btn');
    const closeCashBtn = document.getElementById('pos-close-cash-btn');
    const cashStateLabel = document.getElementById('pos-cash-state-label');
    const currentTicketNumber = document.getElementById('current-ticket-number');

    const ordersBtn = document.getElementById('pos-orders-btn');
    const savedOrdersSearchInput = document.getElementById('saved-orders-search-input');
    const savedOrdersResults = document.getElementById('pos-orders-results');
    const ordersDropdown = document.getElementById('pos-orders-dropdown');

    const quickCustomerToggleBtn = document.getElementById('pos-quick-customer-toggle-btn');
    const quickCustomerPanel = document.getElementById('pos-quick-customer-panel');
    const quickCustomerName = document.getElementById('quick-customer-name');
    const quickCustomerPhone = document.getElementById('quick-customer-phone');
    const quickCustomerEmail = document.getElementById('quick-customer-email');
    const quickCustomerSaveBtn = document.getElementById('pos-quick-customer-save-btn');

    const inventoryToggleBtn = document.getElementById('pos-inventory-toggle-btn');
    const inventoryPanel = document.getElementById('pos-inventory-panel');
    const inventorySearchInput = document.getElementById('inventory-search-input');
    const inventoryResults = document.getElementById('inventory-results');

    const reprintToggleBtn = document.getElementById('pos-reprint-toggle-btn');
    const reprintPanel = document.getElementById('pos-reprint-panel');
    const reprintSearchInput = document.getElementById('reprint-search-input');
    const reprintResults = document.getElementById('reprint-results');

    const holdSlot1Btn = document.getElementById('hold-slot-1-btn');
    const holdSlot2Btn = document.getElementById('hold-slot-2-btn');
    const holdSlot3Btn = document.getElementById('hold-slot-3-btn');

    const openCashPanel = document.getElementById('pos-open-cash-panel');
    const openCashPassword = document.getElementById('open-cash-password');
    const openCashAmount = document.getElementById('open-cash-amount');
    const openCashTimePreview = document.getElementById('open-cash-time-preview');
    const openCashConfirmBtn = document.getElementById('pos-open-cash-confirm-btn');

    const closeCashPanel = document.getElementById('pos-close-cash-panel');
    const closeCashExpectedAmount = document.getElementById('close-cash-expected-amount');
    const closeCashAllowedVariation = document.getElementById('close-cash-allowed-variation');
    const closeCashComment = document.getElementById('close-cash-comment');
    const closeCashConfirmBtn = document.getElementById('pos-close-cash-confirm-btn');

    const remittanceToggleBtn = document.getElementById('pos-remittance-toggle-btn');
    const remittancePanel = document.getElementById('pos-remittance-panel');
    const remittancePassword = document.getElementById('remittance-password');
    const remittanceReceiverName = document.getElementById('remittance-receiver-name');
    const remittanceReceiverDoi = document.getElementById('remittance-receiver-doi');
    const remittanceDestination = document.getElementById('remittance-destination');
    const remittanceNotes = document.getElementById('remittance-notes');
    const remittanceConfirmBtn = document.getElementById('pos-remittance-confirm-btn');
    const payPanel = document.getElementById('pos-pay-panel');
    const payTotalInput = document.getElementById('pos-pay-total');
    const payReceivedInput = document.getElementById('pos-pay-received');
    const payChangeInput = document.getElementById('pos-pay-change');
    const payReferenceInput = document.getElementById('pos-pay-reference');
    const payDocumentLabel = document.getElementById('pos-pay-document-label');
    const payCancelBtn = document.getElementById('pos-pay-cancel-btn');
    const payConfirmBtn = document.getElementById('pos-pay-confirm-btn');
    const payClearBtn = document.getElementById('pos-pay-clear-btn');
    const payExactBtn = document.getElementById('pos-pay-exact-btn');
    const payMessage = document.getElementById('pos-pay-message');
    const payKeys = document.querySelectorAll('.pos-pay-key');

    // ===== HELPERS =====
    function parseMoney(value) {
        if (!value) return 0;
        return parseFloat(String(value).replace(/[^0-9.]/g, '')) || 0;
    }

    function formatMoney(value) {
        return `$${value.toFixed(2)}`;
    }

    function updateChange() {
        const total = parseMoney(payTotalInput.value);
        const received = parseMoney(payReceivedInput.value);
        const change = received - total;

        payChangeInput.value = formatMoney(change >= 0 ? change : 0);
    }

    // ===== PANEL CONTROL =====
    let replaceReceivedOnFirstKey = true;
    function openPayPanel(total, documentType = 'CONTADO') {
        payPanel.hidden = false;
        payTotalInput.value = formatMoney(parseMoney(total));
        payReceivedInput.value = '0.00';
        replaceReceivedOnFirstKey = true;
        payChangeInput.value = '$0.00';
        payReferenceInput.value = '';
        payMessage.textContent = '';
        payDocumentLabel.textContent = documentType.toUpperCase();
    }

    function closePayPanel() {
        payPanel.hidden = true;
    }

    // ===== INPUT MANUAL =====
    payReceivedInput.addEventListener('input', updateChange);

    // ===== CALCULADORA =====
    payKeys.forEach((btn) => {
    btn.addEventListener('click', () => {
        const val = String(btn.dataset.value || '');
        let current = String(payReceivedInput.value || '').trim();

        if (val.startsWith('+')) {
            const baseValue = (
                !current ||
                current === '0.00' ||
                current === '0' ||
                current === '$0.00'
            ) ? '0' : current;

            const num = parseMoney(baseValue);
            payReceivedInput.value = String(num + parseFloat(val.replace('+', '')));
            replaceReceivedOnFirstKey = false;
            updateChange();
            return;
        }

        if (val === '.') {
            if (replaceReceivedOnFirstKey || !current || current === '0.00' || current === '0' || current === '$0.00') {
                payReceivedInput.value = '0.';
                replaceReceivedOnFirstKey = false;
            } else if (!current.includes('.')) {
                payReceivedInput.value = `${current}.`;
            }
            updateChange();
            return;
        }

        if (replaceReceivedOnFirstKey || !current || current === '0.00' || current === '0' || current === '$0.00') {
            payReceivedInput.value = val;
            replaceReceivedOnFirstKey = false;
            updateChange();
            return;
        }

        payReceivedInput.value = current + val;
        updateChange();
    });
});

    // ===== BOTONES =====
    payClearBtn.addEventListener('click', () => {
        payReceivedInput.value = '0.00';
        replaceReceivedOnFirstKey = true;
        updateChange();
    });

    payExactBtn.addEventListener('click', () => {
        payReceivedInput.value = parseMoney(payTotalInput.value).toFixed(2);
        replaceReceivedOnFirstKey = false;
        updateChange();
    });

    payCancelBtn.addEventListener('click', closePayPanel);

    // ===== CONFIRMAR PAGO =====
    payConfirmBtn.addEventListener('click', async () => {
        try {
            payConfirmBtn.disabled = true;
            payMessage.textContent = 'Procesando...';

            const formData = new FormData();
            formData.append('amount_received', parseMoney(payReceivedInput.value));
            formData.append('reference', payReferenceInput.value || '');

            const response = await fetch(paySaleUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.message || 'Error al cobrar.');
            }

            payMessage.textContent = data.message || 'Pago exitoso';

            closePayPanel();

            // FIX: refrescar POS correctamente
            if (typeof refreshPOS === 'function') {
                refreshPOS();
            }

        } catch (error) {
            payMessage.textContent = error.message;
        } finally {
            payConfirmBtn.disabled = false;
        }
    });

    if (creditBtn) {
    creditBtn.addEventListener('click', function () {
        if (creditBtn.disabled) return;

        postForm(creditSaleUrl, {}).then(({ ok, data }) => {
            if (ok && data.success) {
                renderItems([]);
                updateTotals(0, '0.00');

                if (selectedCustomerDisplay) selectedCustomerDisplay.value = '';
                if (customerSearchInput) customerSearchInput.value = '';
                if (productSearchInput) productSearchInput.value = '';

                updateModeButtons('customer');
                updateDocumentButtons('');
                updateDocumentLabel('');
                updateActionButtons('');

                if (currentTicketNumber && data.next_ticket_number) {
                    currentTicketNumber.value = data.next_ticket_number;
                }

                alert('Venta a crédito registrada correctamente.');
            } else {
                alert(data && data.message ? data.message : 'No se pudo registrar el crédito.');
            }
        }).catch(() => {
            alert('Ocurrió un error al registrar el crédito.');
        });
    });
}
     
    let currentCashState = cashStateLabel && cashStateLabel.textContent.trim().toLowerCase() === 'abierta' ? 'open' : 'closed';

    const setModeUrl = posRoot.dataset.setModeUrl;
    const setDocumentTypeUrl = posRoot.dataset.setDocumentTypeUrl;
    const openCashUrl = posRoot.dataset.openCashUrl;
    const closeCashUrl = posRoot.dataset.closeCashUrl;
    const openCashRegisterUrl = posRoot.dataset.openCashRegisterUrl;
    const closeCashRegisterUrl = posRoot.dataset.closeCashRegisterUrl;
    const createRemittanceUrl = posRoot.dataset.createRemittanceUrl;

    const searchCustomersUrl = posRoot.dataset.searchCustomersUrl;
    const selectCustomerUrl = posRoot.dataset.selectCustomerUrl;
    const quickCreateCustomerUrl = posRoot.dataset.quickCreateCustomerUrl;

    const searchProductsUrl = posRoot.dataset.searchProductsUrl;
    const addProductUrl = posRoot.dataset.addProductUrl;

    const clearDraftUrl = posRoot.dataset.clearDraftUrl;
    const updateQuantityBase = posRoot.dataset.updateQuantityBase;

    const saveOrderUrl = posRoot.dataset.saveOrderUrl;
    const savedOrdersUrl = posRoot.dataset.savedOrdersUrl;
    const loadSavedOrderUrl = posRoot.dataset.loadSavedOrderUrl;

    const holdSlotSaveUrl = posRoot.dataset.holdSlotSaveUrl;
    const holdSlotLoadUrl = posRoot.dataset.holdSlotLoadUrl;
    const holdSlotsStatusUrl = posRoot.dataset.holdSlotsStatusUrl;

    const inventoryLookupUrl = posRoot.dataset.inventoryLookupUrl;
    const reprintTicketsUrl = posRoot.dataset.reprintTicketsUrl;
    const paySaleUrl = posRoot.dataset.paySaleUrl;
    const creditSaleUrl = posRoot.dataset.creditSaleUrl;

    function getCsrfToken() {
        const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (tokenInput) return tokenInput.value;

        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));

        return cookieValue ? cookieValue.split('=')[1] : '';
    }

    function postForm(url, data) {
        return fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            },
            body: new URLSearchParams(data),
        }).then(async response => {
            const json = await response.json();
            return { ok: response.ok, data: json };
        });
    }

    function denominationPayload(prefix) {
        return {
            denom_100_00: document.getElementById(`${prefix}-100_00`)?.value || '0',
            denom_50_00: document.getElementById(`${prefix}-50_00`)?.value || '0',
            denom_20_00: document.getElementById(`${prefix}-20_00`)?.value || '0',
            denom_10_00: document.getElementById(`${prefix}-10_00`)?.value || '0',
            denom_5_00: document.getElementById(`${prefix}-5_00`)?.value || '0',
            denom_1_00: document.getElementById(`${prefix}-1_00`)?.value || '0',
            denom_0_25: document.getElementById(`${prefix}-0_25`)?.value || '0',
            denom_0_10: document.getElementById(`${prefix}-0_10`)?.value || '0',
            denom_0_05: document.getElementById(`${prefix}-0_05`)?.value || '0',
            denom_0_01: document.getElementById(`${prefix}-0_01`)?.value || '0',
        };
    }

    function clearDenominationInputs(prefix) {
        [
            '100_00', '50_00', '20_00', '10_00', '5_00',
            '1_00', '0_25', '0_10', '0_05', '0_01'
        ].forEach(code => {
            const input = document.getElementById(`${prefix}-${code}`);
            if (input) input.value = '0';
        });
    }

    function updateModeButtons(mode) {
        if (!modeCustomerBtn || !modeVariosBtn) return;

        if (mode === 'customer') {
            modeCustomerBtn.className = 'primary-btn pressable sound-click';
            modeVariosBtn.className = 'module-button pressable sound-click';
        } else {
            modeCustomerBtn.className = 'module-button pressable sound-click';
            modeVariosBtn.className = 'primary-btn pressable sound-click';
        }

        bindSoundClicks();
    }

    function updateDocumentButtons(documentType) {
        if (!ticketBtn || !ccfBtn) return;

        if (documentType === 'ticket') {
            ticketBtn.className = 'warning-btn pressable sound-click';
            ccfBtn.className = 'module-button pressable sound-click';
        } else if (documentType === 'ccf') {
            ticketBtn.className = 'module-button pressable sound-click';
            ccfBtn.className = 'warning-btn pressable sound-click';
        } else {
            ticketBtn.className = 'module-button pressable sound-click';
            ccfBtn.className = 'module-button pressable sound-click';
        }

        bindSoundClicks();
    }

    function updateDocumentLabel(documentType) {
        if (!documentTypeLabel) return;
        documentTypeLabel.textContent = documentType ? documentType.toUpperCase() : 'pendiente';
    }

    function updateCashState(state, buttonLabel, ticketNumber) {
        currentCashState = state;

        if (cashStateLabel) {
            cashStateLabel.textContent = state === 'open' ? 'ABIERTA' : 'CERRADA';
        }

        if (openCashBtn) {
            openCashBtn.textContent = buttonLabel || (state === 'open' ? 'Caja abierta' : 'Abrir caja');
        }

        if (currentTicketNumber) {
            currentTicketNumber.value = ticketNumber || '';
        }

        const currentDocumentType = documentTypeLabel
            ? documentTypeLabel.textContent.trim().toLowerCase().replace('pendiente', '').trim()
            : '';

        updateActionButtons(currentDocumentType);
    }

    function updateActionButtons(documentType) {
        const hasDocument = documentType === 'ticket' || documentType === 'ccf';
        const enabled = hasDocument && currentCashState === 'open';

        [saveBtn, payBtn, creditBtn].forEach(button => {
            if (!button) return;

            button.disabled = !enabled;

            if (enabled) {
                button.classList.remove('pos-disabled-action');
            } else {
                button.classList.add('pos-disabled-action');
            }
        });
    }

    function renderItems(items) {
        if (!itemsBody) return;

        if (!items || items.length === 0) {
            itemsBody.innerHTML = `
                <tr id="pos-empty-row">
                    <td colspan="6">No hay items agregados.</td>
                </tr>
            `;
            bindRemoveButtons();
            bindQuantityInputs();
            bindSoundClicks(itemsBody);
            return;
        }

        itemsBody.innerHTML = items.map((item, index) => `
            <tr>
                <td>${item.name}</td>
                <td>
                    <input
                        class="pos-quantity-input"
                        type="number"
                        min="1"
                        step="1"
                        value="${item.quantity}"
                        data-product-id="${item.product_id}"
                        ${index === items.length - 1 ? 'data-last-added="1"' : ''}
                    >
                </td>
                <td>$${item.price}</td>
                <td>$${item.discount}</td>
                <td>$${item.subtotal}</td>
                <td>
                    <button class="danger-btn pressable sound-click pos-remove-line-btn"
                            type="button"
                            data-product-id="${item.product_id}">
                        X
                    </button>
                </td>
            </tr>
        `).join('');

        bindRemoveButtons();
        bindQuantityInputs();
        bindSoundClicks(itemsBody);

        const lastAddedInput = document.querySelector('.pos-quantity-input[data-last-added="1"]');
        if (lastAddedInput) {
            lastAddedInput.focus();
            lastAddedInput.select();
        }
    }

    function updateTotals(totalItems, totalAmount) {
        if (totalItemsEl) totalItemsEl.textContent = totalItems ?? 0;
        if (totalAmountEl) totalAmountEl.textContent = `$${totalAmount ?? '0.00'}`;
    }
        function getCurrentPosTotal() {
        const totalText = totalAmountEl ? totalAmountEl.textContent : '$0.00';
        const numeric = String(totalText).replace('$', '').replace(',', '').trim();
        const value = parseFloat(numeric);
        return Number.isNaN(value) ? 0 : value;
    }

    function formatMoney(value) {
        const amount = Number(value || 0);
        return `$${amount.toFixed(2)}`;
    }

    function updatePayChange() {
        if (!payReceivedInput || !payChangeInput) return;

        const total = getCurrentPosTotal();
        const received = parseFloat(payReceivedInput.value || '0');
        const safeReceived = Number.isNaN(received) ? 0 : received;
        const change = safeReceived - total;

        payChangeInput.value = formatMoney(change > 0 ? change : 0);
    }

    function resetPayPanel() {
        if (payPanel) payPanel.setAttribute('hidden', 'hidden');
        if (payReceivedInput) payReceivedInput.value = '0.00';
        if (payChangeInput) payChangeInput.value = '$0.00';
        if (payReferenceInput) payReferenceInput.value = '';
        if (payMessage) payMessage.textContent = '';
    }

    function openPayPanel() {
        if (!payPanel || !payTotalInput || !payReceivedInput || !payDocumentLabel) return;

        const total = getCurrentPosTotal();
        payPanel.removeAttribute('hidden');
        payTotalInput.value = formatMoney(total);
        payReceivedInput.value = total.toFixed(2);
        payDocumentLabel.textContent = documentTypeLabel ? documentTypeLabel.textContent.trim().toUpperCase() : 'CONTADO';
        if (payMessage) payMessage.textContent = '';
        updatePayChange();

        setTimeout(function () {
            payReceivedInput.focus();
            payReceivedInput.select();
        }, 60);
    }

    function hideCustomerResults() {
        if (!customerSearchResults) return;
        customerSearchResults.innerHTML = '';
        customerSearchResults.classList.remove('active');
    }

    function hideProductResults() {
        if (!productSearchResults) return;
        productSearchResults.innerHTML = '';
        productSearchResults.classList.remove('active');
    }

    function closeAllExtraPanels(exceptId = '') {
        const panels = [
            { id: 'quick', el: quickCustomerPanel },
            { id: 'inventory', el: inventoryPanel },
            { id: 'reprint', el: reprintPanel },
            { id: 'open_cash', el: openCashPanel },
            { id: 'close_cash', el: closeCashPanel },
            { id: 'remittance', el: remittancePanel },
        ];

        panels.forEach(panel => {
            if (!panel.el) return;
            if (panel.id === exceptId) return;
            panel.el.setAttribute('hidden', 'hidden');
        });
    }

    function renderCustomerResults(results) {
        if (!customerSearchResults) return;

        if (!results.length) {
            customerSearchResults.innerHTML = '<div class="pos-result-item">Sin coincidencias</div>';
            customerSearchResults.classList.add('active');
            return;
        }

        customerSearchResults.innerHTML = results.map(customer => `
            <button class="pos-result-item pos-customer-option"
                    type="button"
                    data-customer-id="${customer.id}"
                    data-customer-name="${customer.name}">
                <strong>${customer.name}</strong><br>
                <small>${customer.phone || ''} ${customer.email || ''}</small>
            </button>
        `).join('');

        customerSearchResults.classList.add('active');

        document.querySelectorAll('.pos-customer-option').forEach(btn => {
            btn.onclick = function () {
                const customerId = btn.dataset.customerId;
                const customerName = btn.dataset.customerName;

                postForm(selectCustomerUrl, { customer_id: customerId })
                    .then(({ ok, data }) => {
                        if (ok && data.success) {
                            if (selectedCustomerDisplay) selectedCustomerDisplay.value = customerName;
                            if (customerSearchInput) customerSearchInput.value = customerName;
                            updateModeButtons(data.mode);
                            hideCustomerResults();
                        }
                    });
            };
        });
    }

    function renderProductResults(results) {
        if (!productSearchResults) return;

        if (!results.length) {
            productSearchResults.innerHTML = '<div class="pos-result-item">Sin coincidencias</div>';
            productSearchResults.classList.add('active');
            return;
        }

        productSearchResults.innerHTML = results.map(product => `
            <button class="pos-result-item pos-product-option"
                    type="button"
                    data-product-id="${product.id}">
                <strong>${product.name}</strong><br>
                <small>${product.sku} · $${product.price}</small>
            </button>
        `).join('');

        productSearchResults.classList.add('active');

        document.querySelectorAll('.pos-product-option').forEach(btn => {
            btn.onclick = function () {
                const productId = btn.dataset.productId;

                postForm(addProductUrl, {
                    product_id: productId,
                    quantity: 1,
                }).then(({ ok, data }) => {
                    if (ok && data.success) {
                        renderItems(data.items);
                        updateTotals(data.total_items, data.total_amount);
                        productSearchInput.value = '';
                        hideProductResults();
                    } else if (data && data.message) {
                        alert(data.message);
                    }
                });
            };
        });
    }

    function bindRemoveButtons() {
        const removeButtons = document.querySelectorAll('.pos-remove-line-btn');

        removeButtons.forEach(btn => {
            btn.onclick = function () {
                const productId = btn.dataset.productId;

                fetch(`/billing/pos/remove-product/${productId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCsrfToken(),
                    },
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            renderItems(data.items);
                            updateTotals(data.total_items, data.total_amount);
                        }
                    });
            };
        });
    }

    function bindQuantityInputs() {
        const quantityInputs = document.querySelectorAll('.pos-quantity-input');

        quantityInputs.forEach(input => {
            input.addEventListener('focus', function () {
                input.select();
            });

            input.addEventListener('change', function () {
                let quantity = parseInt(input.value || '1', 10);

                if (!quantity || quantity < 1) {
                    quantity = 1;
                    input.value = 1;
                }

                const productId = input.dataset.productId;

                postForm(`${updateQuantityBase}${productId}/`, {
                    quantity: quantity,
                }).then(({ ok, data }) => {
                    if (ok && data.success) {
                        renderItems(data.items);
                        updateTotals(data.total_items, data.total_amount);
                        if (productSearchInput) {
                            productSearchInput.focus();
                        }
                    }
                });
            });
        });
    }

    function renderSavedOrders(results) {
        if (!savedOrdersResults) return;

        if (!results || results.length === 0) {
            savedOrdersResults.innerHTML = '<div class="pos-orders-empty">No hay pedidos guardados.</div>';
            return;
        }

        savedOrdersResults.innerHTML = results.map(order => `
            <button class="pos-order-item sound-click" type="button" data-order-id="${order.id}">
                <div><strong>Pedido #${order.id}</strong> · ${order.customer_name}</div>
                <div><small>${order.document_type.toUpperCase()} · $${order.total} · ${order.created_at}</small></div>
            </button>
        `).join('');

        bindSoundClicks(savedOrdersResults);

        document.querySelectorAll('.pos-order-item').forEach(btn => {
            btn.onclick = function () {
                const orderId = btn.dataset.orderId;

                postForm(loadSavedOrderUrl, { order_id: orderId }).then(({ ok, data }) => {
                    if (ok && data.success) {
                        renderItems(data.items);
                        updateTotals(data.total_items, data.total_amount);
                        updateModeButtons(data.mode);
                        updateDocumentButtons(data.document_type);
                        updateDocumentLabel(data.document_type);
                        updateActionButtons(data.document_type);

                        if (selectedCustomerDisplay) {
                            selectedCustomerDisplay.value = data.customer_name || '';
                        }

                        if (customerSearchInput) {
                            customerSearchInput.value = data.customer_name || '';
                        }

                        if (productSearchInput) {
                            productSearchInput.value = '';
                        }

                        if (ordersDropdown) {
                            ordersDropdown.setAttribute('hidden', 'hidden');
                        }
                    }
                });
            };
        });
    }

    function loadSavedOrders(query = '') {
        if (!savedOrdersResults) return;
        if (!savedOrdersUrl) return;

        fetch(`${savedOrdersUrl}?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    renderSavedOrders(data.results);
                }
            })
            .catch(error => {
                console.error('ERROR LOAD SAVED ORDERS', error);
            });
    }

    function renderInventoryResults(results) {
        if (!inventoryResults) return;

        if (!results || results.length === 0) {
            inventoryResults.innerHTML = '<div class="pos-orders-empty">No hay resultados de inventario.</div>';
            return;
        }

        inventoryResults.innerHTML = results.map(item => `
            <div class="pos-info-card">
                <div><strong>${item.product_name}</strong></div>
                <div><small>${item.sku}</small></div>
                <div>Disponible: <strong>${item.quantity}</strong></div>
                <div>Mínimo: <strong>${item.minimum_stock}</strong></div>
            </div>
        `).join('');
    }

    function loadInventoryLookup(query = '') {
        if (!inventoryLookupUrl || !inventoryResults) return;

        fetch(`${inventoryLookupUrl}?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    renderInventoryResults(data.results);
                }
            });
    }

    function renderReprintResults(results) {
        if (!reprintResults) return;

        if (!results || results.length === 0) {
            reprintResults.innerHTML = '<div class="pos-orders-empty">No hay tickets encontrados.</div>';
            return;
        }

        reprintResults.innerHTML = results.map(item => `
            <div class="pos-info-card">
                <div><strong>Ticket #${item.id}</strong> · ${item.customer_name}</div>
                <div><small>${item.created_at}</small></div>
                <div>Total: <strong>$${item.total}</strong></div>
                <div>Estado: <strong>${item.status}</strong></div>
            </div>
        `).join('');
    }

    function loadReprintTickets(query = '') {
        if (!reprintTicketsUrl || !reprintResults) return;

        fetch(`${reprintTicketsUrl}?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    renderReprintResults(data.results);
                }
            });
    }

    function updateHoldSlotButton(button, occupied) {
        if (!button) return;
        button.className = occupied
            ? 'hold-slot-occupied pressable sound-click'
            : 'hold-slot-empty pressable sound-click';
        bindSoundClicks();
    }

    function refreshHoldSlotsStatus() {
        if (!holdSlotsStatusUrl) return;

        fetch(holdSlotsStatusUrl)
            .then(response => response.json())
            .then(data => {
                if (!data.success) return;

                updateHoldSlotButton(holdSlot1Btn, data.slots.slot_1);
                updateHoldSlotButton(holdSlot2Btn, data.slots.slot_2);
                updateHoldSlotButton(holdSlot3Btn, data.slots.slot_3);
            });
    }

    function handleHoldSlot(slotName) {
        const hasItems = itemsBody && !document.getElementById('pos-empty-row');

        if (hasItems) {
            postForm(holdSlotSaveUrl, { slot: slotName }).then(({ ok, data }) => {
                if (ok && data.success) {
                    renderItems([]);
                    updateTotals(0, '0.00');

                    if (selectedCustomerDisplay) selectedCustomerDisplay.value = '';
                    if (customerSearchInput) customerSearchInput.value = '';
                    if (productSearchInput) productSearchInput.value = '';

                    updateModeButtons('customer');
                    updateDocumentButtons('');
                    updateDocumentLabel('');
                    updateActionButtons('');

                    refreshHoldSlotsStatus();
                }
            });
            return;
        }

        postForm(holdSlotLoadUrl, { slot: slotName }).then(({ ok, data }) => {
            if (ok && data.success) {
                renderItems(data.draft.items);
                updateTotals(data.draft.total_items, data.draft.total_amount);
                updateModeButtons(data.draft.mode);
                updateDocumentButtons(data.draft.document_type);
                updateDocumentLabel(data.draft.document_type);
                updateActionButtons(data.draft.document_type);

                if (selectedCustomerDisplay) selectedCustomerDisplay.value = data.draft.customer_name || '';
                if (customerSearchInput) customerSearchInput.value = data.draft.customer_name || '';

                refreshHoldSlotsStatus();
            }
        });
    }

    if (modeCustomerBtn) {
        modeCustomerBtn.addEventListener('click', function () {
            postForm(setModeUrl, { mode: 'customer' }).then(({ ok, data }) => {
                if (ok && data.success) {
                    updateModeButtons(data.mode);

                    if (selectedCustomerDisplay) {
                        selectedCustomerDisplay.value = data.customer_name || '';
                    }

                    if (customerSearchInput && data.customer_name !== 'Clientes varios') {
                        customerSearchInput.value = data.customer_name || '';
                    }
                }
            });
        });
    }

    if (modeVariosBtn) {
        modeVariosBtn.addEventListener('click', function () {
            postForm(setModeUrl, { mode: 'varios' }).then(({ ok, data }) => {
                if (ok && data.success) {
                    updateModeButtons(data.mode);

                    if (selectedCustomerDisplay) {
                        selectedCustomerDisplay.value = data.customer_name || '';
                    }

                    if (customerSearchInput) {
                        customerSearchInput.value = data.customer_name || '';
                    }
                }
            });
        });
    }

    if (ticketBtn) {
        ticketBtn.addEventListener('click', function () {
            postForm(setDocumentTypeUrl, { document_type: 'ticket' }).then(({ ok, data }) => {
                if (ok && data.success) {
                    updateDocumentButtons(data.document_type);
                    updateDocumentLabel(data.document_type);
                    updateActionButtons(data.document_type);
                }
            });
        });
    }
    if (ccfBtn) {
    ccfBtn.addEventListener('click', function () {
        postForm(setDocumentTypeUrl, { document_type: 'ccf' }).then(({ ok, data }) => {
            if (ok && data.success) {
                updateDocumentButtons(data.document_type);
                updateDocumentLabel(data.document_type);
                updateActionButtons(data.document_type);
            }
        });
    });
}

    if (openCashBtn) {
        openCashBtn.addEventListener('click', function () {
        closeAllExtraPanels('open_cash');

        if (!openCashPanel) return;

        if (openCashPanel.hasAttribute('hidden')) {
            openCashPanel.removeAttribute('hidden');
            const now = new Date();
            if (openCashTimePreview) {
                openCashTimePreview.value = now.toLocaleString();
            }
            if (openCashPassword) {
                openCashPassword.focus();
            }
        } else {
            openCashPanel.setAttribute('hidden', 'hidden');
        }
    });
}
    if (openCashConfirmBtn) {
      openCashConfirmBtn.addEventListener('click', function () {
        postForm(openCashRegisterUrl, {
            password: openCashPassword ? openCashPassword.value.trim() : '',
            opening_amount: openCashAmount ? openCashAmount.value : '0.00',
        }).then(({ ok, data }) => {
            if (ok && data.success) {
                updateCashState(data.cash_state, data.button_label, data.current_ticket_number);
                if (openCashPanel) openCashPanel.setAttribute('hidden', 'hidden');
                if (openCashPassword) openCashPassword.value = '';
            } else if (data && data.message) {
                alert(data.message);
            }
        });
    });
}

if (closeCashBtn) {
    closeCashBtn.addEventListener('click', function () {
        closeAllExtraPanels('close_cash');

        if (!closeCashPanel) return;

        if (closeCashPanel.hasAttribute('hidden')) {
            closeCashPanel.removeAttribute('hidden');
            if (closeCashExpectedAmount) closeCashExpectedAmount.focus();
        } else {
            closeCashPanel.setAttribute('hidden', 'hidden');
        }
    });
}

if (closeCashConfirmBtn) {
    closeCashConfirmBtn.addEventListener('click', function () {
        const payload = {
            expected_amount: closeCashExpectedAmount ? closeCashExpectedAmount.value : '0.00',
            allowed_variation: closeCashAllowedVariation ? closeCashAllowedVariation.value : '5.00',
            closing_comment: closeCashComment ? closeCashComment.value.trim() : '',
            ...denominationPayload('close-denom'),
        };

        postForm(closeCashRegisterUrl, payload).then(({ ok, data }) => {
            if (ok && data.success) {
                updateCashState(data.cash_state, data.button_label, data.current_ticket_number);
                if (closeCashPanel) closeCashPanel.setAttribute('hidden', 'hidden');
                clearDenominationInputs('close-denom');
                if (closeCashComment) closeCashComment.value = '';
            } else if (data && data.message) {
                alert(data.message);
            }
        });
    });
}

if (remittanceToggleBtn) {
    remittanceToggleBtn.addEventListener('click', function () {
        closeAllExtraPanels('remittance');

        if (!remittancePanel) return;

        if (remittancePanel.hasAttribute('hidden')) {
            remittancePanel.removeAttribute('hidden');
            if (remittancePassword) remittancePassword.focus();
        } else {
            remittancePanel.setAttribute('hidden', 'hidden');
        }
    });
}

if (remittanceConfirmBtn) {
    remittanceConfirmBtn.addEventListener('click', function () {
        const payload = {
            password: remittancePassword ? remittancePassword.value.trim() : '',
            receiver_name: remittanceReceiverName ? remittanceReceiverName.value.trim() : '',
            receiver_doi: remittanceReceiverDoi ? remittanceReceiverDoi.value.trim() : '',
            destination: remittanceDestination ? remittanceDestination.value : 'bank',
            notes: remittanceNotes ? remittanceNotes.value.trim() : '',
            ...denominationPayload('remit-denom'),
        };

        postForm(createRemittanceUrl, payload).then(({ ok, data }) => {
            if (ok && data.success) {
                if (remittancePanel) remittancePanel.setAttribute('hidden', 'hidden');
                if (remittancePassword) remittancePassword.value = '';
                if (remittanceReceiverName) remittanceReceiverName.value = '';
                if (remittanceReceiverDoi) remittanceReceiverDoi.value = '';
                if (remittanceNotes) remittanceNotes.value = '';
                clearDenominationInputs('remit-denom');
            } else if (data && data.message) {
                alert(data.message);
            }
        });
    });
}

if (saveBtn) {
    saveBtn.addEventListener('click', function () {
        if (saveBtn.disabled) return;

        postForm(saveOrderUrl, {}).then(({ ok, data }) => {
            if (ok && data.success) {
                renderItems([]);
                updateTotals(0, '0.00');

                if (selectedCustomerDisplay) selectedCustomerDisplay.value = '';
                if (customerSearchInput) customerSearchInput.value = '';
                if (productSearchInput) productSearchInput.value = '';

                updateModeButtons('customer');
                updateDocumentButtons('');
                updateDocumentLabel('');
                updateActionButtons('');

                if (savedOrdersResults) {
                    savedOrdersResults.innerHTML = '<div class="pos-orders-empty">Pedido guardado correctamente.</div>';
                }
            }
        });
    });
}
if (payBtn) {
    payBtn.addEventListener('click', function () {
        if (payBtn.disabled) return;
        openPayPanel();
    });
}

if (payReceivedInput) {
    payReceivedInput.addEventListener('input', function () {
        updatePayChange();
    });
}

if (payClearBtn) {
    payClearBtn.addEventListener('click', function () {
        if (!payReceivedInput) return;
        payReceivedInput.value = '0.00';
        updatePayChange();
        payReceivedInput.focus();
        payReceivedInput.select();
    });
}

if (payExactBtn) {
    payExactBtn.addEventListener('click', function () {
        if (!payReceivedInput) return;
        const total = getCurrentPosTotal();
        payReceivedInput.value = total.toFixed(2);
        updatePayChange();
        payReceivedInput.focus();
        payReceivedInput.select();
    });
}

if (payCancelBtn) {
    payCancelBtn.addEventListener('click', function () {
        resetPayPanel();
    });
}

// if (payKeys && payKeys.length) {
//     payKeys.forEach(function (btn) {
//         btn.addEventListener('click', function () {
//             if (!payReceivedInput) return;

//             const rawValue = btn.dataset.value || '';

//             if (rawValue === '.') {
//                 if (!payReceivedInput.value.includes('.')) {
//                     payReceivedInput.value = `${payReceivedInput.value || '0'}.`;
//                 }
//                 updatePayChange();
//                 return;
//             }

//             if (rawValue === '100.00' || rawValue === '50.00' || rawValue === '20.00') {
//                 const current = parseFloat(payReceivedInput.value || '0');
//                 const safeCurrent = Number.isNaN(current) ? 0 : current;
//                 payReceivedInput.value = (safeCurrent + parseFloat(rawValue)).toFixed(2);
//                 updatePayChange();
//                 return;
//             }

//             const currentValue = payReceivedInput.value || '';

//             if (currentValue === '0.00' || currentValue === '0' || currentValue === '') {
//                 payReceivedInput.value = rawValue;
//             } else {
//                 payReceivedInput.value = `${currentValue}${rawValue}`;
//             }

//             updatePayChange();
//         });
//     });
// }

if (payConfirmBtn) {
    payConfirmBtn.addEventListener('click', function () {
        const total = getCurrentPosTotal();
        const received = parseFloat(payReceivedInput ? payReceivedInput.value || '0' : '0');
        const safeReceived = Number.isNaN(received) ? 0 : received;

        if (safeReceived < total) {
            if (payMessage) {
                payMessage.textContent = 'El monto recibido no cubre el total.';
            }
            return;
        }

        postForm(paySaleUrl, {
            amount_received: safeReceived.toFixed(2),
            reference: payReferenceInput ? payReferenceInput.value.trim() : '',
        }).then(({ ok, data }) => {
            if (ok && data.success) {
                renderItems([]);
                updateTotals(0, '0.00');

                if (selectedCustomerDisplay) selectedCustomerDisplay.value = '';
                if (customerSearchInput) customerSearchInput.value = '';
                if (productSearchInput) productSearchInput.value = '';

                updateModeButtons('customer');
                updateDocumentButtons('');
                updateDocumentLabel('');
                updateActionButtons('');

                if (currentTicketNumber && data.next_ticket_number) {
                    currentTicketNumber.value = data.next_ticket_number;
                }

                resetPayPanel();
                alert(`Venta cobrada. Cambio: $${data.change_amount}`);
            } else {
                if (payMessage) {
                    payMessage.textContent = data && data.message ? data.message : 'No se pudo procesar el pago.';
                }
            }
        }).catch(() => {
            if (payMessage) {
                payMessage.textContent = 'Ocurrió un error al procesar el pago.';
            }
        });
    });
}

if (ordersBtn) {
    ordersBtn.onclick = function (event) {
        event.preventDefault();
        event.stopPropagation();

        if (!ordersDropdown) return;

        const abierto = !ordersDropdown.hasAttribute('hidden');

        if (abierto) {
            ordersDropdown.setAttribute('hidden', 'hidden');
            return;
        }

        ordersDropdown.removeAttribute('hidden');
        loadSavedOrders('');

        if (savedOrdersSearchInput) {
            savedOrdersSearchInput.value = '';
            setTimeout(function () {
                savedOrdersSearchInput.focus();
            }, 80);
        }
    };
}

if (savedOrdersSearchInput) {
    savedOrdersSearchInput.addEventListener('input', function () {
        const q = savedOrdersSearchInput.value.trim();
        loadSavedOrders(q);
    });
}

if (quickCustomerToggleBtn) {
    quickCustomerToggleBtn.addEventListener('click', function () {
        closeAllExtraPanels('quick');
        if (!quickCustomerPanel) return;

        if (quickCustomerPanel.hasAttribute('hidden')) {
            quickCustomerPanel.removeAttribute('hidden');
            if (quickCustomerName) quickCustomerName.focus();
        } else {
            quickCustomerPanel.setAttribute('hidden', 'hidden');
        }
    });
}

if (quickCustomerSaveBtn) {
    quickCustomerSaveBtn.addEventListener('click', function () {
        postForm(quickCreateCustomerUrl, {
            name: quickCustomerName ? quickCustomerName.value.trim() : '',
            phone: quickCustomerPhone ? quickCustomerPhone.value.trim() : '',
            email: quickCustomerEmail ? quickCustomerEmail.value.trim() : '',
        }).then(({ ok, data }) => {
            if (ok && data.success) {
                if (selectedCustomerDisplay) selectedCustomerDisplay.value = data.customer_name || '';
                if (customerSearchInput) customerSearchInput.value = data.customer_name || '';
                updateModeButtons(data.mode);

                if (quickCustomerName) quickCustomerName.value = '';
                if (quickCustomerPhone) quickCustomerPhone.value = '';
                if (quickCustomerEmail) quickCustomerEmail.value = '';

                if (quickCustomerPanel) quickCustomerPanel.setAttribute('hidden', 'hidden');
            } else if (data && data.message) {
                alert(data.message);
            }
        });
    });
}

if (inventoryToggleBtn) {
    inventoryToggleBtn.addEventListener('click', function () {
        closeAllExtraPanels('inventory');
        if (!inventoryPanel) return;

        if (inventoryPanel.hasAttribute('hidden')) {
            inventoryPanel.removeAttribute('hidden');
            if (inventorySearchInput) inventorySearchInput.focus();
        } else {
            inventoryPanel.setAttribute('hidden', 'hidden');
        }
    });
}

if (inventorySearchInput) {
    inventorySearchInput.addEventListener('input', function () {
        const q = inventorySearchInput.value.trim();
        loadInventoryLookup(q);
    });
}

if (reprintToggleBtn) {
    reprintToggleBtn.addEventListener('click', function () {
        closeAllExtraPanels('reprint');
        if (!reprintPanel) return;

        if (reprintPanel.hasAttribute('hidden')) {
            reprintPanel.removeAttribute('hidden');
            loadReprintTickets('');
            if (reprintSearchInput) reprintSearchInput.focus();
        } else {
            reprintPanel.setAttribute('hidden', 'hidden');
        }
    });
}

if (reprintSearchInput) {
    reprintSearchInput.addEventListener('input', function () {
        const q = reprintSearchInput.value.trim();
        loadReprintTickets(q);
    });
}

if (holdSlot1Btn) {
    holdSlot1Btn.addEventListener('click', function () {
        handleHoldSlot('slot_1');
    });
}

if (holdSlot2Btn) {
    holdSlot2Btn.addEventListener('click', function () {
        handleHoldSlot('slot_2');
    });
}

if (holdSlot3Btn) {
    holdSlot3Btn.addEventListener('click', function () {
        handleHoldSlot('slot_3');
    });
}

if (customerSearchInput) {
    customerSearchInput.addEventListener('input', function () {
        const q = customerSearchInput.value.trim();

        if (q.length < 2) {
            hideCustomerResults();
            return;
        }

        fetch(`${searchCustomersUrl}?q=${encodeURIComponent(q)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    renderCustomerResults(data.results);
                }
            });
    });
}

if (productSearchInput) {
    productSearchInput.addEventListener('input', function () {
        const q = productSearchInput.value.trim();

        if (q.length < 2) {
            hideProductResults();
            return;
        }

        fetch(`${searchProductsUrl}?q=${encodeURIComponent(q)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    renderProductResults(data.results);
                }
            });
    });
}

if (clearDraftBtn) {
    clearDraftBtn.addEventListener('click', function () {
        postForm(clearDraftUrl, {}).then(({ ok, data }) => {
            if (ok && data.success) {
                renderItems([]);
                updateTotals(0, '0.00');

                if (selectedCustomerDisplay) selectedCustomerDisplay.value = '';
                if (customerSearchInput) customerSearchInput.value = '';

                updateModeButtons('customer');
                updateDocumentButtons('');
                updateDocumentLabel('');
                updateActionButtons('');
            }
        });
    });
}

document.addEventListener('click', function (event) {
    if (
        customerSearchResults &&
        !customerSearchResults.contains(event.target) &&
        event.target !== customerSearchInput
    ) {
        customerSearchResults.classList.remove('active');
        customerSearchResults.innerHTML = '';
    }

    if (
        productSearchResults &&
        !productSearchResults.contains(event.target) &&
        event.target !== productSearchInput
    ) {
        productSearchResults.classList.remove('active');
    }

    if (
        ordersDropdown &&
        ordersBtn &&
        !ordersDropdown.hasAttribute('hidden') &&
        !ordersDropdown.contains(event.target) &&
        !ordersBtn.contains(event.target)
    ) {
        ordersDropdown.setAttribute('hidden', 'hidden');
    }

    if (
        payPanel &&
        payBtn &&
        !payPanel.hasAttribute('hidden') &&
        !payPanel.contains(event.target) &&
        !payBtn.contains(event.target)
    ) {
        resetPayPanel();
    }
});

bindRemoveButtons();
bindQuantityInputs();
refreshHoldSlotsStatus();
resetPayPanel();

const initialDocumentType = documentTypeLabel
    ? documentTypeLabel.textContent.trim().toLowerCase().replace('pendiente', '').trim()
    : '';

updateActionButtons(initialDocumentType);
});
