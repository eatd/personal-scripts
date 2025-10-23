# Professional Development Toolkit

[![CI/CD Pipeline](https://github.com/eatd/personal-scripts/actions/workflows/ci.yml/badge.svg)](https://github.com/eatd/personal-scripts/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/eatd/personal-scripts/graphs/commit-activity)

> **A production-ready collection of Python utilities demonstrating modern software engineering practices, async programming patterns, and enterprise-grade architecture.**

This repository showcases professional development tools and automation scripts I've built to solve real-world problems in software development, system administration, and DevOps workflows. Each tool is designed with scalability, maintainability, and production-readiness in mind.

---

## 🎯 **Key Differentiators**

### **Modern Python Patterns**
- ✅ **Async/Await** - Concurrent operations with `asyncio` and `aiohttp`
- ✅ **Type Hints** - Full type annotations for better IDE support and type safety
- ✅ **Dataclasses** - Modern data structures with automatic methods
- ✅ **Context Managers** - Proper resource management and cleanup
- ✅ **Walrus Operator** - Python 3.8+ syntax for cleaner code

### **Enterprise Features**
- 🔐 **Security** - Input validation, rate limiting, and vulnerability scanning
- 📊 **Observability** - Structured logging, metrics, and performance monitoring
- 🔄 **Resilience** - Retry logic with exponential backoff and circuit breakers
- 💾 **Caching** - Intelligent caching strategies for performance optimization
- 🧪 **Testing** - Comprehensive test suite with mocking and fixtures

### **DevOps Integration**
- 🚀 **CI/CD** - GitHub Actions pipelines with automated testing and security scans
- 📦 **Containerization** - Docker-ready with minimal dependencies
- 🔍 **Code Quality** - Automated linting (Ruff), formatting (Black), and type checking (mypy)
- 📈 **Code Analysis** - Complexity metrics, dead code detection, and maintainability scoring

---

## 📂 **Project Structure**

```
personal-scripts/
├── .github/workflows/    # CI/CD pipelines with automated testing & security scans
├── automation/          # Enterprise backup, deployment, and workflow automation
├── development-tools/   # Project scaffolding, dependency auditing, port scanning
├── file-management/     # Concurrent duplicate detection, batch operations, smart organization
├── system-utilities/    # Process monitoring, resource tracking, system health checks
├── text-processing/     # Log analysis, document conversion, data extraction
├── web-data/           # Async API clients, URL shortening, data fetching
└── tests/              # Comprehensive test suite with pytest (TDD practices)
```

---

## 🛠️ **Featured Tools**

### **Development Tools** (`development-tools/`)

#### `project_setup.py` - Python Project Scaffolding
```bash
# Create production-ready Python project with one command
python project_setup.py my-api --type fastapi --docker --ci-cd
```
**Features:**
- 🏗️ Modern `pyproject.toml` configuration with Poetry/pip-tools support
- 🧪 Pre-configured testing (pytest, coverage, tox)
- 🔄 GitHub Actions CI/CD templates
- 🐳 Dockerfiles with multi-stage builds
- 📝 Professional README and documentation structure

#### `dependency_audit.py` - Security Vulnerability Scanner
```bash
# Scan project dependencies for known vulnerabilities
python dependency_audit.py --path ./my-project --output audit-report.json
```
**Features:**
- 🔐 Integration with pip-audit and Safety databases
- 📊 Severity classification and CVSS scoring
- 📧 Automated alerts for critical vulnerabilities
- 📄 JSON/HTML report generation for CI/CD

#### `port_checker.py` - Concurrent Network Port Scanner
```bash
# Scan ports with service identification
python port_checker.py 192.168.1.0/24 --ports 22,80,443,3306 --workers 50
```
**Features:**
- ⚡ Concurrent scanning with ThreadPoolExecutor
- 🎯 Service fingerprinting and version detection
- 📊 Export results to JSON/CSV
- 🔍 Common service identification

---

### **Web & API Tools** (`web-data/`)

#### `url_shortener.py` - Async URL Shortener
```bash
# Shorten URLs with caching and multiple service fallback
python url_shortener.py https://example.com/very/long/url --service auto --stats
```
**Features:**
- ⚡ **Async/await** with `aiohttp` for concurrent requests
- 💾 **Intelligent caching** with persistent storage
- 🔄 **Automatic failover** between multiple services (is.gd, TinyURL)
- 🔁 **Retry logic** with exponential backoff
- ⏱️ **Rate limiting** to respect service quotas
- 📊 **Performance metrics** and cache hit rate tracking

**Technical Highlights:**
```python
# Concurrent batch processing with async
async def shorten_urls_batch_async(urls: List[str]) -> List[ShortenResult]:
    tasks = [self.shorten_with_fallback_async(url) for url in urls]
    return await asyncio.gather(*tasks)
```

---

### **File Management** (`file-management/`)

#### `duplicate_finder.py` - Hash-Based Duplicate Detector
```bash
# Find duplicates across directories with concurrent hashing
python duplicate_finder.py /path/to/scan --algorithm sha256 --workers 8 --remove
```
**Features:**
- 🔢 **Concurrent hashing** with ThreadPoolExecutor
- 🎯 **Smart filtering** by size, extension, and patterns
- 🗑️ **Safe deletion** with dry-run mode
- 📊 **Space savings** calculation
- 💾 **JSON export** for further analysis

#### `batch_rename.py` - Professional File Renaming
```bash
# Rename files with patterns, regex, and undo support
python batch_rename.py replace /path/to/files "old" "new" --regex --execute
```
**Features:**
- 🔄 **Undo capability** with operation logging
- 🎨 **Multiple operations**: sequential numbering, case conversion, regex replace, sanitize
- ✅ **Validation** prevents conflicts and invalid filenames
- 🧪 **Dry-run mode** for safety

#### `folder_organizer.py` - Smart File Organization
```bash
# Organize files by type, date, size, or age
python folder_organizer.py type /downloads --execute --conflict rename
```
**Features:**
- 📁 **Multiple strategies**: by type, date, size, age
- ⚙️ **Customizable rules** via JSON configuration
- 🔄 **Conflict resolution**: rename, skip, or overwrite
- ↩️ **Undo support** for safe experimentation

---

### **Automation Suite** (`automation/`)

#### `backup_automation.py` - Enterprise Backup Solution
```bash
# Incremental backups with compression and verification
python backup_automation.py create /data /backups --verify
```
**Features:**
- 📦 **Incremental backups** to save time and space
- 🗜️ **Compression** with multiple algorithms (gzip, bz2, xz)
- ✅ **Integrity verification** with checksums
- 🔄 **Automatic rotation** based on retention policies
- 📊 **Detailed statistics** and compression ratios

---

### **System Utilities** (`system-utilities/`)

#### `process_monitor.py` - Real-Time System Monitor
```bash
# Monitor system resources with configurable alerts
python process_monitor.py --interval 5 --alert-cpu 80 --alert-memory 85
```
**Features:**
- 📊 **Real-time monitoring** of CPU, memory, disk, network
- 🚨 **Configurable alerts** with thresholds
- 💾 **JSON configuration** with environment variables
- 📈 **Historical data** tracking and export
- 🔔 **Multiple notification channels** (email, webhook, stdout)

---

## 🧪 **Testing & Quality Assurance**

### **Test Coverage**
```bash
pytest --cov=. --cov-report=html --cov-report=term-missing
```

**Test Suite Features:**
- ✅ **Unit tests** with pytest and mocking
- ✅ **Integration tests** for end-to-end workflows
- ✅ **Async tests** with pytest-asyncio
- ✅ **Parametrized tests** for comprehensive coverage
- ✅ **Fixtures** for reusable test data

### **Code Quality Pipeline**

```yaml
# Automated quality checks in CI/CD
- Linting (Ruff)
- Formatting (Black, isort)
- Type checking (mypy)
- Security scanning (Bandit, Safety, pip-audit)
- Complexity analysis (Radon)
- Dead code detection (Vulture)
```

---

## 🚀 **Installation & Setup**

### **Quick Start**
```bash
# Clone repository
git clone https://github.com/eatd/personal-scripts.git
cd personal-scripts

# Install dependencies (optional - most tools use stdlib only)
pip install -r requirements.txt

# Run any script
python web-data/url_shortener.py --help
```

### **Development Setup**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .
isort .

# Type checking
mypy .

# Security scan
bandit -r .
```

---

## 📊 **Performance Characteristics**

| Tool | Operation | Performance | Memory |
|------|-----------|------------|--------|
| `duplicate_finder.py` | 10K files | < 30s | < 100MB |
| `url_shortener.py` | 100 URLs (async) | < 5s | < 20MB |
| `batch_rename.py` | 1K files | < 2s | < 10MB |
| `backup_automation.py` | 1GB data | < 60s | < 50MB |
| `process_monitor.py` | Continuous | < 1% CPU | < 15MB |

---

## 🏗️ **Architecture Patterns**

### **Async/Concurrent Design**
```python
# Concurrent processing with proper error handling
async def process_batch(items: List[str]) -> List[Result]:
    async with aiohttp.ClientSession() as session:
        tasks = [process_item(session, item) for item in items]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

### **Configuration Management**
```python
# JSON config with environment variable override
{
  "api": {
    "key": "${API_KEY:default_value}",
    "timeout": "${TIMEOUT:30}",
    "retries": 3
  }
}
```

### **Resilience Patterns**
```python
# Retry with exponential backoff
for attempt in range(max_retries):
    try:
        return await operation()
    except TemporaryError:
        if attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)
```

---

## 🤝 **Contributing**

Contributions are welcome! This repository follows professional development practices:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Write tests** for new functionality
4. **Ensure** all tests pass and code is formatted
5. **Commit** changes (`git commit -m 'Add amazing feature'`)
6. **Push** to branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

### **Code Standards**
- ✅ Type hints for all functions
- ✅ Docstrings for modules, classes, and functions
- ✅ Black formatting (88 character line length)
- ✅ Comprehensive error handling
- ✅ Unit tests with >80% coverage

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 **Author**

**eatd** - [GitHub Profile](https://github.com/eatd)

*This repository demonstrates production-ready Python development with modern practices, async programming, comprehensive testing, and DevOps integration. All tools are designed for real-world use cases with scalability and maintainability as core principles.*

---

## 🔗 **Related Projects**

- Looking for API examples? Check out my REST API projects
- Interested in data processing? See my data pipeline repositories
- Need DevOps automation? Explore my infrastructure-as-code repos

---

**⭐ If you find these tools useful, please consider starring the repository!**
