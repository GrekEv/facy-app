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
    
    // Если на Vercel - используем относительные пути (API на том же домене)
    if (currentHost.includes('vercel.app')) {
        return '';
    }
    
    // Если на другом домене - используем API на Yandex Cloud
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
    console.log('Window location:', window.location.href);
    console.log('API_BASE_URL:', API_BASE_URL);
    
    // Инициализируем обработчики сразу
    initHeaderButtons();
    initCreateModal();
    initFileUploads();
    initDemoToggles();
    initButtons();
    initSmoothScroll();
    initEmailAuth();
    
    // Проверка загрузки изображений
    checkDemoImages();
    
    // Также используем делегирование событий для кнопок реферальной программы
    // на случай если они динамически создаются или обработчики не привязались
    const referralSection = document.querySelector('.referral-section');
    if (referralSection) {
        console.log('Setting up event delegation for referral section');
        referralSection.addEventListener('click', async (e) => {
            const target = e.target.closest('button');
            if (!target) return;
            
            // Проверяем, есть ли уже обработчик на кнопке
            // Если обработчик уже есть, он сработает сам
            // Если нет - обрабатываем здесь
            if (target.id === 'copyReferralLinkBtn') {
                // Проверяем, есть ли обработчик
                if (!target.hasAttribute('data-handler-attached')) {
                    console.log('Copy referral link clicked via delegation (no handler attached)');
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Если userData еще не загружен, загружаем его
                    const telegramUser = tg?.initDataUnsafe?.user;
                    const telegramId = telegramUser?.id;
                    
                    if (!userData && telegramId) {
                        await loadUserData(telegramId);
                    }
                    
                    // Генерируем ссылку если еще не сгенерирована
                    if (!referralLink) {
                        await generateReferralLink();
                    }
                    
                    if (!referralLink) {
                        showNotification('Не удалось сгенерировать реферальную ссылку. Попробуйте позже.', 'error');
                        return;
                    }
                    
                    // Копируем ссылку
                    try {
                        if (navigator.clipboard && navigator.clipboard.writeText) {
                            await navigator.clipboard.writeText(referralLink);
                            showNotification('Ссылка приглашения скопирована!', 'success');
                        } else {
                            const tempInput = document.createElement('input');
                            tempInput.value = referralLink;
                            tempInput.style.position = 'fixed';
                            tempInput.style.opacity = '0';
                            tempInput.style.left = '-9999px';
                            document.body.appendChild(tempInput);
                            tempInput.select();
                            tempInput.setSelectionRange(0, 99999);
                            document.execCommand('copy');
                            document.body.removeChild(tempInput);
                            showNotification('Ссылка приглашения скопирована!', 'success');
                        }
                    } catch (err) {
                        showNotification(`Реферальная ссылка: ${referralLink}`, 'info');
                    }
                }
            } else if (target.id === 'showQRBtn') {
                if (!target.hasAttribute('data-handler-attached')) {
                    console.log('Show QR clicked via delegation (no handler attached)');
                    e.preventDefault();
                    e.stopPropagation();
                    generateQRCode();
                }
            }
        });
    }
    
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
        const apiUrl = API_BASE_URL ? `${API_BASE_URL}/api/user/${telegramId}` : `/api/user/${telegramId}`;
        console.log('Loading user data from:', apiUrl);
        
        const response = await fetch(apiUrl);
        
        if (response.ok) {
            userData = await response.json();
            console.log('User data loaded:', userData);
            
            // Если referral_code отсутствует, ждем немного и перезагружаем (бэкенд должен создать его)
            if (!userData.referral_code) {
                console.warn('Referral code missing, waiting and reloading...');
                await new Promise(resolve => setTimeout(resolve, 1000));
                const retryResponse = await fetch(apiUrl);
                if (retryResponse.ok) {
                    userData = await retryResponse.json();
                    console.log('User data reloaded:', userData);
                }
            }
            
            updatePrice();
            // Генерируем реферальную ссылку при загрузке данных пользователя
            await generateReferralLink();
            
            // Проверяем, нужно ли подтвердить email
            if (userData && !userData.email_verified) {
                // Показываем модальное окно авторизации по email
                setTimeout(() => {
                    showEmailAuthModal();
                }, 1000); // Небольшая задержка для лучшего UX
            }
        } else {
            const errorText = await response.text();
            console.error('Failed to load user data:', response.status, errorText);
            
            // Проверяем, не связана ли ошибка с базой данных
            if (response.status === 503) {
                try {
                    const errorData = JSON.parse(errorText);
                    if (errorData.detail && errorData.detail.includes('база данных')) {
                        console.error('Database not configured!');
                        showNotification('База данных не настроена. Обратитесь к администратору.', 'error');
                    }
                } catch (e) {
                    // Не JSON ответ
                }
            }
        }
    } catch (error) {
        console.error('Error loading user data:', error);
        // Проверяем, не связана ли ошибка с подключением
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            showNotification('Не удалось подключиться к серверу. Проверьте подключение к интернету.', 'error');
        }
    }
}

// Загрузка статистики
async function loadStats() {
    try {
        const statsApiUrl = API_BASE_URL ? `${API_BASE_URL}/api/stats` : '/api/stats';
        const response = await fetch(statsApiUrl);
        
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

// Генерация реферальной ссылки для регистрации
async function generateReferralLink() {
    console.log('generateReferralLink called, userData:', userData);
    
    // Если userData отсутствует, пытаемся загрузить его
    if (!userData) {
        console.warn('User data not available, trying to load...');
        const telegramUser = tg?.initDataUnsafe?.user;
        const telegramId = telegramUser?.id;
        
        if (telegramId) {
            await loadUserData(telegramId);
        } else {
            console.warn('Telegram ID not available');
            return null;
        }
    }
    
    // Если referral_code отсутствует, перезагружаем данные пользователя
    if (!userData?.referral_code) {
        console.warn('Referral code not available, reloading user data...');
        const telegramUser = tg?.initDataUnsafe?.user;
        const telegramId = telegramUser?.id;
        
        if (telegramId) {
            await loadUserData(telegramId);
            // Ждем немного для завершения загрузки
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Проверяем еще раз после перезагрузки
            if (!userData?.referral_code) {
                console.error('Referral code still missing after reload! userData:', JSON.stringify(userData));
                console.error('Backend should generate referral_code automatically. Check API response.');
                return null;
            }
        } else {
            console.error('Telegram ID not available for reload');
            return null;
        }
    }
    
    // Получаем реферальный код пользователя
    const referralCode = userData.referral_code;
    console.log('Referral code:', referralCode);
    
    // Формируем реферальную ссылку на Web App с параметром ref для регистрации
    const webappUrl = window.location.origin || 'https://facy-app.vercel.app';
    referralLink = `${webappUrl}?ref=${referralCode}`;
    console.log('Generated referral link:', referralLink);
    
    return referralLink;
}

// Генерация QR-кода через API
async function generateQRCode() {
    console.log('generateQRCode called');
    
    const referralQRCode = document.getElementById('referralQRCode');
    const referralQRContainer = document.getElementById('referralQRContainer');
    
    if (!referralQRCode || !referralQRContainer) {
        console.error('QR code elements not found!');
        showNotification('Ошибка: элементы QR-кода не найдены', 'error');
        return;
    }
    
    // Получаем telegram_id из Telegram Web App
    const telegramUser = tg?.initDataUnsafe?.user;
    const telegramId = telegramUser?.id;
    
    if (!telegramId) {
        console.error('Telegram ID not found');
        showNotification('Не удалось получить данные пользователя из Telegram', 'error');
        return;
    }
    
    console.log('Generating QR code for telegram_id:', telegramId);
    
    // Если userData еще не загружен, загружаем его
    if (!userData) {
        console.log('User data not loaded, loading...');
        await loadUserData(telegramId);
    }
    
    // Показываем лоадер
    referralQRCode.innerHTML = '<div style="color: var(--text-primary); padding: 2rem;">Загрузка QR-кода...</div>';
    referralQRContainer.style.display = 'flex';
    
    try {
        // Определяем API URL (может быть пустой строкой для относительных путей)
        const qrApiUrl = API_BASE_URL 
            ? `${API_BASE_URL}/api/referral/qr?telegram_id=${telegramId}`
            : `/api/referral/qr?telegram_id=${telegramId}`;
        
        console.log('Fetching QR code from:', qrApiUrl);
        
        const response = await fetch(qrApiUrl);
        
        console.log('QR code response status:', response.status);
        
        if (response.ok) {
            // Получаем изображение как blob
            const blob = await response.blob();
            const imageUrl = URL.createObjectURL(blob);
            
            console.log('QR code image loaded successfully');
            
            // Отображаем QR-код
            referralQRCode.innerHTML = `<img src="${imageUrl}" alt="QR Code" style="max-width: 100%; height: auto; border-radius: 8px;">`;
            showNotification('QR-код успешно загружен!', 'success');
        } else {
            const errorText = await response.text();
            console.error('QR code API error:', errorText);
            let errorMessage = 'Ошибка генерации QR-кода';
            
            try {
                const error = JSON.parse(errorText);
                errorMessage = error.detail || error.message || errorMessage;
            } catch (e) {
                // Если не JSON, используем текст ошибки
                errorMessage = errorText || errorMessage;
            }
            
            throw new Error(errorMessage);
        }
    } catch (error) {
        console.error('Error generating QR code:', error);
        referralQRCode.innerHTML = `<p style="color: var(--text-primary); padding: 1rem; text-align: center;">Ошибка загрузки QR-кода. Попробуйте позже.</p>`;
        showNotification(`Не удалось загрузить QR-код: ${error.message}`, 'error');
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
        
        // Проверяем, что обработчики привязаны (на случай если элементы были пересозданы)
        const generateBtn = document.getElementById('generateBtn');
        const generateVideoBtn = document.getElementById('generateVideoBtn');
        const swapFaceBtn = document.getElementById('swapFaceBtn');
        
        // Если кнопки найдены, но обработчики не привязаны, привязываем их
        if (generateBtn && !generateBtn.hasAttribute('data-handler-attached')) {
            console.log('Re-attaching handler to generateBtn');
            generateBtn.addEventListener('click', (e) => {
                console.log('Generate button clicked!');
                e.preventDefault();
                e.stopPropagation();
                handleGenerateImage();
            });
            generateBtn.setAttribute('data-handler-attached', 'true');
        }
        
        if (generateVideoBtn && !generateVideoBtn.hasAttribute('data-handler-attached')) {
            console.log('Re-attaching handler to generateVideoBtn');
            generateVideoBtn.addEventListener('click', (e) => {
                console.log('Generate video button clicked!');
                e.preventDefault();
                e.stopPropagation();
                handleGenerateVideo();
            });
            generateVideoBtn.setAttribute('data-handler-attached', 'true');
        }
        
        if (swapFaceBtn && !swapFaceBtn.hasAttribute('data-handler-attached')) {
            console.log('Re-attaching handler to swapFaceBtn');
            swapFaceBtn.addEventListener('click', (e) => {
                console.log('Swap face button clicked!');
                e.preventDefault();
                e.stopPropagation();
                handleSwapFace();
            });
            swapFaceBtn.setAttribute('data-handler-attached', 'true');
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

// Проверка загрузки демо-изображений
function checkDemoImages() {
    const beforeImg = document.getElementById('before1');
    const afterImg = document.getElementById('after1');
    
    if (beforeImg) {
        beforeImg.addEventListener('error', function() {
            console.error('Failed to load demo-before-1.png');
            // Показываем placeholder
            this.style.background = 'var(--bg-darker)';
        });
        beforeImg.addEventListener('load', function() {
            console.log('✅ Demo before image loaded');
        });
    }
    
    if (afterImg) {
        afterImg.addEventListener('error', function() {
            console.error('Failed to load demo-after-1.png');
            // Показываем placeholder
            this.style.background = 'var(--bg-darker)';
        });
        afterImg.addEventListener('load', function() {
            console.log('✅ Demo after image loaded');
        });
    }
}

// Инициализация слайдеров "До - После" (только для первого элемента)
function initDemoToggles() {
    // Инициализируем только первый слайдер (demo1)
    const wrapper = document.querySelector('#demo1 .before-after-wrapper');
    
    if (!wrapper) return;
    
    const afterImage = wrapper.querySelector('.after-image');
    const sliderHandle = wrapper.querySelector('.slider-handle');
    
    if (!afterImage || !sliderHandle) return;
    
    // Инициализируем только первый слайдер
    (function() {
        const sliderId = 1;
        
        let isDragging = false;
        let startX = 0;
        let currentX = 0;
        
        // Функция обновления позиции слайдера
        const updateSlider = (clientX) => {
            const rect = wrapper.getBoundingClientRect();
            const x = clientX - rect.left;
            const percent = Math.max(0, Math.min(100, (x / rect.width) * 100));
            
            // Обновляем clip-path для изображения "После"
            afterImage.style.clipPath = `inset(0 ${100 - percent}% 0 0)`;
            
            // Обновляем позицию слайдера
            sliderHandle.style.left = `${percent}%`;
        };
        
        // Обработчик начала перетаскивания
        const startDrag = (e) => {
            isDragging = true;
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            startX = clientX;
            currentX = clientX;
            wrapper.style.cursor = 'grabbing';
            e.preventDefault();
        };
        
        // Обработчик перетаскивания
        const drag = (e) => {
            if (!isDragging) return;
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            currentX = clientX;
            updateSlider(currentX);
            e.preventDefault();
        };
        
        // Обработчик окончания перетаскивания
        const stopDrag = () => {
            if (isDragging) {
                isDragging = false;
                wrapper.style.cursor = 'grab';
            }
        };
        
        // Клик по области слайдера
        wrapper.addEventListener('click', (e) => {
            if (!isDragging) {
                const clientX = e.touches ? e.touches[0].clientX : e.clientX;
                updateSlider(clientX);
            }
        });
        
        // События мыши
        wrapper.addEventListener('mousedown', startDrag);
        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', stopDrag);
        
        // События касания (для мобильных устройств)
        wrapper.addEventListener('touchstart', startDrag, { passive: false });
        wrapper.addEventListener('touchmove', drag, { passive: false });
        wrapper.addEventListener('touchend', stopDrag);
        
        // Инициализация начальной позиции (50%) после загрузки изображений
        const initSliderPosition = () => {
            const rect = wrapper.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            updateSlider(centerX);
        };
        
        // Ждем загрузки изображений
        const afterImg = wrapper.querySelector('.after-image');
        if (afterImg.complete) {
            initSliderPosition();
        } else {
            afterImg.addEventListener('load', initSliderPosition);
        }
        
        console.log(`Slider ${sliderId} initialized`);
    })();
}

// Инициализация кнопок
function initButtons() {
    console.log('Initializing buttons...');
    
    // Привязываем обработчики кнопок генерации сразу при загрузке страницы
    const generateBtn = document.getElementById('generateBtn');
    if (generateBtn) {
        console.log('Found generateBtn, attaching handler');
        generateBtn.addEventListener('click', (e) => {
            console.log('Generate button clicked!');
            e.preventDefault();
            e.stopPropagation();
            handleGenerateImage();
        });
        generateBtn.setAttribute('data-handler-attached', 'true');
    } else {
        console.warn('generateBtn not found!');
    }
    
    const generateVideoBtn = document.getElementById('generateVideoBtn');
    if (generateVideoBtn) {
        console.log('Found generateVideoBtn, attaching handler');
        generateVideoBtn.addEventListener('click', (e) => {
            console.log('Generate video button clicked!');
            e.preventDefault();
            e.stopPropagation();
            handleGenerateVideo();
        });
        generateVideoBtn.setAttribute('data-handler-attached', 'true');
    } else {
        console.warn('generateVideoBtn not found!');
    }
    
    const swapFaceBtn = document.getElementById('swapFaceBtn');
    if (swapFaceBtn) {
        console.log('Found swapFaceBtn, attaching handler');
        swapFaceBtn.addEventListener('click', (e) => {
            console.log('Swap face button clicked!');
            e.preventDefault();
            e.stopPropagation();
            handleSwapFace();
        });
        swapFaceBtn.setAttribute('data-handler-attached', 'true');
    } else {
        console.warn('swapFaceBtn not found!');
    }
    
    // Базовый тариф теперь всегда активен - кнопка заменена на надпись "Активен"
    
    // Кнопка копирования реферальной ссылки
    const copyReferralLinkBtn = document.getElementById('copyReferralLinkBtn');
    if (copyReferralLinkBtn) {
        console.log('Found copyReferralLinkBtn, attaching handler');
        copyReferralLinkBtn.setAttribute('data-handler-attached', 'true');
        copyReferralLinkBtn.addEventListener('click', async (e) => {
            console.log('Copy referral link button clicked!');
            e.preventDefault();
            e.stopPropagation();
            
            // Если userData еще не загружен, загружаем его
            const telegramUser = tg?.initDataUnsafe?.user;
            const telegramId = telegramUser?.id;
            
            if (!telegramId) {
                showNotification('Не удалось получить данные пользователя из Telegram', 'error');
                return;
            }
            
            // Всегда загружаем актуальные данные пользователя перед генерацией ссылки
            console.log('Loading user data before generating referral link...');
            await loadUserData(telegramId);
            
            // Ждем немного, чтобы убедиться, что данные загружены
            if (!userData) {
                console.warn('User data still not loaded, waiting...');
                await new Promise(resolve => setTimeout(resolve, 500));
            }
            
            // Генерируем ссылку если еще не сгенерирована
            if (!referralLink) {
                const link = await generateReferralLink();
                console.log('Generated referral link:', link);
            }
            
            // Если ссылка все еще не сгенерирована, пробуем еще раз
            if (!referralLink && userData) {
                console.warn('Referral link not generated, retrying...');
                await generateReferralLink();
            }
            
            if (!referralLink) {
                console.error('Failed to generate referral link. userData:', userData);
                showNotification('Не удалось сгенерировать реферальную ссылку. Попробуйте позже или обратитесь в поддержку.', 'error');
                return;
            }
            
            console.log('Copying referral link to clipboard:', referralLink);
            
            // Копируем ссылку в буфер обмена
            try {
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    await navigator.clipboard.writeText(referralLink);
                    console.log('Link copied to clipboard successfully');
                    showNotification('Ссылка приглашения скопирована!', 'success');
                } else {
                    // Fallback для старых браузеров
                    const tempInput = document.createElement('input');
                    tempInput.value = referralLink;
                    tempInput.style.position = 'fixed';
                    tempInput.style.opacity = '0';
                    tempInput.style.left = '-9999px';
                    document.body.appendChild(tempInput);
                    tempInput.select();
                    tempInput.setSelectionRange(0, 99999); // Для мобильных устройств
                    document.execCommand('copy');
                    document.body.removeChild(tempInput);
                    console.log('Link copied using fallback method');
                    showNotification('Ссылка приглашения скопирована!', 'success');
                }
            } catch (err) {
                console.error('Error copying to clipboard:', err);
                // Показываем ссылку пользователю если копирование не удалось
                showNotification(`Реферальная ссылка: ${referralLink}`, 'info');
            }
        });
    } else {
        console.warn('copyReferralLinkBtn not found!');
    }
    
    // Кнопка показа QR-кода
    const showQRBtn = document.getElementById('showQRBtn');
    if (showQRBtn) {
        console.log('Found showQRBtn, attaching handler');
        showQRBtn.setAttribute('data-handler-attached', 'true');
        showQRBtn.addEventListener('click', (e) => {
            console.log('Show QR code button clicked!');
            e.preventDefault();
            e.stopPropagation();
            generateQRCode();
        });
    } else {
        console.warn('showQRBtn not found!');
    }
    
    // Кнопка оплаты стандартного тарифа ($20)
    const activateStandardBtn = document.getElementById('activateStandardBtn');
    if (activateStandardBtn) {
        console.log('Found activateStandardBtn, attaching handler');
        console.log('window.STANDARD_PLAN_PAYMENT_URL:', window.STANDARD_PLAN_PAYMENT_URL);
        activateStandardBtn.addEventListener('click', async (e) => {
            console.log('Activate standard plan button clicked!');
            e.preventDefault();
            e.stopPropagation();
            
            // Получаем ссылку на оплату из переменной окружения или используем дефолтную
            const paymentUrl = window.STANDARD_PLAN_PAYMENT_URL || 'https://web.tribute.tg/p/n1Q';
            console.log('Payment URL:', paymentUrl);
            
            if (!paymentUrl || paymentUrl === '') {
                console.error('Payment URL is empty!');
                showNotification('Ошибка: ссылка на оплату не настроена. Обратитесь в поддержку.', 'error');
                return;
            }
            
            try {
                if (tg?.openLink) {
                    console.log('Opening payment link via Telegram:', paymentUrl);
                    tg.openLink(paymentUrl);
                } else {
                    console.log('Opening payment link in new window:', paymentUrl);
                    window.open(paymentUrl, '_blank');
                }
            } catch (error) {
                console.error('Error opening payment link:', error);
                showNotification(`Ошибка при открытии ссылки оплаты: ${error.message}`, 'error');
            }
        });
    } else {
        console.warn('activateStandardBtn not found!');
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
    console.log('handleSwapFace called');
    console.log('API_BASE_URL:', API_BASE_URL);
    
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
    
    // Определяем API URL (может быть пустой строкой для относительных путей)
    const apiUrl = API_BASE_URL ? `${API_BASE_URL}/api/deepfake/swap` : '/api/deepfake/swap';
    console.log('Face Swap API URL:', apiUrl);
    console.log('API_BASE_URL:', API_BASE_URL);
    
    showLoader('Создаем Face Swap...');
    
    try {
        const formData = new FormData();
        formData.append('telegram_id', telegramId);
        formData.append('source_image', sourceImageFile);
        formData.append('target_video', targetVideoFile);
        
        const response = await fetch(apiUrl, {
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
    console.log('API_BASE_URL:', API_BASE_URL);
    
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
    
    // Определяем API URL (может быть пустой строкой для относительных путей)
    const apiUrl = API_BASE_URL ? `${API_BASE_URL}/api/generate/image` : '/api/generate/image';
    console.log('Starting generation with telegram_id:', telegramId, 'prompt:', prompt);
    console.log('Sending request to:', apiUrl);
    console.log('API_BASE_URL:', API_BASE_URL);
    
    showLoader('Генерируем изображение...');
    
    try {
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
    console.log('handleGenerateVideo called');
    console.log('API_BASE_URL:', API_BASE_URL);
    
    const videoPromptInput = document.getElementById('videoPromptInput');
    const videoDurationSelect = document.getElementById('videoDuration');
    
    if (!videoPromptInput) {
        console.error('videoPromptInput not found!');
        return;
    }
    
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
    
    // Определяем API URL (может быть пустой строкой для относительных путей)
    const apiUrl = API_BASE_URL ? `${API_BASE_URL}/api/generate/video` : '/api/generate/video';
    console.log('Video generation API URL:', apiUrl);
    console.log('API_BASE_URL:', API_BASE_URL);
    
    showLoader('Генерируем видео... Это может занять несколько минут.');
    
    try {
        const response = await fetch(apiUrl, {
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
            const taskApiUrl = API_BASE_URL ? `${API_BASE_URL}/api/video/task/${taskId}` : `/api/video/task/${taskId}`;
            const response = await fetch(taskApiUrl);
            
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
    console.log(`Notification [${type}]:`, message);
    
    try {
        if (tg?.showAlert) {
            tg.showAlert(message);
            return;
        }
        
        if (tg?.showPopup) {
            tg.showPopup({
                title: type === 'error' ? 'Ошибка' : type === 'success' ? 'Успех' : 'Информация',
                message: message,
                buttons: [{ type: 'ok' }]
            });
            return;
        }
        
        // Fallback для обычных браузеров
        alert(message);
    } catch (error) {
        console.error('Error showing notification:', error);
        // Последний fallback
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

// Инициализация модального окна авторизации по email
function initEmailAuth() {
    const emailAuthModal = document.getElementById('emailAuthModal');
    const emailAuthModalClose = document.getElementById('emailAuthModalClose');
    const sendCodeBtn = document.getElementById('sendCodeBtn');
    const verifyCodeBtn = document.getElementById('verifyCodeBtn');
    const resendCodeBtn = document.getElementById('resendCodeBtn');
    const emailInput = document.getElementById('emailInput');
    const codeInput = document.getElementById('codeInput');
    
    if (!emailAuthModal) return;
    
    // Закрытие модального окна
    if (emailAuthModalClose) {
        emailAuthModalClose.addEventListener('click', () => {
            hideEmailAuthModal();
        });
    }
    
    // Отправка кода
    if (sendCodeBtn) {
        sendCodeBtn.addEventListener('click', async () => {
            const email = emailInput?.value?.trim();
            if (!email) {
                showNotification('Введите email', 'error');
                return;
            }
            
            const telegramUser = tg?.initDataUnsafe?.user;
            const telegramId = telegramUser?.id;
            
            if (!telegramId) {
                showNotification('Не удалось получить данные пользователя из Telegram', 'error');
                return;
            }
            
            sendCodeBtn.disabled = true;
            sendCodeBtn.innerHTML = '<span class="btn-text">Отправка...</span>';
            
            try {
                const apiUrl = API_BASE_URL 
                    ? `${API_BASE_URL}/api/auth/send-verification-code`
                    : `/api/auth/send-verification-code`;
                
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        telegram_id: telegramId,
                        email: email
                    })
                });
                
                const result = await response.json();
                
                if (response.ok && result.success) {
                    showNotification(result.message || 'Код отправлен на ваш email', 'success');
                    // Переходим ко второму шагу
                    showEmailAuthStep2(email);
                } else {
                    showNotification(result.detail || result.message || 'Ошибка отправки кода', 'error');
                }
            } catch (error) {
                console.error('Error sending verification code:', error);
                showNotification('Ошибка отправки кода. Попробуйте позже.', 'error');
            } finally {
                sendCodeBtn.disabled = false;
                sendCodeBtn.innerHTML = '<span class="btn-text">Отправить код</span><span class="btn-icon">📧</span>';
            }
        });
    }
    
    // Проверка кода
    if (verifyCodeBtn) {
        verifyCodeBtn.addEventListener('click', async () => {
            const code = codeInput?.value?.trim();
            if (!code || code.length !== 6) {
                showNotification('Введите 6-значный код', 'error');
                return;
            }
            
            const telegramUser = tg?.initDataUnsafe?.user;
            const telegramId = telegramUser?.id;
            
            if (!telegramId) {
                showNotification('Не удалось получить данные пользователя из Telegram', 'error');
                return;
            }
            
            verifyCodeBtn.disabled = true;
            verifyCodeBtn.innerHTML = '<span class="btn-text">Проверка...</span>';
            
            try {
                const apiUrl = API_BASE_URL 
                    ? `${API_BASE_URL}/api/auth/verify-email-code`
                    : `/api/auth/verify-email-code`;
                
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        telegram_id: telegramId,
                        code: code
                    })
                });
                
                const result = await response.json();
                
                if (response.ok && result.success) {
                    showNotification(result.message || 'Email успешно подтвержден!', 'success');
                    // Перезагружаем данные пользователя
                    await loadUserData(telegramId);
                    // Закрываем модальное окно
                    hideEmailAuthModal();
                } else {
                    showNotification(result.detail || result.message || 'Неверный код', 'error');
                }
            } catch (error) {
                console.error('Error verifying code:', error);
                showNotification('Ошибка проверки кода. Попробуйте позже.', 'error');
            } finally {
                verifyCodeBtn.disabled = false;
                verifyCodeBtn.innerHTML = '<span class="btn-text">Подтвердить</span><span class="btn-icon">✓</span>';
            }
        });
    }
    
    // Повторная отправка кода
    if (resendCodeBtn) {
        resendCodeBtn.addEventListener('click', async () => {
            const email = emailInput?.value?.trim();
            if (!email) {
                showNotification('Введите email', 'error');
                return;
            }
            
            // Возвращаемся к первому шагу и отправляем код заново
            showEmailAuthStep1();
            sendCodeBtn.click();
        });
    }
    
    // Ввод кода - только цифры
    if (codeInput) {
        codeInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '');
        });
    }
}

// Показать модальное окно авторизации по email
function showEmailAuthModal() {
    const emailAuthModal = document.getElementById('emailAuthModal');
    if (emailAuthModal) {
        emailAuthModal.classList.add('show');
        showEmailAuthStep1();
    }
}

// Скрыть модальное окно авторизации по email
function hideEmailAuthModal() {
    const emailAuthModal = document.getElementById('emailAuthModal');
    if (emailAuthModal) {
        emailAuthModal.classList.remove('show');
    }
}

// Показать шаг 1 (ввод email)
function showEmailAuthStep1() {
    const step1 = document.getElementById('emailAuthStep1');
    const step2 = document.getElementById('emailAuthStep2');
    if (step1) step1.style.display = 'flex';
    if (step2) step2.style.display = 'none';
}

// Показать шаг 2 (ввод кода)
function showEmailAuthStep2(email) {
    const step1 = document.getElementById('emailAuthStep1');
    const step2 = document.getElementById('emailAuthStep2');
    const emailDisplay = document.getElementById('emailDisplay');
    
    if (step1) step1.style.display = 'none';
    if (step2) step2.style.display = 'flex';
    if (emailDisplay) emailDisplay.textContent = email;
    
    // Фокус на поле ввода кода
    const codeInput = document.getElementById('codeInput');
    if (codeInput) {
        setTimeout(() => codeInput.focus(), 100);
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
