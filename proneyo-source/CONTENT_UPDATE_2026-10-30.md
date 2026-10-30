# Обновление от 30 октября 2026

Добавлены отдельные блоки роликового массажа тела, коррекции локальных жировых отложений и LED-ухода для лица. Стиль, цвета и существующая структура сайта сохранены.

Три материала опубликованы в HTML и доступны обычными ссылками с главной и из раздела статей:

- `/articles/rolikovyy-massazh-tela/`
- `/articles/lokalnaya-korrekciya-tela/`
- `/articles/led-uhod-dlya-lica/`

Тексты объясняют процедуры без обещаний гарантированного результата. Источники AAD, FDA и ASPS перечислены в каждом материале. Автор обозначен как организация «Про НЕЁ», без приписывания текста конкретному специалисту или заявления о медицинской рецензии.

Имена и отдельные показатели опыта специалистов заменены единым блоком «Более 17 лет опыта» по указанию владельца. Формулировка не сообщает дату основания компании. В навигации теперь «О студии».

В абонементе 10 000 ₽ состав и нюансы предлагается уточнить по телефону; кнопка открывает звонок. Удалены публичные упоминания исключённых процедур в абонементах, прайсе, карточках, JSON, модальном окне, статьях и SEO-разметке. Неопубликованные прежние URL материалов удалены. Для четырёх вариантов аппаратной коррекции используется согласованное общее название, без названия метода. Исходный каталог DIKIDI с 73 позициями сохранён в `content-drafts/prices-dikidi-2026-10-22.json`; публичный каталог содержит 70 позиций. Цены сохранённых услуг не менялись, дата проверки каталога не обновлялась.

Сервис-воркер автоматически получил новую версию кеша. Новые статьи включены в sitemap и статический HTML. Генератор поддерживает фотографии карточек статей и авторство организации.

## Изображения

Использован встроенный ImageGen. Три фотографии обработаны/перегенерированы на основе предоставленных владельцем референсов. Эти изображения иллюстрируют процедуры; они не служат доказательством результатов лечения. Реальные снимки помещения использованы отдельно, без генеративного изменения интерьера. Оптимизация в WebP выполнена для публикации на сайте.

| Референс | Файл в проекте | Использование |
| --- | --- | --- |
| IMG_1053.jpeg | `dist/assets/roller-care-2026.webp` | Блок роликового массажа и статья |
| IMG_1018.jpeg | `dist/assets/local-body-care-2026.webp` | Локальная коррекция, статья, абонемент 10 000 ₽ и карточка направления |
| IMG_1043.jpeg | `dist/assets/led-face-care-2026.webp` | LED-уход, статья и карточка SPA |
| 63FBDE24-1E34-4927-A73B-E72F689E687D.jpeg | `dist/assets/studio-room-2026.webp` | Настоящий кабинет |
| 4EE6C91B-09C4-41EC-ACE0-204FDA1E94B4.png | `dist/assets/studio-details-2026.webp` | Настоящие детали интерьера |
| 396EB9D2-3D73-4418-AE54-55536070624C.jpeg | `dist/assets/studio-sign-2026.webp` | Настоящая вывеска |

## Задания на генерацию

### Роликовый массаж

Use case: lighting-weather. Edit target: attached real roller body massage photo. Produce one premium photorealistic editorial image for a beauty studio website, landscape 4:3. Preserve this exact large grey handheld device with rows of small metallic gold spheres and subdued amber inner light, and its contact with the adult woman's thigh. Preserve anatomy, natural skin texture, proportions, black gloves and the genuine treatment action. Reframe wider as needed with cream towel respectfully covering the rest of her body, no nudity. Improve the dim lighting to soft warm daylight and a refined ivory and warm beige spa palette with a tiny muted berry accent in the blurred background. Clean linen, calm professional atmosphere, realistic camera photograph, crisp handpiece, gently soft background. Keep faces out of frame. No text, no logo, no before/after, no body reshaping, no false visual results, no exaggerated orange neon.

### Локальная коррекция

Use case: lighting-weather, identity-preserve. Edit target: attached actual beauty treatment photo. Create a single polished landscape 4:3 editorial photograph for the same studio's website. Preserve the exact brunette practitioner's recognizable face, her white uniform, black gloves, the same white-and-black broad body applicator, its tube, the adjacent actual white and black machine, and the position against the adult client's abdomen. Preserve client identity and body shape, natural skin, and cream towel covering lower body and chest, no nudity. Improve soft daylight, white balance, contour lighting, subtle natural skin retouch only. Calm clean ivory, warm beige and muted berry environment, keep authentic marble wall design. Remove the decorative Aesthet wall text and any visible branding or screen writing. More coherent professional composition with a little breathing room around the apparatus. No syringes, no needles, no text, no before/after results, no body slimming, no glossy plastic faces.

### LED-уход

Use case: lighting-weather. Edit target: attached actual LED facial care photo. Create one premium landscape 4:3 photograph for a beauty studio website. Preserve the same actual open curved white LED canopy with rows of red lights, the adult woman's identity, relaxed lying pose, protective dark eye goggles and disposable cap. Improve viewpoint to tasteful three-quarter side view so the canopy shape and face are clear, without changing the treatment. Preserve realistic anatomy and skin texture. Soften the harsh red cast into a believable warm red LED glow limited to the face inside the canopy; balance the rest of the scene with soft cream daylight, clean ivory linen, warm beige interior and subtle muted berry tones. Crisp professional photography, calm caring atmosphere. Crop below shoulders and use modest towel coverage. No text, no branding, no UV/tanning appearance, no needles, no heavy steam, no beauty filter, no invented treatment results.

## Проверки

- `python3 scripts/check_seo.py`: HTML 14 страниц, 13 индексируемых страниц, 70 позиций прайса, ссылки, локальные изображения и SEO-разметка.
- `python3 scripts/test_seo_pipeline.py`: восемь проверок генерации, переноса домена, публикации статей и доступности содержимого без JavaScript.
- `node --check dist/app.js` и `node --check dist/sw.js`.
- Браузерная проверка на широком экране и во встроенных окнах 320, 390, 768 px. Исправлено переполнение блока опыта; на повторной проверке горизонтального переполнения нет.
