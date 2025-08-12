import streamlit as st
import requests
import time
import uuid  # Para generar un session_id único

# Título de la aplicación
st.title("Chatbot OMI-Test")

organization_ids = {
    "zentia": 1010000,
    "proposito_accion": 1010001
}

# Dropdown para seleccionar el app_name (fijo arriba)
app_name = st.selectbox(
    "Selecciona el tipo de agente:",
    ("zentia", "proposito_accion"),
    index=0
)

# Generar un session_id único al cargar la página o hacer refresh
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Inicializar el historial de la conversación
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar el historial de la conversación
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Función para el efecto de typewriter
def typewriter_effect(text, speed=0.01):
    placeholder = st.empty()
    displayed_text = ""
    for char in text:
        displayed_text += char
        placeholder.markdown(displayed_text)
        time.sleep(speed)
    return displayed_text

# Entrada del usuario
if prompt := st.chat_input("Escribe tu pregunta:"):
    # Agregar la pregunta del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Enviar la pregunta y el app_name al endpoint
    with st.spinner("El agente está pensando..."):
        try:
            org_id = organization_ids[app_name]
            response = requests.post(
                "http://172.206.131.179/omi",
                json={
                    "message": prompt,
                    "id_organization": org_id,
                    "user_id": 1377
                }
            )
            if response.status_code == 200:
                agent_response = response.json().get("message", "(Sin respuesta del agente)")
            else:
                agent_response = "Error al conectar con el agente."
        except Exception as e:
            agent_response = f"Error: {str(e)}"

    # Mostrar la respuesta del agente con efecto de typewriter
    st.session_state.messages.append({"role": "assistant", "content": agent_response})
    with st.chat_message("assistant"):
        typewriter_effect(agent_response) 