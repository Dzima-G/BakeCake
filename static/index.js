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
        }
    },
    mounted() {
        function bindRadioUpdate(name, previewId) {
            document.querySelectorAll(`input[name="${name}"]`).forEach(input => {
                input.addEventListener("change", function () {
                    const label = document.querySelector(`label[for="${this.id}"]`);
                    document.getElementById(previewId).textContent = label ? label.textContent : this.value;
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
                document.getElementById("preview-text").textContent = this.value || "Без надписи";
            });
        }
    }
}).mount('#VueApp');

document.addEventListener("DOMContentLoaded", () => {

    // модалка
    function showModal(message) {
        const modal = document.getElementById("success-modal");
        if (!modal) return;

        const content = modal.querySelector(".content");
        if (content) {
            content.textContent = message;
        }

        modal.style.display = "block";

        setTimeout(() => {
            modal.style.display = "none";
            location.reload();
        }, 2000);
    }

    // обработка формы заказа
    document.getElementById("order-form").addEventListener("submit", async function (e) {
        e.preventDefault();  // не даём форме перезагрузить страницу сама
        const form = e.target;
        const url = form.action;
        const formData = new FormData(form);

        try {
            const response = await fetch(url, {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value
                }
            });

            if (response.ok) {
                // 🔹 если сервер вернул 200 — обновляем страницу
                window.location.reload();
            } else {
                alert("❌ Ошибка на сервере");
            }
        } catch (err) {
            console.error("Ошибка сети:", err);
            alert("❌ Ошибка сети");
        }
    });
});
