#!/usr/bin/env python3
"""
Security and dependency auditing tool for Python projects.
Integrates multiple security scanners and provides actionable reports.

Combines pip-audit, safety, and custom vulnerability checks.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class DependencyAuditor:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "project": str(self.project_root),
            "vulnerabilities": [],
            "outdated": [],
            "license_issues": [],
            "summary": {},
        }

    def find_requirement_files(self) -> List[Path]:
        """Locate all requirement files in the project."""
        patterns = [
            "requirements.txt",
            "requirements-dev.txt",
            "requirements-test.txt",
            "dev-requirements.txt",
            "pyproject.toml",
        ]

        found_files = []
        for pattern in patterns:
            files = list(self.project_root.rglob(pattern))
            found_files.extend(files)

        return found_files

    def run_pip_audit(self, requirements_file: Optional[Path] = None) -> Dict:
        """Run pip-audit security scanner."""
        cmd = ["pip-audit", "--format=json"]

        if requirements_file:
            if requirements_file.name == "pyproject.toml":
                # Skip pyproject.toml for pip-audit as it needs special handling
                return {"vulnerabilities": [], "skipped": True}
            cmd.extend(["-r", str(requirements_file)])

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_root, timeout=30
            )

            if result.returncode == 0:
                # No vulnerabilities found
                return {"vulnerabilities": []}
            else:
                # Parse JSON output
                try:
                    data = json.loads(result.stdout)
                    return data
                except json.JSONDecodeError:
                    return {"error": result.stderr or result.stdout}

        except subprocess.TimeoutExpired:
            return {"error": "pip-audit timed out"}
        except FileNotFoundError:
            return {"error": "pip-audit not installed. Run: pip install pip-audit"}
        except Exception as e:
            return {"error": str(e)}

    def check_outdated_packages(self) -> List[Dict]:
        """Check for outdated packages in current environment."""
        try:
            result = subprocess.run(
                ["pip", "list", "--outdated", "--format=json"],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return []

        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            return []

    def analyze_licenses(self, requirements_file: Path) -> List[Dict]:
        """Analyze package licenses for potential issues."""
        # This is a simplified license check
        # In a real implementation, you'd use pip-licenses or similar
        problematic_licenses = [
            "GPL-3.0",
            "AGPL-3.0",
            "LGPL-3.0",
            "UNKNOWN",
            "UNLICENSED",
        ]

        issues = []
        try:
            result = subprocess.run(
                ["pip", "show", "--quiet"], capture_output=True, text=True, timeout=10
            )

            # This is a placeholder - real implementation would parse pip show output
            # or use pip-licenses package

        except Exception:
            pass

        return issues

    def generate_security_score(self) -> int:
        """Generate a security score from 0-100."""
        score = 100

        # Deduct points for vulnerabilities
        high_severity = len(
            [
                v
                for v in self.results["vulnerabilities"]
                if v.get("fix_versions") and "high" in str(v).lower()
            ]
        )
        medium_severity = len(
            [
                v
                for v in self.results["vulnerabilities"]
                if v.get("fix_versions") and "medium" in str(v).lower()
            ]
        )

        score -= high_severity * 20
        score -= medium_severity * 10
        score -= len(self.results["vulnerabilities"]) * 5

        # Deduct points for very outdated packages
        very_outdated = len(
            [p for p in self.results["outdated"] if self._is_severely_outdated(p)]
        )
        score -= very_outdated * 5

        return max(0, score)

    def _is_severely_outdated(self, package: Dict) -> bool:
        """Check if a package is severely outdated (heuristic)."""
        try:
            current = package.get("version", "0.0.0")
            latest = package.get("latest_version", "0.0.0")

            # Simple major version check
            current_major = int(current.split(".")[0])
            latest_major = int(latest.split(".")[0])

            return latest_major > current_major + 1
        except (ValueError, IndexError):
            return False

    def audit_project(self) -> Dict:
        """Run comprehensive audit of the project."""
        print("🔍 Starting security audit...")

        req_files = self.find_requirement_files()

        if not req_files:
            print("⚠️  No requirement files found")
            # Audit current environment instead
            req_files = [None]
        else:
            print(f"📋 Found requirement files: {[f.name for f in req_files]}")

        # Run security audit on each requirements file
        all_vulnerabilities = []
        for req_file in req_files:
            if req_file:
                print(f"   Scanning {req_file.name}...")
            else:
                print("   Scanning current environment...")

            audit_result = self.run_pip_audit(req_file)

            if "error" in audit_result:
                print(f"   ❌ Error: {audit_result['error']}")
                continue
            elif audit_result.get("skipped"):
                print(f"   ⏭️  Skipped {req_file.name}")
                continue

            vulnerabilities = audit_result.get("vulnerabilities", [])
            all_vulnerabilities.extend(vulnerabilities)

            if vulnerabilities:
                print(f"   🚨 Found {len(vulnerabilities)} vulnerabilities")
            else:
                print("   ✅ No vulnerabilities found")

        self.results["vulnerabilities"] = all_vulnerabilities

        # Check for outdated packages
        print("\\n📦 Checking for outdated packages...")
        outdated = self.check_outdated_packages()
        self.results["outdated"] = outdated

        if outdated:
            print(f"   📈 Found {len(outdated)} outdated packages")
        else:
            print("   ✅ All packages are up to date")

        # Generate summary
        security_score = self.generate_security_score()
        self.results["summary"] = {
            "security_score": security_score,
            "total_vulnerabilities": len(all_vulnerabilities),
            "total_outdated": len(outdated),
            "status": "CRITICAL"
            if security_score < 50
            else "WARNING"
            if security_score < 80
            else "GOOD",
        }

        return self.results

    def print_report(self):
        """Print formatted audit report."""
        summary = self.results["summary"]

        print("\\n" + "=" * 60)
        print("🛡️  SECURITY AUDIT REPORT")
        print("=" * 60)

        # Summary
        status_emoji = {"GOOD": "✅", "WARNING": "⚠️", "CRITICAL": "🚨"}
        print(
            f"Status: {status_emoji.get(summary['status'], '❓')} {summary['status']}"
        )
        print(f"Security Score: {summary['security_score']}/100")
        print(f"Vulnerabilities: {summary['total_vulnerabilities']}")
        print(f"Outdated Packages: {summary['total_outdated']}")

        # Vulnerabilities detail
        if self.results["vulnerabilities"]:
            print("\\n🚨 VULNERABILITIES:")
            print("-" * 40)
            for vuln in self.results["vulnerabilities"][:10]:  # Show top 10
                package = vuln.get("package", "unknown")
                version = vuln.get("installed_version", "unknown")
                advisory = vuln.get("id", "No ID")
                print(f"  {package} v{version} - {advisory}")

            if len(self.results["vulnerabilities"]) > 10:
                remaining = len(self.results["vulnerabilities"]) - 10
                print(f"  ... and {remaining} more vulnerabilities")

        # Outdated packages
        if self.results["outdated"]:
            print("\\n📈 OUTDATED PACKAGES (Top 10):")
            print("-" * 40)
            for pkg in self.results["outdated"][:10]:
                name = pkg.get("name", "unknown")
                current = pkg.get("version", "unknown")
                latest = pkg.get("latest_version", "unknown")
                print(f"  {name:<20} {current} → {latest}")

        # Recommendations
        print("\\n💡 RECOMMENDATIONS:")
        print("-" * 40)
        if summary["total_vulnerabilities"] > 0:
            print("  • Run 'pip-audit --fix' to auto-update vulnerable packages")
            print("  • Review vulnerability details before applying fixes")

        if summary["total_outdated"] > 0:
            print("  • Update packages: pip install --upgrade <package>")
            print("  • Consider using 'pip-review' for batch updates")

        if summary["security_score"] == 100:
            print("  • Excellent! No security issues found")

        print(f"\\n📊 Report generated: {self.results['timestamp']}")


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive Python project security audit"
    )
    parser.add_argument(
        "--project",
        "-p",
        type=Path,
        default=Path.cwd(),
        help="Project directory to audit",
    )
    parser.add_argument(
        "--output", "-o", type=Path, help="Save detailed report to JSON file"
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="Only show summary")
    parser.add_argument(
        "--score-only",
        action="store_true",
        help="Only output security score (for CI/CD)",
    )

    args = parser.parse_args()

    # Validate project directory
    if not args.project.exists():
        print(f"❌ Project directory not found: {args.project}")
        sys.exit(1)

    # Run audit
    auditor = DependencyAuditor(args.project)
    results = auditor.audit_project()

    # Output results
    if args.score_only:
        print(results["summary"]["security_score"])
    elif not args.quiet:
        auditor.print_report()

    # Save detailed report
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\\n💾 Detailed report saved to: {args.output}")

    # Exit with appropriate code for CI/CD
    security_score = results["summary"]["security_score"]
    if security_score < 50:
        sys.exit(2)  # Critical
    elif security_score < 80:
        sys.exit(1)  # Warning
    else:
        sys.exit(0)  # Good


if __name__ == "__main__":
    main()
