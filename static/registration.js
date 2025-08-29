(function () {
    const modalEl = document.getElementById('RegModal');
    if (!modalEl) return;

    // ---------- helpers ----------
    function getCookie(name) {
        const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
        return m ? m.pop() : '';
    }

    function showMsg(container, text, extraClass, color) {
        let box = container.querySelector('.auth-msg');
        if (!box) {
            box = document.createElement('div');
            box.className = 'auth-msg text-center mt-2';
            container.insertBefore(box, container.firstChild);
        }
        // сбрасываем прошлые цвета/классы и задаём новые
        box.classList.remove('auth-error', 'auth-success', 'text-danger');
        if (extraClass) box.classList.add(extraClass);
        if (color) box.style.color = color; else box.style.removeProperty('color');
        box.textContent = text;
    }

    const linkLogin = modalEl.querySelector('#tab-login');
    const linkReg = modalEl.querySelector('#tab-register');
    const paneLogin = modalEl.querySelector('#pane-login');
    const paneReg = modalEl.querySelector('#pane-register');

    function setTitleStyles(active) { // 'login' | 'register'
        if (!linkLogin || !linkReg) return;
        const on = el => {
            el.classList.add('cake_blue');
            el.classList.remove('cake_grey');
            el.setAttribute('aria-selected', 'true');
        };
        const off = el => {
            el.classList.add('cake_grey');
            el.classList.remove('cake_blue');
            el.setAttribute('aria-selected', 'false');
        };
        if (active === 'register') {
            off(linkLogin);
            on(linkReg);
        } else {
            on(linkLogin);
            off(linkReg);
        }
    }

    function activateTab(active) { // 'login' | 'register'
        if (!paneLogin || !paneReg) return;
        if (active === 'register') {
            paneLogin.classList.remove('show', 'active');
            paneReg.classList.add('show', 'active');
            setTitleStyles('register');
        } else {
            paneReg.classList.remove('show', 'active');
            paneLogin.classList.add('show', 'active');
            setTitleStyles('login');
        }
    }

    [[linkLogin, 'login'], [linkReg, 'register']].forEach(([el, name]) => {
        if (!el) return;
        el.addEventListener('click', (e) => {
            e.preventDefault();
            activateTab(name);
        });
    });

    activateTab('login');

    async function handleSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const body = new FormData(form);

        // блокируем кнопку и очищаем предыдущее сообщение
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.disabled = true;
        const holder = form.closest('.tab-pane') || form.closest('.modal-content') || modalEl;
        const oldMsg = holder.querySelector('.auth-msg');
        if (oldMsg) oldMsg.remove();

        const res = await fetch(form.action, {
            method: 'POST',
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            body
        });
        let data = {};
        try {
            data = await res.json();
        } catch (_) {
        }

        const content = form.closest('.tab-pane') || form.closest('.modal-content') || modalEl;

        if (res.ok && data.ok) {
            // цвет успеха меняется здесь (поставь свой HEX/RGB)
            showMsg(content, data.message || 'Готово', 'auth-success');
            setTimeout(() => {
                const inst = window.bootstrap?.Modal.getInstance(modalEl) || new window.bootstrap.Modal(modalEl);
                inst.hide();
                window.location.reload();
            }, 1500);
        } else {
            const firstErr = data?.errors ? Object.values(data.errors).flat()[0] : (data?.message || 'Ошибка');
            showMsg(content, firstErr, 'auth-error');
        }

        if (submitBtn) submitBtn.disabled = false;
    }

    modalEl.querySelectorAll('form[action$="/login/"], form[action$="/register/"]').forEach(f => {
        f.addEventListener('submit', handleSubmit);
    });
})();
