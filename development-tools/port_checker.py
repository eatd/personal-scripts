#!/usr/bin/env python3
"""
Port availability checker for development environments.
Scans common development ports and identifies running services.

Useful for debugging port conflicts and service discovery.
"""

import argparse
import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class ServiceInfo:
    port: int
    name: str
    description: str
    is_open: bool = False
    response_time: Optional[float] = None


class PortChecker:
    # Common development services and their default ports
    COMMON_SERVICES = {
        22: ("SSH", "Secure Shell"),
        80: ("HTTP", "Web Server"),
        443: ("HTTPS", "Secure Web Server"),
        3000: ("React/Node", "React Dev Server / Node.js"),
        3001: ("React Alt", "Alternative React Dev Server"),
        4000: ("Ruby/Jekyll", "Ruby on Rails / Jekyll"),
        5000: ("Flask/Express", "Flask Development Server"),
        5173: ("Vite", "Vite Development Server"),
        5432: ("PostgreSQL", "PostgreSQL Database"),
        5672: ("RabbitMQ", "Message Queue"),
        6379: ("Redis", "Redis Cache/Database"),
        8000: ("Django/HTTP", "Django Development Server"),
        8080: ("HTTP Alt", "Alternative HTTP Server"),
        8443: ("HTTPS Alt", "Alternative HTTPS Server"),
        8888: ("Jupyter", "Jupyter Notebook Server"),
        9000: ("Dev Server", "Various Development Servers"),
        9200: ("Elasticsearch", "Elasticsearch Search Engine"),
        27017: ("MongoDB", "MongoDB Database"),
        3306: ("MySQL", "MySQL Database"),
        1433: ("SQL Server", "Microsoft SQL Server"),
        11211: ("Memcached", "Memory Caching System"),
        25: ("SMTP", "Email Server"),
        110: ("POP3", "Email Retrieval"),
        143: ("IMAP", "Email Access"),
        21: ("FTP", "File Transfer Protocol"),
        53: ("DNS", "Domain Name System"),
    }

    def __init__(self, timeout: float = 2.0, max_workers: int = 50):
        self.timeout = timeout
        self.max_workers = max_workers
        self.results: List[ServiceInfo] = []

    def check_single_port(self, host: str, port: int) -> Tuple[bool, float]:
        """Check if a single port is open and measure response time."""
        start_time = time.time()

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                result = sock.connect_ex((host, port))
                response_time = time.time() - start_time
                return result == 0, response_time
        except (socket.gaierror, socket.timeout):
            return False, time.time() - start_time

    def scan_ports(
        self, host: str, ports: List[int], show_progress: bool = True
    ) -> List[ServiceInfo]:
        """Scan multiple ports concurrently."""
        services = []

        # Create ServiceInfo objects
        for port in ports:
            name, desc = self.COMMON_SERVICES.get(port, ("Unknown", "Unknown Service"))
            services.append(ServiceInfo(port, name, desc))

        if show_progress:
            print(f"🔍 Scanning {len(ports)} ports on {host}...")

        # Concurrent port scanning
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all port checks
            future_to_service = {
                executor.submit(self.check_single_port, host, service.port): service
                for service in services
            }

            completed = 0
            for future in as_completed(future_to_service):
                service = future_to_service[future]
                try:
                    is_open, response_time = future.result()
                    service.is_open = is_open
                    service.response_time = response_time
                except Exception as e:
                    print(f"Error checking port {service.port}: {e}")

                completed += 1
                if show_progress and completed % 10 == 0:
                    print(f"   Progress: {completed}/{len(ports)} ports scanned")

        self.results = services
        return services

    def scan_range(
        self, host: str, start_port: int, end_port: int, show_progress: bool = True
    ) -> List[ServiceInfo]:
        """Scan a range of ports."""
        ports = list(range(start_port, end_port + 1))

        # Create generic ServiceInfo for range scan
        services = []
        for port in ports:
            name, desc = self.COMMON_SERVICES.get(
                port, (f"Port {port}", "Unknown Service")
            )
            services.append(ServiceInfo(port, name, desc))

        if show_progress:
            print(f"🔍 Scanning ports {start_port}-{end_port} on {host}...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_service = {
                executor.submit(self.check_single_port, host, service.port): service
                for service in services
            }

            completed = 0
            for future in as_completed(future_to_service):
                service = future_to_service[future]
                try:
                    is_open, response_time = future.result()
                    service.is_open = is_open
                    service.response_time = response_time
                except Exception:
                    pass  # Skip errors in range scans

                completed += 1
                if show_progress and completed % 50 == 0:
                    print(f"   Progress: {completed}/{len(services)} ports scanned")

        # Only return open ports for range scans to reduce noise
        open_services = [s for s in services if s.is_open]
        self.results = open_services
        return open_services

    def get_open_ports(self) -> List[ServiceInfo]:
        """Get list of open ports from last scan."""
        return [service for service in self.results if service.is_open]

    def print_results(self, show_closed: bool = False):
        """Print formatted scan results."""
        open_ports = self.get_open_ports()
        closed_ports = [s for s in self.results if not s.is_open]

        print("\\n" + "=" * 60)
        print("🔍 PORT SCAN RESULTS")
        print("=" * 60)

        if open_ports:
            print(f"\\n✅ OPEN PORTS ({len(open_ports)}):")
            print("-" * 50)
            for service in sorted(open_ports, key=lambda x: x.port):
                response_ms = (
                    service.response_time * 1000 if service.response_time else 0
                )
                print(f"  {service.port:5d} - {service.name:<15} ({response_ms:.1f}ms)")
                if service.description != "Unknown Service":
                    print(f"         {service.description}")
        else:
            print("\\n❌ No open ports found")

        if show_closed and closed_ports:
            print(f"\\n🔒 CLOSED PORTS ({len(closed_ports)}):")
            print("-" * 50)
            for service in sorted(closed_ports, key=lambda x: x.port)[
                :20
            ]:  # Limit output
                print(f"  {service.port:5d} - {service.name}")
            if len(closed_ports) > 20:
                print(f"  ... and {len(closed_ports) - 20} more closed ports")

        # Summary
        total_scanned = len(self.results)
        print("\\n📊 SUMMARY:")
        print(f"   Total scanned: {total_scanned}")
        print(f"   Open ports: {len(open_ports)}")
        print(f"   Closed ports: {len(closed_ports)}")


def validate_host(host: str) -> bool:
    """Validate if host is reachable."""
    try:
        socket.gethostbyname(host)
        return True
    except socket.gaierror:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Development port scanner and service detector"
    )
    parser.add_argument(
        "host", nargs="?", default="localhost", help="Target host (default: localhost)"
    )
    parser.add_argument("--port", "-p", type=int, help="Scan specific port")
    parser.add_argument(
        "--range",
        "-r",
        nargs=2,
        type=int,
        metavar=("START", "END"),
        help="Scan port range (e.g., --range 8000 8100)",
    )
    parser.add_argument(
        "--common",
        "-c",
        action="store_true",
        help="Scan common development ports (default)",
    )
    parser.add_argument("--all", action="store_true", help="Show closed ports as well")
    parser.add_argument(
        "--timeout",
        "-t",
        type=float,
        default=1.0,
        help="Connection timeout in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=50,
        help="Number of concurrent workers (default: 50)",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress progress output"
    )

    args = parser.parse_args()

    # Validate host
    if not validate_host(args.host):
        print(f"❌ Cannot resolve host: {args.host}")
        sys.exit(1)

    # Initialize scanner
    scanner = PortChecker(timeout=args.timeout, max_workers=args.workers)

    # Determine scan type
    if args.port:
        # Single port scan
        ports = [args.port]
        scanner.scan_ports(args.host, ports, show_progress=not args.quiet)
    elif args.range:
        # Range scan
        start, end = args.range
        if start > end or start < 1 or end > 65535:
            print("❌ Invalid port range. Ports must be 1-65535 and start <= end")
            sys.exit(1)
        scanner.scan_range(args.host, start, end, show_progress=not args.quiet)
    else:
        # Common ports scan (default)
        common_ports = list(scanner.COMMON_SERVICES.keys())
        scanner.scan_ports(args.host, common_ports, show_progress=not args.quiet)

    # Display results
    scanner.print_results(show_closed=args.all)

    # Exit code based on results (useful for scripts)
    open_ports = scanner.get_open_ports()
    if not open_ports:
        sys.exit(1)  # No open ports found


if __name__ == "__main__":
    main()
