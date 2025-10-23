# pip install qrcode[pil]
from pathlib import Path
from tkinter import Tk, filedialog, messagebox, simpledialog

try:
    import qrcode
    from PIL import Image
except ImportError:
    qrcode = None
    Image = None


def generate_qr_code(data, output_path, size=10, border=4):
    """Generate QR code from data and save as image."""
    if not qrcode:
        return "Error: qrcode library not installed. Run: pip install qrcode[pil]"

    try:
        qr = qrcode.QRCode(
            version=1,  # Controls the size of the QR Code
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)

        return f"QR code saved successfully to: {output_path}"

    except Exception as e:
        return f"Error generating QR code: {e}"


def main():
    root = Tk()
    root.withdraw()

    if not qrcode:
        messagebox.showerror(
            "Missing Dependency",
            "QR code library not installed.\n\n"
            "Please install it using:\n"
            "pip install qrcode[pil]",
        )
        return

    # Get data to encode
    qr_data = simpledialog.askstring(
        "QR Code Data",
        "Enter text or URL to encode in QR code:\n"
        "Examples:\n"
        "- https://www.example.com\n"
        "- Your phone number\n"
        "- Any text message",
    )

    if not qr_data:
        return

    # Get QR code size
    size_str = simpledialog.askstring(
        "QR Code Size",
        "Enter box size (1-20, default 10):\nLarger numbers = bigger QR code",
    )
    try:
        size = int(size_str) if size_str else 10
        size = max(1, min(20, size))  # Clamp between 1 and 20
    except ValueError:
        size = 10

    # Select output location
    output_file = filedialog.asksaveasfilename(
        title="Save QR code as",
        defaultextension=".png",
        filetypes=[
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg"),
            ("All files", "*.*"),
        ],
    )

    if not output_file:
        return

    print(f"Generating QR code for: {qr_data[:50]}{'...' if len(qr_data) > 50 else ''}")
    print(f"Size: {size}x{size} pixels per box")

    result = generate_qr_code(qr_data, output_file, size)

    if result.startswith("Error"):
        print(result)
        messagebox.showerror("Error", result)
    else:
        print(result)
        messagebox.showinfo(
            "Success",
            f"QR code generated successfully!\n"
            f"Saved as: {Path(output_file).name}\n"
            f"Data: {qr_data[:50]}{'...' if len(qr_data) > 50 else ''}",
        )


if __name__ == "__main__":
    main()
