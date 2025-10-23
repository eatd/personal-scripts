#!/usr/bin/env python3
"""
Project scaffolding tool for Python development.
Creates consistent project structure with modern Python tooling setup.

Author: Personal development workflow optimization
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_CONFIG = {
    "structure": {
        "src": True,
        "tests": True,
        "docs": False,
        "scripts": False,
        "config": False,
    },
    "tools": {
        "pytest": True,
        "black": True,
        "ruff": True,
        "mypy": False,
        "pre_commit": False,
    },
    "templates": {"github_actions": False, "dockerfile": False, "makefile": False},
}


class ProjectScaffold:
    def __init__(self, name, config=None):
        self.name = name
        self.root = Path(name)
        self.config = config or DEFAULT_CONFIG

    def create_structure(self):
        """Create the basic project structure."""
        print(f"📁 Creating project structure for '{self.name}'...")

        # Create root directory
        self.root.mkdir(exist_ok=True)

        # Source code structure
        if self.config["structure"]["src"]:
            src_dir = self.root / "src" / self.name
            src_dir.mkdir(parents=True, exist_ok=True)
            (src_dir / "__init__.py").touch()

            # Main module with basic structure
            main_content = f'''"""
{self.name.title()} - Main module
"""

__version__ = "0.1.0"
__author__ = "Development Portfolio"

def main():
    """Main entry point."""
    print(f"{{__name__}} v{{__version__}}")

if __name__ == "__main__":
    main()
'''
            (src_dir / "main.py").write_text(main_content)

        # Test structure
        if self.config["structure"]["tests"]:
            tests_dir = self.root / "tests"
            tests_dir.mkdir(exist_ok=True)
            (tests_dir / "__init__.py").touch()

            test_content = f'''"""
Test suite for {self.name}
"""
import pytest
from src.{self.name}.main import main

def test_main_runs():
    """Test that main function executes."""
    # Basic smoke test
    try:
        main()
        assert True
    except Exception as e:
        pytest.fail(f"main() raised {{e}}")

def test_version_defined():
    """Test that version is properly defined."""
    from src.{self.name} import __version__
    assert __version__
    assert isinstance(__version__, str)
'''
            (tests_dir / f"test_{self.name}.py").write_text(test_content)

        # Additional directories
        for dir_name, enabled in self.config["structure"].items():
            if enabled and dir_name not in ["src", "tests"]:
                (self.root / dir_name).mkdir(exist_ok=True)

    def create_requirements(self):
        """Create requirements files."""
        base_reqs = []
        dev_reqs = ["pytest>=7.0", "pytest-cov>=4.0"]

        if self.config["tools"]["black"]:
            dev_reqs.append("black>=23.0")
        if self.config["tools"]["ruff"]:
            dev_reqs.append("ruff>=0.1.0")
        if self.config["tools"]["mypy"]:
            dev_reqs.append("mypy>=1.0")

        # Write requirements files
        (self.root / "requirements.txt").write_text("\\n".join(base_reqs) + "\\n")
        (self.root / "requirements-dev.txt").write_text("\\n".join(dev_reqs) + "\\n")

    def create_pyproject_toml(self):
        """Create modern Python project configuration."""
        config = f'''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{self.name}"
version = "0.1.0"
description = "Python project: {self.name}"
authors = [{{name = "Developer", email = "dev@example.com"}}]
license = {{text = "MIT"}}
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]

[project.scripts]
{self.name} = "src.{self.name}.main:main"

[tool.black]
line-length = 88
target-version = ["py38"]

[tool.ruff]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = []
line-length = 88
target-version = "py38"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src --cov-report=term-missing"
'''
        (self.root / "pyproject.toml").write_text(config)

    def init_git(self):
        """Initialize git repository with standard configuration."""
        print("🔧 Initializing git repository...")

        # Initialize git
        subprocess.run(["git", "init"], cwd=self.root, capture_output=True)

        # Create comprehensive .gitignore
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
*.log
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Local development
local_settings.py
.local/
"""
        (self.root / ".gitignore").write_text(gitignore_content)

        # Initial commit
        subprocess.run(["git", "add", "."], cwd=self.root, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"Initial commit: {self.name} project scaffold"],
            cwd=self.root,
            capture_output=True,
        )

    def create_readme(self):
        """Create professional README."""
        readme_content = f"""# {self.name.title()}

A Python project created with professional development practices.

## Features

- Modern Python packaging with `pyproject.toml`
- Comprehensive test suite with pytest
- Code formatting with Black
- Linting with Ruff
- Git integration with sensible defaults

## Installation

```bash
# Development installation
pip install -e ".[dev]"

# Production installation
pip install {self.name}
```

## Usage

```bash
# Run the application
{self.name}

# Or as a module
python -m src.{self.name}.main
```

## Development

```bash
# Run tests
pytest

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Run tests with coverage
pytest --cov=src --cov-report=html
```

## License

MIT License - see LICENSE file for details.

---

*Generated with project scaffold tool - {datetime.now().strftime("%Y-%m-%d")}*
"""
        (self.root / "README.md").write_text(readme_content)


def load_config(config_file):
    """Load configuration from JSON file."""
    try:
        with open(config_file) as f:
            user_config = json.load(f)

        # Merge with defaults
        config = DEFAULT_CONFIG.copy()
        for section, values in user_config.items():
            if section in config:
                config[section].update(values)
            else:
                config[section] = values

        return config
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"⚠️  Config file error: {e}")
        print("Using default configuration...")
        return DEFAULT_CONFIG


def main():
    parser = argparse.ArgumentParser(
        description="Create professional Python project scaffold"
    )
    parser.add_argument("name", help="Project name")
    parser.add_argument(
        "--config", "-c", help="Configuration file (JSON)", default=None
    )
    parser.add_argument("--no-git", action="store_true", help="Skip git initialization")
    parser.add_argument(
        "--minimal", action="store_true", help="Create minimal structure only"
    )

    args = parser.parse_args()

    # Load configuration
    if args.config:
        config = load_config(args.config)
    elif args.minimal:
        config = {
            "structure": {"src": True, "tests": False, "docs": False},
            "tools": {"pytest": False, "black": False, "ruff": False},
            "templates": {},
        }
    else:
        config = DEFAULT_CONFIG

    # Validate project name
    if not args.name.isidentifier():
        print(f"❌ Invalid project name: '{args.name}'")
        print("Project name must be a valid Python identifier")
        sys.exit(1)

    if Path(args.name).exists():
        print(f"❌ Directory '{args.name}' already exists")
        sys.exit(1)

    # Create project
    scaffold = ProjectScaffold(args.name, config)

    try:
        scaffold.create_structure()
        scaffold.create_requirements()
        scaffold.create_pyproject_toml()
        scaffold.create_readme()

        if not args.no_git:
            scaffold.init_git()

        print(f"✅ Project '{args.name}' created successfully!")
        print(f"📁 Location: {Path(args.name).absolute()}")
        print("\\n🚀 Next steps:")
        print(f"   cd {args.name}")
        print("   python -m venv venv")
        print(
            "   source venv/bin/activate  # or venv\\\\Scripts\\\\activate on Windows"
        )
        print("   pip install -e '.[dev]'")
        print("   pytest")

    except Exception as e:
        print(f"❌ Error creating project: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
