import os
import time
import requests
import subprocess
import PyPDF2
from ollama import chat, ChatResponse

def start_ollama_server():
    # Start the Ollama server if it's not already running
    try:
        requests.get("http://localhost:11434")
    except requests.RequestException:
        subprocess.Popen(
            ["ollama", "serve"],
            start_new_session=True
        )
        time.sleep(5)


def extract_text_from_pdf(pdf_name: str) -> str:
    # Extract all text from a PDF file given its name (without .pdf extension)
    # Returns the extracted text as a single string
    file_path = f"{pdf_name}.pdf"
    all_text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            all_text += page.extract_text() or ""
            all_text += "\n"
    return all_text

def ask_ollama(text: str, question: str) -> str:
    start_ollama_server()  # Ensure the Ollama server is running
    response: ChatResponse = chat(
        # This is the model name you want to use

        model="llama3.2",
        messages=[
            {"role": "system", "content": "You are a helpful assistant who reads PDF text and answers questions."},
            {"role": "user", "content": f"{question}\n\n{text}"}
        ],
        stream=False
    )
    return response.message.content

def main():
    # Main function to run the PDF reader and question-answering loop
    print("-"* 10 + "\n")
    print("PDF-Reader\n")
    print("-" * 10 + "\n")

    # Prompt user for PDF file name (without .pdf extension)
    pdf_name = input("PDF-file (out the .pdf): ").strip()
    pdf_text = extract_text_from_pdf(pdf_name)
    print("PDF loding..!\n")

    while True:
        # Prompt user for a question or command
        question = input("Write a question (or 'switch' for new PDF, 'exit' or 'quit' to exit the program): ").strip()

        if question.lower() == "exit" or question.lower() == "quit":
            # Exit the program
            print("Exit....")
            break

        elif question.lower() == "switch":
            # Switch to a new PDF file
            pdf_name = input("New PDF file name (without .pdf): ").strip()
            pdf_text = extract_text_from_pdf(pdf_name)
            print("New PDF loaded!\n")
            continue

        else:
            # Ask a question about the current PDF
            print("Thinking…")
            response = ask_ollama(pdf_text, question)
            
            print("\nAnswer from LLaMA:\n")
            print(response)
            print("\n" + "-" * 40)

if __name__ == "__main__":
    main()
