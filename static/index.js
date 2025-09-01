Vue.createApp({
    name: "App",
    data() {
        return {
            Designed: false,
        }
    },
    methods: {
        ToStep4() {
            const levels = document.querySelector('input[name="levels"]:checked');
            const form = document.querySelector('input[name="form"]:checked');
            const topping = document.querySelector('input[name="topping"]:checked');

            if (!levels || !form || !topping) {
                alert("⚠ Пожалуйста, выберите уровни, форму и топпинг перед продолжением.");
                return;
            }

            this.Designed = true;

            // копируем значения из конструктора в форму заказа
            this.$nextTick(() => {
                const cakeForm = document.getElementById("cake-form");
                const orderForm = document.getElementById("order-form");

                if (cakeForm && orderForm) {
                    new FormData(cakeForm).forEach((value, key) => {
                        let hidden = orderForm.querySelector(`[name="${key}"]`);
                        if (!hidden) {
                            hidden = document.createElement("input");
                            hidden.type = "hidden";
                            hidden.name = key;
                            orderForm.appendChild(hidden);
                        }
                        hidden.value = value;
                    });
                }
            });

            // обновляем блок превью
            this.$nextTick(() => {
                function bindRadioUpdate(name, previewId) {
                    document.querySelectorAll(`input[name="${name}"]`).forEach(input => {
                        input.addEventListener("change", function () {
                            const label = document.querySelector(`label[for="${this.id}"]`);
                            const text = label && label.textContent.trim()
                                ? label.textContent.trim()
                                : this.value;
                            document.getElementById(previewId).textContent = text;
                        });
                    });
                }

                bindRadioUpdate("levels", "preview-levels");
                bindRadioUpdate("form", "preview-form");
                bindRadioUpdate("topping", "preview-topping");
                bindRadioUpdate("berries", "preview-berries");
                bindRadioUpdate("decorations", "preview-decor");

                const textInput = document.querySelector('input[name="text"]');
                if (textInput) {
                    textInput.addEventListener("input", function () {
                        document.getElementById("preview-text").textContent =
                            this.value || "Без надписи";
                    });
                }

                // 👉 сразу подставляем текущие выбранные значения в превью
                ["levels", "form", "topping", "berries", "decorations"].forEach(name => {
                    const input = document.querySelector(`input[name="${name}"]:checked`);
                    if (input) {
                        const label = document.querySelector(`label[for="${input.id}"]`);
                        const text = label && label.textContent.trim()
                            ? label.textContent.trim()
                            : input.value;
                        const previewId = "preview-" + (name === "decorations" ? "decor" : name);
                        const target = document.getElementById(previewId);
                        if (target) target.textContent = text;
                    }
                });

                if (textInput && textInput.value.trim() !== "") {
                    document.getElementById("preview-text").textContent = textInput.value;
                }
            });
        }
    },


}).mount('#VueApp');


// Глобальная функция показа модалки (без reload)
function showModal(message) {
    const modal = document.getElementById("success-modal");
    if (!modal) return;
    const content = modal.querySelector(".content");
    if (content) content.textContent = message || "Готово";
    modal.style.display = "block";
    setTimeout(() => {
        modal.style.display = "none";
    }, 4000);
}

// Делегирование: сработает, даже если форма появилась позже (после Designed = true)
document.addEventListener("submit", async function (e) {
    const form = e.target;
    if (!(form instanceof HTMLFormElement)) return;
    if (form.id !== "order-form") return;

    e.preventDefault();

    try {
        const response = await fetch(form.action, {
            method: "POST",
            body: new FormData(form),
            headers: {
                "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value
            }
        });

        // Пытаемся разобрать JSON и показать сообщение сервера
        const data = await response.json().catch(() => ({}));

        if (response.ok && data.ok) {
            showModal(data.message || "Заказ создан успешно!");
            setTimeout(() => {
                window.location.href = data.redirect_url || "/lk/";
            }, 4000);
        } else {
            alert("❌ Ошибка: " + (data.message || "Неизвестная ошибка"));
        }
    } catch (err) {
        console.error("Ошибка сети:", err);
        alert("❌ Ошибка сети");
    }
}, true); // capture=true — перехватываем раньше, чем форма уйдёт обычным POST

document.addEventListener("DOMContentLoaded", () => {
    const dateInput = document.querySelector('input[name="delivery_date"]');
    const timeInput = document.querySelector('input[name="delivery_time"]');

    if (!dateInput || !timeInput) return;

    function updateDateTimeLimits() {
        const now = new Date();
        const minDateTime = new Date(now.getTime() + 15 * 60 * 60 * 1000); // +15 часов

        // ограничиваем выбор даты
        dateInput.min = minDateTime.toISOString().split("T")[0];

        // если пользователь выбрал дату = минимальной
        if (dateInput.value) {
            const selectedDate = new Date(dateInput.value + "T00:00:00");

            if (selectedDate.toDateString() === minDateTime.toDateString()) {
                // ставим минимальное время = часы+минуты через 15 часов
                const hh = String(minDateTime.getHours()).padStart(2, "0");
                const mm = String(minDateTime.getMinutes()).padStart(2, "0");
                timeInput.min = `${hh}:${mm}`;
            } else {
                timeInput.removeAttribute("min");
            }
        }
    }

    // при загрузке сразу ставим ограничения
    updateDateTimeLimits();

    // при изменении даты — пересчитываем время
    dateInput.addEventListener("change", updateDateTimeLimits);
});

function updateTotal() {
    let total = 0;

    // складываем все выбранные радио
    document.querySelectorAll("input[type=radio]:checked").forEach(input => {
        const label = document.querySelector(`label[for="${input.id}"]`);
        if (label && label.dataset.price) {
            total += parseInt(label.dataset.price, 10);
        }
    });

    // если есть надпись
    const textInput = document.querySelector('input[name="text"]');
    if (textInput && textInput.value.trim() !== "" && textInput.dataset.price) {
        total += parseInt(textInput.dataset.price, 10);
    }

    // выводим
    const totalElem = document.getElementById("order-total");
    if (totalElem) totalElem.textContent = `Итого: ${total} ₽`;

    const previewTotal = document.getElementById("preview-total");
    if (previewTotal) previewTotal.textContent = `Итого: ${total} ₽`;
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("input[type=radio]").forEach(input => {
        input.addEventListener("change", updateTotal);
    });
    const textInput = document.querySelector('input[name="text"]');
    if (textInput) {
        textInput.addEventListener("input", updateTotal);
    }
});