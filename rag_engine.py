import os
from google import genai
from dotenv import load_dotenv
from indexer import search_codebase

load_dotenv()

# Initialize Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def ask_question(question: str):
    matches = search_codebase(question, top_k=4)

    context = ""
    for i, m in enumerate(matches):
        meta = m["metadata"]
        context += f"\n--- Source {i+1}: {meta['file_path']} (lines {meta['start_line']}-{meta['end_line']}) ---\n"
        context += f"Function/Class: {meta['name']} ({meta['type']})\n"
        context += f"Recent commits: {meta['commits']}\n"
        context += f"Code:\n{m['document']}\n"

    prompt = f"""You are a senior engineer helping a new teammate understand a codebase.
Answer ONLY using the context below. Always mention the exact file path, function name, and line numbers.
If the context doesn't answer the question, say so honestly instead of guessing.

Question: {question}

Context:
{context}"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return {"answer": response.text, "sources": matches}

if __name__ == "__main__":
    result = ask_question("Where is user authentication handled?")
    print("\n" + "=" * 60)
    print("🤖 GEMINI ANSWER:")
    print("=" * 60)
    print(result["answer"])