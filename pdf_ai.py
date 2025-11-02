import os
import time
import PyPDF2
from ollama import chat, ChatResponse

def extract_text_from_pdf(pdf_name: str) -> str:
    """Extract all text from a PDF file."""
    # Ensure .pdf extension
    if not pdf_name.lower().endswith(".pdf"):
        pdf_name += ".pdf"

    if not os.path.exists(pdf_name):
        raise FileNotFoundError(f"Cannot find PDF file: {pdf_name}")

    try:
        all_text = ""
        with open(pdf_name, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            if not reader.pages:
                raise ValueError("PDF file appears to be empty")
            
            for i, page in enumerate(reader.pages, 1):
                text = page.extract_text() or ""
                if text.strip():
                    all_text += text + "\n"
                else:
                    print(f"Warning: Page {i} appears empty or unreadable")
        
        if not all_text.strip():
            raise ValueError("No text could be extracted from the PDF")

        return all_text
    except PyPDF2.errors.PdfReadError as e:
        raise ValueError(f"Error reading PDF: {e}")
    except Exception as e:
        raise ValueError(f"Unexpected error: {e}")

def ask_ollama(text: str, question: str, max_retries: int = 3, timeout: int = 30) -> str:
    """Ask Ollama a question about the PDF text."""
    for attempt in range(max_retries):
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant who reads PDF text and answers questions."},
                {"role": "user", "content": f"{question}\n\n{text}"}
            ]
            response: ChatResponse = chat(
                model="tinyllama",
                messages=messages,
                stream=False,
                options={"timeout": timeout}
            )
            return response.message.content
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed. Retrying...")
                time.sleep(2)
            else:
                raise Exception(f"Failed after {max_retries} attempts. Last error: {e}")

def main():
    print("----------\n PDF Reader\n----------")

    while True:
        try:
            pdf_name = input("PDF file (with or without .pdf): ").strip()
            if not pdf_name:
                continue

            print("Loading PDF...")
            pdf_text = extract_text_from_pdf(pdf_name)
            print(f"Loaded {len(pdf_text.split())} words from PDF\n")

            while True:
                question = input("Question ('switch' for new PDF, 'exit' to quit): ").strip()
                if not question:
                    continue

                if question.lower() == "exit":
                    print("Exiting...")
                    return
                elif question.lower() == "switch":
                    break

                print("Thinking...")
                try:
                    answer = ask_ollama(pdf_text, question)
                    print("\nAnswer:\n", answer)
                    print("-" * 40)
                except Exception as e:
                    print(f"Error getting response: {e}")

        except FileNotFoundError:
            print(f"Error: PDF '{pdf_name}' not found.")
        except Exception as e:
            print(f"Error loading PDF: {e}")

if __name__ == "__main__":
    main()
