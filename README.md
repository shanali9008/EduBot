# EduBot 📚🤖

Ask questions about a PDF book or a YouTube video, and get answers based only on that content.

You upload a PDF or paste a YouTube link, EduBot reads it, and then you can
ask it questions in plain English. It only answers from what's actually in
the source — if the answer isn't there, it says so instead of guessing.

## How it works

There are two parts:

- A **FastAPI backend** (`api.py`) that does the heavy lifting — reading the
  PDF or fetching the YouTube transcript, breaking it into chunks, and
  turning those chunks into embeddings so they can be searched.
- A **Streamlit frontend** (`app.py`) — a simple web page where you upload
  files, paste links, and chat.

The backend keeps one source "active" at a time. Upload a new PDF or video
and it replaces whatever was there before. There's no memory of past
questions yet — every question is answered fresh, based only on the current
source.

## Project structure

```
.
├── api.py            # FastAPI backend — upload & chat endpoints
├── app.py             # Streamlit frontend
├── rag_pipeline.py    # Loading, chunking, embeddings, vector search
├── llm.py             # Prompt + Groq LLM call
└── requirements.txt
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root with your Groq API key:
   ```
   GROQ_API_KEY=your_key_here
   ```
   Get one for free at [console.groq.com](https://console.groq.com).

3. Start the backend:
   ```bash
   uvicorn api:app --reload
   ```
   This runs on `http://127.0.0.1:8000` by default.

4. In a separate terminal, start the frontend:
   ```bash
   streamlit run app.py
   ```

Both need to be running at the same time — the Streamlit app just talks to
the FastAPI server, it doesn't do any of the processing itself.

## Using it

1. Open the Streamlit app in your browser.
2. In the sidebar, either:
   - Paste a YouTube URL (or just the video ID), or
   - Upload a PDF.
3. Wait for the "processed successfully" message.
4. Ask a question in the chat box at the bottom.

Only one source is active at a time — uploading something new replaces
whatever you were working with before.

## Known limitations (for now)

- **No chat memory.** Every question is independent. Follow-ups like "what
  about the second part?" won't know what "the second part" refers to.
- **No source switching.** You can't keep two sources loaded and flip
  between them — it's always just the most recently uploaded one.
- **YouTube fetching can get blocked.** YouTube sometimes blocks transcript
  requests coming from cloud servers or data-center IPs. If you're running
  this on a cloud VM and YouTube uploads fail, try running it from a normal
  home internet connection instead, or look into the proxy support in
  [`youtube-transcript-api`](https://github.com/jdepoix/youtube-transcript-api)
  if you plan to deploy this somewhere.
- **Books aren't split by chapter.** PDFs are chunked in fixed-size blocks,
  not by chapter or topic — that's a possible future improvement.

## What might come later

- Chat memory, so follow-up questions actually work
- Ability to keep multiple sources loaded and switch between them
- Chapter/topic-aware splitting for books instead of fixed-size chunks
- Proxy support for more reliable YouTube fetching

## Requirements

- Python 3.10+
- A [Groq API key](https://console.groq.com) (free tier available)
