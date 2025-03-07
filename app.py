import streamlit as st
import requests

# ✅ Streamlit UI Config
st.set_page_config(page_title="AI-Powered SQL Query Interface", layout="wide")

st.title("🔍 RAMP GPT")
st.markdown("### Enter your question below to get instant answers!")

# ✅ Role Selection Dropdown
st.sidebar.markdown("## 👤 Select Your Role")
role = st.sidebar.selectbox("Choose your role:", ["Admin", "Owner", "Customer"])

# ✅ User ID Selection (Manual for Now)
st.sidebar.markdown("## 🔑 Enter Your User ID")
user_id = st.sidebar.number_input("User ID", min_value=1, step=1)

# ✅ Input field for natural language query
question = st.text_input("💬 Ask a Question:", placeholder="e.g., How many services are available?")

# ✅ Button to submit query
if st.button("🔍 Get Answer"):
    if question.strip() == "":
        st.warning("⚠️ Please enter a question.")
    elif not user_id:
        st.warning("⚠️ Please enter a valid User ID.")
    else:
        st.info("⏳ Generating query and fetching results...")

        # ✅ Send request to FastAPI with selected role and user ID
        api_url = "http://127.0.0.1:8000/ask_question"
        payload = {"user_id": user_id, "role": role, "question": question}

        try:
            response = requests.post(api_url, json=payload)

            if response.status_code == 200:
                data = response.json()

                # ✅ Extract query results & execution time
                query_result = data.get("query_result", {})
                raw_answer = query_result.get("raw_answer", "No raw answer received.")
                human_readable_answer = query_result.get("human_readable", "No human-readable answer available.")
                sql_error = data.get("sql_error", False)
                execution_time = data.get("execution_time", 0)  # ✅ Get execution time

                if sql_error:
                    st.error(f"❌ Error: {human_readable_answer}")
                else:
                    st.success("✅ Answer Retrieved!")

                    # ✅ Display human-readable answer first
                    st.markdown(f"**🔹 Answer:** {human_readable_answer}")

                    # ✅ Display query execution time
                    st.markdown(f"⏱ **Query Execution Time:** {execution_time} seconds")

                    # ✅ Show raw SQL results in a structured format if available
                    if isinstance(raw_answer, list) and raw_answer:
                        st.markdown("### 📝 Raw SQL Query Results:")
                        st.write(raw_answer)

            else:
                st.error(f"❌ API Error: {response.text}")

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Network Error: {e}")

# ✅ Footer
st.markdown("---")
st.markdown("🤖 Powered by RAMP AI")
