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
# app_name = st.selectbox(
#     "Selecciona el tipo de agente:",
#     ("zentia", "proposito_accion"),
#     index=0
# )

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

    # Enviar la pregunta al endpoint
    with st.spinner("El agente está pensando..."):
        try:
            response = requests.post(
                "http://zentia-demo-26.southcentralus.azurecontainer.io/rutas",
                json={
                    "questions": prompt
                }
            )
            if response.status_code == 200:
                agent_response = response.json()
            else:
                agent_response = {"error": "Error al conectar con el agente."}
        except Exception as e:
            agent_response = {"error": f"Error: {str(e)}"}

    # Mostrar la respuesta del agente
    import json
    formatted_response = json.dumps(agent_response, indent=2, ensure_ascii=False)
    st.session_state.messages.append({"role": "assistant", "content": formatted_response})
    with st.chat_message("assistant"):
        st.json(agent_response) 