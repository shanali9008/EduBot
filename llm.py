from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from rag_pipe import similarity_search


def create_llm():
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0
    )

    return llm


prompt = PromptTemplate(
    template="""
      You are a helpful assistant.
      Answer ONLY from the provided context.
      If the context is insufficient, just say you don't know.

      {context}
      Question: {question}
    """,
    input_variables=['context', 'question']
)


output_parser = StrOutputParser()

llm = create_llm()

rag_chain = prompt | llm | output_parser


def generate_answer(question, vector_store):
    documents = similarity_search(vector_store, question)

    context = ""
    for document in documents:
        context = context + document.page_content
        context = context + "\n\n"

    answer = rag_chain.invoke({
        "context": context,
        "question": question
    })

    return answer