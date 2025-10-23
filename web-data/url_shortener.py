# pip install requests
import urllib.parse
import urllib.request
from tkinter import Tk, messagebox, simpledialog

try:
    import requests
except ImportError:
    requests = None


def shorten_url_tinyurl(long_url):
    """Shorten URL using TinyURL service (no API key required)."""
    try:
        api_url = (
            f"http://tinyurl.com/api-create.php?url={urllib.parse.quote(long_url)}"
        )

        if requests:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                return response.text.strip()
        else:
            # Fallback using urllib
            import urllib.request

            with urllib.request.urlopen(api_url) as response:
                return response.read().decode().strip()

        return f"Error: HTTP {response.status_code}"

    except Exception as e:
        return f"Error: {e}"


def shorten_url_is_gd(long_url):
    """Shorten URL using is.gd service (no API key required)."""
    try:
        api_url = "https://is.gd/create.php"
        data = {"format": "simple", "url": long_url}

        if requests:
            response = requests.post(api_url, data=data, timeout=10)
            if response.status_code == 200:
                short_url = response.text.strip()
                if short_url.startswith("http"):
                    return short_url
                else:
                    return f"Error: {short_url}"
        else:
            # Fallback using urllib
            import urllib.parse
            import urllib.request

            data_encoded = urllib.parse.urlencode(data).encode()
            with urllib.request.urlopen(api_url, data=data_encoded) as response:
                short_url = response.read().decode().strip()
                if short_url.startswith("http"):
                    return short_url
                else:
                    return f"Error: {short_url}"

        return f"Error: HTTP {response.status_code}"

    except Exception as e:
        return f"Error: {e}"


def validate_url(url):
    """Basic URL validation."""
    if not url:
        return False

    # Add protocol if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Basic URL pattern check
    import re

    pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    return pattern.match(url), url


def copy_to_clipboard(text):
    """Copy text to clipboard."""
    try:
        root = Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        root.destroy()
        return True
    except Exception:
        return False


def main():
    root = Tk()
    root.withdraw()

    # Get URL to shorten
    long_url = simpledialog.askstring(
        "URL Shortener",
        "Enter the URL to shorten:\n"
        "Examples:\n"
        "- https://www.example.com/very/long/path\n"
        "- www.example.com (https:// will be added)\n"
        "- example.com",
    )

    if not long_url:
        return

    # Validate and normalize URL
    is_valid, normalized_url = validate_url(long_url)
    if not is_valid:
        messagebox.showerror("Invalid URL", "Please enter a valid URL.")
        return

    print(f"Shortening URL: {normalized_url}")

    # Choose service
    service = messagebox.askyesnocancel(
        "Choose Service",
        "Which URL shortening service would you like to use?\n\n"
        "Yes: TinyURL (http://tinyurl.com)\n"
        "No: is.gd (https://is.gd)\n"
        "Cancel: Exit",
    )

    if service is None:  # Cancel
        return

    # Shorten URL
    if service:  # TinyURL
        print("Using TinyURL service...")
        short_url = shorten_url_tinyurl(normalized_url)
    else:  # is.gd
        print("Using is.gd service...")
        short_url = shorten_url_is_gd(normalized_url)

    # Display result
    if short_url.startswith("Error"):
        print(short_url)
        messagebox.showerror("Error", f"Failed to shorten URL:\n{short_url}")
    else:
        print(f"Original URL: {normalized_url}")
        print(f"Shortened URL: {short_url}")

        # Copy to clipboard
        if copy_to_clipboard(short_url):
            clipboard_msg = "\\n(Copied to clipboard)"
        else:
            clipboard_msg = ""

        messagebox.showinfo(
            "Success",
            f"URL shortened successfully!\\n\\n"
            f"Original: {normalized_url[:50]}{'...' if len(normalized_url) > 50 else ''}\\n"
            f"Shortened: {short_url}{clipboard_msg}",
        )


if __name__ == "__main__":
    main()
