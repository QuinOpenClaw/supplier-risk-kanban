/* ── SortableJS Drag & Drop ── */
document.addEventListener("DOMContentLoaded", () => {
    initSortable();
});

// Re-init after HTMX swaps (card add / delete / column refresh)
document.addEventListener("htmx:afterSwap", () => {
    initSortable();
});

function initSortable() {
    document.querySelectorAll(".card-list").forEach((list) => {
        if (list._sortable) list._sortable.destroy();
        list._sortable = new Sortable(list, {
            group: "kanban",
            animation: 150,
            ghostClass: "sortable-ghost",
            dragClass: "sortable-drag",
            handle: ".card",
            onEnd: handleCardDrop,
        });
    });
}

function handleCardDrop(evt) {
    const cardId = evt.item.dataset.cardId;
    const newColumnId = evt.to.dataset.columnId;
    const newPosition = evt.newIndex;

    fetch(`${window.API_BASE}/cards/${cardId}/move`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            column_id: parseInt(newColumnId),
            position: newPosition,
        }),
    }).then((res) => {
        if (!res.ok) {
            console.error("Move failed, reloading...");
            location.reload();
        }
        updateCardCounts();
    });
}

function updateCardCounts() {
    document.querySelectorAll(".column").forEach((col) => {
        const count = col.querySelectorAll(".card").length;
        const badge = col.querySelector(".card-count");
        if (badge) badge.textContent = count;
    });
}

/* ── New Card Form ── */
function openNewCardForm(columnId) {
    const form = document.getElementById(`new-card-form-${columnId}`);
    const btn = document.getElementById(`add-card-btn-${columnId}`);
    form.classList.remove("hidden");
    btn.classList.add("hidden");
    form.querySelector('input[name="title"]').focus();
}

function closeNewCardForm(columnId) {
    const form = document.getElementById(`new-card-form-${columnId}`);
    const btn = document.getElementById(`add-card-btn-${columnId}`);
    form.classList.add("hidden");
    btn.classList.remove("hidden");
    form.reset();
}

/* ── Modal ── */
function openEditModal(cardId) {
    const overlay = document.getElementById("modal-overlay");
    const container = document.getElementById("modal-container");
    overlay.classList.remove("hidden");

    fetch(`${window.API_BASE}/cards/${cardId}`)
        .then((r) => r.text())
        .then((html) => {
            container.innerHTML = html;
            htmx.process(container);
        });
}

function closeModal(evt) {
    const overlay = document.getElementById("modal-overlay");
    overlay.classList.add("hidden");
    document.getElementById("modal-container").innerHTML = "";
}

/* ── JSON Import ── */
document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("import-file");
    if (fileInput) {
        fileInput.addEventListener("change", handleImport);
    }
});

function handleImport(evt) {
    const file = evt.target.files[0];
    if (!file) return;

    const match = location.pathname.match(/\/boards\/(\d+)/);
    const boardId = match ? match[1] : "1";

    const formData = new FormData();
    formData.append("file", file);

    fetch(`${window.API_BASE}/boards/${boardId}/import`, {
        method: "POST",
        body: formData,
    })
        .then((r) => r.json())
        .then((data) => {
            if (data.error) {
                alert("Import failed: " + data.error);
            } else {
                const msg = `Imported ${data.created} card(s).`;
                if (data.errors.length > 0) {
                    alert(msg + "\n\nWarnings:\n" + data.errors.join("\n"));
                } else {
                    alert(msg);
                }
                location.reload();
            }
        })
        .catch((err) => alert("Import error: " + err));

    evt.target.value = "";
}

/* ── Card Search ── */
function searchCards(query) {
    const q = query.trim().toLowerCase();
    document.querySelectorAll('.card').forEach(card => {
        if (!q) {
            card.style.display = '';
            return;
        }
        const text = (card.dataset.search || card.innerText).toLowerCase();
        card.style.display = text.includes(q) ? '' : 'none';
    });

    // Update card counts per column after filtering
    document.querySelectorAll('.column').forEach(col => {
        const total = col.querySelectorAll('.card').length;
        const visible = col.querySelectorAll('.card:not([style*="none"])').length;
        const badge = col.querySelector('.card-count');
        if (badge) badge.textContent = q ? visible + '/' + total : total;
    });
}

// Clear search on import reload
document.addEventListener('htmx:afterSwap', () => {
    const s = document.getElementById('card-search');
    if (s && s.value) searchCards(s.value);
    initSortable();
});
