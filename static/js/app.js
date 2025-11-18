// Telegram Web App
const tg = window.Telegram?.WebApp;
if (tg) {
    tg.expand();
    tg.setHeaderColor('#0a0a0f');
    tg.setBackgroundColor('#0a0a0f');
}

// API Base URL - автоматическое определение:
// - Если на Vercel (не onlyface.art) - используем API на Yandex Cloud
// - Если на onlyface.art - используем локальный API (относительные пути)
const getApiBaseUrl = () => {
    // Проверяем переменную окружения, но игнорируем неправильные значения
    if (window.API_BASE_URL) {
        const url = window.API_BASE_URL;
        // Игнорируем URL с payment в пути или heleket домен
        if (!url.includes('/payment') && !url.includes('heleket')) {
            return url;
        }
    }
    
    // Определяем текущий домен
    const currentHost = window.location.hostname;
    
    // Если на домене onlyface.art - используем локальный API (пустая строка для относительных путей)
    if (currentHost === 'onlyface.art' || currentHost.includes('onlyface')) {
        return '';
    }
    
    // Если на Vercel или другом домене - используем API на Yandex Cloud
    return 'https://onlyface.art';
};

const API_BASE_URL = getApiBaseUrl();
console.log('API_BASE_URL determined:', API_BASE_URL);
console.log('window.API_BASE_URL:', window.API_BASE_URL);
console.log('window.location.hostname:', window.location.hostname);

// Глобальные переменные
let userData = null;
let sourceImageFile = null;
let targetVideoFile = null;
let statsData = null;

// Инициализация приложения
document.addEventListener('DOMContentLoaded', async () => {
    console.log('OnlyFace App initialized');
    
    // Инициализируем обработчики сразу
    initHeaderButtons();
    initCreateModal();
    initFileUploads();
    initDemoToggles();
    initButtons();
    initSmoothScroll();
    
    // Загружаем данные пользователя в фоне (не блокируем интерфейс)
    const telegramUser = tg?.initDataUnsafe?.user;
    if (telegramUser && telegramUser.id) {
        loadUserData(telegramUser.id).catch(err => {
            console.error('Error loading user data:', err);
        });
    }
    
    // Загружаем статистику в фоне
    loadStats().catch(err => {
        console.error('Error loading stats:', err);
    });
});

// Загрузка данных пользователя (автоматически создается если не существует)
async function loadUserData(telegramId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/user/${telegramId}`);
        
        if (response.ok) {
            userData = await response.json();
            updatePrice();
            updateReferralLink();
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
        const response = await fetch(`${API_BASE_URL}/api/stats`);
        
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


// Обновление цены
function updatePrice() {
    // Здесь можно динамически обновлять цену на основе данных пользователя
    const priceElement = document.getElementById('priceAmount');
    if (priceElement && userData) {
        // Пример: цена может зависеть от статуса пользователя
        priceElement.textContent = userData.is_premium ? 'XXX' : 'XXX';
    }
}

// Глобальная переменная для хранения реферальной ссылки
let referralLink = null;

// Обновление реферальной ссылки и генерация QR-кода
function updateReferralLink() {
    const referralQRCode = document.getElementById('referralQRCode');
    if (!referralQRCode || !userData) return;
    
    // Получаем реферальный код пользователя
    const referralCode = userData.referral_code;
    if (!referralCode) return;
    
    // Формируем реферальную ссылку на оплату с параметром ref
    const paymentUrl = window.STANDARD_PLAN_PAYMENT_URL || 'https://web.tribute.tg/p/n1Q';
    referralLink = `${paymentUrl}?ref=${referralCode}`;
    
    // Генерируем QR-код
    if (typeof QRCode !== 'undefined') {
        QRCode.toCanvas(referralQRCode, referralLink, {
            width: 180,
            margin: 2,
            color: {
                dark: '#000000',
                light: '#FFFFFF'
            }
        }, function (error) {
            if (error) {
                console.error('Error generating QR code:', error);
                // Fallback - показываем ссылку текстом
                referralQRCode.innerHTML = `<p style="color: var(--text-primary); word-break: break-all; padding: 1rem;">${referralLink}</p>`;
            }
        });
    } else {
        // Если библиотека не загрузилась, показываем ссылку текстом
        referralQRCode.innerHTML = `<p style="color: var(--text-primary); word-break: break-all; padding: 1rem;">${referralLink}</p>`;
    }
}

// Инициализация кнопок хедера (убрана кнопка создания видео)
function initHeaderButtons() {
    // Кнопка создания видео убрана из хедера
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
        
        // Убеждаемся, что обработчики привязаны к кнопкам внутри модального окна
        const generateBtn = document.getElementById('generateBtn');
        if (generateBtn && !generateBtn.dataset.listenerAttached) {
            generateBtn.addEventListener('click', (e) => {
                console.log('Generate button clicked from modal!');
                e.preventDefault();
                handleGenerateImage();
            });
            generateBtn.dataset.listenerAttached = 'true';
        }
        
        const generateVideoBtn = document.getElementById('generateVideoBtn');
        if (generateVideoBtn && !generateVideoBtn.dataset.listenerAttached) {
            generateVideoBtn.addEventListener('click', (e) => {
                console.log('Generate video button clicked from modal!');
                e.preventDefault();
                handleGenerateVideo();
            });
            generateVideoBtn.dataset.listenerAttached = 'true';
        }
        
        const swapFaceBtn = document.getElementById('swapFaceBtn');
        if (swapFaceBtn && !swapFaceBtn.dataset.listenerAttached) {
            swapFaceBtn.addEventListener('click', (e) => {
                console.log('Swap face button clicked from modal!');
                e.preventDefault();
                handleSwapFace();
            });
            swapFaceBtn.dataset.listenerAttached = 'true';
        }
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
    console.log('generateBtn found:', generateBtn);
    if (generateBtn) {
        generateBtn.addEventListener('click', (e) => {
            console.log('Generate button clicked!');
            e.preventDefault();
            handleGenerateImage();
        });
    } else {
        console.error('generateBtn not found in DOM!');
    }
    
    // Кнопка генерации видео
    const generateVideoBtn = document.getElementById('generateVideoBtn');
    if (generateVideoBtn) {
        generateVideoBtn.addEventListener('click', handleGenerateVideo);
    }
    
    // Базовый тариф теперь всегда активен - кнопка заменена на надпись "Активен"
    
    // Кнопка поделиться реферальной ссылкой
    const shareReferralBtn = document.getElementById('shareReferralBtn');
    if (shareReferralBtn) {
        shareReferralBtn.addEventListener('click', async () => {
            if (!referralLink) {
                showNotification('Реферальная ссылка не загружена', 'error');
                return;
            }
            const shareText = `🎁 Привет! Попробуй OnlyFace - приложение для замены лиц и генерации видео!\n\n${referralLink}\n\nПри оплате подписки по этой ссылке мы оба получим бонусы! 🚀`;
            
            // Используем Telegram Share API если доступен
            if (tg?.shareUrl) {
                tg.shareUrl(referralLink);
            } else if (navigator.share) {
                // Используем Web Share API
                try {
                    await navigator.share({
                        title: 'OnlyFace - Приглашение',
                        text: shareText,
                        url: referralLink
                    });
                } catch (err) {
                    // Если пользователь отменил или произошла ошибка
                    console.log('Share cancelled or error:', err);
                }
            } else {
                // Fallback - копируем в буфер обмена
                try {
                    await navigator.clipboard.writeText(shareText);
                    showNotification('Текст для отправки скопирован! Вставьте его в сообщение другу.', 'success');
                } catch (err) {
                    // Создаем временный элемент для копирования
                    const tempInput = document.createElement('input');
                    tempInput.value = referralLink;
                    document.body.appendChild(tempInput);
                    tempInput.select();
                    document.execCommand('copy');
                    document.body.removeChild(tempInput);
                    showNotification('Ссылка скопирована! Отправьте её другу.', 'success');
                }
            }
        });
    }
    
    // Кнопка оплаты стандартного тарифа ($20)
    const activateStandardBtn = document.getElementById('activateStandardBtn');
    if (activateStandardBtn) {
        activateStandardBtn.addEventListener('click', async () => {
            // Получаем ссылку на оплату из переменной окружения или используем дефолтную
            const paymentUrl = window.STANDARD_PLAN_PAYMENT_URL || 'https://web.tribute.tg/p/n1Q';
            
            if (tg?.openLink) {
                tg.openLink(paymentUrl);
            } else {
                window.open(paymentUrl, '_blank');
            }
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
    
    // Получаем telegram_id из Telegram Web App
    const telegramUser = tg?.initDataUnsafe?.user;
    const telegramId = telegramUser?.id;
    
    if (!telegramId) {
        showNotification('Не удалось получить данные пользователя из Telegram', 'error');
        return;
    }
    
    // Автоматически загружаем данные пользователя из Telegram, если еще не загружены
    if (!userData) {
        await loadUserData(telegramId);
    }
    
    // Проверка баланса убрана - бесплатный доступ
    
    showLoader('Создаем Face Swap...');
    
    try {
        const formData = new FormData();
        formData.append('telegram_id', telegramId);
        formData.append('source_image', sourceImageFile);
        formData.append('target_video', targetVideoFile);
        
        const response = await fetch(`${API_BASE_URL}/api/deepfake/swap`, {
            method: 'POST',
            body: formData
        });
        
        hideLoader();
        
        if (response.ok) {
            const result = await response.json();
            
            if (result.success) {
                showResult(result.video_url, 'video');
                closeCreateModal();
                await loadUserData(telegramId);
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
    console.log('handleGenerateImage called');
    
    const promptInput = document.getElementById('promptInput');
    if (!promptInput) {
        console.error('promptInput not found!');
        showNotification('Ошибка: поле ввода не найдено', 'error');
        return;
    }
    
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
    
    // Получаем telegram_id из Telegram Web App или используем тестовый ID
    const telegramUser = tg?.initDataUnsafe?.user;
    let telegramId = telegramUser?.id;
    
    // Если нет Telegram ID, используем тестовый ID для разработки
    if (!telegramId) {
        telegramId = 123456789; // Тестовый ID
        console.warn('Telegram ID not found, using test ID:', telegramId);
    }
    
    console.log('Starting generation with telegram_id:', telegramId, 'prompt:', prompt);
    showLoader('Генерируем изображение...');
    
    try {
        const apiUrl = `${API_BASE_URL}/api/generate/image`;
        console.log('Sending request to:', apiUrl);
        console.log('API_BASE_URL:', API_BASE_URL);
        
        const requestBody = {
            telegram_id: telegramId,
            prompt: prompt,
            model: 'flux',
            style: 'realistic'
        };
        console.log('Request body:', requestBody);
        
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        let result;
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            result = await response.json();
        } else {
            const text = await response.text();
            console.error('Non-JSON response:', text);
            hideLoader();
            showNotification(`Ошибка сервера: ${text.substring(0, 100)}`, 'error');
            return;
        }
        
        console.log('Response data:', result);
        
        hideLoader();
        
        if (response.ok) {
            if (result.success) {
                console.log('Generation successful, image_url:', result.image_url);
                showResult(result.image_url, 'image');
                closeCreateModal();
                if (telegramUser?.id) {
                    await loadUserData(telegramUser.id);
                }
                showNotification('Изображение успешно сгенерировано!', 'success');
            } else {
                console.error('Generation failed:', result.message);
                showNotification(result.message || 'Ошибка при генерации', 'error');
            }
        } else {
            console.error('HTTP error:', result);
            showNotification(result.detail || result.message || 'Ошибка сервера', 'error');
        }
    } catch (error) {
        hideLoader();
        console.error('Error generating image:', error);
        console.error('Error stack:', error.stack);
        showNotification(`Произошла ошибка: ${error.message}`, 'error');
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
    
    // Получаем telegram_id из Telegram Web App
    const telegramUser = tg?.initDataUnsafe?.user;
    const telegramId = telegramUser?.id;
    
    if (!telegramId) {
        showNotification('Не удалось получить данные пользователя из Telegram', 'error');
        return;
    }
    
    // Автоматически загружаем данные пользователя из Telegram, если еще не загружены
    if (!userData) {
        await loadUserData(telegramId);
    }
    
    // Проверка баланса убрана - бесплатный доступ
    
    showLoader('Генерируем видео... Это может занять несколько минут.');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/generate/video`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                telegram_id: telegramId,
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
                    await loadUserData(telegramId);
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
    
    // Получаем telegram_id из Telegram Web App
    const telegramUser = tg?.initDataUnsafe?.user;
    const telegramId = telegramUser?.id;
    
    const checkStatus = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/video/task/${taskId}`);
            
            if (response.ok) {
                const status = await response.json();
                
                if (status.status === 'completed' && status.video_url) {
                    hideLoader();
                    showResult(status.video_url, 'video');
                    closeCreateModal();
                    if (telegramId) {
                        await loadUserData(telegramId);
                    }
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
