/**
 * Cloudflare Worker proxy for forwarding all requests
 * to http://razr.freedynamicdns.org:5001/
 */

const TARGET_URL = 'http://razr.freedynamicdns.org:5001';

export default {
    async fetch(request, env, ctx) {
        try {
            // Получаем URL запроса
            const url = new URL(request.url);

            // Убираем /newapi в начале пути, если он есть
            let pathname = url.pathname;
            if (pathname.startsWith('/newapi')) {
                pathname = pathname.substring(7); // убираем '/newapi'
            }
            if (pathname === '') {
                pathname = '/'; // если путь пустой, делаем корневой
            }

            // Создаем новый URL с целевым хостом, но сохраняем путь и параметры
            const targetUrl = new URL(pathname + url.search, TARGET_URL);            // Логируем запрос
            console.info({
                message: 'Proxying request',
                method: request.method,
                path: url.pathname,
                target: targetUrl.toString()
            });

            // Создаем новый запрос с теми же заголовками и телом
            const modifiedRequest = new Request(targetUrl, {
                method: request.method,
                headers: request.headers,
                body: request.body,
                redirect: 'follow'
            });

            // Отправляем запрос к целевому серверу
            const response = await fetch(modifiedRequest);

            // Возвращаем ответ от целевого сервера
            return response;

        } catch (error) {
            console.error('Proxy error:', error);
            return new Response('Proxy error occurred: ' + error.message, {
                status: 500,
                headers: { 'Content-Type': 'text/plain' }
            });
        }
    }
};
