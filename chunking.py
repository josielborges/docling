from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv
from utils.tokenizer_utils import OpenAITokenizerWrapper

load_dotenv()

tokenizer = OpenAITokenizerWrapper()
MAX_TOKENS = 8191

# Extacting the data
converter = DocumentConverter()
result = converter.convert("data/file.pdf")

# Applying Hybrid Chunker (see more at https://docling-project.github.io/docling/examples/hybrid_chunking/)
chunker = HybridChunker(
    tokenizer=tokenizer,
    max_tokens=MAX_TOKENS,
    merge_peers=True, # to join small chunks
)

chunk_iter = chunker.chunk(dl_doc=result.document)
chunks = list(chunk_iter)

for chunk in chunks:
    print("")
    print(chunk)