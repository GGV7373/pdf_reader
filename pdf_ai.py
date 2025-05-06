import PyPDF2
from ollama import chat, ChatResponse

def extract_text_from_pdf(pdf_name: str) -> str:
    file_path = f"{pdf_name}.pdf"
    all_text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            all_text += page.extract_text() or ""
            all_text += "\n"
    return all_text

def ask_ollama(text: str, question: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant who reads PDF text and answers questions."
        },
        {
            "role": "user",
            "content": f"{question}\n\n{text}"
        }
    ]
    response: ChatResponse = chat(
        model="llama3.2",
        messages=messages,
        stream=False
    )
    return response.message.content

def main():
    print("----------")
    print(" PDF-leser")
    print("----------")

    pdf_name = input("PDF-file (out the .pdf): ").strip()
    pdf_text = extract_text_from_pdf(pdf_name)
    print("PDF loding..!\n")

    while True:
        question = input("Write a question (or 'switch' for new PDF, 'exit' to quit): ").strip()

        if question.lower() == "exit":
            print("Exit....")
            break

        elif question.lower() == "switch":
            pdf_name = input("New PDF file name (without .pdf): ").strip()
            pdf_text = extract_text_from_pdf(pdf_name)
            print("New PDF loaded!\n")
            continue

        else:
            print("\nThinking…”)
            response = ask_ollama(pdf_text, question)
            print("\nAnswer from LLaMA:\n")
            print(response)
            print("\n" + "-" * 40)

if __name__ == "__main__":
    main()
