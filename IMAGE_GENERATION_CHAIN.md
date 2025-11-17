```javascript
async function handleGenerateImage() {
    const promptInput = document.getElementById('promptInput');
    const prompt = promptInput.value.trim();
    
    if (!prompt) {
        showNotification('Введите описание сцены', 'error');
        return;
    }
    
    if (!checkContentSafety(prompt)) {
        showNotification('Обнаружено недопустимое содержание', 'error');
        return;
    }
    
    const telegramUser = tg?.initDataUnsafe?.user;
    let telegramId = telegramUser?.id || 123456789;
    
    const apiUrl = `${API_BASE_URL}/api/generate/image`;
    const requestBody = {
        telegram_id: telegramId,
        prompt: prompt,
        model: 'flux',
        style: 'realistic'
    };
    
    const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
    });
    
    const result = await response.json();
    
    if (result.success) {
        showResult(result.image_url, 'image');
        showNotification('Изображение успешно сгенерировано!', 'success');
    } else {
        showNotification(result.message || 'Ошибка при генерации', 'error');
    }
}
```

```python
@app.post("/api/generate/image", response_model=GenerateImageResponse)
async def generate_image(
    request: GenerateImageRequest,
    session: AsyncSession = Depends(get_session)
):
    is_allowed, reason = content_moderation.check_text_content(request.prompt)
    if not is_allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Запрос отклонен: {reason}"
        )
    
    user = await user_service.get_or_create_user(
        session,
        telegram_id=request.telegram_id
    )
    
    generation = Generation(
        user_id=user.id,
        generation_type="image",
        prompt=request.prompt,
        model=request.model,
        style=request.style,
        cost=0,
        status="processing"
    )
    session.add(generation)
    await session.commit()
    
    result = await image_generation_service.generate_image(
        prompt=request.prompt,
        model=request.model or "flux",
        style=request.style
    )
    
    if result.get("status") == "success":
        image_url = result.get("images", [""])[0]
        
        user.total_generations += 1
        generation.status = "completed"
        generation.result_file = image_url
        await session.commit()
        
        return GenerateImageResponse(
            success=True,
            message="Image generated successfully",
            image_url=image_url,
            generation_id=generation.id
        )
    else:
        generation.status = "failed"
        generation.error_message = result.get("message", "Unknown error")
        await session.commit()
        raise HTTPException(status_code=500, detail=result.get("message"))
```

```python
class ImageGenerationService:
    def __init__(self):
        self.api_url = settings.FFANS_API_URL
        self.api_key = settings.FFANS_API_KEY
        self.openai_key = settings.OPENAI_API_KEY
        self.provider = settings.IMAGE_GENERATION_PROVIDER
    
    async def generate_image(
        self,
        prompt: str,
        model: str = "flux",
        style: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024
    ) -> Dict[str, Any]:
        if self.openai_key and self.provider == "openai":
            logger.info("Using OpenAI DALL-E for image generation")
            return await self._generate_with_openai(prompt, model, width, height)
        
        if self.openai_key:
            logger.info("OpenAI key found, using OpenAI DALL-E as fallback")
            return await self._generate_with_openai(prompt, model, width, height)
```

```python
async def _generate_with_openai(self, prompt: str, model: str, width: int, height: int) -> Dict[str, Any]:
    size_map = {
        (1024, 1024): "1024x1024",
        (1024, 1536): "1024x1536",
        (1536, 1024): "1536x1024"
    }
    size = size_map.get((width, height), "1024x1024")
    
    dall_e_model = "dall-e-3"
    
    async with aiohttp.ClientSession() as session:
        headers = {
            'Authorization': f'Bearer {self.openai_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "model": dall_e_model,
            "prompt": prompt,
            "size": size,
            "quality": "standard",
            "n": 1
        }
        
        async with session.post(
            "https://api.openai.com/v1/images/generations",
            json=payload,
            headers=headers
        ) as response:
            if response.status == 200:
                result = await response.json()
                
                if "data" in result and len(result["data"]) > 0:
                    image_url = result["data"][0].get("url", "")
                    return {
                        "status": "success",
                        "message": "Image generated successfully",
                        "images": [image_url],
                        "task_id": result.get("created", "")
                    }
            else:
                error_text = await response.text()
                return {
                    "status": "error",
                    "message": f"OpenAI API error: {error_text}"
                }
```

```bash
OPENAI_API_KEY=sk-ваш_ключ_openai
IMAGE_GENERATION_PROVIDER=openai
```
