from indexer import index_repo, search_codebase

result = index_repo("https://github.com/tiangolo/full-stack-fastapi-template")
print(result)

matches = search_codebase("where is authentication handled")
for m in matches:
    print(m["metadata"]["file_path"], m["metadata"]["name"])