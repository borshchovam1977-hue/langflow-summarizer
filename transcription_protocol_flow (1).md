# Схема работы сервисов Транскрибации и Протоколирования

```mermaid
graph TD
    User([Пользователь])
    APIGW[API Gateway]
    
    subgraph "Процесс 1: Транскрибация (ASR)"
        TranscribeWorker[Transcribe Worker]
        Whisper[ASR Модель\n(Whisper/NVIDIA)]
        Diarization[Диаризация\n(Разделение голосов)]
        ResultText[(JSON/Text\nс таймкодами)]
    end

    subgraph "Процесс 2: Протоколирование (LLM)"
        ProtocolWorker[Protocol Worker]
        ContextWindow[Управление контекстом\n(Chunking)]
        LLM[LLM Модель\n(DeepSeek/GPT/Local)]
        ResultProtocol[(Готовый протокол\nЗадачи / Решения)]
    end

    %% Flow 1: Transcribe
    User -- "1. Загрузка AUDIO\n(POST /task/transcribe)" --> APIGW
    APIGW --> TranscribeWorker
    TranscribeWorker --> Whisper --> Diarization
    Diarization --> ResultText
    ResultText -.-> User
    
    %% Flow 2: Protocol
    User -- "2. Отправка ТЕКСТА\n(POST /task/protocol)" --> APIGW
    APIGW --> ProtocolWorker
    ProtocolWorker --> ContextWindow
    ContextWindow -- "Инструкции + Текст" --> LLM
    LLM -- "Извлечение сущностей" --> ResultProtocol
    ResultProtocol -- "200 OK" --> User

    style User fill:#f9f,stroke:#333
    style Whisper fill:#bfb,stroke:#333
    style LLM fill:#bbf,stroke:#333
    style ResultText fill:#eee,stroke:#333,stroke-dasharray: 5 5
```
