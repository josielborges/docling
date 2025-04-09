from docling.document_converter import DocumentConverter
from utils.sitemap_utils import parse_sitemap

converter = DocumentConverter()

# Converting document
result = converter.convert("data/pdf_file.pdf")

document = result.document
markdown_output = document.export_to_markdown()
json_output = document.export_to_dict()

print(markdown_output)

with open("data/document_markdown_output.md", "w") as f:
    f.write(markdown_output)


# Converting a web page
result = converter.convert("https://docling-project.github.io/docling/")

document = result.document
markdown_output = document.export_to_markdown()

print(markdown_output)

with open("data/web_page_markdown_output.md", "w") as f:
    f.write(markdown_output)


#Converting multiple web pages
sitemap_urls = parse_sitemap("https://docling-project.github.io/docling/sitemap.xml")
results = converter.convert_all(sitemap_urls)

documents = []
for result in results:
    if result.document:
        documents.append(result.document)
        markdown_output = result.document.export_to_markdown()
        print(markdown_output)  

        with open("data/multiple_web_pages_markdown_output.md", "a") as f:
            f.write(markdown_output)