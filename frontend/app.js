const API_BASE = (typeof window !== "undefined" && window.API_BASE_URL) || '';

const api = {
    buildUrl(path, params = {}) {
        const url = new URL(path, API_BASE);
        for (const [key, value] of Object.entries(params)) {
            if (value !== undefined && value !== null && value !== "") {
                url.searchParams.append(key, value);
            }
        }
        return url.toString();
    },

    async createExpense(payload) {
        const res = await fetch(this.buildUrl("/expenses"), {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        if (!res.ok) throw await this._error(res);
        return res.json();
    },

    async listExpenses(filters = {}) {
        const res = await fetch(this.buildUrl("/expenses", filters));
        if (!res.ok) throw await this._error(res);
        return res.json();
    },

    async updateExpense(id, payload) {
        const res = await fetch(this.buildUrl(`/expenses/${id}`), {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        if (!res.ok) throw await this._error(res);
        return res.json();
    },

    async deleteExpense(id) {
        const res = await fetch(this.buildUrl(`/expenses/${id}`), { method: "DELETE" });
        if (!res.ok) throw await this._error(res);
        return true;
    },

    async _error(res) {
        let detail = res.statusText;
        try {
            const body = await res.json();
            detail = body.detail || detail;
        } catch (_) { }
        const err = new Error(typeof detail === "string" ? detail : "API error");
        err.status = res.status;
        err.detail = detail;
        return err;
    },
};

function formatAmount(value) {
    const num = typeof value === "number" ? value : parseFloat(value);
    const safe = Number.isNaN(num) ? 0 : num;
    return safe.toLocaleString("ru-RU", {
        style: "currency",
        currency: "RUB",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}

function formatDate(isoString) {
    if (!isoString) return "";
    const [y, m, d] = isoString.split("-");
    return `${d}.${m}.${y}`;
}

if (typeof module !== "undefined" && module.exports) {
    module.exports = { api, formatAmount, formatDate };
}


if (typeof window !== "undefined" && typeof document !== "undefined") {
    document.addEventListener("DOMContentLoaded", () => {
        const form = document.getElementById("expense-form");
        const formTitle = document.getElementById("form-title");
        const submitBtn = document.getElementById("submit-btn");
        const cancelBtn = document.getElementById("cancel-btn");
        const formError = document.getElementById("form-error");
        const filterForm = document.getElementById("filter-form");
        const filterReset = document.getElementById("filter-reset");
        const listEl = document.getElementById("expense-list");
        const totalCountEl = document.getElementById("total-count");
        const totalAmountEl = document.getElementById("total-amount");

        let editingId = null;
        let currentFilters = {};

        document.getElementById("expense_date").valueAsDate = new Date();

        async function refresh() {
            try {
                const data = await api.listExpenses(currentFilters);
                renderList(data);
            } catch (err) {
                listEl.innerHTML = `<p class="empty">Ошибка загрузки: ${err.message}</p>`;
            }
        }

        function renderList(data) {
            totalCountEl.textContent = data.total;
            totalAmountEl.textContent = formatAmount(data.total_amount);

            if (data.items.length === 0) {
                listEl.innerHTML = '<p class="empty">Записей пока нет</p>';
                return;
            }

            listEl.innerHTML = data.items.map(item => `
                <div class="expense-item" data-id="${item.id}">
                    <div class="expense-amount">${formatAmount(item.amount)}</div>
                    <div class="expense-meta">
                        <span class="expense-category">${escapeHtml(item.category)}</span>
                        ${item.note ? `<span class="expense-note">${escapeHtml(item.note)}</span>` : ""}
                    </div>
                    <span class="expense-date">${formatDate(item.expense_date)}</span>
                    <div class="expense-actions">
                        <button type="button" class="btn-edit" data-action="edit" data-id="${item.id}">Изменить</button>
                        <button type="button" class="btn btn-danger" data-action="delete" data-id="${item.id}">Удалить</button>
                    </div>
                </div>
            `).join("");
        }

        function escapeHtml(s) {
            return String(s)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#39;");
        }

        function resetForm() {
            form.reset();
            document.getElementById("expense_date").valueAsDate = new Date();
            document.getElementById("expense-id").value = "";
            editingId = null;
            formTitle.textContent = "Новая запись";
            submitBtn.textContent = "Добавить";
            cancelBtn.hidden = true;
            formError.hidden = true;
        }

        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            formError.hidden = true;

            const payload = {
                amount: parseFloat(document.getElementById("amount").value),
                category: document.getElementById("category").value.trim(),
                expense_date: document.getElementById("expense_date").value,
                note: document.getElementById("note").value.trim() || null,
            };

            try {
                if (editingId) {
                    await api.updateExpense(editingId, payload);
                } else {
                    await api.createExpense(payload);
                }
                resetForm();
                await refresh();
            } catch (err) {
                formError.textContent = `Ошибка: ${err.message}`;
                formError.hidden = false;
            }
        });

        cancelBtn.addEventListener("click", resetForm);

        listEl.addEventListener("click", async (e) => {
            const btn = e.target.closest("[data-action]");
            if (!btn) return;
            const id = btn.dataset.id;
            const action = btn.dataset.action;

            if (action === "delete") {
                if (!confirm("Удалить запись?")) return;
                try {
                    await api.deleteExpense(id);
                    await refresh();
                } catch (err) {
                    alert(`Ошибка удаления: ${err.message}`);
                }
            } else if (action === "edit") {
                const item = document.querySelector(`.expense-item[data-id="${id}"]`);
                if (!item) return;
                try {
                    const data = await api.listExpenses(currentFilters);
                    const exp = data.items.find(x => x.id === id);
                    if (!exp) return;
                    document.getElementById("amount").value = exp.amount;
                    document.getElementById("category").value = exp.category;
                    document.getElementById("expense_date").value = exp.expense_date;
                    document.getElementById("note").value = exp.note || "";
                    document.getElementById("expense-id").value = exp.id;
                    editingId = exp.id;
                    formTitle.textContent = "Редактирование";
                    submitBtn.textContent = "Сохранить";
                    cancelBtn.hidden = false;
                    window.scrollTo({ top: 0, behavior: "smooth" });
                } catch (err) {
                    alert(`Ошибка: ${err.message}`);
                }
            }
        });

        filterForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            currentFilters = {
                category: document.getElementById("filter-category").value.trim(),
                date_from: document.getElementById("filter-date-from").value,
                date_to: document.getElementById("filter-date-to").value,
            };
            await refresh();
        });

        filterReset.addEventListener("click", async () => {
            filterForm.reset();
            currentFilters = {};
            await refresh();
        });

        refresh();
    });
}
