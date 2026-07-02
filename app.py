import streamlit as st
import requests

st.set_page_config(page_title="EduBot", page_icon="📚", layout="wide")

FASTAPI_BASE_URL = "http://127.0.0.1:8000"


# session state to remember what is currently active
if "source_type" not in st.session_state:
    st.session_state.source_type = None   # "pdf" or "youtube"
if "source_name" not in st.session_state:
    st.session_state.source_name = None   # filename or url/id
if "last_question" not in st.session_state:
    st.session_state.last_question = None
if "last_answer" not in st.session_state:
    st.session_state.last_answer = None


st.title("🤖 EduBot")


with st.sidebar:
    st.header("Add a source")

    st.subheader("🎥 YouTube video")
    yt_input = st.text_input("Video URL or ID", key="yt_input")
    if st.button("Process video", use_container_width=True):
        if yt_input.strip():
            with st.spinner("Fetching transcript and indexing..."):
                try:
                    response = requests.post(
                        f"{FASTAPI_BASE_URL}/upload/youtube",
                        json={"url": yt_input.strip()}
                    )

                    if response.status_code == 200:
                        st.session_state.source_type = "youtube"
                        st.session_state.source_name = yt_input.strip()
                        st.session_state.last_question = None
                        st.session_state.last_answer = None
                        st.success(response.json().get("message"))
                    else:
                        st.error(f"Backend Error: {response.json().get('detail')}")
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the FastAPI server. Is it running?")
        else:
            st.warning("Enter a video URL or ID first.")

    st.divider()

    st.subheader("📖 Book (PDF)")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    if st.button("Process book", use_container_width=True):
        if uploaded_file is not None:
            with st.spinner("Processing..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    response = requests.post(
                        f"{FASTAPI_BASE_URL}/upload/pdf",
                        files=files
                    )

                    if response.status_code == 200:
                        st.session_state.source_type = "pdf"
                        st.session_state.source_name = uploaded_file.name
                        st.session_state.last_question = None
                        st.session_state.last_answer = None
                        st.success(response.json().get("message"))
                    else:
                        st.error(f"Backend Error: {response.json().get('detail')}")
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the FastAPI server. Is it running?")
        else:
            st.warning("Upload a PDF first.")


# main area
if st.session_state.source_type is None:
    st.info("Add a YouTube video or upload a PDF from the sidebar to start.")
    st.stop()

if st.session_state.source_type == "pdf":
    st.caption(f"📖 Currently working with PDF: `{st.session_state.source_name}`")
else:
    st.caption(f"🎥 Currently working with YouTube video: `{st.session_state.source_name}`")


question = st.chat_input("Ask a question about this source...")
if question:
    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                f"{FASTAPI_BASE_URL}/chat",
                json={"question": question}
            )

            if response.status_code == 200:
                st.session_state.last_question = question
                st.session_state.last_answer = response.json().get("answer")
            else:
                st.error(f"Backend Error: {response.json().get('detail')}")
        except requests.exceptions.ConnectionError:
            st.error("Lost connection to the FastAPI server.")


if st.session_state.last_question:
    with st.chat_message("user"):
        st.write(st.session_state.last_question)
    with st.chat_message("assistant"):
        st.write(st.session_state.last_answer)