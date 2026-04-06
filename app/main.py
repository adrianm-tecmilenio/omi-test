import streamlit as st
import requests
import json
import uuid

# ─── CSS personalizado ───
st.markdown("""
<style>
    .plan-header {
        text-align: center;
        padding: 10px 16px;
        border-radius: 8px;
        margin-bottom: 12px;
        font-weight: 700;
        font-size: 1.1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ─── Título ───
st.title("Chatbot generación de planes test")

# ─── Session state init ───
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []


# ─── Helper: renderizar un plan ───
def render_plan(msg):
    """Renderiza el plan de trabajo."""
    plan = msg["plan"]
    titulo = plan.get("titulo", "Plan de trabajo")
    st.markdown(
        f'<div class="plan-header">📋 {titulo}</div>',
        unsafe_allow_html=True,
    )
    st.json(plan)


# ─── Renderizar historial ───
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    elif message["role"] == "plan":
        with st.chat_message("assistant"):
            render_plan(message)


# ─── Entrada del usuario ───
if prompt := st.chat_input("Escribe tu pregunta:"):
    # Agregar pregunta al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Llamar al endpoint
    with st.spinner("El agente está pensando..."):
        try:
            response = requests.post(
                "http://zentia-demo-26.southcentralus.azurecontainer.io/rutas",
                json={"questions": prompt},
            )
            if response.status_code == 200:
                plan_data = response.json()
            else:
                plan_data = {"error": f"Status {response.status_code}"}
        except Exception as e:
            plan_data = {"error": str(e)}

    # Guardar plan en el historial
    plan_msg = {
        "role": "plan",
        "plan": plan_data,
    }
    st.session_state.messages.append(plan_msg)

    # Renderizar el plan
    with st.chat_message("assistant"):
        render_plan(plan_msg)