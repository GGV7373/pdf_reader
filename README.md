# PDF Reader with Ollama AI

This project allows you to ask questions about the contents of a PDF file using an AI model from Ollama. The script extracts text from your PDF and sends it to an AI model to answer your questions interactively.

## Prerequisites

- Python 3.8 or newer
- [Ollama](https://ollama.com/) installed and running on your system
- The required Python packages: `ollama` and `pypdf`

## Installation

1. **Install Ollama**  
   Follow the instructions at [Ollama.com](https://ollama.com/) to download and set up Ollama on your machine.

2. **Install Python dependencies**  
   Run the following command in your terminal:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Place your PDF file in the same folder as `main.py`.
2. Run the script:
   ```
   python main.py
   ```
3. When prompted, enter the name of your PDF file (without the `.pdf` extension).  
   Or open it straight away: `python main.py example.pdf`
4. Ask questions about the PDF content.  
   - Type `switch` to load a different PDF.
   - Type `exit` to quit the program.

## Customizing the AI Model

You can change the AI model by editing the `MODEL` variable in the `main.py` file.  
For example, replace `"llama3.2"` with another model name supported by Ollama.

## Example

```
PDF file (without .pdf): example
Write a question (or 'switch' for new PDF, 'exit' to quit): What is the main topic?
Thinking…
Answer from LLaMA:
...
```

---
For any issues, refer to the Ollama documentation or check your Python installation.
