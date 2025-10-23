# Built-in modules only
import re
from datetime import datetime
from pathlib import Path
from tkinter import Tk, filedialog, messagebox


def parse_log_file(file_path, patterns=None):
    """Parse log file and extract information based on patterns."""
    if patterns is None:
        # Default patterns for common log formats
        patterns = {
            "error": re.compile(r".*?error.*?", re.IGNORECASE),
            "warning": re.compile(r".*?warning.*?", re.IGNORECASE),
            "timestamp": re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"),
            "ip_address": re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"),
            "http_status": re.compile(r" [1-5]\d{2} "),
        }

    results = {
        "total_lines": 0,
        "errors": [],
        "warnings": [],
        "timestamps": [],
        "ip_addresses": set(),
        "http_statuses": {},
        "summary": {},
    }

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            for line_num, line in enumerate(file, 1):
                results["total_lines"] += 1
                line = line.strip()

                # Check for errors
                if patterns["error"].search(line):
                    results["errors"].append((line_num, line))

                # Check for warnings
                if patterns["warning"].search(line):
                    results["warnings"].append((line_num, line))

                # Extract timestamps
                timestamp_match = patterns["timestamp"].search(line)
                if timestamp_match:
                    results["timestamps"].append(timestamp_match.group())

                # Extract IP addresses
                ip_matches = patterns["ip_address"].findall(line)
                results["ip_addresses"].update(ip_matches)

                # Extract HTTP status codes
                status_match = patterns["http_status"].search(line)
                if status_match:
                    status = status_match.group().strip()
                    results["http_statuses"][status] = (
                        results["http_statuses"].get(status, 0) + 1
                    )

    except Exception as e:
        return {"error": f"Could not parse log file: {e}"}

    # Generate summary
    results["summary"] = {
        "total_lines": results["total_lines"],
        "total_errors": len(results["errors"]),
        "total_warnings": len(results["warnings"]),
        "unique_ips": len(results["ip_addresses"]),
        "time_range": get_time_range(results["timestamps"]),
    }

    return results


def get_time_range(timestamps):
    """Get the time range from a list of timestamps."""
    if not timestamps:
        return "No timestamps found"

    try:
        parsed_times = []
        for ts in timestamps:
            try:
                parsed_times.append(datetime.strptime(ts, "%Y-%m-%d %H:%M:%S"))
            except ValueError:
                continue

        if parsed_times:
            earliest = min(parsed_times)
            latest = max(parsed_times)
            return f"{earliest} to {latest}"
    except Exception:
        pass

    return f"First: {timestamps[0]}, Last: {timestamps[-1]}"


def generate_report(results, output_file):
    """Generate a detailed report from the parsing results."""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("LOG ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n\n")

        # Summary
        f.write("SUMMARY\n")
        f.write("-" * 20 + "\n")
        for key, value in results["summary"].items():
            f.write(f"{key.replace('_', ' ').title()}: {value}\n")
        f.write("\n")

        # Errors
        if results["errors"]:
            f.write(f"ERRORS ({len(results['errors'])})\n")
            f.write("-" * 20 + "\n")
            for line_num, error in results["errors"][:50]:  # Limit to first 50
                f.write(f"Line {line_num}: {error}\n")
            if len(results["errors"]) > 50:
                f.write(f"... and {len(results['errors']) - 50} more errors\n")
            f.write("\n")

        # Warnings
        if results["warnings"]:
            f.write(f"WARNINGS ({len(results['warnings'])})\n")
            f.write("-" * 20 + "\n")
            for line_num, warning in results["warnings"][:50]:  # Limit to first 50
                f.write(f"Line {line_num}: {warning}\n")
            if len(results["warnings"]) > 50:
                f.write(f"... and {len(results['warnings']) - 50} more warnings\n")
            f.write("\n")

        # IP Addresses
        if results["ip_addresses"]:
            f.write(f"UNIQUE IP ADDRESSES ({len(results['ip_addresses'])})\n")
            f.write("-" * 20 + "\n")
            for ip in sorted(results["ip_addresses"]):
                f.write(f"{ip}\n")
            f.write("\n")

        # HTTP Status Codes
        if results["http_statuses"]:
            f.write("HTTP STATUS CODES\n")
            f.write("-" * 20 + "\n")
            for status, count in sorted(results["http_statuses"].items()):
                f.write(f"{status}: {count}\n")
            f.write("\n")


def main():
    root = Tk()
    root.withdraw()

    # Select log file
    log_file = filedialog.askopenfilename(
        title="Select log file to analyze",
        filetypes=[
            ("Log files", "*.log"),
            ("Text files", "*.txt"),
            ("All files", "*.*"),
        ],
    )

    if not log_file:
        return

    print(f"Parsing log file: {Path(log_file).name}")
    print("This may take a while for large files...")

    # Parse the log file
    results = parse_log_file(log_file)

    if "error" in results:
        print(results["error"])
        messagebox.showerror("Error", results["error"])
        return

    # Display summary
    print("\nLOG ANALYSIS SUMMARY:")
    print("=" * 40)
    for key, value in results["summary"].items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    # Ask if user wants to save detailed report
    save_report = messagebox.askyesno(
        "Save Report",
        f"Analysis complete!\n\n"
        f"Found {results['summary']['total_errors']} errors "
        f"and {results['summary']['total_warnings']} warnings.\n\n"
        f"Would you like to save a detailed report?",
    )

    if save_report:
        output_file = filedialog.asksaveasfilename(
            title="Save analysis report as",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
        )

        if output_file:
            generate_report(results, output_file)
            print(f"\nDetailed report saved to: {output_file}")
            messagebox.showinfo(
                "Success",
                f"Report saved successfully!\nSaved as: {Path(output_file).name}",
            )


if __name__ == "__main__":
    main()
