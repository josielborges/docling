import lancedb

uri = "data/lance_db"
db  = lancedb.connect(uri)

table = db.open_table("docling")

result = table.search(query="oi", query_type="vector").limit(5)
print(result.to_pandas())
print(result.to_pandas().loc[0, "metadata"])