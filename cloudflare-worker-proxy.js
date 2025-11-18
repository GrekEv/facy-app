// Cloudflare Worker для прокси OpenAI API
// Скопируйте этот код в Cloudflare Workers → Create Worker
// 
// Инструкция:
// 1. Зайдите на https://workers.cloudflare.com
// 2. Нажмите "Create Worker"
// 3. Вставьте этот код
// 4. Нажмите "Deploy"
// 5. Скопируйте URL Worker'а (например: https://openai-proxy.your-username.workers.dev)
// 6. Добавьте в .env: OPENAI_PROXY=https://openai-proxy.your-username.workers.dev

export default {
  async fetch(request) {
    // Разрешаем CORS для всех запросов
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        },
      });
    }

    const url = new URL(request.url);
    
    // Поддерживаем все эндпоинты OpenAI API
    const openaiPath = url.pathname;
    const openaiUrl = `https://api.openai.com${openaiPath}${url.search}`;
    
    // Получаем оригинальный запрос
    let body = null;
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      try {
        body = await request.text();
      } catch (e) {
        // Если тело пустое, игнорируем ошибку
      }
    }
    
    // Копируем заголовки, но удаляем те, которые могут вызвать проблемы
    const headers = new Headers(request.headers);
    headers.delete('host');
    headers.delete('cf-connecting-ip');
    headers.delete('cf-ray');
    headers.delete('cf-visitor');
    
    // Устанавливаем правильный Host для OpenAI
    headers.set('Host', 'api.openai.com');
    
    try {
      // Перенаправляем запрос к OpenAI API
      const openaiResponse = await fetch(openaiUrl, {
        method: request.method,
        headers: headers,
        body: body
      });

      // Получаем ответ
      const responseData = await openaiResponse.text();
      
      // Возвращаем ответ с правильными заголовками
      return new Response(responseData, {
        status: openaiResponse.status,
        statusText: openaiResponse.statusText,
        headers: {
          'Content-Type': openaiResponse.headers.get('Content-Type') || 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
      });
    } catch (error) {
      // Обработка ошибок
      return new Response(JSON.stringify({
        error: {
          message: `Proxy error: ${error.message}`,
          type: 'proxy_error'
        }
      }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
  }
};

