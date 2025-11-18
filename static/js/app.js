const tg = window.Telegram?.WebApp;
if (tg) {
    tg.expand();
    tg.setHeaderColor('#0a0a0f');
    tg.setBackgroundColor('#0a0a0f');
}
const getApiBaseUrl = () => {
    if (window.API_BASE_URL && window.API_BASE_URL !== '{{API_BASE_URL}}') {
        const url = window.API_BASE_URL.trim();
        if (url && !url.includes('/payment') && !url.includes('heleket')) {
            return url;
        }
    }
    if (window.API_BASE_URL === '{{API_BASE_URL}}') {
        console.warn('API_BASE_URL placeholder not replaced by server, using relative paths');
    }
    const currentHost = window.location.hostname;
    if (currentHost === 'onlyface.art' || currentHost.includes('onlyface')) {
        return '';
    }
    if (currentHost.includes('vercel.app')) {
        return '';
    }
    return 'https:
};
const API_BASE_URL = getApiBaseUrl();
console.log('API_BASE_URL determined:', API_BASE_URL);
console.log('window.API_BASE_URL:', window.API_BASE_URL);
console.log('window.location.hostname:', window.location.hostname);
let userData = null;
let sourceImageFile = null;
let targetVideoFile = null;
let statsData = null;
document.addEventListener('DOMContentLoaded', async () => {
    console.log('OnlyFace App initialized');
    console.log('Window location:', window.location.href);
    console.log('API_BASE_URL:', API_BASE_URL);
    initHeaderButtons();
    initCreateModal();
    initFileUploads();
    initDemoToggles();
    initButtons();
    initSmoothScroll();
    initEmailAuth();
    checkDemoImages();
    const referralSection = document.querySelector('.referral-section');
    if (referralSection) {
        console.log('Setting up event delegation for referral section');
        referralSection.addEventListener('click', async (e) => {
            const target = e.target.closest('button');
            if (!target) return;
            if (target.id === 'copyReferralLinkBtn') {
                if (!target.hasAttribute('data-handler-attached')) {
                    console.log('Copy referral link clicked via delegation (no handler attached)');
                    e.preventDefault();
                    e.stopPropagation();
                    const telegramUser = tg?.initDataUnsafe?.user;
                    const telegramId = telegramUser?.id;
                    if (!userData && telegramId) {
                        await loadUserData(telegramId);
                    }
                    if (!referralLink) {
                        await generateReferralLink();
                    }
                    if (!referralLink) {
                        showNotification('Не удалось сгенерировать реферальную ссылку. Попробуйте позже.', 'error');
                        return;
                    }
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
    const telegramUser = tg?.initDataUnsafe?.user;
    if (telegramUser && telegramUser.id) {
        loadUserData(telegramUser.id).catch(err => {
            console.error('Error loading user data:', err);
        });
    }
    loadStats().catch(err => {
        console.error('Error loading stats:', err);
    });
});
async function loadUserData(telegramId) {
    try {
        const apiUrl = API_BASE_URL ? `${API_BASE_URL}/api/user/${telegramId}` : `/api/user/${telegramId}`;
        console.log('Loading user data from:', apiUrl);
        const response = await fetch(apiUrl);
        if (response.ok) {
            userData = await response.json();
            console.log('User data loaded:', userData);
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
            await generateReferralLink();
            if (userData && !userData.email_verified) {
                setTimeout(() => {
                    showEmailAuthModal();
                }, 1000);
            }
        } else {
            const errorText = await response.text();
            console.error('Failed to load user data:', response.status, errorText);
            if (response.status === 503) {
                try {
                    const errorData = JSON.parse(errorText);
                    if (errorData.detail && errorData.detail.includes('база данных')) {
                        console.error('Database not configured!');
                        showNotification('База данных не настроена. Обратитесь к администратору.', 'error');
                    }
                } catch (e) {
                }
            }
        }
    } catch (error) {
        console.error('Error loading user data:', error);
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            showNotification('Не удалось подключиться к серверу. Проверьте подключение к интернету.', 'error');
        }
    }
}
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
function updatePrice() {
    const priceElement = document.getElementById('priceAmount');
    if (priceElement && userData) {
        priceElement.textContent = userData.is_premium ? 'XXX' : 'XXX';
    }
}
let referralLink = null;
async function generateReferralLink() {
    console.log('generateReferralLink called, userData:', userData);
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
    if (!userData?.referral_code) {
        console.warn('Referral code not available, reloading user data...');
        const telegramUser = tg?.initDataUnsafe?.user;
        const telegramId = telegramUser?.id;
        if (telegramId) {
            await loadUserData(telegramId);
            await new Promise(resolve => setTimeout(resolve, 500));
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
    const referralCode = userData.referral_code;
    console.log('Referral code from userData:', referralCode);
    if (!referralCode) {
        console.error('Referral code is still missing after all attempts!');
        console.error('Full userData object:', JSON.stringify(userData, null, 2));
        return null;
    }
    const webappUrl = window.WEBAPP_URL || window.location.origin || 'https:
    referralLink = `${webappUrl}?ref=${referralCode}`;
    console.log('Generated referral link:', referralLink);
    console.log('WEBAPP_URL from env:', window.WEBAPP_URL);
    return referralLink;
}
async function generateQRCode() {
    console.log('generateQRCode called');
    const referralQRCode = document.getElementById('referralQRCode');
    const referralQRContainer = document.getElementById('referralQRContainer');
    if (!referralQRCode || !referralQRContainer) {
        console.error('QR code elements not found!');
        showNotification('Ошибка: элементы QR-кода не найдены', 'error');
        return;
    }
    const telegramUser = tg?.initDataUnsafe?.user;
    const telegramId = telegramUser?.id;
    if (!telegramId) {
        console.error('Telegram ID not found');
        showNotification('Не удалось получить данные пользователя из Telegram', 'error');
        return;
    }
    console.log('Generating QR code for telegram_id:', telegramId);
    if (!userData) {
        console.log('User data not loaded, loading...');
        await loadUserData(telegramId);
    }
    referralQRCode.innerHTML = '<div style="color: var(--text-primary); padding: 2rem;">Загрузка QR-кода...</div>';
    referralQRContainer.style.display = 'flex';
    try {
        const qrApiUrl = API_BASE_URL 
            ? `${API_BASE_URL}/api/referral/qr?telegram_id=${telegramId}`
            : `/api/referral/qr?telegram_id=${telegramId}`;
        console.log('Fetching QR code from:', qrApiUrl);
        const response = await fetch(qrApiUrl);
        console.log('QR code response status:', response.status);
        if (response.ok) {
            const blob = await response.blob();
            const imageUrl = URL.createObjectURL(blob);
            console.log('QR code image loaded successfully');
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
function initHeaderButtons() {
}
function initCreateModal() {
    const createModal = document.getElementById('createModal');
    const modalClose = document.getElementById('modalClose');
    const startFreeBtn = document.getElementById('startFreeBtn');
    const startBtn = document.getElementById('startBtn');
    const createTabs = document.querySelectorAll('.create-tab');
    if (startFreeBtn) {
        startFreeBtn.addEventListener('click', openCreateModal);
    }
    if (startBtn) {
        startBtn.addEventListener('click', openCreateModal);
    }
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
    createTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;
            createTabs.forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.create-section').forEach(s => s.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(`${targetTab}-section`).classList.add('active');
        });
    });
}
function openCreateModal() {
    const modal = document.getElementById('createModal');
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
        const generateBtn = document.getElementById('generateBtn');
        const generateVideoBtn = document.getElementById('generateVideoBtn');
        const swapFaceBtn = document.getElementById('swapFaceBtn');
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
function closeCreateModal() {
    const modal = document.getElementById('createModal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
}
function initFileUploads() {
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
function displayPreview(file, previewElement, type) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const element = type === 'image' 
            ? `<img src="${e.target.result}" alt="Preview">`
            : `<video src="${e.target.result}" controls></video>`;
        previewElement.innerHTML = element;
        previewElement.classList.add('show');
        const label = previewElement.previousElementSibling;
        if (label && label.classList.contains('upload-label')) {
            label.style.display = 'none';
        }
    };
    reader.readAsDataURL(file);
}
function checkDemoImages() {
    const beforeImg = document.getElementById('before1');
    const afterImg = document.getElementById('after1');
    if (beforeImg) {
        beforeImg.addEventListener('error', function() {
            console.error('Failed to load demo-before-1.png');
            this.style.background = 'var(--bg-darker)';
        });
        beforeImg.addEventListener('load', function() {
            console.log('Demo before image loaded');
        });
    }
    if (afterImg) {
        afterImg.addEventListener('error', function() {
            console.error('Failed to load demo-after-1.png');
            this.style.background = 'var(--bg-darker)';
        });
        afterImg.addEventListener('load', function() {
            console.log('Demo after image loaded');
        });
    }
}
function initDemoToggles() {
    const wrapper = document.querySelector('#demo1 .before-after-wrapper');
    if (!wrapper) return;
    const afterImage = wrapper.querySelector('.after-image');
    const sliderHandle = wrapper.querySelector('.slider-handle');
    if (!afterImage || !sliderHandle) return;
    (function() {
        const sliderId = 1;
        let isDragging = false;
        let startX = 0;
        let currentX = 0;
        const updateSlider = (clientX) => {
            const rect = wrapper.getBoundingClientRect();
            const x = clientX - rect.left;
            const percent = Math.max(0, Math.min(100, (x / rect.width) * 100));
            afterImage.style.clipPath = `inset(0 ${100 - percent}% 0 0)`;
            sliderHandle.style.left = `${percent}%`;
        };
        const startDrag = (e) => {
            isDragging = true;
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            startX = clientX;
            currentX = clientX;
            wrapper.style.cursor = 'grabbing';
            e.preventDefault();
        };
        const drag = (e) => {
            if (!isDragging) return;
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            currentX = clientX;
            updateSlider(currentX);
            e.preventDefault();
        };
        const stopDrag = () => {
            if (isDragging) {
                isDragging = false;
                wrapper.style.cursor = 'grab';
            }
        };
        wrapper.addEventListener('click', (e) => {
            if (!isDragging) {
                const clientX = e.touches ? e.touches[0].clientX : e.clientX;
                updateSlider(clientX);
            }
        });
        wrapper.addEventListener('mousedown', startDrag);
        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', stopDrag);
        wrapper.addEventListener('touchstart', startDrag, { passive: false });
        wrapper.addEventListener('touchmove', drag, { passive: false });
        wrapper.addEventListener('touchend', stopDrag);
        const initSliderPosition = () => {
            const rect = wrapper.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            updateSlider(centerX);
        };
        const afterImg = wrapper.querySelector('.after-image');
        if (afterImg.complete) {
            initSliderPosition();
        } else {
            afterImg.addEventListener('load', initSliderPosition);
        }
        console.log(`Slider ${sliderId} initialized`);
    })();
}
function initButtons() {
    console.log('Initializing buttons...');
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
    const copyReferralLinkBtn = document.getElementById('copyReferralLinkBtn');
    if (copyReferralLinkBtn) {
        console.log('Found copyReferralLinkBtn, attaching handler');
        copyReferralLinkBtn.setAttribute('data-handler-attached', 'true');
        copyReferralLinkBtn.addEventListener('click', async (e) => {
            console.log('Copy referral link button clicked!');
            e.preventDefault();
            e.stopPropagation();
            const telegramUser = tg?.initDataUnsafe?.user;
            const telegramId = telegramUser?.id;
            if (!telegramId) {
                showNotification('Не удалось получить данные пользователя из Telegram', 'error');
                return;
            }
            console.log('Loading user data before generating referral link...');
            await loadUserData(telegramId);
            if (!userData) {
                console.warn('User data still not loaded, waiting...');
                await new Promise(resolve => setTimeout(resolve, 500));
            }
            if (!referralLink) {
                const link = await generateReferralLink();
                console.log('Generated referral link:', link);
            }
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
            try {
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    await navigator.clipboard.writeText(referralLink);
                    console.log('Link copied to clipboard successfully');
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
                    console.log('Link copied using fallback method');
                    showNotification('Ссылка приглашения скопирована!', 'success');
                }
            } catch (err) {
                console.error('Error copying to clipboard:', err);
                showNotification(`Реферальная ссылка: ${referralLink}`, 'info');
            }
        });
    } else {
        console.warn('copyReferralLinkBtn not found!');
    }
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
    const activateStandardBtn = document.getElementById('activateStandardBtn');
    if (activateStandardBtn) {
        console.log('Found activateStandardBtn, attaching handler');
        console.log('window.STANDARD_PLAN_PAYMENT_URL:', window.STANDARD_PLAN_PAYMENT_URL);
        activateStandardBtn.addEventListener('click', async (e) => {
            console.log('Activate standard plan button clicked!');
            e.preventDefault();
            e.stopPropagation();
            const paymentUrl = window.STANDARD_PLAN_PAYMENT_URL || 'https:
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
function initSmoothScroll() {
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
    const telegramUser = tg?.initDataUnsafe?.user;
    const telegramId = telegramUser?.id;
    if (!telegramId) {
        showNotification('Не удалось получить данные пользователя из Telegram', 'error');
        return;
    }
    if (!userData) {
        await loadUserData(telegramId);
    }
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
    if (!checkContentSafety(prompt)) {
        showNotification('⛔ Обнаружено недопустимое содержание. Пожалуйста, ознакомьтесь с политикой контента.', 'error');
        return;
    }
    const telegramUser = tg?.initDataUnsafe?.user;
    let telegramId = telegramUser?.id;
    if (!telegramId) {
        telegramId = 123456789;
        console.warn('Telegram ID not found, using test ID:', telegramId);
    }
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
            console.error('Response status:', response.status);
            console.error('Response headers:', response.headers);
            hideLoader();
            if (response.status === 405) {
                showNotification('Метод не разрешен. Проверьте настройки сервера.', 'error');
            } else if (response.status === 500) {
                showNotification('Внутренняя ошибка сервера. Проверьте логи.', 'error');
            } else if (text.includes('<!DOCTYPE')) {
                showNotification('Сервер вернул HTML вместо JSON. Проверьте настройки API.', 'error');
            } else {
                showNotification(`Ошибка сервера (${response.status}): ${text.substring(0, 100)}`, 'error');
            }
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
    if (!checkContentSafety(prompt)) {
        showNotification('⛔ Обнаружено недопустимое содержание. Пожалуйста, ознакомьтесь с политикой контента.', 'error');
        return;
    }
    const telegramUser = tg?.initDataUnsafe?.user;
    const telegramId = telegramUser?.id;
    if (!telegramId) {
        showNotification('Не удалось получить данные пользователя из Telegram', 'error');
        return;
    }
    if (!userData) {
        await loadUserData(telegramId);
    }
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
                if (result.task_id) {
                    showNotification('Генерация видео началась. Проверяем статус...', 'info');
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
async function checkVideoTaskStatus(taskId, generationId) {
    let attempts = 0;
    const maxAttempts = 60;
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
                        setTimeout(checkStatus, 5000);
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
function closeResultModal() {
    const resultModal = document.getElementById('resultModal');
    if (resultModal) {
        resultModal.classList.remove('show');
        document.body.style.overflow = '';
    }
}
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
        alert(message);
    } catch (error) {
        console.error('Error showing notification:', error);
        alert(message);
    }
}
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
function initEmailAuth() {
    const emailAuthModal = document.getElementById('emailAuthModal');
    const emailAuthModalClose = document.getElementById('emailAuthModalClose');
    const sendCodeBtn = document.getElementById('sendCodeBtn');
    const verifyCodeBtn = document.getElementById('verifyCodeBtn');
    const resendCodeBtn = document.getElementById('resendCodeBtn');
    const emailInput = document.getElementById('emailInput');
    const codeInput = document.getElementById('codeInput');
    if (!emailAuthModal) return;
    if (emailAuthModalClose) {
        emailAuthModalClose.addEventListener('click', () => {
            hideEmailAuthModal();
        });
    }
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
                    showEmailAuthStep2(email);
                } else {
                    showNotification(result.detail || result.message || 'Ошибка отправки кода', 'error');
                }
            } catch (error) {
                console.error('Error sending verification code:', error);
                showNotification('Ошибка отправки кода. Попробуйте позже.', 'error');
            } finally {
                sendCodeBtn.disabled = false;
                sendCodeBtn.innerHTML = '<span class="btn-text">Отправить код</span>';
            }
        });
    }
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
                    await loadUserData(telegramId);
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
    if (resendCodeBtn) {
        resendCodeBtn.addEventListener('click', async () => {
            const email = emailInput?.value?.trim();
            if (!email) {
                showNotification('Введите email', 'error');
                return;
            }
            showEmailAuthStep1();
            sendCodeBtn.click();
        });
    }
    if (codeInput) {
        codeInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '');
        });
    }
}
function showEmailAuthModal() {
    const emailAuthModal = document.getElementById('emailAuthModal');
    if (emailAuthModal) {
        emailAuthModal.classList.add('show');
        showEmailAuthStep1();
    }
}
function hideEmailAuthModal() {
    const emailAuthModal = document.getElementById('emailAuthModal');
    if (emailAuthModal) {
        emailAuthModal.classList.remove('show');
    }
}
function showEmailAuthStep1() {
    const step1 = document.getElementById('emailAuthStep1');
    const step2 = document.getElementById('emailAuthStep2');
    if (step1) step1.style.display = 'flex';
    if (step2) step2.style.display = 'none';
}
function showEmailAuthStep2(email) {
    const step1 = document.getElementById('emailAuthStep1');
    const step2 = document.getElementById('emailAuthStep2');
    const emailDisplay = document.getElementById('emailDisplay');
    if (step1) step1.style.display = 'none';
    if (step2) step2.style.display = 'flex';
    if (emailDisplay) emailDisplay.textContent = email;
    const codeInput = document.getElementById('codeInput');
    if (codeInput) {
        setTimeout(() => codeInput.focus(), 100);
    }
}
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
