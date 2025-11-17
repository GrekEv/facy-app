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
    // Если установлена переменная окружения - используем её
    if (window.API_BASE_URL) {
        return window.API_BASE_URL;
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

// Глобальные переменные
let userData = null;
let sourceImageFile = null;
let targetVideoFile = null;
let statsData = null;

// Инициализация приложения
document.addEventListener('DOMContentLoaded', async () => {
    console.log('OnlyFace App initialized');
    
    // Получаем данные пользователя из Telegram (всегда доступны в Telegram Web App)
    const telegramUser = tg?.initDataUnsafe?.user;
    
    if (telegramUser && telegramUser.id) {
        // Автоматически загружаем/создаем пользователя при загрузке страницы
        await loadUserData(telegramUser.id);
    }
    
    // Загружаем статистику
    await loadStats();
    
    // Инициализируем обработчики
    initHeaderButtons();
    initCreateModal();
    initFileUploads();
    initDemoToggles();
    initButtons();
    initSmoothScroll();
});

// Загрузка данных пользователя (автоматически создается если не существует)
async function loadUserData(telegramId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/user/${telegramId}`);
        
        if (response.ok) {
            userData = await response.json();
            updatePrice();
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

// Инициализация кнопок хедера
function initHeaderButtons() {
    const createVideoBtn = document.getElementById('createVideoBtn');
    
    if (createVideoBtn) {
        createVideoBtn.addEventListener('click', () => {
            openCreateModal();
        });
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
    
    // Получаем telegram_id из Telegram Web App или используем тестовый ID
    const telegramUser = tg?.initDataUnsafe?.user;
    let telegramId = telegramUser?.id;
    
    // Если нет Telegram ID, используем тестовый ID для разработки
    if (!telegramId) {
        telegramId = 123456789; // Тестовый ID
        console.warn('Telegram ID not found, using test ID:', telegramId);
    }
    
    // Автоматически загружаем данные пользователя из Telegram, если еще не загружены
    if (!userData && telegramUser?.id) {
        await loadUserData(telegramUser.id);
    }
    
    showLoader('Генерируем изображение...');
    
    try {
        console.log('Sending request to:', `${API_BASE_URL}/api/generate/image`);
        console.log('Request body:', {
            telegram_id: telegramId,
            prompt: prompt,
            model: 'flux',
            style: 'realistic'
        });
        
        const response = await fetch(`${API_BASE_URL}/api/generate/image`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                telegram_id: telegramId,
                prompt: prompt,
                model: 'flux',
                style: 'realistic'
            })
        });
        
        console.log('Response status:', response.status);
        const result = await response.json();
        console.log('Response data:', result);
        
        hideLoader();
        
        if (response.ok) {
            if (result.success) {
                showResult(result.image_url, 'image');
                closeCreateModal();
                if (telegramUser?.id) {
                    await loadUserData(telegramUser.id);
                }
                showNotification('Изображение успешно сгенерировано!', 'success');
            } else {
                showNotification(result.message || 'Ошибка при генерации', 'error');
            }
        } else {
            showNotification(result.detail || 'Ошибка сервера', 'error');
        }
    } catch (error) {
        hideLoader();
        console.error('Error generating image:', error);
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
