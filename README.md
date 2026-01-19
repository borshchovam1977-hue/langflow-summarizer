# 📄 Langflow Document Summarizer

Веб-приложение для суммаризации документов с использованием Langflow API.

## 🚀 Возможности

- 📁 Суммаризация загруженных файлов (PDF, TXT, DOCX)
- 🔗 Суммаризация веб-страниц по URL
- 📝 Суммаризация текста
- 🎨 Два формата вывода: стандартный и улучшенный

## ⚙️ Настройка

### Локальный запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/YOUR_USERNAME/langflow-summarizer.git
cd langflow-summarizer
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.streamlit/secrets.toml`:
```toml
LANGFLOW_API_KEY = "ваш-api-ключ"
LANGFLOW_API_URL = "https://ваш-url/api/v1/run/ваш-flow-id"
```

4. Запустите приложение:
```bash
streamlit run streamlit_app.py
```

### Деплой на Streamlit Cloud

1. Загрузите код на GitHub
2. Перейдите на [share.streamlit.io](https://share.streamlit.io)
3. Подключите репозиторий
4. В настройках добавьте Secrets:
   - `LANGFLOW_API_KEY`
   - `LANGFLOW_API_URL`

## 📋 Структура проекта

```
langflow-summarizer/
├── streamlit_app.py    # Основное приложение
├── requirements.txt    # Зависимости Python
└── README.md          # Документация
```

## 🔐 Secrets

Приложение использует следующие секреты:

| Ключ | Описание |
|------|----------|
| `LANGFLOW_API_KEY` | API ключ для Langflow |
| `LANGFLOW_API_URL` | URL эндпоинта Langflow API |

## 📄 Лицензия

MIT License
