import streamlit as st
from pathlib import Path

from config import UPLOAD_PATH
from rag.indexing import index_pdf
from rag.chain import get_rag_chain, refresh_rag_chain
from rag.retriever import refresh_retriever
from rag.summarizer import summarize_pdf
from rag.quiz import generate_quiz
from rag.notes import generate_notes
from rag.flashcards import generate_flashcards  # Import the new flashcards function

# ----------------------------------
# Page Configuration (FIRST Streamlit command)
# ----------------------------------

st.set_page_config(
    page_title="AI PDF Assistant",
    page_icon="🤖",
    layout="wide"
)

UPLOAD_PATH.mkdir(exist_ok=True)

# ----------------------------------
# Initialize Session State
# ----------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "rag_chain" not in st.session_state:
    try:
        st.session_state.rag_chain = get_rag_chain()
    except Exception:
        st.session_state.rag_chain = None

if "summary" not in st.session_state:
    st.session_state.summary = None

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if "notes" not in st.session_state:
    st.session_state.notes = None

if "flashcards" not in st.session_state:
    st.session_state.flashcards = None



# ----------------------------------
# Sidebar
# ----------------------------------

with st.sidebar:

    st.header("📂 Document")

    # Support multiple uploads
    uploaded_files = st.file_uploader(
        "Upload PDF(s)",
        type=["pdf"],
        accept_multiple_files=True
    )

    if st.button("📚 Index PDF", use_container_width=True):
        if not uploaded_files:
            st.warning("Please upload at least one PDF.")
        else:
            try:
                with st.spinner("Indexing PDFs..."):
                    indexed = []
                    for uploaded_file in uploaded_files:
                        pdf_path = UPLOAD_PATH / uploaded_file.name
                        with open(pdf_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        index_pdf(pdf_path)
                        indexed.append(uploaded_file.name)
                    
                    # Refresh only once after all are indexed
                    refresh_retriever()
                    refresh_rag_chain()
                    st.session_state.rag_chain = get_rag_chain()
                    
                st.success(f"✅ Successfully indexed {len(indexed)} PDF(s).")
                st.markdown("### Indexed Documents")
                for pdf in indexed:
                    st.write(f"• {pdf}")
                st.divider()
            except Exception as e:
                st.error(e)

    # ----------------------------------
    # PDF Summary
    # ----------------------------------

    st.divider()
    st.subheader("📄 PDF Summary")

    available_pdfs = sorted(
        [pdf.name for pdf in UPLOAD_PATH.glob("*.pdf")]
    )

    if available_pdfs:
        selected_summary_pdf = st.selectbox(
            "Choose a PDF",
            available_pdfs,
            key="summary_pdf"
        )

        if st.button("📝 Generate Executive Summary", use_container_width=True):
            pdf_path = UPLOAD_PATH / selected_summary_pdf
            try:
                with st.spinner("Generating summary..."):
                    st.session_state.summary = summarize_pdf(str(pdf_path))
            except Exception as e:
                st.error(f"Summary generation failed:\n\n{e}")
    else:
        st.info("Index at least one PDF to enable summarization.")

    # ----------------------------------
    # Smart Notes Generator
    # ----------------------------------
    
    st.divider()
    st.subheader("📝 Smart Notes")

    if available_pdfs:
        selected_notes_pdf = st.selectbox(
            "Select PDF",
            available_pdfs,
            key="notes_pdf_select"
        )

        if st.button("Generate Notes", use_container_width=True):
            try:
                with st.spinner("Generating Notes..."):
                    pdf_path = UPLOAD_PATH / selected_notes_pdf
                    st.session_state.notes = generate_notes(str(pdf_path))
            except Exception as e:
                st.error(e)
    else:
        st.info("Upload a PDF first.")

    # ----------------------------------
    # Quiz Generator
    # ----------------------------------

    st.divider()
    st.subheader("❓ Quiz Generator")

    if available_pdfs:
        selected_quiz_pdf = st.selectbox(
            "Select PDF",
            available_pdfs,
            key="quiz_pdf"
        )

        num_questions = st.slider(
            "Number of Questions",
            min_value=5,
            max_value=20,
            value=10
        )

        if st.button("Generate Quiz", use_container_width=True):
            try:
                with st.spinner("Generating Quiz..."):
                    pdf_path = UPLOAD_PATH / selected_quiz_pdf
                    st.session_state.quiz = generate_quiz(pdf_path, num_questions)
            except Exception as e:
                st.error(e)
    else:
        st.info("Upload and index a PDF first.")

    # ----------------------------------
    # Flashcards Generator
    # ----------------------------------
    
    st.divider()
    st.subheader("🧠 Flashcards")

    if available_pdfs:
        selected_flashcard_pdf = st.selectbox(
            "Select PDF",
            available_pdfs,
            key="flashcard_pdf_select"
        )
        
        num_cards = st.slider(
            "Number of Flashcards",
            min_value=5,
            max_value=20,
            value=10
        )

        if st.button("Generate Flashcards", use_container_width=True):
            try:
                with st.spinner("Generating Flashcards..."):
                    pdf_path = UPLOAD_PATH / selected_flashcard_pdf
                    # Make sure your generate_flashcards function accepts both pdf_path and num_cards!
                    st.session_state.flashcards = generate_flashcards(str(pdf_path), num_cards)
            except Exception as e:
                st.error(e)
    else:
        st.info("Upload a PDF first.")

# ----------------------------------
# Main UI - Tabs
# ----------------------------------

st.title("🤖 AI PDF Assistant")
st.caption("Ask questions, generate summaries, notes, quizzes, and flashcards from your uploaded PDFs.")

# Create the Tabs (Now with Flashcards!)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 Chat", "📄 Summary", "📝 Notes", "❓ Quiz", "🧠 Flashcards"])

# ----------------------------------
# Tab 1: Chat History & Input
# ----------------------------------
with tab1:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask a question about your uploaded PDFs...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if st.session_state.rag_chain is None:
                answer = "❌ No indexed PDF found. Please upload and index a PDF."
                st.error(answer)
            else:
                try:
                    with st.spinner("Searching document..."):
                        stream, docs = st.session_state.rag_chain.stream(
                            prompt,
                            st.session_state.messages
                        )

                    # Write the stream to the UI
                    answer = st.write_stream(
                        chunk.content for chunk in stream if chunk.content
                    )

                    if docs:
                        st.divider()
                        # Extract unique document names and page numbers
                        sources = sorted(
                            {
                                (doc.metadata.get("source", "Unknown"), doc.metadata.get("page", 0) + 1)
                                for doc in docs
                            }
                        )

                        st.markdown("### 📄 Sources")
                        for source, page in sources:
                            st.write(f"**{source}** — Page {page}")

                except Exception as e:
                    answer = f"❌ {e}"
                    st.error(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})

# ----------------------------------
# Tab 2: Summary
# ----------------------------------
with tab2:
    if st.session_state.summary:
        st.header("📄 Executive Summary")
        st.markdown(st.session_state.summary)
    else:
        st.info("Generate a summary from the sidebar to view it here.")

# ----------------------------------
# Tab 3: Smart Notes
# ----------------------------------
with tab3:
    if st.session_state.notes:
        st.header("📝 Smart Notes")
        st.markdown(st.session_state.notes)
    else:
        st.info("Generate notes from the sidebar to view them here.")

# ----------------------------------
# Tab 4: Interactive Quiz
# ----------------------------------
with tab4:
    if st.session_state.quiz:
        st.header("❓ Interactive Quiz")
        user_answers = []

        # Assuming quiz is a list of dictionaries with 'question', 'options', 'answer', and 'explanation'
        if isinstance(st.session_state.quiz, list):
            for i, q in enumerate(st.session_state.quiz):
                st.subheader(f"Question {i+1}")
                answer = st.radio(
                    q["question"],
                    q["options"],
                    key=f"quiz_radio_{i}"
                )
                user_answers.append(answer)

            if st.button("✅ Submit Quiz"):
                score = 0
                st.divider()
                st.header("📊 Results")

                for i, q in enumerate(st.session_state.quiz):
                    correct = q["options"][q["answer"]]

                    if user_answers[i] == correct:
                        score += 1
                        st.success(f"Question {i+1}: Correct ✅")
                    else:
                        st.error(f"Question {i+1}: Incorrect ❌")

                    st.write(f"**Correct Answer:** {correct}")
                    st.write(f"**Explanation:** {q['explanation']}")
                    st.divider()

                st.success(f"🎉 Final Score: {score}/{len(st.session_state.quiz)}")
        else:
            # Fallback if the LLM didn't return a JSON list
            st.markdown(st.session_state.quiz)
    else:
        st.info("Generate a quiz from the sidebar to view it here.")

# ----------------------------------
# Tab 5: Flashcards
# ----------------------------------
with tab5:
    if st.session_state.flashcards:
        st.header("🧠 Flashcards")
        st.caption("Click on a question to reveal the answer!")
        
        # Check if the flashcards were returned as a structured list of JSON dicts
        if isinstance(st.session_state.flashcards, list):
            for i, card in enumerate(st.session_state.flashcards):
                # The expander acts as the "front" of the card
                with st.expander(f"**Flashcard {i+1}:** {card.get('front', card.get('question', 'Question'))}"):
                    # The content inside acts as the "back" of the card
                    st.markdown(f"{card.get('back', card.get('answer', 'Answer'))}")
        else:
            # Fallback if the LLM returned standard markdown text
            st.markdown(st.session_state.flashcards)
    else:
        st.info("Generate flashcards from the sidebar to view them here.")