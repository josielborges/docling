import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import lancedb
import os

load_dotenv()

OPENAI_MODEL = "gpt-4o-mini"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI()


@st.cache_resource
def init_db():
    db = lancedb.connect("data/lance_db")
    return db.open_table("docling")

def get_context(query: str, table, num_results: int = 5) -> str:
    results = table.search(query=query).limit(num_results).to_pandas()
    
    contexts = []

    for _, row in results.iterrows():
        filename = row["metadata"]["filename"]
        page_numbers = row["metadata"]["page_numbers"]
        title = row["metadata"]["title"]

        source_parts = []
        if filename:
            source_parts.append(filename)
        
        if page_numbers.size > 0:
            source_parts.append(f"p. {', '.join(str(p) for p in page_numbers)}")

        source = f"\nSource: {' - '.join(source_parts)}"

        if title:
            source += f"\nTitle: {title}"

        contexts.append(f"{row['text']}{source}")

    return contexts

def get_chat_response(messages, context: str) -> str:
    system_prompt = f"""
    You are a helpful assistant that answers question based on the provide context.
    Use only the information from the context to answer the question. If you don't know the answer, just say that you don't know, don't try to make up an answer.
    
    Context:
    {context}
    """

    message_with_context = [
        {
            "role": "system",
            "content": system_prompt,        
        },
        *messages
    ]

    stream = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=message_with_context,
        stream=True,
        temperature=0.7
    )

    response = st.write_stream(stream=stream)
    
    return response


# Streamlit app
st.title("Document Q&A")

if "messages" not in st.session_state:
    st.session_state.messages = []

db = init_db()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Ask a question about the documents?"):
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.status("Generating response...", expanded=False) as status:
        contexts = get_context(prompt, db)
        st.markdown(
            """
                <style>
                .search-result {
                    margin: 10px 0;
                    padding: 10px;
                    border-radius: 4px;
                    background-color: #f0f2f6;
                }
                .search-result summary {
                    cursor: pointer;
                    color: #0f52ba;
                    font-weight: 500;
                }
                .search-result summary:hover {
                    color: #1e90ff;
                }
                .metadata {
                    font-size: 0.9em;
                    color: #666;
                    font-style: italic;
                }
                </style>
            """,
                unsafe_allow_html=True,
            )
        
        st.write("Found relevant documents:")
        for chunk in contexts:

            parts = chunk.split("\n")
            text = parts[0]
            metadata = {
                line.split(": ")[0]: line.split(": ")[1]
                for line in parts[1:]
                if ": " in line
            }

            source = metadata.get("Source", "Unknown source")
            title = metadata.get("Title", "Unknown section")

            st.markdown(
                f"""
                    <div class="search-result">
                        <details>
                            <summary>{source}</summary>
                            <div class="metadata">Section: {title}</div>
                            <div style="margin-top: 8px;">{chunk}</div>
                        </details>
                    </div>
                """,
                unsafe_allow_html=True,
            )

    with st.chat_message("assistant"):
        response = get_chat_response(st.session_state.messages, '\n\n'.join(contexts))

    st.session_state.messages.append({"role": "assistant", "content": response})