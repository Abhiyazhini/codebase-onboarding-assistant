import ast

def parse_python_file(file_path: str):
    """
    Reads one .py file and returns a list of dictionaries,
    one per function/class found in the file.
    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        code_string = f.read()

    try:
        tree = ast.parse(code_string)
    except SyntaxError:
        # Some files won't parse cleanly (e.g. Python 2 syntax, corrupted files)
        # We skip them instead of crashing the whole pipeline
        return []

    chunks = []
    lines = code_string.splitlines()

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            start = node.lineno
            end = getattr(node, "end_lineno", start)
            code_segment = "\n".join(lines[start - 1:end])

            chunks.append({
                "file_path": file_path,
                "name": node.name,
                "type": node.__class__.__name__,
                "start_line": start,
                "end_line": end,
                "code": code_segment,
            })

    return chunks