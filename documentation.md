! Прописать возможные значения параметров

# Документация Генеративного Бекенда

## Базовый URL

`http://158.160.34.122:8085/backend`

______________________________________________________________________

## Общие заголовки (gen-backend)

Все запросы в gen-backend (таски, text generation, tokenize) отправляются с прокси-заголовками:

| Header            | Значение                    | Примечание                                                      |
| ----------------- | --------------------------- | --------------------------------------------------------------- |
| `Accept`          | `application/json`          | Всегда выставляется.                                            |
| `X-Platform-Name` | `libre_chat`                | Идентификатор названия платформы                                |
| `X-Platform-Type` | `web`                       | Идентификатор типа платформы                                    |
| `X-Email`         | email текущего пользователя | Используется как идентификатор пользователя на внешнем сервисе. |
| `X-Endpoint`      | см. ниже по эндпоинтам      | Тип задачи                                                      |

Значение `X-Endpoint`:

- при создании задач: `summary` / `protocol` / `transcribe` / `document_control`
- при получении результата: `pull`
- при отмене задачи: `abort`
- при синхронной генерации/токенизации: `text_generation`

______________________________________________________________________

## Допустимые форматы входных файлов и форматы результата

| Задача      | Допустимые расширения входного файла                                                             | Формат результата |
| ----------- | ------------------------------------------------------------------------------------------------ | ----------------- |
| Summary     | `.txt`, `.rtf`, `.docx`, `.doc`, `.pdf`                                                          | `.md`             |
| Protocol    | `.txt`, `.rtf`, `.docx`, `.doc`, `.pdf`, `.mp4`, `.m4a`, `.mp3`, `.ogg`, `.aac`, `.wav`, `.webm` | `.txt`            |
| Transcribe  | `.m4a`, `.mp3`, `.ogg`, `.aac`, `.wav`, `.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`                  | `.txt`            |
| Doc Control | `.docx`                                                                                          | `.docx` (в zip)   |

______________________________________________________________________

## Таблица эндпоинтов

### A. Тасковые эндпоинты (создание / получение результата / отмена)

| Группа      | Операция                        | Метод и путь                           |
| ----------- | ------------------------------- | -------------------------------------- |
| Summary     | Создать задачу суммаризации     | `POST /v1/task/summary`                |
| Summary     | Получить результат (polling)    | `GET /v1/task/summary/{job_id}`        |
| Summary     | Отменить задачу                 | `DELETE /v1/task/summary/{job_id}`     |
| Protocol    | Создать задачу протоколирования | `POST /v1/task/protocol`               |
| Protocol    | Получить результат (polling)    | `GET /v1/task/protocol/{job_id}`       |
| Protocol    | Отменить задачу                 | `DELETE /v1/task/protocol/{job_id}`    |
| Transcribe  | Создать задачу транскрипции     | `POST /v1/task/transcribe`             |
| Transcribe  | Получить результат (polling)    | `GET /v1/task/transcribe/{job_id}`     |
| Transcribe  | Отменить задачу                 | `DELETE /v1/task/transcribe/{job_id}`  |
| Doc Control | Создать задачу нормоконтроля    | `POST /v1/task/doc_control`            |
| Doc Control | Получить результат (polling)    | `GET /v1/task/doc_control/{job_id}`    |
| Doc Control | Отменить задачу                 | `DELETE /v1/task/doc_control/{job_id}` |

Полный URL строится как: `{BASE_URL}{path}`
пример: `http://158.160.34.122:8085/backend/v1/task/summary`

______________________________________________________________________

### B. Синхронные эндпоинты (без job_id)

| Группа          | Операция               | Метод и путь                         |
| --------------- | ---------------------- | ------------------------------------ |
| Text Generation | Синхронная генерация   | `POST /v1/task/text_generation_sync` |
| Tokenize        | Синхронная токенизация | `POST /v1/task/tokenize_sync`        |

______________________________________________________________________

## Правила получения результата (polling) и логирование статусов

Для всех задач (Summary, Protocol, Transcribe, Doc Control) при polling используются одинаковые сообщения логирования:

- `200`: `Задача {job_id} завершена"`
- `202`: `Задача еще выполняется. Ждём и повторяем запрос."`
- `404`: `Задача {job_id} еще не поставлена в очередь на исполнение. Нужно повторить пуллинг запрос через некоторое время."`

`filename` извлекается из `Content-Disposition`:

- приоритет `filename*` (RFC 5987/6266),
- fallback на `filename`.

______________________________________________________________________

## Детальная спецификация по каждому эндпоинту

______________________________________________________________________

# A. Summary

## A1. Создать задачу суммаризации

**Метод/URL**
`POST http://158.160.34.122:8085/backend/v1/task/summary`

**Content-Type запроса**
`multipart/form-data`

**Тело запроса (form-data)**

| Поле                 | Тип         | Описание                                                 |
| -------------------- | ----------- | -------------------------------------------------------- |
| `file`               | file(bytes) | Входной файл.                                            |
| `model_name`         | string      | Имя модели.                                              |
| `client`             | string      | Клиент для LLM. Определяется выбранной моделью.          |
| `task_type`          | string      | Общий алгоритм работы                                    |
| `output_file_format` | string      | Формат ответа (`md`).                                    |
| `template_name`      | string      | Имя шаблона ответа (`default30`).                        |
| `pipeline_mode`      | string      | Алгорм обработки файлов (`hera`, `cahm`, `single_step`). |
| `temperature`        | float       | 0.0..2.0                                                 |
| `top_p`              | float       | (0.0..1.0\]                                              |

**Заголовки**

- Общие заголовки gen-backend (см. выше)
- `X-Endpoint: summary`

**Ответы**

- `201 Created`, JSON:
  ```json
  {
    "id": "string",
    "eta_seconds": 10
  }
  ```
  Поле `id` используется как `job_id`. Поле `eta_seconds` может быть `null`.
- `400` — некорректные параметры/формат.
- `413` — слишком большой файл.
- `415` — неподдерживаемый `Content-Type`.
- `422` — валидация запроса не пройдена.
- `429` — превышен лимит.
- `460` — Ошибка извлечения текста из файла.
- `461` — Файл пустой.
- `462` — Файл слишком короткий.
- `470` — Network ошибка при отправке запроса в LLM.
- `471` — Корректный ответ не был получен от LLM после нескольких повторных запросов.
- `480` — Ошибка в иерархическом сжатии.
- `5xx` — Ошибка сервиса.

**Пример form-data (значения)**

```json
{
  "model_name": "t-pro-it-1",
  "client": "openai",
  "template_name": "default30"
}
```

**Пример curl**

```bash
curl -X POST "http://158.160.34.122:8085/backend/v1/task/summary"   -H "Accept: application/json"   -H "X-Platform-Name: libre_chat"   -H "X-Platform-Type: web"   -H "X-Email: user@example.com"   -H "X-Endpoint: summary"   -F "file=@./input.pdf;type=application/octet-stream"   -F "model_name=t-pro-it-1"   -F "client=openai"   -F "template_name=default30"
```

______________________________________________________________________

## A2. Получить результат суммаризации (polling)

**Метод/URL**
`GET http://158.160.34.122:8085/backend/v1/task/summary/{job_id}`

**Заголовки**

- Общие заголовки gen-backend
- `X-Endpoint: pull`

**Ответы**

- `200 OK`, **файл (bytes)**
  Возвращается файл результата в формате `.md` + `Content-Disposition`.
- `202 Accepted` — задача ещё выполняется.
- `404 Not Found` — задание не найдено.
- `429 Too Many Requests` — превышен лимит.
- `5xx` — ошибка сервиса.

**Пример curl**

```bash
curl -X GET "http://158.160.34.122:8085/backend/v1/task/summary/JOB_ID"   -H "Accept: application/json"   -H "X-Platform-Name: libre_chat"   -H "X-Platform-Type: web"   -H "X-Email: user@example.com"   -H "X-Endpoint: pull"   --output result.md
```

______________________________________________________________________

## A3. Отменить задачу суммаризации

**Метод/URL**
`DELETE http://158.160.34.122:8085/backend/v1/task/summary/{job_id}`

**Заголовки**

- Общие заголовки gen-backend
- `X-Endpoint: abort`

**Ответы**

- `200 OK` — отмена подтверждена.
- `404 Not Found` — задание не найдено.
- `409 Conflict` — отмена невозможна (например, задача уже завершена).
- `429 Too Many Requests` — превышен лимит.
- `5xx` — ошибка сервиса.

**Пример curl**

```bash
curl -X DELETE "http://158.160.34.122:8085/backend/v1/task/summary/JOB_ID"   -H "Accept: application/json"   -H "X-Platform-Name: libre_chat"   -H "X-Platform-Type: web"   -H "X-Email: user@example.com"   -H "X-Endpoint: abort"
```

______________________________________________________________________

# B. Protocol

## B1. Создать задачу протоколирования

**Метод/URL**
`POST http://158.160.34.122:8085/backend/v1/task/protocol`

**Content-Type запроса**
`multipart/form-data`

**Входной файл**
Допустимые расширения: `.txt`, `.rtf`, `.docx`, `.doc`, `.pdf`, `.mp4`, `.m4a`, `.mp3`, `.ogg`, `.aac`, `.wav`, `.webm`

**Тело запроса (form-data)**

| Поле                    | Тип         | Описание                                                 |
| ----------------------- | ----------- | -------------------------------------------------------- |
| `file`                  | file(bytes) | Входной файл.                                            |
| `model_name`            | string      | Имя модели.                                              |
| `client`                | string      | `vllm` \| `deepseek` \| `openai`.                        |
| `task_type`             | string      | Общий алгоритм работы                                    |
| `output_file_format`    | string      | Формат ответа (например `txt`).                          |
| `template_name`         | string      | Имя шаблона ответа.                                      |
| `pipeline_mode`         | string      | Алгорм обработки файлов (`hera`, `cahm`, `single_step`). |
| `temperature`           | float       | 0.0..2.0                                                 |
| `top_p`                 | float       | (0.0..1.0\]                                              |
| `language`              | string      | Язык аудио (например `ru`/`en`).                         |
| `diarize`               | bool        | Диаризация (`true`/`false`).                             |
| `display_time_segments` | bool        | Возвращать таймкоды (`true`/`false`).                    |
| `min_speakers`          | int         | Минимум говорящих.                                       |
| `max_speakers`          | int         | Максимум говорящих.                                      |
| `align_step`            | bool        | Дополнительный шаг выравнивания (`true`/`false`).        |

**Заголовки**

- Общие заголовки gen-backend
- `X-Endpoint: protocol`

**Ответы**

- `201 Created`, JSON:
  ```json
  {
    "id": "string",
    "eta_seconds": 10
  }
  ```
- `400` — некорректные параметры/формат.
- `413` — слишком большой файл.
- `415` — неподдерживаемый `Content-Type`.
- `422` — валидация запроса не пройдена.
- `429` — превышен лимит.
- `455` — Ошибка в запросе транскрибации.
- `460` — Ошибка извлечения текста из файла.
- `461` — Файл пустой.
- `462` — Файл слишком короткий.
- `470` — Network ошибка при отправке запроса в LLM.
- `471` — Корректный ответ не был получен от LLM после нескольких повторных запросов.
- `472` — Ошибка при определении имен участников.
- `480` — Ошибка в иерархическом сжатии.
- `5xx` — Ошибка сервиса.

**Пример form-data (значения)**

```json
{
  "model_name": "t-pro-it-1",
  "client": "openai",
  "template_name": "default"
}
```

**Пример curl**

```bash
curl -X POST "http://158.160.34.122:8085/backend/v1/task/protocol"   -H "Accept: application/json"   -H "X-Platform-Name: libre_chat"   -H "X-Platform-Type: web"   -H "X-Email: user@example.com"   -H "X-Endpoint: protocol"   -F "file=@./meeting.mp3;type=application/octet-stream"   -F "model_name=t-pro-it-1"   -F "client=openai"   -F "template_name=default"
```

______________________________________________________________________

## B2. Получить результат протоколирования (polling)

**Метод/URL**
`GET http://158.160.34.122:8085/backend/v1/task/protocol/{job_id}`

**Заголовки**

- Общие заголовки gen-backend
- `X-Endpoint: pull`

**Ответы**

- `200 OK`, **файл (bytes)**
  Возвращается файл результата в формате `.txt` + `Content-Disposition`.
- `202 Accepted` — задача ещё выполняется.
- `404 Not Found` — задание не найдено.
- `429 Too Many Requests` — превышен лимит.
- `5xx` — ошибка сервиса.

**Пример curl**

```bash
curl -X GET "http://158.160.34.122:8085/backend/v1/task/protocol/JOB_ID"   -H "Accept: application/json"   -H "X-Platform-Name: libre_chat"   -H "X-Platform-Type: web"   -H "X-Email: user@example.com"   -H "X-Endpoint: pull"   --output protocol.txt
```

______________________________________________________________________

## B3. Отменить задачу протоколирования

**Метод/URL**
`DELETE http://158.160.34.122:8085/backend/v1/task/protocol/{job_id}`

**Заголовки**

- Общие заголовки gen-backend
- `X-Endpoint: abort`

**Ответы**

- `200 OK` — отменено.
- `404 Not Found`
- `409 Conflict`
- `429 Too Many Requests`
- `5xx`

**Пример curl**

```bash
curl -X DELETE "http://158.160.34.122:8085/backend/v1/task/protocol/JOB_ID"   -H "Accept: application/json"   -H "X-Platform-Name: libre_chat"   -H "X-Platform-Type: web"   -H "X-Email: user@example.com"   -H "X-Endpoint: abort"
```

______________________________________________________________________

# C. Transcribe

## C1. Создать задачу транскрипции

**Метод/URL**
`POST http://158.160.34.122:8085/backend/v1/task/transcribe`

**Content-Type запроса**
`multipart/form-data`

**Входной файл**
Допустимые расширения: `.m4a`, `.mp3`, `.ogg`, `.aac`, `.wav`, `.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`

**Тело запроса (form-data)**

| Поле                    | Тип         | Описание                                          |
| ----------------------- | ----------- | ------------------------------------------------- |
| `file`                  | file(bytes) | Аудио/видео файл.                                 |
| `model_name`            | string      | Имя модели (например `local`).                    |
| `response_type`         | string      | Тип ответа. Всегда `txt`.                         |
| `language`              | string      | Язык аудио (например `ru`/`en`).                  |
| `diarize`               | bool        | Диаризация (`true`/`false`).                      |
| `display_time_segments` | bool        | Возвращать таймкоды (`true`/`false`).             |
| `min_speakers`          | int         | Минимум говорящих.                                |
| `max_speakers`          | int         | Максимум говорящих.                               |
| `align_step`            | bool        | Дополнительный шаг выравнивания (`true`/`false`). |

**Заголовки**

- Общие заголовки gen-backend
- `X-Endpoint: transcribe`

**Ответы**

- `201 Created`, JSON:
  ```json
  {
    "id": "string",
    "eta_seconds": 10
  }
  ```
- `400 Bad Request`
- `413 Payload Too Large`
- `415 Unsupported Media Type`
- `422 Unprocessable Entity`
- `429 Too Many Requests`
- `5xx`

**Пример form-data (значения)**

```json
{
  "model_name": "local",
  "response_type": "txt",
  "language": "ru",
  "diarize": true,
  "display_time_segments": true,
  "min_speakers": 1,
  "max_speakers": 5,
  "align_step": false
}
```

**Пример curl**

```bash
curl -X POST "http://158.160.34.122:8085/backend/v1/task/transcribe"   -H "Accept: application/json"   -H "X-Platform-Name: libre_chat"   -H "X-Platform-Type: web"   -H "X-Email: user@example.com"   -H "X-Endpoint: transcribe"   -F "file=@./audio.wav;type=application/octet-stream"   -F "model_name=local"   -F "response_type=txt"   -F "language=ru"   -F "diarize=true"   -F "display_time_segments=true"   -F "min_speakers=1"   -F "max_speakers=5"   -F "align_step=false"
```

______________________________________________________________________

## C2. Получить результат транскрипции (polling)

**Метод/URL**
`GET http://158.160.34.122:8085/backend/v1/task/transcribe/{job_id}`

**Заголовки**

- Общие заголовки gen-backend
- `X-Endpoint: pull`

**Ответы**

- `200 OK` — файл результата в формате `.txt` + `Content-Disposition`.
- `202 Accepted` — выполняется.
- `400 Bad Request` — некорректный запрос.
- `404 Not Found` — не найдено.
- `422 Unprocessable Entity` — неверные параметры.
- `429 Too Many Requests`
- `500 Internal Server Error` — внутренняя ошибка сервиса.
- `5xx`

**Пример curl**

```bash
curl -X GET "http://158.160.34.122:8085/backend/v1/task/transcribe/JOB_ID"   -H "Accept: application/json"   -H "X-Platform-Name: libre_chat"   -H "X-Platform-Type: web"   -H "X-Email: user@example.com"   -H "X-Endpoint: pull"   --output transcript.txt
```

______________________________________________________________________

## C3. Отменить задачу транскрипции

**Метод/URL**
`DELETE http://158.160.34.122:8085/backend/v1/task/transcribe/{job_id}`

**Заголовки**

- Общие заголовки gen-backend
- `X-Endpoint: abort`

**Ответы**

- `200 OK` — отменено.
- `404 Not Found`
- `409 Conflict`
- `429 Too Many Requests`
- `5xx`

**Пример curl**

```bash
curl -X DELETE "http://158.160.34.122:8085/backend/v1/task/transcribe/JOB_ID"   -H "Accept: application/json"   -H "X-Platform-Name: libre_chat"   -H "X-Platform-Type: web"   -H "X-Email: user@example.com"   -H "X-Endpoint: abort"
```

______________________________________________________________________

# D. Document Control

## D1. Создать задачу нормоконтроля DOCX

**Метод/URL**
`POST http://158.160.34.122:8085/backend/v1/task/doc_control`

**Content-Type запроса**
`multipart/form-data`

**Входной файл**
Допустимые расширения: `.docx`

**Тело запроса (form-data)**

| Поле         | Тип          | Описание                                     |
| ------------ | ------------ | -------------------------------------------- |
| `file`       | file(bytes)  | Входной DOCX.                                |
| `request_id` | string       | Идентификатор запроса (uuid hex).            |
| `mode`       | string       | Режим: `modify` \| `revision` \| `comments`. |
| `rules`      | string(JSON) | JSON-строка с правилами контроля документа.  |
| `model_name` | string       | Имя модели.                                  |
| `client`     | string       | `vllm` \| `deepseek` \| `openai`.            |

**Как формировать `rules`**

`rules` — это JSON-объект, где ключи — **подправила**. Чтобы включить подправило, нужно добавить его ключ в объект `rules`.
Значения зависят от конкретного подправила:

- если подправилу не нужны параметры — можно передавать пустой объект `{}`.
- если подправило требует параметры — передавайте объект параметров.

Набор подправил и их параметры (сводно):

| Группа (для понимания)       | Подправила (ключи в `rules`)                                                                                                                                                    |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Орфография и пунктуация      | `rule_syntax_and_spelling: {}`                                                                                                                                                  |
| Стиль оформления документов  | `docx_formatter: { ... }` (настройки полей/шрифтов/межстрочного интервала и т.п.; см. пример ниже)                                                                              |
| Содержание и стиль изложения | `rule_no_descriptive_sentences: {}`, `rule_text_brevity: {}`                                                                                                                    |
| Правила типографики          | `normalize_quotation_marks: {"quote_style":"guillemets_ru"}`, `convert_quarters_to_roman: {}`, `expand_money_expressions: {"max_value": 1000000000}`, `rule_capitalization: {}` |

Пример `docx_formatter` (фрагмент структуры):

```json
{
  "docx_formatter": {
    "document": {
      "margins_mm": {"left": 30, "right": 10, "top": 20, "bottom": 20}
    },
    "paragraph": {
      "font": {
        "family": ["Times New Roman", "PT Astra Serif"],
        "size_pt": 13,
        "bold": false,
        "italic": false,
        "underline": false
      },
      "line_spacing": 1.5
    },
    "headings": {
      "Heading 1": {"font": {"family": ["Times New Roman"], "size_pt": 13, "bold": true, "italic": false, "underline": false}},
      "Heading 2": {"font": {"family": ["Times New Roman"], "size_pt": 13, "bold": true, "italic": true, "underline": false}},
      "Heading 3": {"font": {"family": ["Times New Roman"], "size_pt": 13, "bold": true, "italic": false, "underline": false}},
      "Heading 4": {"font": {"family": ["Times New Roman"], "size_pt": 13, "bold": false, "italic": false, "underline": true}}
    },
    "apply_to_tables": true,
    "inline_formatting": {"preserve_word_emphasis": true, "allowed": ["bold", "italic", "underline"]}
  }
}
```

Пример: включить только орфографию/пунктуацию и типографику:

```json
{
  "rule_syntax_and_spelling": {},
  "normalize_quotation_marks": {"quote_style": "guillemets_ru"},
  "convert_quarters_to_roman": {},
  "expand_money_expressions": {"max_value": 1000000000},
  "rule_capitalization": {}
}
```

**Заголовки**

- Общие заголовки gen-backend
- `X-Endpoint: document_control`

**Ответы**

- `201 Created`, JSON:
  ```json
  {
    "id": "string",
    "eta_seconds": 10
  }
  ```
- `400 Bad Request`
- `413 Payload Too Large`
- `415 Unsupported Media Type`
- `422 Unprocessable Entity`
- `429 Too Many Requests`
- `5xx`

**Пример form-data (значения)**

```json
{
  "request_id": "b4df1a0d2c3e4f5a6b7c8d9e0f112233",
  "mode": "revision",
  "rules": {
    "rule_syntax_and_spelling": {},
    "normalize_quotation_marks": {"quote_style": "guillemets_ru"},
    "convert_quarters_to_roman": {},
    "expand_money_expressions": {"max_value": 1000000000},
    "rule_capitalization": {}
  },
  "model_name": "t-pro-it-1",
  "client": "openai"
}
```

**Пример curl**

```bash
curl -X POST "http://158.160.34.122:8085/backend/v1/task/doc_control"   -H "Accept: application/json"   -H "X-Platform-Name: libre_chat"   -H "X-Platform-Type: web"   -H "X-Email: user@example.com"   -H "X-Endpoint: document_control"   -F "file=@./document.docx;type=application/octet-stream"   -F "request_id=b4df1a0d2c3e4f5a6b7c8d9e0f112233"   -F "mode=revision"   -F 'rules={"rule_syntax_and_spelling":{},"normalize_quotation_marks":{"quote_style":"guillemets_ru"},"convert_quarters_to_roman":{},"expand_money_expressions":{"max_value":1000000000},"rule_capitalization":{}}'   -F "model_name=t-pro-it-1"   -F "client=openai"
```

______________________________________________________________________

## D2. Получить результат нормоконтроля (polling)

**Метод/URL**
`GET http://158.160.34.122:8085/backend/v1/task/doc_control/{job_id}`

**Заголовки**

- Общие заголовки gen-backend
- `X-Endpoint: pull`

**Ответы**

- `200 OK` — архив (zip) с результатом + `Content-Disposition`
  На стороне вызывающего backend результат обрабатывается как **архив (zip)**, из которого извлекается:
  - первый `.docx` (результирующий документ),
  - опциональный `meta.json` (метаданные отчёта).
- `202 Accepted` — выполняется.
- `404 Not Found` — не найдено.
- `429 Too Many Requests`
- `5xx`

**Пример curl**

```bash
curl -X GET "http://158.160.34.122:8085/backend/v1/task/doc_control/JOB_ID"   -H "Accept: application/json"   -H "X-Platform-Name: libre_chat"   -H "X-Platform-Type: web"   -H "X-Email: user@example.com"   -H "X-Endpoint: pull"   --output result.zip
```

______________________________________________________________________

## D3. Отменить задачу нормоконтроля

**Метод/URL**
`DELETE http://158.160.34.122:8085/backend/v1/task/doc_control/{job_id}`

**Заголовки**

- Общие заголовки gen-backend
- `X-Endpoint: abort`

**Ответы**

- `200 OK` — отменено.
- `404 Not Found`
- `409 Conflict`
- `429 Too Many Requests`
- `5xx`

**Пример curl**

```bash
curl -X DELETE "http://158.160.34.122:8085/backend/v1/task/doc_control/JOB_ID"   -H "Accept: application/json"   -H "X-Platform-Name: libre_chat"   -H "X-Platform-Type: web"   -H "X-Email: user@example.com"   -H "X-Endpoint: abort"
```

______________________________________________________________________

# E. Text Generation (sync)

## E1. Синхронная генерация текста

**Метод/URL**
`POST http://158.160.34.122:8085/backend/v1/task/text_generation_sync`

**Content-Type запроса**
`application/x-www-form-urlencoded`

**Тело запроса (form fields)**

| Поле              | Тип                 | Описание                                                        |
| ----------------- | ------------------- | --------------------------------------------------------------- |
| `messages_raw`    | string(JSON)        | JSON-строка массива сообщений `[{role, content}, ...]`.         |
| `model_name`      | string              | Имя модели.                                                     |
| `client`          | string              | `vllm` \| `deepseek` \| `openai`.                               |
| `response_type`   | string              | Тип ответа (например `txt`).                                    |
| `temperature`     | float               | 0.0..2.0                                                        |
| `top_p`           | float               | (0.0..1.0\]                                                     |
| `max_tokens`      | int                 | > 0                                                             |
| `system_prompt`   | string              | Переопределение системного промпта.                             |
| `response_format` | string(JSON object) | Структурированный формат, если поддерживается внешним сервисом. |

**Заголовки**

- Общие заголовки gen-backend
- `Content-Type: application/x-www-form-urlencoded`
- `X-Endpoint: text_generation`

**Ответы**

- `200 OK`, JSON (минимально используемое поле):
  ```json
  {
    "content": "string"
  }
  ```
- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `422 Unprocessable Entity`
- `429 Too Many Requests`
- `5xx`

**Пример тела (значения)**

```json
{
  "messages_raw": [
    {
      "role": "user",
      "content": "Hello"
    }
  ],
  "model_name": "t-pro-it-1",
  "client": "vllm",
  "response_type": "txt",
  "temperature": 0.7,
  "top_p": 0.9,
  "max_tokens": 256,
  "system_prompt": "You are a helpful chatbot"
}
```

**Пример curl**

```bash
curl -X POST "http://158.160.34.122:8085/backend/v1/task/text_generation_sync"   -H "Accept: application/json"   -H "Content-Type: application/x-www-form-urlencoded"   -H "X-Platform-Name: libre_chat"   -H "X-Platform-Type: web"   -H "X-Email: user@example.com"   -H "X-Endpoint: text_generation"   --data-urlencode 'messages_raw=[{"role":"user","content":"Hello"}]'   --data-urlencode 'model_name=t-pro-it-1'   --data-urlencode 'client=vllm'   --data-urlencode 'response_type=txt'   --data-urlencode 'temperature=0.7'   --data-urlencode 'top_p=0.9'   --data-urlencode 'max_tokens=256'
```

______________________________________________________________________

# F. Tokenize (sync)

## F1. Синхронная токенизация

**Метод/URL**
`POST http://158.160.34.122:8085/backend/v1/task/tokenize_sync`

**Content-Type запроса**
`application/x-www-form-urlencoded`

**Тело запроса (form fields)**

| Поле                 | Тип    | Описание                                         |
| -------------------- | ------ | ------------------------------------------------ |
| `prompt`             | string | Текст для токенизации.                           |
| `client`             | string | `vllm` \| `deepseek` \| `openai`.                |
| `model_name`         | string | Имя модели.                                      |
| `preset`             | string | Пресет токенизации (если поддерживается).        |
| `add_special_tokens` | bool   | Добавлять специальные токены (`true`/`false`).   |
| `base_url`           | string | Base URL внешнего токенизатора (если требуется). |
| `api_key`            | string | API ключ внешнего токенизатора (если требуется). |
| `prefix`             | string | Опциональный префикс.                            |

**Заголовки**

- Общие заголовки gen-backend
- `Content-Type: application/x-www-form-urlencoded`
- `X-Endpoint: text_generation`

**Ответы**

- `200 OK`, JSON — структура зависит от внешнего сервиса токенизации.
- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `422 Unprocessable Entity`
- `429 Too Many Requests`
- `5xx`

**Пример curl**

```bash
curl -X POST "http://158.160.34.122:8085/backend/v1/task/tokenize_sync"   -H "Accept: application/json"   -H "Content-Type: application/x-www-form-urlencoded"   -H "X-Platform-Name: libre_chat"   -H "X-Platform-Type: web"   -H "X-Email: user@example.com"   -H "X-Endpoint: text_generation"   --data-urlencode 'prompt=Hello'   --data-urlencode 'client=vllm'   --data-urlencode 'model_name=t-pro-it-1'   --data-urlencode 'add_special_tokens=true'
```

______________________________________________________________________

## Последовательность вызовов (job_id + polling)

### Шаг 1 — создать задачу

- `POST /v1/task/<kind>`
- Успешный ответ: `201` и JSON с `id` (это `job_id`).

### Шаг 2 — получать результат (polling)

- `GET /v1/task/<kind>/{job_id}`
- Возможные ответы:
  - `202` — ещё не готово → ждать и повторять
  - `200` — готово → скачать файл (bytes)
  - `404` — задача не найдена → ждать и повторять
  - `429` — превышен лимит → завершить как ошибка
  - `5xx` — ошибка сервиса → завершить как ошибка

### Шаг 3 (опционально) — отменить

- `DELETE /v1/task/<kind>/{job_id}`
- `200` означает подтверждение отмены.

______________________________________________________________________

## Пример последовательности (Summary)

1. Создать:

- `POST http://158.160.34.122:8085/backend/v1/task/summary`
- получить `{ "id": "JOB_ID" }`

2. Polling:

- `GET  http://158.160.34.122:8085/backend/v1/task/summary/JOB_ID`
- пока `202` → повторять
- при `200` → скачать файл `.md`

3. Abort (если нужно):

- `DELETE http://158.160.34.122:8085/backend/v1/task/summary/JOB_ID`
