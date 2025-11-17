// Telegram Web App
const tg = window.Telegram?.WebApp;
if (tg) {
    tg.expand();
    tg.setHeaderColor('#0a0a0f');
    tg.setBackgroundColor('#0a0a0f');
}

// Глобальные переменные
let userData = null;
let sourceImageFile = null;
let targetVideoFile = null;
let statsData = null;

// Инициализация приложения
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Facy App initialized');
    
    // Получаем данные пользователя из Telegram (всегда доступны в Telegram Web App)
    const telegramUser = tg?.initDataUnsafe?.user;
    
    if (telegramUser && telegramUser.id) {
        // Проверяем, первый ли это вход
        const isFirstVisit = !localStorage.getItem(`user_${telegramUser.id}_visited`);
        
        if (isFirstVisit) {
            // Показываем модальное окно приветствия
            showWelcomeModal(telegramUser);
    } else {
            // Автоматически загружаем данные пользователя при загрузке страницы
            await loadUserData(telegramUser.id);
        }
    }
    
    // Загружаем статистику
    await loadStats();
    
    // Инициализируем обработчики
    initWelcomeModal(); // Сначала инициализируем модальные окна
    initHeaderButtons();
    initCreateModal();
    initFileUploads();
    initDemoToggles();
    initButtons();
    initSmoothScroll();
});

// Загрузка данных пользователя
async function loadUserData(telegramId) {
    try {
        const response = await fetch(`/api/user/${telegramId}`);
        
        if (response.ok) {
            userData = await response.json();
            updatePrice();
            updateHeaderButtons();
        } else {
            console.error('Failed to load user data');
        }
    } catch (error) {
        console.error('Error loading user data:', error);
    }
}

// Загрузка статистики
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        
        if (response.ok) {
            statsData = await response.json();
            console.log('Stats loaded:', statsData);
        } else {
            console.error('Failed to load stats');
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Показать модальное окно приветствия
function showWelcomeModal(telegramUser) {
    const welcomeModal = document.getElementById('welcomeModal');
    if (welcomeModal) {
        welcomeModal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
}

// Закрыть модальное окно приветствия
function closeWelcomeModal() {
    const welcomeModal = document.getElementById('welcomeModal');
    if (welcomeModal) {
        welcomeModal.classList.remove('show');
        document.body.style.overflow = '';
    }
}

// Инициализация модальных окон
function initWelcomeModal() {
    const welcomeRegisterBtn = document.getElementById('welcomeRegisterBtn');
    const skipReferralBtn = document.getElementById('skipReferralBtn');
    const submitLoginBtn = document.getElementById('submitLoginBtn');
    const submitRegisterBtn = document.getElementById('submitRegisterBtn');
    const goToRegisterLink = document.getElementById('goToRegisterLink');
    const goToLoginLink = document.getElementById('goToLoginLink');
    const copyPartnerCodeBtn = document.getElementById('copyPartnerCodeBtn');
    const copyPartnerLinkBtn = document.getElementById('copyPartnerLinkBtn');
    
    if (welcomeRegisterBtn) {
        welcomeRegisterBtn.addEventListener('click', handleRegister);
    }
    
    if (skipReferralBtn) {
        skipReferralBtn.addEventListener('click', handleSkipReferral);
    }
    
    if (submitLoginBtn) {
        submitLoginBtn.addEventListener('click', handleFormLogin);
    }
    
    if (submitRegisterBtn) {
        submitRegisterBtn.addEventListener('click', handleFormRegister);
    }
    
    if (goToRegisterLink) {
        goToRegisterLink.addEventListener('click', (e) => {
            e.preventDefault();
            closeLoginModal();
            openRegisterModal();
        });
    }
    
    if (goToLoginLink) {
        goToLoginLink.addEventListener('click', (e) => {
            e.preventDefault();
            closeRegisterModal();
            openLoginModal();
        });
    }
    
    if (copyPartnerCodeBtn) {
        copyPartnerCodeBtn.addEventListener('click', () => {
            const code = document.getElementById('partnerCodeDisplay').value;
            if (navigator.clipboard) {
                navigator.clipboard.writeText(code);
                showNotification('Партнерский код скопирован!', 'success');
            }
        });
    }
    
    if (copyPartnerLinkBtn) {
        copyPartnerLinkBtn.addEventListener('click', () => {
            const link = document.getElementById('partnerLinkDisplay').value;
            if (navigator.clipboard) {
                navigator.clipboard.writeText(link);
                showNotification('Партнерская ссылка скопирована!', 'success');
            }
        });
    }
    
    // Кнопки закрытия модальных окон
    const welcomeModalClose = document.getElementById('welcomeModalClose');
    const loginModalClose = document.getElementById('loginModalClose');
    const registerModalClose = document.getElementById('registerModalClose');
    const partnerModalClose = document.getElementById('partnerModalClose');
    
    if (welcomeModalClose) {
        welcomeModalClose.addEventListener('click', closeWelcomeModal);
    }
    
    if (loginModalClose) {
        loginModalClose.addEventListener('click', closeLoginModal);
    }
    
    if (registerModalClose) {
        registerModalClose.addEventListener('click', closeRegisterModal);
    }
    
    if (partnerModalClose) {
        partnerModalClose.addEventListener('click', closePartnerModal);
    }
    
    // Закрытие модальных окон по клику вне их
    const modals = [
        { id: 'welcomeModal', close: closeWelcomeModal },
        { id: 'loginModal', close: closeLoginModal },
        { id: 'registerModal', close: closeRegisterModal },
        { id: 'partnerModal', close: closePartnerModal }
    ];
    
    modals.forEach(({ id, close }) => {
        const modal = document.getElementById(id);
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    close();
                }
            });
        }
    });
}

// Обработка регистрации
async function handleRegister() {
    // Данные пользователя автоматически доступны из Telegram Web App
    const telegramUser = tg?.initDataUnsafe?.user;
    const telegramId = telegramUser?.id;
    
    const referralCodeInput = document.getElementById('referralCodeInput');
    const referralCode = referralCodeInput?.value.trim().toUpperCase() || null;
    
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                telegram_id: telegramId,
                username: telegramUser?.username,
                first_name: telegramUser?.first_name,
                last_name: telegramUser?.last_name,
                referral_code: referralCode
            })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            userData = result.user;
            if (telegramId) {
                localStorage.setItem(`user_${telegramId}_visited`, 'true');
            }
            closeWelcomeModal();
            updateHeaderButtons();
            showNotification('Регистрация успешна! Добро пожаловать!', 'success');
            // Предлагаем создать первое видео/изображение
            setTimeout(() => {
                showNotification('Создай свое первое видео или изображение!', 'info');
                openCreateModal();
            }, 1000);
        } else {
            // Пользователь уже зарегистрирован
            if (result.user) {
                userData = result.user;
                if (telegramId) {
                    localStorage.setItem(`user_${telegramId}_visited`, 'true');
                }
                closeWelcomeModal();
                updateHeaderButtons();
            } else {
                showNotification(result.message || 'Ошибка регистрации', 'error');
            }
        }
    } catch (error) {
        console.error('Error registering:', error);
        showNotification('Произошла ошибка при регистрации', 'error');
    }
}

// Обработка пропуска реферального кода
async function handleSkipReferral() {
    await handleRegister();
}

// Обновление цены
function updatePrice() {
    // Здесь можно динамически обновлять цену на основе данных пользователя
    const priceElement = document.getElementById('priceAmount');
    if (priceElement && userData) {
        // Пример: цена может зависеть от статуса пользователя
        priceElement.textContent = userData.is_premium ? 'XXX' : 'XXX';
    }
}

// Инициализация кнопок хедера
function initHeaderButtons() {
    const createVideoBtn = document.getElementById('createVideoBtn');
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    const partnerBtn = document.getElementById('partnerBtn');
    
    if (createVideoBtn) {
        createVideoBtn.addEventListener('click', () => {
            if (userData) {
            openCreateModal();
            } else {
                showNotification('Пожалуйста, войдите или зарегистрируйтесь', 'error');
            }
        });
    }
    
    if (registerBtn) {
        registerBtn.addEventListener('click', () => {
            openRegisterModal();
        });
    }
    
    if (loginBtn) {
        loginBtn.addEventListener('click', () => {
            if (userData) {
                handleLogout();
            } else {
                openLoginModal();
            }
        });
    }
    
    if (partnerBtn) {
        partnerBtn.addEventListener('click', () => {
            if (userData) {
                openPartnerModal();
            } else {
                showNotification('Для доступа к партнерке необходимо войти', 'error');
            }
        });
    }
    
    // Обновляем видимость кнопок
    updateHeaderButtons();
}

// Обновление кнопок хедера в зависимости от статуса пользователя
function updateHeaderButtons() {
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    const partnerBtn = document.getElementById('partnerBtn');
    
    if (userData) {
        // Пользователь зарегистрирован
        if (loginBtn) loginBtn.textContent = 'Выход';
        if (registerBtn) registerBtn.style.display = 'none';
        if (partnerBtn) partnerBtn.style.display = 'inline-block';
    } else {
        // Пользователь не зарегистрирован
        if (loginBtn) loginBtn.textContent = 'Вход';
        if (registerBtn) registerBtn.style.display = 'inline-block';
        if (partnerBtn) partnerBtn.style.display = 'none';
    }
}

// Открыть модальное окно входа
function openLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
}

// Закрыть модальное окно входа
function closeLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
        // Очищаем поля
        document.getElementById('loginUsername').value = '';
        document.getElementById('loginPassword').value = '';
    }
}

// Открыть модальное окно регистрации
function openRegisterModal() {
    const modal = document.getElementById('registerModal');
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
}

// Закрыть модальное окно регистрации
function closeRegisterModal() {
    const modal = document.getElementById('registerModal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
        // Очищаем поля
        document.getElementById('registerUsername').value = '';
        document.getElementById('registerPassword').value = '';
        document.getElementById('registerReferralCode').value = '';
    }
}

// Открыть модальное окно партнерки
function openPartnerModal() {
    if (!userData) {
        showNotification('Для доступа к партнерке необходимо войти', 'error');
        return;
    }
    
    const modal = document.getElementById('partnerModal');
    if (modal) {
        // Заполняем данные партнерки
        const partnerCode = userData.referral_code || 'Не доступен';
        const partnerLink = `https://t.me/your_bot?start=ref_${partnerCode}`;
        
        document.getElementById('partnerCodeDisplay').value = partnerCode;
        document.getElementById('partnerLinkDisplay').value = partnerLink;
        
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
}

// Закрыть модальное окно партнерки
function closePartnerModal() {
    const modal = document.getElementById('partnerModal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
}

// Обработка входа через форму
async function handleFormLogin() {
    const usernameInput = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;
    
    if (!usernameInput) {
        showNotification('Введите логин', 'error');
        return;
    }
    
    // Пытаемся определить, это Telegram ID или username
    const isTelegramId = /^\d+$/.test(usernameInput);
    const requestBody = {};
    
    if (isTelegramId) {
        requestBody.telegram_id = parseInt(usernameInput);
    } else {
        requestBody.username = usernameInput;
    }
    
    // Пароль опциональный (для Telegram Web App не обязателен)
    if (password) {
        requestBody.password = password;
    }
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            userData = result.user;
            updateHeaderButtons();
            closeLoginModal();
            showNotification('Вход выполнен успешно!', 'success');
        } else {
            showNotification(result.message || 'Неверный логин или пароль', 'error');
        }
    } catch (error) {
        console.error('Error logging in:', error);
        showNotification('Произошла ошибка при входе', 'error');
    }
}

// Обработка регистрации через форму
async function handleFormRegister() {
    const username = document.getElementById('registerUsername').value.trim();
    const password = document.getElementById('registerPassword').value;
    const referralCode = document.getElementById('registerReferralCode').value.trim().toUpperCase() || null;
    
    if (!username || !password) {
        showNotification('Заполните все обязательные поля', 'error');
        return;
    }
    
    // Получаем данные из Telegram, если доступны
    const telegramUser = tg?.initDataUnsafe?.user;
    const telegramId = telegramUser?.id;
    
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                telegram_id: telegramId || 0, // Если нет Telegram ID, используем 0
                username: username,
                password: password,
                referral_code: referralCode
            })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            userData = result.user;
            updateHeaderButtons();
            closeRegisterModal();
            showNotification('Регистрация успешна! Добро пожаловать!', 'success');
            // Предлагаем создать первое видео/изображение
            setTimeout(() => {
                showNotification('Создай свое первое видео или изображение!', 'info');
                openCreateModal();
            }, 1000);
        } else {
            showNotification(result.message || 'Ошибка регистрации', 'error');
        }
    } catch (error) {
        console.error('Error registering:', error);
        showNotification('Произошла ошибка при регистрации', 'error');
    }
}

// Обработка выхода
async function handleLogout() {
    try {
        const response = await fetch('/api/logout', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            userData = null;
            const telegramUser = tg?.initDataUnsafe?.user;
            if (telegramUser) {
                localStorage.removeItem(`user_${telegramUser.id}_visited`);
            }
            updateHeaderButtons();
            showNotification('Выход выполнен успешно', 'success');
        }
    } catch (error) {
        console.error('Error logging out:', error);
        // Выход на клиенте в любом случае
        userData = null;
        const telegramUser = tg?.initDataUnsafe?.user;
        if (telegramUser) {
            localStorage.removeItem(`user_${telegramUser.id}_visited`);
        }
        updateHeaderButtons();
    }
}

// Инициализация модального окна создания
function initCreateModal() {
    const createModal = document.getElementById('createModal');
    const modalClose = document.getElementById('modalClose');
    const startFreeBtn = document.getElementById('startFreeBtn');
    const startBtn = document.getElementById('startBtn');
    const createTabs = document.querySelectorAll('.create-tab');
    
    // Открытие модального окна
    if (startFreeBtn) {
        startFreeBtn.addEventListener('click', openCreateModal);
    }
    
    if (startBtn) {
        startBtn.addEventListener('click', openCreateModal);
    }
    
    // Закрытие модального окна
    if (modalClose) {
        modalClose.addEventListener('click', closeCreateModal);
    }
    
    if (createModal) {
        createModal.addEventListener('click', (e) => {
            if (e.target === createModal) {
                closeCreateModal();
            }
        });
    }
    
    // Переключение вкладок
    createTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;
            
            // Убираем активный класс у всех вкладок и секций
            createTabs.forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.create-section').forEach(s => s.classList.remove('active'));
            
            // Добавляем активный класс
            tab.classList.add('active');
            document.getElementById(`${targetTab}-section`).classList.add('active');
        });
    });
}

// Открытие модального окна создания
function openCreateModal() {
    const modal = document.getElementById('createModal');
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
}

// Закрытие модального окна создания
function closeCreateModal() {
    const modal = document.getElementById('createModal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
}

// Загрузка файлов
function initFileUploads() {
    // Загрузка исходного изображения
    const sourceImageInput = document.getElementById('sourceImage');
    const sourcePreview = document.getElementById('sourcePreview');
    
    if (sourceImageInput && sourcePreview) {
        sourceImageInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                sourceImageFile = file;
                displayPreview(file, sourcePreview, 'image');
            }
        });
    }
    
    // Загрузка целевого видео
    const targetVideoInput = document.getElementById('targetVideo');
    const targetPreview = document.getElementById('targetPreview');
    
    if (targetVideoInput && targetPreview) {
        targetVideoInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                targetVideoFile = file;
                displayPreview(file, targetPreview, 'video');
            }
        });
    }
}

// Отображение превью
function displayPreview(file, previewElement, type) {
    const reader = new FileReader();
    
    reader.onload = (e) => {
        const element = type === 'image' 
            ? `<img src="${e.target.result}" alt="Preview">`
            : `<video src="${e.target.result}" controls></video>`;
        
        previewElement.innerHTML = element;
        previewElement.classList.add('show');
        
        // Скрываем label
        const label = previewElement.previousElementSibling;
        if (label && label.classList.contains('upload-label')) {
            label.style.display = 'none';
        }
    };
    
    reader.readAsDataURL(file);
}

// Инициализация переключателей демо
function initDemoToggles() {
    const toggleButtons = document.querySelectorAll('.toggle-btn');
    
    toggleButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const demoItem = btn.closest('.demo-item');
            const allToggles = demoItem.querySelectorAll('.toggle-btn');
            
            // Убираем активный класс у всех кнопок в этом элементе
            allToggles.forEach(t => t.classList.remove('active'));
            
            // Добавляем активный класс
            btn.classList.add('active');
            
            // Здесь можно добавить логику переключения видео До/После
            const demoType = btn.dataset.demo;
            console.log('Demo type:', demoType);
        });
    });
}

// Инициализация кнопок
function initButtons() {
    // Кнопка создания DeepFake
    const swapFaceBtn = document.getElementById('swapFaceBtn');
    if (swapFaceBtn) {
        swapFaceBtn.addEventListener('click', handleSwapFace);
    }
    
    // Кнопка генерации изображения
    const generateBtn = document.getElementById('generateBtn');
    if (generateBtn) {
        generateBtn.addEventListener('click', handleGenerateImage);
    }
    
    // Кнопка генерации видео
    const generateVideoBtn = document.getElementById('generateVideoBtn');
    if (generateVideoBtn) {
        generateVideoBtn.addEventListener('click', handleGenerateVideo);
    }
    
    // Кнопка активации тарифа
    const activateBtn = document.getElementById('activateBtn');
    if (activateBtn) {
        activateBtn.addEventListener('click', () => {
            showNotification('Функция оплаты будет доступна в следующей версии', 'info');
        });
    }
    
    // Кнопка получения партнерской ссылки
    const getLinkBtn = document.getElementById('getLinkBtn');
    if (getLinkBtn) {
        getLinkBtn.addEventListener('click', () => {
            openPartnerModal();
        });
    }
    
    // Модальное окно результата
    const resultModalClose = document.getElementById('resultModalClose');
    if (resultModalClose) {
        resultModalClose.addEventListener('click', closeResultModal);
    }
    
    const resultModal = document.getElementById('resultModal');
    if (resultModal) {
        resultModal.addEventListener('click', (e) => {
            if (e.target === resultModal) {
                closeResultModal();
            }
        });
    }
    
    // Кнопка скачивания
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            const preview = document.getElementById('resultPreview');
            const media = preview.querySelector('img, video');
            if (media) {
                window.open(media.src, '_blank');
            }
        });
    }
    
    // Кнопка поделиться
    const shareBtn = document.getElementById('shareBtn');
    if (shareBtn) {
        shareBtn.addEventListener('click', () => {
            if (tg?.shareUrl) {
                const preview = document.getElementById('resultPreview');
                const media = preview.querySelector('img, video');
                if (media) {
                    tg.shareUrl(media.src);
                }
            } else {
                showNotification('Функция "Поделиться" будет доступна в следующей версии!', 'info');
            }
        });
    }
    
    // FAQ и Policy
    const faqBtn = document.getElementById('faqBtn');
    if (faqBtn) {
        faqBtn.addEventListener('click', (e) => {
            e.preventDefault();
            showNotification('FAQ будет доступен в следующей версии', 'info');
        });
    }
    
    const policyBtn = document.getElementById('policyBtn');
    if (policyBtn) {
        policyBtn.addEventListener('click', (e) => {
            e.preventDefault();
            showNotification('Политика конфиденциальности будет доступна в следующей версии', 'info');
        });
    }
}

// Плавная прокрутка к партнерке
function scrollToPartnership() {
    const partnership = document.querySelector('.partnership');
    if (partnership) {
        partnership.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Инициализация плавной прокрутки
function initSmoothScroll() {
    // Добавляем плавную прокрутку для всех якорных ссылок
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

// Обработка замены лица
async function handleSwapFace() {
    if (!sourceImageFile) {
        showNotification('Загрузите фото с лицом', 'error');
        return;
    }
    
    if (!targetVideoFile) {
        showNotification('Загрузите целевое видео', 'error');
        return;
    }
    
    // Автоматически загружаем данные пользователя из Telegram, если еще не загружены
    if (!userData) {
        const telegramUser = tg?.initDataUnsafe?.user;
        if (telegramUser?.id) {
            await loadUserData(telegramUser.id);
        }
    }
    
    // Проверяем баланс
    if (userData.balance < 50 && userData.free_generations === 0) {
        showNotification('Недостаточно поинтов. Пополните баланс!', 'error');
        return;
    }
    
    showLoader('Создаем Face Swap...');
    
    try {
        const formData = new FormData();
        formData.append('telegram_id', userData.telegram_id);
        formData.append('source_image', sourceImageFile);
        formData.append('target_video', targetVideoFile);
        
        const response = await fetch('/api/deepfake/swap', {
            method: 'POST',
            body: formData
        });
        
        hideLoader();
        
        if (response.ok) {
            const result = await response.json();
            
            if (result.success) {
                showResult(result.video_url, 'video');
                closeCreateModal();
                await loadUserData(userData.telegram_id);
                showNotification('Face Swap успешно создан!', 'success');
            } else {
                showNotification(result.message || 'Ошибка при создании', 'error');
            }
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Ошибка сервера', 'error');
        }
    } catch (error) {
        hideLoader();
        console.error('Error:', error);
        showNotification('Произошла ошибка. Попробуйте позже.', 'error');
    }
}

// Обработка генерации изображения
async function handleGenerateImage() {
    const promptInput = document.getElementById('promptInput');
    if (!promptInput) return;
    
    const prompt = promptInput.value.trim();
    
    if (!prompt) {
        showNotification('Введите описание сцены', 'error');
        return;
    }
    
    // Проверка на запрещенный контент (базовая клиентская проверка)
    if (!checkContentSafety(prompt)) {
        showNotification('⛔ Обнаружено недопустимое содержание. Пожалуйста, ознакомьтесь с политикой контента.', 'error');
        return;
    }
    
    // Автоматически загружаем данные пользователя из Telegram, если еще не загружены
    if (!userData) {
        const telegramUser = tg?.initDataUnsafe?.user;
        if (telegramUser?.id) {
            await loadUserData(telegramUser.id);
        }
    }
    
    // Проверяем баланс
    if (userData.balance < 10 && userData.free_generations === 0) {
        showNotification('Недостаточно поинтов. Пополните баланс!', 'error');
        return;
    }
    
    showLoader('Генерируем изображение...');
    
    try {
        const response = await fetch('/api/generate/image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                telegram_id: userData.telegram_id,
                prompt: prompt,
                model: 'flux',
                style: 'realistic'
            })
        });
        
        hideLoader();
        
        if (response.ok) {
            const result = await response.json();
            
            if (result.success) {
                showResult(result.image_url, 'image');
                closeCreateModal();
                await loadUserData(userData.telegram_id);
                showNotification('Изображение успешно сгенерировано!', 'success');
            } else {
                showNotification(result.message || 'Ошибка при генерации', 'error');
            }
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Ошибка сервера', 'error');
        }
    } catch (error) {
        hideLoader();
        console.error('Error:', error);
        showNotification('Произошла ошибка. Попробуйте позже.', 'error');
    }
}

// Обработка генерации видео
async function handleGenerateVideo() {
    const videoPromptInput = document.getElementById('videoPromptInput');
    const videoDurationSelect = document.getElementById('videoDuration');
    
    if (!videoPromptInput) return;
    
    const prompt = videoPromptInput.value.trim();
    const duration = videoDurationSelect ? parseInt(videoDurationSelect.value) : 5;
    
    if (!prompt) {
        showNotification('Введите описание видео сцены', 'error');
        return;
    }
    
    // Проверка на запрещенный контент (базовая клиентская проверка)
    if (!checkContentSafety(prompt)) {
        showNotification('⛔ Обнаружено недопустимое содержание. Пожалуйста, ознакомьтесь с политикой контента.', 'error');
        return;
    }
    
    // Автоматически загружаем данные пользователя из Telegram, если еще не загружены
    if (!userData) {
        const telegramUser = tg?.initDataUnsafe?.user;
        if (telegramUser?.id) {
            await loadUserData(telegramUser.id);
        }
    }
    
    // Проверяем баланс (видео дороже - 30 поинтов)
    if (userData.balance < 30 && userData.free_generations === 0) {
        showNotification('Недостаточно поинтов. Пополните баланс!', 'error');
        return;
    }
    
    showLoader('Генерируем видео... Это может занять несколько минут.');
    
    try {
        const response = await fetch('/api/generate/video', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                telegram_id: userData.telegram_id,
                prompt: prompt,
                model: 'runway',
                style: 'realistic',
                duration: duration,
                fps: 24,
                width: 1280,
                height: 720
            })
        });
        
        hideLoader();
        
        if (response.ok) {
            const result = await response.json();
            
            if (result.success) {
                // Если есть task_id, значит генерация асинхронная
                if (result.task_id) {
                    showNotification('Генерация видео началась. Проверяем статус...', 'info');
                    // Можно добавить проверку статуса через polling
                    await checkVideoTaskStatus(result.task_id, result.generation_id);
                } else if (result.video_url) {
                    showResult(result.video_url, 'video');
                    closeCreateModal();
                    await loadUserData(userData.telegram_id);
                    showNotification('Видео успешно сгенерировано!', 'success');
                } else {
                    showNotification('Видео генерируется. Проверьте позже.', 'info');
                }
            } else {
                showNotification(result.message || 'Ошибка при генерации', 'error');
            }
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Ошибка сервера', 'error');
        }
    } catch (error) {
        hideLoader();
        console.error('Error:', error);
        showNotification('Произошла ошибка. Попробуйте позже.', 'error');
    }
}

// Проверка статуса задачи генерации видео
async function checkVideoTaskStatus(taskId, generationId) {
    let attempts = 0;
    const maxAttempts = 60; // Проверяем до 5 минут (60 попыток по 5 секунд)
    
    const checkStatus = async () => {
        try {
            const response = await fetch(`/api/video/task/${taskId}`);
            
            if (response.ok) {
                const status = await response.json();
                
                if (status.status === 'completed' && status.video_url) {
                    hideLoader();
                    showResult(status.video_url, 'video');
                    closeCreateModal();
                    await loadUserData(userData.telegram_id);
                    showNotification('Видео успешно сгенерировано!', 'success');
                    return true;
                } else if (status.status === 'failed') {
                    hideLoader();
                    showNotification(status.message || 'Ошибка при генерации видео', 'error');
                    return true;
                } else if (status.status === 'processing') {
                    showLoader(`Генерируем видео... Прогресс: ${status.progress || 0}%`);
                    attempts++;
                    if (attempts < maxAttempts) {
                        setTimeout(checkStatus, 5000); // Проверяем каждые 5 секунд
                    } else {
                        hideLoader();
                        showNotification('Генерация видео занимает больше времени, чем ожидалось. Проверьте позже.', 'info');
                    }
                    return false;
                }
            }
        } catch (error) {
            console.error('Error checking video status:', error);
            attempts++;
            if (attempts < maxAttempts) {
                setTimeout(checkStatus, 5000);
            } else {
                hideLoader();
                showNotification('Не удалось проверить статус генерации. Проверьте позже.', 'error');
            }
            return false;
        }
    };
    
    await checkStatus();
}

// Получение партнерской ссылки (используется для кнопки в секции партнерки)
async function handleGetPartnerLink() {
    if (!userData) {
        showNotification('Для доступа к партнерке необходимо войти', 'error');
            return;
        }
    openPartnerModal();
}

// Показать результат
function showResult(url, type = 'image') {
    const resultPreview = document.getElementById('resultPreview');
    const resultModal = document.getElementById('resultModal');
    
    if (!resultPreview || !resultModal) return;
    
    if (type === 'image') {
        resultPreview.innerHTML = `<img src="${url}" alt="Generated image">`;
    } else {
        resultPreview.innerHTML = `<video src="${url}" controls autoplay></video>`;
    }
    
    resultModal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

// Закрыть модальное окно результата
function closeResultModal() {
    const resultModal = document.getElementById('resultModal');
    if (resultModal) {
        resultModal.classList.remove('show');
        document.body.style.overflow = '';
    }
}

// Показать уведомление
function showNotification(message, type = 'info') {
    if (tg?.showAlert) {
        tg.showAlert(message);
    } else if (tg?.showPopup) {
        tg.showPopup({
            title: type === 'error' ? 'Ошибка' : type === 'success' ? 'Успех' : 'Информация',
            message: message,
            buttons: [{ type: 'ok' }]
        });
    } else {
        alert(message);
    }
}

// Показать/скрыть лоадер
function showLoader(text = 'Загрузка...') {
    const loader = document.getElementById('loader');
    if (loader) {
        const loaderText = loader.querySelector('.loader-text');
        if (loaderText) {
            loaderText.textContent = text;
        }
        loader.classList.add('show');
    }
}

function hideLoader() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.classList.remove('show');
    }
}

// Проверка контента на безопасность (клиентская сторона)
function checkContentSafety(text) {
    const bannedKeywords = [
        'porn', 'порно', 'xxx', 'sex', 'секс', 'nude', 'голый', 'голая',
        'nsfw', '18+', 'adult', 'эротика', 'erotic', 'naked', 'обнаженн'
    ];
    
    const textLower = text.toLowerCase();
    
    for (const keyword of bannedKeywords) {
        if (textLower.includes(keyword)) {
            return false;
        }
    }
    
    return true;
}
