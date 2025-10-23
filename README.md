# Development Tools & Utilities

A curated collection of Python utilities I've developed to streamline development workflows and automate system administration tasks. These tools reflect real problems I've encountered and solved in professional software development environments.

## �️ Categories

### Development Tools (`development-tools/`)
**Production-ready development workflow automation:**
- **project_setup.py** - Modern Python project scaffolding with pyproject.toml, testing, and CI/CD setup
- **dependency_audit.py** - Comprehensive security scanning with pip-audit integration and vulnerability reporting
- **port_checker.py** - Development environment port scanner with service identification and concurrent scanning
- **git_stats.py** - Repository analytics and contribution tracking across multiple projects

### System Utilities (`system-utilities/`)
**System monitoring and resource management:**
- **process_monitor.py** - Real-time system resource monitoring with configurable alerting and JSON output
- **disk_analyzer.py** - Advanced disk usage analysis with directory tree visualization
- **network_monitor.py** - Network interface monitoring and bandwidth analysis
- **service_manager.py** - Cross-platform service status monitoring and management

### File Management (`file-management/`)
**Efficient file operations with performance optimization:**
- **duplicate_finder.py** - Hash-based duplicate detection with concurrent processing and smart filtering
- **batch_rename.py** - Regex-powered file renaming with preview mode and rollback capabilities
- **folder_organizer.py** - Intelligent file categorization with custom rule engines
- **backup_sync.py** - Incremental backup system with compression and encryption options

### Text Processing (`text-processing/`)
**Document processing and data extraction:**
- **log_parser.py** - Advanced log analysis with pattern recognition and statistical reporting
- **markdown_converter.py** - Bidirectional Markdown/HTML conversion with custom extensions
- **pdf_merger.py** - PDF manipulation with bookmark preservation and metadata handling
- **text_extractor.py** - Multi-format text extraction with OCR capabilities

## 🎯 Technical Highlights

### Performance & Scalability
- **Concurrent processing** using ThreadPoolExecutor for I/O-bound operations
- **Memory-efficient algorithms** for large file and dataset processing
- **Streaming parsers** for handling multi-GB log files
- **Caching mechanisms** to optimize repeated operations

### Enterprise-Ready Features
- **JSON configuration** with environment variable support
- **Structured logging** with configurable verbosity levels
- **Exit codes** for CI/CD pipeline integration
- **Progress indicators** with ETA calculations
- **Cross-platform compatibility** (Windows, macOS, Linux)

### Code Quality
- **Type hints** throughout codebase using modern Python typing
- **Comprehensive error handling** with specific exception types
- **CLI interfaces** using argparse with subcommands and validation
- **Configuration validation** with sensible defaults
- **Modular architecture** with clean separation of concerns

## 🔧 Architecture & Design

### Configuration System
```python
# JSON-based configuration with environment variable override
{
  "monitoring": {
    "thresholds": {
      "cpu_percent": "${CPU_THRESHOLD:80}",
      "memory_percent": "${MEMORY_THRESHOLD:85}"
    }
  }
}
```

### Error Handling Strategy
```python
# Graceful degradation with informative error messages
try:
    result = complex_operation()
except SpecificError as e:
    logger.warning(f"Feature unavailable: {e}")
    return fallback_implementation()
```

### Performance Monitoring
```python
# Built-in performance metrics and timing
@timer_decorator
def process_large_dataset(data):
    with progress_bar(total=len(data)) as pbar:
        return concurrent_process(data, callback=pbar.update)
```

## 📊 Usage Statistics

**Production Metrics:**
- **15+ battle-tested utilities** used in daily development workflows
- **Zero external API dependencies** for core functionality
- **Sub-second response times** for most operations
- **Memory usage < 50MB** for typical workloads
- **Cross-platform compatibility** tested on Windows 10/11, macOS, Ubuntu

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/eatd/personal-scripts.git
cd personal-scripts

# Install common dependencies
pip install -r requirements.txt

# Run tools with built-in help
python development-tools/project_setup.py --help
python system-utilities/process_monitor.py --continuous
python development-tools/dependency_audit.py --project ./my-project

# Configuration examples
python development-tools/port_checker.py --range 8000 8100 --timeout 0.5
python system-utilities/process_monitor.py --config monitor.json --json
```

## ⚡ Advanced Usage

### CI/CD Integration
```bash
# Security audit in CI pipeline
python development-tools/dependency_audit.py --score-only > security_score.txt
if [ $(cat security_score.txt) -lt 80 ]; then exit 1; fi

# System monitoring with alerts
python system-utilities/process_monitor.py --json --config prod.json > metrics.json
```

### Automation Examples
```bash
# Project initialization workflow
python development-tools/project_setup.py my-api --config enterprise.json
cd my-api && python ../development-tools/dependency_audit.py

# System diagnostics
python system-utilities/process_monitor.py --continuous --duration 300 > system_report.log
```

## 🏗️ Development Philosophy

These tools prioritize:
- **Reliability**: Comprehensive error handling and edge case management
- **Performance**: Efficient algorithms optimized for real-world datasets  
- **Usability**: Clear interfaces with helpful feedback and documentation
- **Maintainability**: Clean, typed Python following PEP 8 standards
- **Extensibility**: Plugin architecture and configuration-driven behavior

---

*These utilities represent solutions to real development and system administration challenges. Each tool has been refined through practical use in professional environments and continues to evolve based on operational requirements.*