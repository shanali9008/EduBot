from fastapi import FastAPI, UploadFile, File, HTTPException, status
from pydantic import BaseModel
import shutil
import os

from rag_pipe import process_pdf, process_youtube
from llm import generate_answer


app = FastAPI()

# single global vector store -- only one source (pdf or youtube) is active at a time
vector_store = None


class YouTubeRequest(BaseModel):
    url: str


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "EduBot API is Running"}


# Upload PDF
@app.post("/upload/pdf")
def upload_pdf(file: UploadFile = File(...)):

    global vector_store

    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF files are allowed."
        )

    file_path = file.filename

    try:
        with open(file_path, "wb") as pdf_file:
            shutil.copyfileobj(file.file, pdf_file)

        vector_store = process_pdf(file_path)

        return {"message": "PDF processed successfully."}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process PDF: {str(e)}"
        )

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


# Upload YouTube
@app.post("/upload/youtube")
def upload_youtube(data: YouTubeRequest):

    global vector_store

    if not data.url.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="YouTube URL or video ID cannot be empty."
        )

    try:
        vector_store = process_youtube(data.url)
        return {"message": "YouTube video processed successfully."}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process YouTube video. Ensure the URL is correct and captions are available. Error: {str(e)}"
        )


# Chat
@app.post("/chat")
def chat(data: ChatRequest):

    global vector_store

    if vector_store is None:
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF or YouTube video first."
        )

    answer = generate_answer(
        question=data.question,
        vector_store=vector_store
    )

    return {
        "answer": answer
    }