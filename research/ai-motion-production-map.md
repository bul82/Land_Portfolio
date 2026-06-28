# AI и motion-пайплайн для лендингов

Обновлено: 25 июня 2026.

Цель документа: после ручного улучшения лендингов подключать нейронки и motion-референсы не хаотично, а как производственный процесс: что генерируем, чем проверяем, где это реально улучшает конверсию и где лучше оставить статичный интерфейс.

## Где AI реально полезен

### Hero и case-cover изображения

Инструменты:
- Nano Banana / Gemini image generation: генерация и итеративное редактирование изображений через текст + изображения. По документации Google AI, Nano Banana относится к native image generation Gemini и поддерживает генерацию/редактирование с текстом и изображениями. Источник: https://ai.google.dev/gemini-api/docs/image-generation
- Gemini / Nano Banana overview: полезно для быстрых вариантов, точечного редактирования, текстур и визуалов под конкретный бренд. Источник: https://gemini.google/overview/image-generation/

Применение:
- Fluff & Care: более дорогие салонные кадры, крупные детали шерсти, косметика, руки мастера, спокойный питомец.
- Liberty Academy: рабочее место студента, laptop dashboard, passport/notebook, теплый дневной свет, без фейкового текста.
- Land Lawyer: документы, кадастровые планы, планшет с абстрактной картой, стол юриста, строгий свет.
- Portfolio: case covers, mockup wall, hero visual с витриной проектов.

Правило:
- Использовать промпты из `/Users/bul82/Documents/Land_REF/IMAGE_PROMPT_RULES.md`.
- Не генерировать “красивую картинку вообще”. Генерировать сцену под блок: hero, карточка кейса, CTA, before/after, trust block.

### Видео и motion-превью

Инструменты:
- Kling AI: video generation, image generation, sound generation, effects; официальный сайт позиционирует Kling как creative studio для изображений и видео. Источник: https://kling.ai/
- Runway Gen-4: работает с визуальными референсами и инструкциями для создания изображений/видео с консистентным стилем, субъектами и локациями. Источник: https://runwayml.com/research/introducing-runway-gen-4
- Pika: idea-to-video платформа, сильна для коротких эффектов и оживления изображений. Источник: https://pika.art/

Применение:
- Portfolio hover-video: 5-8 секунд, показывать продукт/сайт в действии без пустого стартового кадра.
- Land Lawyer: легкое движение по документам/плану участка, не “киношность”, а доверие и аккуратность.
- Liberty Academy: короткий motion учебного dashboard + карточки прогресса.
- Fluff & Care: мягкий salon loop: towel, brush, finished look. Без резкой динамики.

Ограничения:
- AI-video легко дает пластиковый рекламный ролик. Для лендингов лучше короткие loop-сцены и интерфейсные walkthrough, чем “вау-фильм”.
- Для реальных сайтов надежнее Playwright-запись экрана + ffmpeg, как сделано в портфолио. Kling/Runway/Pika использовать для атмосферных вставок и hero-loop, где нет риска исказить интерфейс.

### Апскейл, чистка и варианты

Задачи:
- повысить качество старых covers;
- убрать визуальный мусор;
- сделать 2-3 варианта палитры;
- подготовить mobile crop отдельно от desktop crop;
- сделать poster frame для видео.

Критерии приемки:
- один главный фокус;
- нет фейкового читаемого текста;
- палитра совпадает с лендингом;
- изображение читается в карточке 16:9 и на мобильном;
- вес оптимизирован.

## Где искать motion-идеи не через нейронки

### Библиотеки и showcase

- GSAP Showcase: примеры scroll, SVG, UI, text и complex web animation от агентств и разработчиков. Источник: https://gsap.com/showcase/
- GSAP homepage/docs: GSAP подходит для “animate anything JS can touch”; применять точечно, если нужна сложная scroll-сцена. Источник: https://gsap.com/
- Motion.dev examples: production-ready snippets для React, JavaScript, Vue; хорош для легких hover/reveal/form transitions. Источник: https://motion.dev/examples
- Motion.dev docs: использовать, если проект на современном JS/React или нужен компактный motion без тяжелого GSAP. Источник: https://motion.dev/docs
- Rive: интерактивная анимация с state machines, может использоваться для hero-illustrations, product demos, interactive icons. Источник: https://rive.app/
- Rive websites use case: Rive отдельно описывает website use cases: animated graphics, hero sections, interactive product demos. Источник: https://rive.app/use-cases/websites
- Codrops: tutorials, creative demos, case studies, motion highlights и curated Webzibition. Источник: https://tympanus.net/codrops/
- Codrops Creative Hub: open-source demos, design experiments, interactive concepts. Источник: https://tympanus.net/codrops/hub/

### Что вытаскивать из референсов

Не копировать сайт. Забираем приемы:
- sticky storytelling: блок “как идет работа” фиксируется, справа меняется визуал;
- scroll-driven preview: при скролле меняется состояние сайта/CRM/формы;
- hover-video cards: карточка кейса запускает видео без скачка размера;
- form micro-feedback: после выбора услуги форма показывает следующий шаг;
- animated counters: только для реальных метрик, без бессмысленного “100%”;
- reveal sections: мягкий fade/translate 12-24px, без театральной анимации;
- CTA affordance: кнопка имеет понятный hover, focus, active state;
- trust motion: документы/отзывы/кейсы появляются спокойно, не “прыгают”.

## Применение по текущим проектам

### Land_Grooming

Следующие улучшения:
- mini video-loop в блоке before/after: медленное раскрытие результата;
- hover состояния карточек пород: легкое приближение фото + подсветка цены;
- форма записи: после выбора времени показывать “что будет дальше”;
- Rive/Lottie не нужны, достаточно CSS/JS.

AI-задачи:
- 2-3 premium salon кадра для trust/masters;
- mobile crop hero без потери питомца;
- короткий Kling/Runway loop только если он выглядит как реальная съемка.

### Land_Lang

Следующие улучшения:
- sticky блок “маршрут студента”: уровень -> цель -> расписание -> результат;
- dashboard preview можно оживить scroll-driven состояниями;
- пробная заявка должна показывать следующий шаг: “куратор предложит окна”.

AI-задачи:
- Nano Banana для учебного desktop scene без фейкового текста;
- Runway/Kling для 5-секундного study desk motion;
- Motion.dev для легких карточек прогресса.

### Land_Lawyer

Следующие улучшения:
- блок “срочно/можно планово”;
- документы и риски показать визуально: выписка, план, ограничения;
- форма должна запрашивать дату сделки/суда/ответа администрации.

AI-задачи:
- строгие кадры документов, плана участка, планшета с картой;
- видео только очень спокойное: движение света, прокрутка документа, zoom на карту.

### Land_Portfolio

Следующие улучшения:
- в каждой карточке кейса один и тот же паттерн: poster -> hover-video -> CTA;
- добавить “после запуска” и “следующие улучшения” как доказательство системности;
- motion не должен грузить страницу: preload metadata, короткие webm, poster обязательно.

AI-задачи:
- обновлять case covers после каждого редизайна;
- генерировать отдельные prompts для hero/card/mobile.

## Мини-процесс на каждый новый визуал

1. Определить блок и задачу: hero, case cover, trust, CTA, motion preview.
2. Сформулировать промпт по `IMAGE_PROMPT_RULES.md`.
3. Сгенерировать 2-4 варианта.
4. Проверить: фокус, палитра, отсутствие мусора, mobile crop.
5. Сжать изображение и подготовить poster.
6. Если нужен motion: сначала Playwright/реальная запись, потом AI-video только для атмосферных вставок.
7. Проверить desktop/mobile и вес.

## Практический приоритет

1. Довести текущие реальные лендинги по блокам доверия/заявок.
2. Обновить covers и hover-video в портфолио после каждого изменения.
3. Для каждого проекта создать 3 prompt-брифа: hero, case-card, inner visual.
4. После этого тестировать Kling/Runway/Pika на одном проекте, не сразу на всех.
5. Motion внедрять от простого к сложному: CSS reveal -> hover video -> scroll-driven preview -> GSAP/Rive только при явной пользе.
