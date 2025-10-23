# pip install markdown2
import re
from pathlib import Path
from tkinter import Tk, filedialog, messagebox

try:
    import markdown2
except ImportError:
    markdown2 = None


def markdown_to_html(markdown_text):
    """Convert Markdown to HTML."""
    if markdown2:
        return markdown2.markdown(
            markdown_text, extras=["fenced-code-blocks", "tables"]
        )
    else:
        # Basic markdown conversion without external library
        html = markdown_text

        # Headers
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)

        # Bold and italic
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)

        # Links
        html = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', html)

        # Code blocks
        html = re.sub(
            r"```(.+?)```", r"<pre><code>\1</code></pre>", html, flags=re.DOTALL
        )
        html = re.sub(r"`(.+?)`", r"<code>\1</code>", html)

        # Paragraphs
        html = re.sub(r"\n\n", "</p><p>", html)
        html = "<p>" + html + "</p>"
        html = html.replace("<p></p>", "")

        return html


def html_to_markdown(html_text):
    """Convert HTML to Markdown (basic conversion)."""
    markdown = html_text

    # Headers
    markdown = re.sub(r"<h1.*?>(.*?)</h1>", r"# \1", markdown, flags=re.IGNORECASE)
    markdown = re.sub(r"<h2.*?>(.*?)</h2>", r"## \1", markdown, flags=re.IGNORECASE)
    markdown = re.sub(r"<h3.*?>(.*?)</h3>", r"### \1", markdown, flags=re.IGNORECASE)

    # Bold and italic
    markdown = re.sub(
        r"<strong.*?>(.*?)</strong>", r"**\1**", markdown, flags=re.IGNORECASE
    )
    markdown = re.sub(r"<b.*?>(.*?)</b>", r"**\1**", markdown, flags=re.IGNORECASE)
    markdown = re.sub(r"<em.*?>(.*?)</em>", r"*\1*", markdown, flags=re.IGNORECASE)
    markdown = re.sub(r"<i.*?>(.*?)</i>", r"*\1*", markdown, flags=re.IGNORECASE)

    # Links
    markdown = re.sub(
        r'<a.*?href="(.*?)".*?>(.*?)</a>', r"[\2](\1)", markdown, flags=re.IGNORECASE
    )

    # Code
    markdown = re.sub(r"<code.*?>(.*?)</code>", r"`\1`", markdown, flags=re.IGNORECASE)
    markdown = re.sub(
        r"<pre.*?><code.*?>(.*?)</code></pre>",
        r"```\n\1\n```",
        markdown,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Remove HTML tags
    markdown = re.sub(r"<.*?>", "", markdown)

    # Clean up extra whitespace
    markdown = re.sub(r"\n\s*\n", "\n\n", markdown)

    return markdown.strip()


def main():
    root = Tk()
    root.withdraw()

    # Select input file
    input_file = filedialog.askopenfilename(
        title="Select file to convert",
        filetypes=[
            ("Markdown files", "*.md;*.markdown"),
            ("HTML files", "*.html;*.htm"),
            ("All files", "*.*"),
        ],
    )

    if not input_file:
        return

    input_path = Path(input_file)

    try:
        with open(input_path, "r", encoding="utf-8") as file:
            content = file.read()
    except Exception as e:
        messagebox.showerror("Error", f"Could not read file: {e}")
        return

    # Determine conversion direction
    if input_path.suffix.lower() in [".md", ".markdown"]:
        # Markdown to HTML
        converted_content = markdown_to_html(content)
        default_extension = ".html"
        conversion_type = "Markdown to HTML"
    elif input_path.suffix.lower() in [".html", ".htm"]:
        # HTML to Markdown
        converted_content = html_to_markdown(content)
        default_extension = ".md"
        conversion_type = "HTML to Markdown"
    else:
        # Ask user which conversion to perform
        is_markdown = messagebox.askyesno(
            "Conversion Type",
            "Which conversion would you like to perform?\n\n"
            "Yes: Treat as Markdown → Convert to HTML\n"
            "No: Treat as HTML → Convert to Markdown",
        )
        if is_markdown:
            converted_content = markdown_to_html(content)
            default_extension = ".html"
            conversion_type = "Markdown to HTML"
        else:
            converted_content = html_to_markdown(content)
            default_extension = ".md"
            conversion_type = "HTML to Markdown"

    # Save converted content
    output_file = filedialog.asksaveasfilename(
        title=f"Save converted file as ({conversion_type})",
        defaultextension=default_extension,
        filetypes=[
            ("HTML files", "*.html")
            if default_extension == ".html"
            else ("Markdown files", "*.md"),
            ("All files", "*.*"),
        ],
    )

    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(converted_content)

            print(
                f"Successfully converted {input_path.name} to {Path(output_file).name}"
            )
            print(f"Conversion: {conversion_type}")
            messagebox.showinfo(
                "Success",
                f"File converted successfully!\n"
                f"Conversion: {conversion_type}\n"
                f"Saved as: {Path(output_file).name}",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")


if __name__ == "__main__":
    main()
