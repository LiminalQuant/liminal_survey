import streamlit as st
import json
import matplotlib.pyplot as plt
import pandas as pd
import ast
import hashlib
from .storage import save_response, load_data


# ==========================
# 🔒 Проверка пароля
# ==========================
def check_password():
    def make_hash(password):
        return hashlib.sha256(password.encode()).hexdigest()

    correct_hash = make_hash(st.secrets["password"])
    password = st.text_input("Введите пароль для доступа к аналитике", type="password")

    if make_hash(password) == correct_hash:
        st.session_state["authenticated"] = True
        st.success("✅ Доступ разрешён")
        st.rerun()
    elif password:
        st.error("⛔ Неверный пароль")


# ==========================
# 🧩 Генерация формы по JSON-конфигу
# ==========================
def render_form(config_path):
    import json
    from .storage import save_response

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    st.title(config["title"])
    st.markdown(config.get("description", ""))

    # --- форма ---
    with st.form("survey_form"):
        answers = {}

        # 1️⃣ Основной вопрос: Да / Нет
        main_q = next((q for q in config["questions"] if q["key"] == "answer"), None)
        if main_q:
            answers["answer"] = st.radio(main_q["label"], main_q["options"], horizontal=True)

        # 2️⃣ Показать слайдер только если ответ "Да"
        amount_q = next((q for q in config["questions"] if q["key"] == "amount"), None)
        if amount_q and answers.get("answer") == "Да":
            answers["amount"] = st.slider(
                amount_q["label"],
                amount_q["min"],
                amount_q["max"],
                amount_q.get("default", amount_q["min"]),
                step=amount_q["step"],
            )

        # 3️⃣ Отправка
        submitted = st.form_submit_button("Отправить")
        if submitted:
            # если ответ "Нет" — удаляем ключ amount
            if answers.get("answer") == "Нет" and "amount" in answers:
                del answers["amount"]

            save_response(config["survey_id"], answers)
            st.success("✅ Ответ записан. Всё анонимно.")




# ==========================
# 📊 Аналитика
# ==========================
def render_dashboard(survey_id):
    # Проверка авторизации
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        check_password()
        st.stop()

    # --- Загружаем данные ---
    df = load_data()
    if df.empty:
        st.info("Нет данных")
        return

    df = df[df["survey_id"] == survey_id]
    if df.empty:
        st.info("Нет данных для этого опроса")
        return

    # Преобразуем строку в словарь
    df["answers"] = df["answers"].apply(ast.literal_eval)
    df = pd.json_normalize(df["answers"])

    st.subheader("📊 Аналитика ответов")
    plt.style.use("dark_background")

    # --- Если есть поле answer ---
    if "answer" in df.columns:
        yes = (df["answer"] == "Да").sum()
        no = (df["answer"] == "Нет").sum()

        fig1, ax1 = plt.subplots(figsize=(4, 4), dpi=150)
        ax1.pie(
            [yes, no],
            labels=[f"Да ({yes})", f"Нет ({no})"],
            colors=["#FFD700", "#333"],
            autopct=lambda p: f"{p:.1f}%" if p > 0 else "",
            textprops={"color": "#DDDDDD", "fontsize": 9},
        )
        ax1.set_title("Распределение ответов", color="#FFD700", fontsize=12, pad=12)
        st.pyplot(fig1, use_container_width=True)

    # --- Если есть поле amount ---
    if "amount" in df.columns and df["amount"].any():
        fig2, ax2 = plt.subplots(figsize=(6, 3.5), dpi=150)
        ax2.hist(df["amount"], bins=10, color="#FFD700", alpha=0.8, edgecolor="#222222")
        ax2.set_facecolor("#0A0A0A")
        ax2.set_title("Распределение трат", color="#FFD700", fontsize=12)
        ax2.set_xlabel("Сумма, ₽", color="#CCCCCC", fontsize=9)
        ax2.set_ylabel("Количество", color="#CCCCCC", fontsize=9)
        ax2.grid(True, linestyle="--", alpha=0.3, color="#333")
        for spine in ax2.spines.values():
            spine.set_color("#333")
        ax2.tick_params(colors="#AAAAAA", labelsize=8)
        st.pyplot(fig2, use_container_width=True)

        mean_amount = df["amount"].mean()
        median_amount = df["amount"].median()
        st.markdown(
            f"**💰 Средняя сумма:** {mean_amount:,.0f} ₽  |  **Медиана:** {median_amount:,.0f} ₽"
        )
