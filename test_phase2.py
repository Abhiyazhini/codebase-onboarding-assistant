from ast_parser import parse_python_file
from git_extractor import get_python_files

# 1. Get all Python files in the cloned repository
files = get_python_files("cloned_repo")
print(f"Total Python files found: {len(files)}")

# 2. Find the first file that actually contains functions or classes
selected_file = None
chunks = []

for f in files:
    extracted = parse_python_file(f)
    if len(extracted) > 0:
        selected_file = f
        chunks = extracted
        break

# 3. Print the results
if selected_file:
    print("\n" + "=" * 60)
    print(f"📄 TESTED FILE: {selected_file}")
    print(f"🧩 CHUNKS FOUND: {len(chunks)}")
    print("=" * 60)

    # Print the first extracted AST chunk
    first_chunk = chunks[0]
    print(f"\n✅ First Chunk Extracted: [{first_chunk['type']}] {first_chunk['name']}")
    print(f"📍 Lines: {first_chunk['start_line']} - {first_chunk['end_line']}")
    print("-" * 60)
    print(first_chunk["code"])
    print("-" * 60)
else:
    print("No functions or classes found in any of the files.")