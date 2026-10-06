import streamlit as st
from agent import ask_agent

st.set_page_config(
    page_title="Text-to-SQL Agent",
    page_icon="🧠",
    layout="wide",
)

st.title("Text-to-SQL Agent")
st.caption("Ask business questions about the Superstore orders data.")

question = st.text_input(
    "Enter your question",
    placeholder="Ask a question about the Superstore orders data...",
)

run_clicked = st.button("Run", type="primary")

if run_clicked:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking and querying the database...", show_time=True):
            response = ask_agent(question)

        if response["error"] is not None:
            st.error(response["answer"])
        else:
            st.success("Query completed successfully.")
            st.subheader("Answer")
            st.write(response["answer"])

            st.subheader("Result")
            st.dataframe(response["result"], use_container_width=True)

            with st.expander("Generated SQL"):
                st.code(response["generated_sql"], language="sql")

            with st.expander("Validated SQL"):
                st.code(response["safe_sql"], language="sql")