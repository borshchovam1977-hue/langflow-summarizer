
```mermaid
graph TD
    User([Пользователь])
    API_Gateway[API Gateway]
    
    subgraph "Инициализация (POST)"
        Valid[Валидация запроса & заголовков]
        Queue[Очередь задач]
    end

    subgraph "Ядро обработки (Pipeline worker)"
        DocParse[Парсинг DOCX]
        Formatter[Formatter: Стили, поля, шрифты]
        Chunking[Разбиение на чанки + Markdown]
        
        subgraph "Параллельная обработка правил"
            TextRules[[Текстовые правила (RegEx/Python)]]
            LLMRules[[LLM правила (AI Models)]]
        end
        
        Validator{LLM Валидатор}
        ApplyChanges[Локализация и вставка изменений в DOCX]
        MetaGen[Генерация отчета meta.json]
        ZipPack[Упаковка в ZIP]
    end

    User -- "1. Загрузка файла & настроек\n(POST /doc-control)" --> API_Gateway
    API_Gateway -- "2. Проверка X-Platform, X-Email" --> Valid
    Valid --> Queue
    Queue -- "Job ID" --> API_Gateway
    API_Gateway -- "201 Created + Job ID" --> User

    Queue -.-> DocParse
    DocParse --> Formatter
    Formatter --> Chunking
    Chunking --> TextRules & LLMRules
    TextRules & LLMRules --> Validator
    
    Validator -- "Отсев галлюцинаций" --> ApplyChanges
    ApplyChanges -- "Режим: Revision / Comments" --> MetaGen
    MetaGen --> ZipPack
    
    User -- "3. Опрос готовности\n(GET /doc-control/{id})" --> API_Gateway
    API_Gateway -- "202 Accepted (В процессе)" --> User
    ZipPack -.-> API_Gateway
    API_Gateway -- "200 OK + ZIP файл" --> User

    style User fill:#f9f,stroke:#333
    style Validator fill:#ff9,stroke:#f66
    style LLMRules fill:#bbf,stroke:#333
    style TextRules fill:#bfb,stroke:#333
```
