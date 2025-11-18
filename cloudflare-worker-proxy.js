// Cloudflare Worker дл� п�ок�� OpenAI API
// �коп��уйте �тот код в Cloudflare Workers � Create Worker
// 
// Ин�т�укц��:
// 1. Зайд�те на https://workers.cloudflare.com
// 2. �ажм�те "Create Worker"
// 3. ��тав�те �тот код
// 4. �ажм�те "Deploy"
// 5. �коп��уйте URL Worker'а (нап��ме�: https://openai-proxy.your-username.workers.dev)
// 6. �о�ав�те в .env: OPENAI_PROXY=https://openai-proxy.your-username.workers.dev

export default {
  async fetch(request) {
    // �аз�ешаем CORS дл� в�е� зап�о�ов
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
    
    // �одде�ж�ваем в�е �ндпо�нт� OpenAI API
    const openaiPath = url.pathname;
    const openaiUrl = `https://api.openai.com${openaiPath}${url.search}`;
    
    // �олучаем о����нал�н�й зап�о�
    let body = null;
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      try {
        body = await request.text();
      } catch (e) {
        // Е�л� тело пу�тое, ��но���уем ош��ку
      }
    }
    
    // �оп��уем за�оловк�, но удал�ем те, кото��е мо�ут в�зват� п�о�лем�
    const headers = new Headers(request.headers);
    headers.delete('host');
    headers.delete('cf-connecting-ip');
    headers.delete('cf-ray');
    headers.delete('cf-visitor');
    
    // У�танавл�ваем п�ав�л�н�й Host дл� OpenAI
    headers.set('Host', 'api.openai.com');
    
    try {
      // �е�енап�авл�ем зап�о� к OpenAI API
      const openaiResponse = await fetch(openaiUrl, {
        method: request.method,
        headers: headers,
        body: body
      });

      // �олучаем ответ
      const responseData = await openaiResponse.text();
      
      // �озв�а�аем ответ � п�ав�л�н�м� за�оловкам�
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
      // О��а�отка ош��ок
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

