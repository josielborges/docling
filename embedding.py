from typing import List

import lancedb
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector

from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv
from openai import OpenAI
from utils.tokenizer_utils import OpenAITokenizerWrapper

import lancedb

load_dotenv()

client = OpenAI()

tokenizer = OpenAITokenizerWrapper()
MAX_TOKENS = 8191
EMBEDDING_MODEL = "text-embedding-3-large"

# Extacting the data
converter = DocumentConverter()
result = converter.convert("data/file.docx")

# Applying Hybrid Chunker (see more at https://docling-project.github.io/docling/examples/hybrid_chunking/)
chunker = HybridChunker(
    tokenizer=tokenizer,
    max_tokens=MAX_TOKENS,
    merge_peers=True, # to join small chunks
)

chunk_iter = chunker.chunk(dl_doc=result.document)
chunks = list(chunk_iter)

# creating the database
db = lancedb.connect("data/lance_db")

func = get_registry().get("openai").create(name=EMBEDDING_MODEL)

# Schemas
class ChunkMetadata(LanceModel):
    """
    You must order the fields in alphabetical order.
    This is a requirement of the Pydantic implementation.
    """
    filename: str | None
    page_numbers: List[int] | None
    title: str | None

class Chunks(LanceModel):
    text: str = func.SourceField()
    vector: Vector(func.ndims()) = func.VectorField()
    metadata: ChunkMetadata

table = db.create_table("docling", schema=Chunks, mode="overwrite")

# Preparing chunks for the database

processed_chunks = [
    {
        "text": chunk.text,
        "metadata": {
            "filename": chunk.meta.origin.filename,
            "page_numbers": [
                page_no
                for page_no in sorted(set(
                    prov.page_no
                    for item in chunk.meta.doc_items
                    for prov in item.prov
                ))
            ] or [],
            "title": chunk.meta.headings[0] if chunk.meta.headings else "",
        },

    }
    for chunk in chunks
]

print(table.to_pandas())

# Add the chunks to the table (automatically embeds the text)
table.add(processed_chunks)

# Load the table
print(table.to_pandas())
print(table.count_rows())