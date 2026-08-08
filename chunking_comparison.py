from ast_parser import parse_python_file
from git_extractor import get_python_files

def naive_chunk(file_path: str, chunk_size: int = 300):
    """The 'wrong' way most RAG tutorials do it — blind character splitting."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    chunks = []
    for i in range(0, len(code), chunk_size):
        chunks.append(code[i:i + chunk_size])
    return chunks

def find_demo_file(files, min_functions=3):
    """Finds a file with enough functions to make a good demo comparison."""
    for f in files:
        chunks = parse_python_file(f)
        if len(chunks) >= min_functions:
            return f, chunks
    return None, []

if __name__ == "__main__":
    files = get_python_files("cloned_repo")
    demo_file, ast_chunks = find_demo_file(files)

    if not demo_file:
        print("No file with enough functions found — try a bigger repo")
        exit()

    naive_chunks = naive_chunk(demo_file)

    print("=" * 70)
    print(f"DEMO FILE: {demo_file}")
    print("=" * 70)

    print(f"\n📊 SUMMARY")
    print(f"Naive chunking produced: {len(naive_chunks)} chunks (fixed 300-char blocks)")
    print(f"AST chunking produced:   {len(ast_chunks)} chunks (one per function/class)")

    print("\n" + "=" * 70)
    print("❌ NAIVE CHUNK EXAMPLE (a function cut mid-logic)")
    print("=" * 70)
    # Grab a middle chunk — early ones are often just imports
    middle_index = len(naive_chunks) // 2
    print(naive_chunks[middle_index])
    print("\n⚠️  Notice: this chunk starts or ends mid-function, mid-line, or mid-statement.")
    print("An LLM given this as context has no idea what function this belongs to.")

    print("\n" + "=" * 70)
    print("✅ AST CHUNK EXAMPLE (one complete function)")
    print("=" * 70)
    example = ast_chunks[0]
    print(f"Function: {example['name']} ({example['type']})")
    print(f"Lines: {example['start_line']}-{example['end_line']}")
    print(example["code"])
    print("\n✅ Notice: this is a complete, self-contained unit of logic —")
    print("the LLM can actually reason about what this function does.")