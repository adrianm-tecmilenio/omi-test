import streamlit as st
import requests
import json
import uuid

# ─── CSS personalizado para la UI de comparación ───
st.markdown("""
<style>
    /* Contenedor de cada plan */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
        border-radius: 12px;
    }

    /* Estilo de los botones de selección */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Header de cada plan */
    .plan-header {
        text-align: center;
        padding: 8px 16px;
        border-radius: 8px;
        margin-bottom: 8px;
        font-weight: 700;
        font-size: 1.05rem;
    }
    .plan-header-complete {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .plan-header-example {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }

    /* Badge de selección */
    .selected-badge {
        text-align: center;
        padding: 10px 16px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        margin-top: 8px;
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
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


# ─── Helper: renderizar una comparación ───
def render_comparison(msg, idx):
    """Renderiza dos planes lado a lado con opción de elegir."""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="plan-header plan-header-complete">📋 Plan Completo</div>',
            unsafe_allow_html=True,
        )
        st.json(msg["complete_plan"])
        if msg["selected"] is None:
            if st.button("✅ Elegir este", key=f"select_complete_{idx}"):
                st.session_state.messages[idx]["selected"] = "complete_plan"
                st.rerun()
        elif msg["selected"] == "complete_plan":
            st.markdown(
                '<div class="selected-badge">✅ Elegido</div>',
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown(
            '<div class="plan-header plan-header-example">🧩 Plan Ejemplo</div>',
            unsafe_allow_html=True,
        )
        st.json(msg["example_plan"])
        if msg["selected"] is None:
            if st.button("✅ Elegir este", key=f"select_example_{idx}"):
                st.session_state.messages[idx]["selected"] = "example_plan"
                st.rerun()
        elif msg["selected"] == "example_plan":
            st.markdown(
                '<div class="selected-badge">✅ Elegido</div>',
                unsafe_allow_html=True,
            )

    # Mostrar confirmación debajo de las columnas
    if msg["selected"] is not None:
        label = "Plan Completo" if msg["selected"] == "complete_plan" else "Plan Ejemplo"
        st.success(f"Elegiste: **{label}**")


# ─── Renderizar historial ───
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    elif message["role"] == "comparison":
        with st.chat_message("assistant"):
            render_comparison(message, i)


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
                "http://localhost:8000/rutas",
                json={"questions": prompt},
            )
            if response.status_code == 200:
                data = response.json()
                complete_plan = data.get("complete_plan", {})
                example_plan = data.get("example_plan", {})
            else:
                complete_plan = {"error": f"Status {response.status_code}"}
                example_plan = {"error": f"Status {response.status_code}"}
        except Exception as e:
            complete_plan = {"error": str(e)}
            example_plan = {"error": str(e)}

    # Guardar comparación en el historial
    comparison_msg = {
        "role": "comparison",
        "complete_plan": complete_plan,
        "example_plan": example_plan,
        "selected": None,
    }
    st.session_state.messages.append(comparison_msg)

    # Renderizar la comparación
    with st.chat_message("assistant"):
        render_comparison(comparison_msg, len(st.session_state.messages) - 1)