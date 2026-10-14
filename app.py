
import io
import streamlit as st
from pypdf import PdfReader
from google import genai

st.set_page_config(
    page_title="KnowMate AI",
    page_icon="📚",
    layout="centered",
)

st.title("📚 KnowMate AI")
st.write("Upload a PDF or TXT document and ask questions about it.")

MODEL = "gemini-3.5-flash-lite"


@st.cache_data
def extract_document(file_bytes, filename):
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))
        return [
            (page.extract_text() or "", i + 1)
            for i, page in enumerate(reader.pages)
        ]

    text = file_bytes.decode("utf-8", errors="ignore")
    return [(text, 1)]



def find_relevant_text(pages, question, limit=4, extra_context=""):
    import re
    import math
    from collections import Counter

    stop_words = {
        "the", "and", "for", "that", "this", "with", "what",
        "when", "where", "which", "who", "how", "does", "are",
        "was", "were", "can", "could", "would", "should", "about",
        "from", "into", "have", "has", "its", "their", "there",
        "please", "explain", "tell", "me", "you", "your",
        "is", "are", "did", "do", "it", "he", "she", "they"
    }

    def tokenize(text):
        tokens = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
        return [
            token for token in tokens
            if len(token) > 1 and token not in stop_words
        ]

    query = tokenize(question + " " + extra_context)
    if not query:
        query = tokenize(question)

    query_counts = Counter(query)
    chunks = []
    size = 1200
    overlap = 200

    for text, page_num in pages:
        for start in range(0, max(len(text), 1), size - overlap):
            chunk = text[start:start + size].strip()
            if not chunk:
                continue

            chunk_words = tokenize(chunk)
            counts = Counter(chunk_words)

            overlap_score = sum(
                min(count, counts[word])
                for word, count in query_counts.items()
                if word in counts
            )

            rarity_score = sum(
                math.log(1 + 1 / (1 + counts[word]))
                for word in set(query)
                if word in counts
            )

            score = overlap_score + rarity_score

            if score > 0:
                chunks.append((score, chunk, page_num))

    chunks.sort(key=lambda item: item[0], reverse=True)

    selected = []
    seen = set()

    for item in chunks:
        signature = item[1][:180].lower()
        if signature in seen:
            continue

        seen.add(signature)
        selected.append(item)

        if len(selected) >= limit:
            break

    if selected:
        return selected

    fallback = []
    for text, page_num in pages:
        if text.strip():
            fallback.append((0, text[:size], page_num))
        if len(fallback) >= limit:
            break

    return fallback


with st.sidebar:
    st.header("About KnowMate")
    st.write(
        "An AI document assistant powered by Gemini. "
        "Upload a document, ask questions, and explore its contents."
    )

    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()


uploaded_file = st.file_uploader(
    "Upload your document",
    type=["pdf", "txt"],
)

if uploaded_file is None:
    st.info("Upload a PDF or TXT file to start chatting.")
    st.stop()

try:
    pages = extract_document(
        uploaded_file.getvalue(),
        uploaded_file.name,
    )
except Exception as e:
    st.error(f"Could not read the document: {e}")
    st.stop()

if not any(text.strip() for text, _ in pages):
    st.warning(
        "No readable text found. Scanned PDFs may need OCR."
    )
    st.stop()

st.success(f"Document loaded: {uploaded_file.name}")

doc_id = f"{uploaded_file.name}_{uploaded_file.size}"

if st.session_state.get("doc_id") != doc_id:
    st.session_state.doc_id = doc_id
    st.session_state.messages = []

if "messages" not in st.session_state:
    st.session_state.messages = []

st.subheader("💬 Chat with your document")

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input(
    "Ask a question about your document..."
)

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })

    with st.chat_message("user"):
        st.markdown(question)

    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)

        with st.chat_message("assistant"):
            with st.spinner("Reading the document and thinking..."):
                

                history = st.session_state.messages[-7:-1]

                previous_chat = "\n".join(
                    f'{m["role"]}: {m["content"]}'
                    for m in history
                )

                recent_context = "\n".join(
                    f'{m["role"]}: {m["content"]}'
                    for m in history[-4:]
                )

                relevant = find_relevant_text(
                    pages,
                    question,
                    extra_context=recent_context
                )

                context = "\n\n".join(
                    f"[Page {page_num}]\n{chunk}"
                    for _, chunk, page_num in relevant
                )

                prompt = f"""
You are KnowMate, a document question-answering assistant.

Rules:
- Answer the CURRENT QUESTION, not an earlier question.
- Use the supplied document excerpts as your factual source.
- Use previous chat only to understand follow-up references,
  such as "he", "it", or "what does that mean?"
- Verify factual claims against the document excerpts.
- Never invent facts that are not supported by the document.
- If the answer is missing, say you couldn't find it in the
  provided document excerpts.
- Mention source page numbers when possible.
- Reply in the same language as the user's question.
- Keep answers clear and concise.

PREVIOUS CONVERSATION:
{previous_chat}

DOCUMENT EXCERPTS:
{context}

CURRENT QUESTION:
{question}
"""
                response = client.models.generate_content(
                    model=MODEL,
                    contents=prompt,
                )

                answer = response.text or (
                    "I couldn't generate an answer. Please try again."
                )

                st.markdown(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
        })

    except Exception as e:
        # Keep the failed question out of history so it can be retried
        if (
            st.session_state.messages
            and st.session_state.messages[-1]["role"] == "user"
            and st.session_state.messages[-1]["content"] == question
        ):
            st.session_state.messages.pop()

        st.error(f"Could not generate the answer: {e}")
