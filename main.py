import sys
import httpx
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from ollama import chat, ResponseError

# This is the model name you want to use
MODEL = "llama3.2"
# How many tokens the model can read at once (raise for very long PDFs, needs more RAM)
CONTEXT_SIZE = 32768

def read_pdf_text(file) -> str:
    # Extract all text from an open PDF file (or uploaded file) as a single string
    all_text = ""
    for page in PdfReader(file).pages:
        all_text += page.extract_text() or ""
        all_text += "\n"
    return all_text

def extract_text_from_pdf(pdf_name: str) -> str:
    # Extract all text from a PDF file given its name (with or without .pdf extension)
    file_path = pdf_name if pdf_name.lower().endswith(".pdf") else f"{pdf_name}.pdf"
    with open(file_path, "rb") as f:
        return read_pdf_text(f)

def is_too_long(text: str) -> bool:
    # Roughly 4 characters per token
    return len(text) / 4 > CONTEXT_SIZE

def start_conversation(text: str) -> list:
    # Start a new chat history with the PDF text, so follow-up questions remember earlier answers
    return [
        {"role": "system", "content": "You are a helpful assistant who reads PDF text and answers questions."},
        {"role": "user", "content": f"Here is the PDF text:\n\n{text}"},
    ]

def stream_answer(messages: list):
    # Ask Ollama with the chat history and yield the answer piece by piece as it arrives
    try:
        for chunk in chat(model=MODEL, messages=messages, stream=True, options={"num_ctx": CONTEXT_SIZE}):
            yield chunk.message.content
    except httpx.ConnectError as e:
        # When streaming, ollama raises httpx's error instead of ConnectionError
        raise ConnectionError(e) from e

def ollama_error_message(e: Exception) -> str:
    # Turn an Ollama error into a message a user can act on
    if isinstance(e, ConnectionError):
        return "Could not reach Ollama. Is it running? (start it with 'ollama serve')"
    return f"Ollama error: {e.error} (try 'ollama pull {MODEL}')"

def ask_ollama(messages: list, question: str) -> None:
    # Send the question with the chat history to Ollama and print the answer as it arrives
    messages.append({"role": "user", "content": question})
    answer = ""
    try:
        for piece in stream_answer(messages):
            print(piece, end="", flush=True)
            answer += piece
    except (ConnectionError, ResponseError) as e:
        messages.pop()
        print(ollama_error_message(e))
        return
    print()
    messages.append({"role": "assistant", "content": answer})

def load_pdf(prompt: str, pdf_name: str = "") -> list:
    # Keep asking until a PDF is loaded, then return a new conversation for it
    while True:
        pdf_name = pdf_name or input(prompt).strip()
        try:
            text = extract_text_from_pdf(pdf_name)
        except (OSError, PdfReadError) as e:
            print(f"Could not open '{pdf_name}': {e}\nTry again.\n")
            pdf_name = ""
            continue
        if not text.strip():
            # Scanned PDFs are just images, so there is no text to read
            print(f"No text found in '{pdf_name}' (is it a scanned PDF?). Try another.\n")
            pdf_name = ""
            continue
        if is_too_long(text):
            print("Warning: this PDF is very long, the model may only read part of it (raise CONTEXT_SIZE).")
        print("PDF loaded!\n")
        return start_conversation(text)

def main():
    # Main function to run the PDF reader and question-answering loop
    print("-"* 10 + "\n")
    print(" PDF-Reader\n")
    print("-" * 10 + "\n")

    # Use the PDF given on the command line (python main.py file.pdf), or ask for one
    messages = load_pdf("PDF file (without .pdf): ", sys.argv[1] if len(sys.argv) > 1 else "")

    while True:
        # Prompt user for a question or command
        question = input("Write a question (or 'switch' for new PDF, 'exit' to quit): ").strip()

        if question.lower() == "exit":
            # Exit the program
            print("Exit....")
            break

        elif question.lower() == "switch":
            # Switch to a new PDF file (starts a fresh conversation)
            messages = load_pdf("New PDF file name (without .pdf): ")
            continue

        elif question:
            # Ask a question about the current PDF
            print("\nAnswer from LLaMA:\n")
            ask_ollama(messages, question)
            print("\n" + "-" * 40)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C or Ctrl+Z/Ctrl+D quits without a long error message
        print("\nExit....")
