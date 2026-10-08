from pypdf import PdfReader
from ollama import chat, ResponseError

# This is the model name you want to use
MODEL = "llama3.2"
# How many tokens the model can read at once (raise for very long PDFs, needs more RAM)
CONTEXT_SIZE = 32768

def extract_text_from_pdf(pdf_name: str) -> str:
    # Extract all text from a PDF file given its name (with or without .pdf extension)
    # Returns the extracted text as a single string
    file_path = pdf_name if pdf_name.lower().endswith(".pdf") else f"{pdf_name}.pdf"
    all_text = ""
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            all_text += page.extract_text() or ""
            all_text += "\n"
    return all_text

def start_conversation(text: str) -> list:
    # Start a new chat history with the PDF text, so follow-up questions remember earlier answers
    return [
        {"role": "system", "content": "You are a helpful assistant who reads PDF text and answers questions."},
        {"role": "user", "content": f"Here is the PDF text:\n\n{text}"},
    ]

def ask_ollama(messages: list, question: str) -> None:
    # Send the question with the chat history to Ollama and print the answer as it arrives
    messages.append({"role": "user", "content": question})
    answer = ""
    try:
        for chunk in chat(model=MODEL, messages=messages, stream=True, options={"num_ctx": CONTEXT_SIZE}):
            print(chunk.message.content, end="", flush=True)
            answer += chunk.message.content
    except ConnectionError:
        messages.pop()
        print("Could not reach Ollama. Is it running? (start it with 'ollama serve')")
        return
    except ResponseError as e:
        messages.pop()
        print(f"Ollama error: {e.error} (try 'ollama pull {MODEL}')")
        return
    print()
    messages.append({"role": "assistant", "content": answer})

def load_pdf(prompt: str) -> list:
    # Keep asking until a PDF is loaded, then return a new conversation for it
    while True:
        pdf_name = input(prompt).strip()
        try:
            text = extract_text_from_pdf(pdf_name)
        except FileNotFoundError:
            print(f"Could not find '{pdf_name}'. Try again.\n")
            continue
        print("PDF loaded!\n")
        return start_conversation(text)

def main():
    # Main function to run the PDF reader and question-answering loop
    print("-"* 10 + "\n")
    print(" PDF-Reader\n")
    print("-" * 10 + "\n")

    # Prompt user for PDF file name (without .pdf extension)
    messages = load_pdf("PDF file (without .pdf): ")

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
    main()
