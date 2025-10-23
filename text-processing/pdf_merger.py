# pip install PyPDF2
from pathlib import Path
from tkinter import Tk, filedialog, messagebox

import PyPDF2


def merge_pdfs(pdf_paths, output_path):
    """Merge multiple PDF files into one."""
    merger = PyPDF2.PdfMerger()

    try:
        for pdf_path in pdf_paths:
            print(f"Adding: {Path(pdf_path).name}")
            merger.append(pdf_path)

        with open(output_path, "wb") as output_file:
            merger.write(output_file)

        merger.close()
        return True

    except Exception as e:
        print(f"Error merging PDFs: {e}")
        return False


def main():
    root = Tk()
    root.withdraw()

    # Select PDF files
    pdf_files = filedialog.askopenfilenames(
        title="Select PDF files to merge", filetypes=[("PDF files", "*.pdf")]
    )

    if len(pdf_files) < 2:
        messagebox.showwarning(
            "Warning", "Please select at least 2 PDF files to merge."
        )
        return

    # Select output location
    output_file = filedialog.asksaveasfilename(
        title="Save merged PDF as",
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
    )

    if not output_file:
        return

    print(f"Merging {len(pdf_files)} PDF files...")
    print("Files to merge:")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"  {i}. {Path(pdf_file).name}")

    if merge_pdfs(pdf_files, output_file):
        print(f"\nSuccessfully merged PDFs into: {output_file}")
        messagebox.showinfo(
            "Success", f"PDFs merged successfully!\nSaved as: {Path(output_file).name}"
        )
    else:
        messagebox.showerror(
            "Error", "Failed to merge PDFs. Check console for details."
        )


if __name__ == "__main__":
    main()
