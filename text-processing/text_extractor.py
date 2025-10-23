# pip install PyPDF2 python-docx pillow pytesseract
# Also install Tesseract OCR from: https://github.com/tesseract-ocr/tesseract
from pathlib import Path
from tkinter import Tk, filedialog, messagebox

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from docx import Document
except ImportError:
    Document = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    Image = None
    pytesseract = None


def extract_from_pdf(file_path):
    """Extract text from PDF file."""
    if not PyPDF2:
        return "Error: PyPDF2 not installed. Run: pip install PyPDF2"

    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        return f"Error reading PDF: {e}"


def extract_from_docx(file_path):
    """Extract text from Word document."""
    if not Document:
        return "Error: python-docx not installed. Run: pip install python-docx"

    try:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        return f"Error reading DOCX: {e}"


def extract_from_image(file_path):
    """Extract text from image using OCR."""
    if not Image or not pytesseract:
        return "Error: PIL or pytesseract not installed. Run: pip install pillow pytesseract"

    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        return f"Error reading image: {e}"


def extract_text(file_path):
    """Extract text based on file extension."""
    file_path = Path(file_path)
    extension = file_path.suffix.lower()

    if extension == ".pdf":
        return extract_from_pdf(file_path)
    elif extension in [".docx", ".doc"]:
        return extract_from_docx(file_path)
    elif extension in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
        return extract_from_image(file_path)
    elif extension == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            return f"Error reading text file: {e}"
    else:
        return f"Unsupported file type: {extension}"


def main():
    root = Tk()
    root.withdraw()

    # Select file
    file_path = filedialog.askopenfilename(
        title="Select file to extract text from",
        filetypes=[
            (
                "All supported",
                "*.pdf;*.docx;*.doc;*.txt;*.png;*.jpg;*.jpeg;*.tiff;*.bmp",
            ),
            ("PDF files", "*.pdf"),
            ("Word documents", "*.docx;*.doc"),
            ("Text files", "*.txt"),
            ("Images", "*.png;*.jpg;*.jpeg;*.tiff;*.bmp"),
            ("All files", "*.*"),
        ],
    )

    if not file_path:
        return

    print(f"Extracting text from: {Path(file_path).name}")
    extracted_text = extract_text(file_path)

    if extracted_text.startswith("Error"):
        print(extracted_text)
        messagebox.showerror("Error", extracted_text)
        return

    if not extracted_text.strip():
        print("No text found in the file.")
        messagebox.showinfo("Result", "No text was found in the selected file.")
        return

    # Ask where to save the extracted text
    output_file = filedialog.asksaveasfilename(
        title="Save extracted text as",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")],
    )

    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(extracted_text)
            print(f"Text extracted and saved to: {output_file}")
            messagebox.showinfo(
                "Success",
                f"Text extracted successfully!\nSaved as: {Path(output_file).name}",
            )
        except Exception as e:
            error_msg = f"Error saving file: {e}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)
    else:
        # Show text in console if no save location selected
        print("\nExtracted text:")
        print("=" * 50)
        print(extracted_text[:1000] + ("..." if len(extracted_text) > 1000 else ""))


if __name__ == "__main__":
    main()
