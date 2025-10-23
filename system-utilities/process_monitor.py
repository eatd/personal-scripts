#!/usr/bin/env python3
"""
System resource monitor with alerting capabilities.
Tracks CPU, memory, disk usage and process information.

Designed for development environment monitoring and system diagnostics.
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import psutil


class SystemMonitor:
    def __init__(self, config_file: Optional[Path] = None):
        self.config = self.load_config(config_file)
        self.alerts = []
        self.start_time = datetime.now()

    def load_config(self, config_file: Optional[Path]) -> Dict:
        """Load monitoring configuration."""
        default_config = {
            "thresholds": {
                "cpu_percent": 80.0,
                "memory_percent": 85.0,
                "disk_percent": 90.0,
                "process_memory_mb": 1000,
                "process_cpu_percent": 50.0,
            },
            "monitoring": {
                "interval_seconds": 5,
                "top_processes": 10,
                "alert_cooldown": 300,  # 5 minutes
            },
            "ignore_processes": [
                "System Idle Process",
                "System",
                "Registry",
                "Secure System",
            ],
        }

        if config_file and config_file.exists():
            try:
                with open(config_file) as f:
                    user_config = json.load(f)

                # Merge configs
                for section, values in user_config.items():
                    if section in default_config:
                        default_config[section].update(values)
                    else:
                        default_config[section] = values

            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Config error: {e}, using defaults")

        return default_config

    def get_system_info(self) -> Dict:
        """Collect comprehensive system information."""
        # CPU Information
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        # Memory Information
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # Disk Information
        disk_usage = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage[partition.mountpoint] = {
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": (usage.used / usage.total) * 100,
                }
            except (PermissionError, FileNotFoundError):
                continue

        # Network Information
        network = psutil.net_io_counters()

        # Boot time
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time

        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count,
                "frequency": cpu_freq._asdict() if cpu_freq else None,
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent,
                "swap_total": swap.total,
                "swap_used": swap.used,
                "swap_percent": swap.percent,
            },
            "disk": disk_usage,
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv,
            },
            "system": {
                "boot_time": boot_time.isoformat(),
                "uptime_seconds": uptime.total_seconds(),
            },
        }

    def get_process_info(self, limit: int = 10) -> List[Dict]:
        """Get information about running processes."""
        processes = []

        for proc in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_info", "status"]
        ):
            try:
                info = proc.info

                # Skip system processes if configured
                if info["name"] in self.config["ignore_processes"]:
                    continue

                memory_mb = (
                    info["memory_info"].rss / 1024 / 1024 if info["memory_info"] else 0
                )

                processes.append(
                    {
                        "pid": info["pid"],
                        "name": info["name"],
                        "cpu_percent": info["cpu_percent"] or 0,
                        "memory_mb": memory_mb,
                        "status": info["status"],
                    }
                )

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # Sort by CPU usage, then by memory
        processes.sort(key=lambda x: (x["cpu_percent"], x["memory_mb"]), reverse=True)

        return processes[:limit]

    def check_alerts(self, system_info: Dict, processes: List[Dict]) -> List[Dict]:
        """Check for alert conditions."""
        alerts = []
        thresholds = self.config["thresholds"]

        # CPU Alert
        if system_info["cpu"]["percent"] > thresholds["cpu_percent"]:
            alerts.append(
                {
                    "type": "HIGH_CPU",
                    "severity": "WARNING",
                    "message": f"CPU usage: {system_info['cpu']['percent']:.1f}%",
                    "threshold": thresholds["cpu_percent"],
                    "value": system_info["cpu"]["percent"],
                }
            )

        # Memory Alert
        if system_info["memory"]["percent"] > thresholds["memory_percent"]:
            alerts.append(
                {
                    "type": "HIGH_MEMORY",
                    "severity": "WARNING",
                    "message": f"Memory usage: {system_info['memory']['percent']:.1f}%",
                    "threshold": thresholds["memory_percent"],
                    "value": system_info["memory"]["percent"],
                }
            )

        # Disk Alerts
        for mount, disk_info in system_info["disk"].items():
            if disk_info["percent"] > thresholds["disk_percent"]:
                alerts.append(
                    {
                        "type": "HIGH_DISK",
                        "severity": "CRITICAL",
                        "message": f"Disk usage on {mount}: {disk_info['percent']:.1f}%",
                        "threshold": thresholds["disk_percent"],
                        "value": disk_info["percent"],
                        "mount": mount,
                    }
                )

        # Process Alerts
        for proc in processes[:5]:  # Check top 5 processes
            if proc["memory_mb"] > thresholds["process_memory_mb"]:
                alerts.append(
                    {
                        "type": "HIGH_PROCESS_MEMORY",
                        "severity": "INFO",
                        "message": f"Process {proc['name']} (PID {proc['pid']}): {proc['memory_mb']:.1f}MB",
                        "threshold": thresholds["process_memory_mb"],
                        "value": proc["memory_mb"],
                        "process": proc["name"],
                        "pid": proc["pid"],
                    }
                )

            if proc["cpu_percent"] > thresholds["process_cpu_percent"]:
                alerts.append(
                    {
                        "type": "HIGH_PROCESS_CPU",
                        "severity": "INFO",
                        "message": f"Process {proc['name']} (PID {proc['pid']}): {proc['cpu_percent']:.1f}% CPU",
                        "threshold": thresholds["process_cpu_percent"],
                        "value": proc["cpu_percent"],
                        "process": proc["name"],
                        "pid": proc["pid"],
                    }
                )

        return alerts

    def format_bytes(self, bytes_value: int) -> str:
        """Format bytes in human readable format."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"

    def print_status(
        self, system_info: Dict, processes: List[Dict], alerts: List[Dict]
    ):
        """Print formatted system status."""
        print("\\n" + "=" * 70)
        print(f"🖥️  SYSTEM MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        # System Overview
        uptime_hours = system_info["system"]["uptime_seconds"] / 3600
        print(f"⏱️  Uptime: {uptime_hours:.1f} hours")

        # CPU Status
        cpu = system_info["cpu"]
        cpu_emoji = (
            "🔥" if cpu["percent"] > 80 else "⚡" if cpu["percent"] > 50 else "✅"
        )
        print(f"{cpu_emoji} CPU: {cpu['percent']:.1f}% ({cpu['count']} cores)")

        # Memory Status
        mem = system_info["memory"]
        mem_emoji = (
            "🔥" if mem["percent"] > 85 else "⚠️" if mem["percent"] > 70 else "✅"
        )
        print(
            f"{mem_emoji} Memory: {mem['percent']:.1f}% ({self.format_bytes(mem['used'])}/{self.format_bytes(mem['total'])})"
        )

        # Disk Status
        print("\\n💾 DISK USAGE:")
        for mount, disk in system_info["disk"].items():
            disk_emoji = (
                "🔥" if disk["percent"] > 90 else "⚠️" if disk["percent"] > 80 else "✅"
            )
            print(
                f"   {disk_emoji} {mount}: {disk['percent']:.1f}% ({self.format_bytes(disk['used'])}/{self.format_bytes(disk['total'])})"
            )

        # Top Processes
        print(f"\\n🔄 TOP PROCESSES ({len(processes)}):")
        print("   PID    NAME                 CPU%    MEMORY     STATUS")
        print("   " + "-" * 55)
        for proc in processes:
            memory_str = f"{proc['memory_mb']:.1f}MB"
            print(
                f"   {proc['pid']:<6} {proc['name']:<20} {proc['cpu_percent']:<7.1f} {memory_str:<10} {proc['status']}"
            )

        # Alerts
        if alerts:
            print(f"\\n🚨 ALERTS ({len(alerts)}):")
            severity_emoji = {"CRITICAL": "🔥", "WARNING": "⚠️", "INFO": "ℹ️"}
            for alert in alerts:
                emoji = severity_emoji.get(alert["severity"], "❓")
                print(f"   {emoji} {alert['message']}")
        else:
            print("\\n✅ No alerts - system running normally")

    def monitor_continuous(self, interval: int = 5, duration: Optional[int] = None):
        """Run continuous monitoring."""
        print(f"🔍 Starting continuous monitoring (interval: {interval}s)")
        if duration:
            print(f"   Duration: {duration} seconds")
        print("   Press Ctrl+C to stop\\n")

        iteration = 0
        start_time = time.time()

        try:
            while True:
                # Check duration limit
                if duration and (time.time() - start_time) > duration:
                    break

                # Collect data
                system_info = self.get_system_info()
                processes = self.get_process_info(
                    self.config["monitoring"]["top_processes"]
                )
                alerts = self.check_alerts(system_info, processes)

                # Clear screen and display (simple version for cross-platform compatibility)
                if iteration > 0:
                    print("\\n" + "=" * 70)

                self.print_status(system_info, processes, alerts)

                iteration += 1
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\\n\\n🛑 Monitoring stopped by user")
            elapsed = time.time() - start_time
            print(f"📊 Monitored for {elapsed:.1f} seconds ({iteration} iterations)")


def main():
    parser = argparse.ArgumentParser(
        description="System resource monitor and alerting tool"
    )
    parser.add_argument("--config", "-c", type=Path, help="Configuration file (JSON)")
    parser.add_argument(
        "--continuous", action="store_true", help="Run continuous monitoring"
    )
    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=5,
        help="Monitoring interval in seconds (default: 5)",
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=int,
        help="Monitoring duration in seconds (continuous mode)",
    )
    parser.add_argument(
        "--processes",
        "-p",
        type=int,
        default=10,
        help="Number of top processes to show (default: 10)",
    )
    parser.add_argument(
        "--json", "-j", action="store_true", help="Output in JSON format"
    )

    args = parser.parse_args()

    # Initialize monitor
    monitor = SystemMonitor(args.config)

    if args.continuous:
        # Continuous monitoring mode
        monitor.monitor_continuous(args.interval, args.duration)
    else:
        # Single snapshot mode
        system_info = monitor.get_system_info()
        processes = monitor.get_process_info(args.processes)
        alerts = monitor.check_alerts(system_info, processes)

        if args.json:
            # JSON output for programmatic use
            output = {"system": system_info, "processes": processes, "alerts": alerts}
            print(json.dumps(output, indent=2, default=str))
        else:
            # Human-readable output
            monitor.print_status(system_info, processes, alerts)

        # Exit code based on alert severity
        if any(alert["severity"] == "CRITICAL" for alert in alerts):
            sys.exit(2)
        elif any(alert["severity"] == "WARNING" for alert in alerts):
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == "__main__":
    main()
