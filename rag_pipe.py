from langchain_community.document_loaders import PyPDFLoader
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv


load_dotenv()


# pdf loader
def load_pdf(file_path):
    loader = PyPDFLoader(file_path)
    pages = loader.load()

    return pages


# pulls the 11-character video id out of a full url, or returns it unchanged
def get_video_id(url_or_id):
    url_or_id = url_or_id.strip()

    if "v=" in url_or_id:
        after_v = url_or_id.split("v=")[1]
        video_id = after_v.split("&")[0]
        return video_id

    if "youtu.be/" in url_or_id:
        video_id = url_or_id.split("youtu.be/")[1]
        video_id = video_id.split("?")[0]
        return video_id

    return url_or_id


# youtube loader
def load_youtube(video_id):
    api = YouTubeTranscriptApi()

    try:
        transcript = api.fetch(video_id, languages=["en"])
    except TranscriptsDisabled:
        raise Exception("Captions are disabled for this video.")

    full_text = ""
    for snippet in transcript:
        full_text = full_text + snippet.text + " "

    document = Document(
        page_content=full_text,
        metadata={"source": "youtube", "video_id": video_id}
    )

    return [document]


# chunking
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(documents)

    return chunks


# embeddings
def create_embeddings():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return embeddings


# vector store
def create_vector_store(chunks, embeddings):
    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    return vector_store


# retriever
def similarity_search(vector_store, question):
    documents = vector_store.similarity_search(
        query=question,
        k=4
    )

    return documents


# full pipeline for a pdf upload
def process_pdf(file_path):
    pages = load_pdf(file_path)
    chunks = split_documents(pages)
    embeddings = create_embeddings()
    vector_store = create_vector_store(chunks, embeddings)

    return vector_store


# full pipeline for a youtube video
def process_youtube(url_or_id):
    video_id = get_video_id(url_or_id)
    documents = load_youtube(video_id)
    chunks = split_documents(documents)
    embeddings = create_embeddings()
    vector_store = create_vector_store(chunks, embeddings)

    return vector_store