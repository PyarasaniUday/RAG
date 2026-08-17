try:
    # pyrefly: ignore [missing-import]
    from langchain.prompts import PromptTemplate
except ImportError:
    from langchain_core.prompts import PromptTemplate

# Prompt Template String
RAG_PROMPT_TEMPLATE = """You are Tech Fusion, a technical document assistant.

Answer the user's question using ONLY the provided context.

If the answer cannot be found in the context, say:
'I could not find this information in the provided documents.'

Do not hallucinate or invent information.

Context:
{context}

Question:
{question}

Answer:"""

def get_rag_prompt_template() -> PromptTemplate:
    """Returns the LangChain PromptTemplate instance for RAG."""
    return PromptTemplate(
        input_variables=["context", "question"],
        template=RAG_PROMPT_TEMPLATE
    )

def format_rag_prompt(context: str, question: str) -> str:
    """Formats the RAG prompt with the given context and question."""
    return RAG_PROMPT_TEMPLATE.format(context=context, question=question)
