import streamlit as st
import requests
import base64

st.set_page_config(page_title="Langflow Summarizer", page_icon="📄", layout="centered")

st.title("📄 Langflow Document Summarizer")
st.markdown("Загрузите файл и выберите формат суммаризации")

# ============================================
# API Configuration
# ============================================
API_KEY = st.secrets.get("LANGFLOW_API_KEY", "")
API_URL = st.secrets.get("LANGFLOW_API_URL", "")

# Проверка конфигурации
if not API_KEY or not API_URL:
    st.error("⚠️ Не настроены API ключи. Добавьте LANGFLOW_API_KEY и LANGFLOW_API_URL в Secrets.")
    st.info("""
    **Как настроить:**
    1. Перейдите в Settings → Secrets в Streamlit Cloud
    2. Добавьте:
    ```
    LANGFLOW_API_KEY = "ваш-api-ключ"
    LANGFLOW_API_URL = "https://ваш-url/api/v1/run/ваш-flow-id"
    ```
    """)
    st.stop()

# ============================================
# Component IDs
# ============================================
UNIVERSAL_LOADER_ID = "MergeDataComponent-qn7rf"
PROMPT_ID = "Prompt-mZiHh"

# ============================================
# Форматы суммаризации
# ============================================
FORMATS = {
    "standard": "📝 Стандартный",
    "enhanced": "📊 Улучшенный"
}


def send_request(input_value, loader_params=None, prompt_params=None):
    """Отправляет запрос в Langflow API"""
    tweaks = {}
    
    if loader_params:
        tweaks[UNIVERSAL_LOADER_ID] = loader_params
    
    if prompt_params:
        tweaks[PROMPT_ID] = prompt_params
    
    payload = {
        "input_value": input_value,
        "output_type": "chat",
        "input_type": "text",
        "tweaks": tweaks
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    return requests.post(API_URL, json=payload, headers=headers, timeout=120)


def display_result(response):
    """Отображает результат запроса"""
    if response.ok:
        st.success("✅ Готово!")
        response_json = response.json()
        
        try:
            text = response_json["outputs"][0]["outputs"][0]["results"]["message"]["text"]
            st.subheader("📋 Результат:")
            st.markdown(text)
        except (KeyError, IndexError):
            st.warning("Структура ответа отличается от ожидаемой")
        
        with st.expander("🔍 Полный JSON"):
            st.json(response_json)
    else:
        st.error(f"❌ Ошибка: {response.status_code}")
        st.code(response.text)


# ============================================
# Tabs для разных режимов
# ============================================
tab_file, tab_url, tab_text = st.tabs(["📁 Файл", "🔗 URL", "📝 Текст"])


# ============================================
# TAB 1: Загрузка файла
# ============================================
with tab_file:
    uploaded_file = st.file_uploader(
        "Выберите документ:",
        type=["pdf", "txt", "docx"],
        key="file_uploader_tab1"
    )
    
    if uploaded_file:
        st.info(f"📎 **{uploaded_file.name}** ({uploaded_file.size:,} байт)")
    
    st.divider()
    st.subheader("⚙️ Параметры суммаризации")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        file_format = st.radio(
            "Формат:",
            options=list(FORMATS.keys()),
            format_func=lambda x: FORMATS[x],
            key="file_sum_format",
            horizontal=True
        )
    with col2:
        file_language = st.selectbox(
            "Язык:",
            ["Russian", "English", "German", "French"],
            key="file_sum_lang"
        )
    with col3:
        file_max_length = st.select_slider(
            "Длина:",
            options=[200, 300, 500, 750, 1000],
            value=500,
            key="file_sum_len"
        )
    
    if file_format == "enhanced":
        st.caption("📊 Структура: тема → тезисы → детали → выводы → заключение")
    else:
        st.caption("📝 Краткое резюме с 3-5 ключевыми моментами")
    
    st.divider()
    
    if st.button("🚀 Суммаризировать файл", use_container_width=True, type="primary", key="btn_file_submit"):
        if not uploaded_file:
            st.error("❌ Сначала загрузите файл!")
        else:
            with st.spinner("Обработка..."):
                try:
                    file_content = uploaded_file.read()
                    file_base64 = base64.b64encode(file_content).decode('utf-8')
                    
                    params = {
                        "summarization_format": file_format,
                        "summarization_language": file_language,
                        "max_summary_length": str(file_max_length)
                    }
                    
                    loader_params = {
                        "file_base64": file_base64,
                        "file_name": uploaded_file.name,
                        **params
                    }
                    
                    response = send_request(
                        f"Summarize: {uploaded_file.name}",
                        loader_params=loader_params,
                        prompt_params=params
                    )
                    display_result(response)
                    
                except Exception as e:
                    st.error(f"❌ {str(e)}")


# ============================================
# TAB 2: URL
# ============================================
with tab_url:
    url_input = st.text_input(
        "Введите URL:", 
        placeholder="https://example.com/article", 
        key="url_input_field"
    )
    url_parse_format = st.selectbox(
        "Формат парсинга:", 
        ["Text", "Raw HTML", "PDF"], 
        key="url_parse_format_select"
    )
    
    st.divider()
    st.subheader("⚙️ Параметры суммаризации")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        url_sum_format = st.radio(
            "Формат:",
            options=list(FORMATS.keys()),
            format_func=lambda x: FORMATS[x],
            key="url_sum_format",
            horizontal=True
        )
    with col2:
        url_language = st.selectbox(
            "Язык:",
            ["Russian", "English", "German", "French"],
            key="url_sum_lang"
        )
    with col3:
        url_max_length = st.select_slider(
            "Длина:",
            options=[200, 300, 500, 750, 1000],
            value=500,
            key="url_sum_len"
        )
    
    if url_sum_format == "enhanced":
        st.caption("📊 Структура: тема → тезисы → детали → выводы → заключение")
    else:
        st.caption("📝 Краткое резюме с 3-5 ключевыми моментами")
    
    st.divider()
    
    if st.button("🔗 Загрузить и суммаризировать", use_container_width=True, type="primary", key="btn_url_submit"):
        if not url_input.strip():
            st.error("❌ Введите URL!")
        else:
            with st.spinner("Загрузка URL..."):
                try:
                    params = {
                        "summarization_format": url_sum_format,
                        "summarization_language": url_language,
                        "max_summary_length": str(url_max_length)
                    }
                    
                    loader_params = {
                        "urls": [url_input],
                        "format": url_parse_format,
                        **params
                    }
                    
                    response = send_request(
                        f"Summarize URL: {url_input}",
                        loader_params=loader_params,
                        prompt_params=params
                    )
                    display_result(response)
                    
                except Exception as e:
                    st.error(f"❌ {str(e)}")


# ============================================
# TAB 3: Текст
# ============================================
with tab_text:
    text_input = st.text_area(
        "Введите текст:",
        height=200,
        placeholder="Вставьте текст для суммаризации...",
        key="text_input_area"
    )
    
    st.divider()
    st.subheader("⚙️ Параметры суммаризации")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        text_sum_format = st.radio(
            "Формат:",
            options=list(FORMATS.keys()),
            format_func=lambda x: FORMATS[x],
            key="text_sum_format",
            horizontal=True
        )
    with col2:
        text_language = st.selectbox(
            "Язык:",
            ["Russian", "English", "German", "French"],
            key="text_sum_lang"
        )
    with col3:
        text_max_length = st.select_slider(
            "Длина:",
            options=[200, 300, 500, 750, 1000],
            value=500,
            key="text_sum_len"
        )
    
    if text_sum_format == "enhanced":
        st.caption("📊 Структура: тема → тезисы → детали → выводы → заключение")
    else:
        st.caption("📝 Краткое резюме с 3-5 ключевыми моментами")
    
    st.divider()
    
    if st.button("📝 Суммаризировать текст", use_container_width=True, type="primary", key="btn_text_submit"):
        if not text_input.strip():
            st.error("❌ Введите текст!")
        else:
            with st.spinner("Обработка..."):
                try:
                    params = {
                        "summarization_format": text_sum_format,
                        "summarization_language": text_language,
                        "max_summary_length": str(text_max_length)
                    }
                    
                    response = send_request(
                        text_input,
                        prompt_params=params
                    )
                    display_result(response)
                    
                except Exception as e:
                    st.error(f"❌ {str(e)}")


# ============================================
# Sidebar
# ============================================
with st.sidebar:
    st.header("ℹ️ О приложении")
    
    st.markdown("""
    ### Форматы суммаризации:
    
    **📝 Стандартный**
    - Краткое резюме
    - 3-5 ключевых моментов
    
    **📊 Улучшенный**
    - 🎯 Основная тема
    - 📌 Ключевые тезисы
    - 📊 Важные детали
    - 💡 Выводы
    - 📝 Заключение
    """)
    
    st.divider()
    st.caption("Langflow Document Summarizer")
    st.caption("Powered by MWS GPT")


# Footer
st.markdown("---")
st.caption("Langflow Document Summarizer | Powered by MWS GPT")
