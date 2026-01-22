flowchart TD
    Start([Начало]) --> PrepareRequest[Подготовка файла и параметров]
    
    PrepareRequest --> PostTask{Отправка задачи
POST /v1/task/...}
    
    PostTask -- Ошибка (4xx, 5xx) --> ErrorEnd([Конец с ошибкой])
    PostTask -- Успех (201 Created) --> GetID[Сохранить job_id
и eta_seconds]
    
    GetID --> Wait[Ожидание таймера
(ETA или фикс. время)]
    Wait --> PollTask{Опрос статуса
GET /v1/task/.../job_id}
    
    PollTask -- 404/500 --> ErrorEnd
    PollTask -- Задача в процессе --> Wait
    PollTask -- Успех (200 OK) --> Result([Обработка результата
JSON или Markdown])
    
    subgraph "Управление заголовком X-Endpoint"
    style PostTask stroke:#f66,stroke-width:2px
    style PollTask stroke:#6f6,stroke-width:2px
    style AbortTask stroke:#66f,stroke-width:2px
    
    Note1[POST: X-Endpoint = тип задачи]
    Note2[GET: X-Endpoint = pull]
    Note3[DELETE: X-Endpoint = abort]
    end

    Result --> UserAction{Действие пользователя}
    UserAction -- Отменить --> AbortTask{Отмена
DELETE .../job_id}
    UserAction -- Готово --> Finish([Конец])
    AbortTask --> Finish
