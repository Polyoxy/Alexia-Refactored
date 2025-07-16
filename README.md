# Alexia - Agentic AI Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen.svg)](https://docs.alexia.ai)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/AuroraFoundation?label=Sponsor&logo=GitHub)](https://github.com/sponsors/AuroraFoundation)
[![Patreon](https://img.shields.io/badge/Patreon-Support-orange.svg)](https://patreon.com/your-patreon-username)

Alexia is a sophisticated AI assistant that combines natural language understanding with intelligent tool orchestration. Built for developers and professionals, Alexia delivers a seamless, productive experience through its advanced agentic capabilities and polished terminal interface.

🔍 **Now with enhanced directory navigation and tool execution!**

## 🚀 Key Features

### Intelligent AI Interaction
- **Natural Language Processing**: Advanced understanding of complex queries
- **Agentic Tool Orchestration**: Smart tool invocation based on context
- **Secure Tool Management**: User-confirmed tool execution
- **Natural Directory Navigation**: Intuitive path handling with commands like "go to my documents"

### Enhanced Terminal Experience
- **Rich Markdown Support**: Beautifully formatted output
- **Interactive UI Elements**: Progress indicators and status updates
- **Professional Styling**: Clean, modern interface
- **Clear Tool Execution**: Visual feedback for all operations

### Smart File System Integration
- **Natural Language Path Resolution**: Understands paths like "desktop" or "downloads"
- **Context-Aware Navigation**: Maintains directory context across commands
- **Safe Operations**: Confirmation prompts for all file system changes

### Development-Focused
- **Modular Architecture**: Easy to extend and customize
- **Built-in Tools**: File system integration and more
- **Professional Integration**: Designed for developer workflows
- **Debugging Support**: Built-in logging and inspection tools

### Robust Features
- **Asynchronous Processing**: Smooth tool execution
- **Error Handling**: Graceful session management
- **Documentation**: Comprehensive guides and examples

## 🚀 Quick Start

```bash
# Clone and install
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Start Alexia
python -m alexia.ui.__main__

# Try these examples:
>>> list files in this directory
>>> go to my documents
>>> show me what's on my desktop
>>> create a new file called hello.txt
```

## 📋 Getting Started

### Basic Usage

1. **Start Alexia**
   ```bash
   python -m alexia.ui.__main__
   ```

2. **Interact with AI**
   - Type natural language queries
   - AI automatically uses appropriate tools
   - Confirm tool usage when prompted

3. **Exit Session**
   - Type `/exit` or `/quit`
   - Press Ctrl+C

### Command Line Options

```bash
python -m alexia.ui.__main__ --help
```

Available options:
- `--host`: Specify Ollama host URL
- `--model`: Set default AI model
- `--system`: Custom system prompt
- `-q, --quiet`: Suppress startup messages

### Intelligent Tools

Alexia features an intelligent tool system that automatically selects the best tools for your tasks:

- **File System**: Navigate and manage files with natural language
  ```
  list files in this directory
  go to my documents
  show me what's on my desktop
  create a new file called hello.txt
  ```
- **Code Analysis**: Understand and work with source code
- **Web Integration**: Access external resources
- **Custom Tools**: Extend functionality with your own tools

### Natural Language Directory Navigation

Alexia understands various ways to navigate your file system:
- **Basic Navigation**: "go to documents", "navigate to downloads"
- **Relative Paths**: "go up one level", "go to parent directory"
- **Home Shortcuts**: "go home", "take me to root"
- **Smart Suggestions**: Auto-completes partial directory names

Example commands:
```
go to my documents
navigate to desktop
list files in downloads
what's in this folder?
```

#### Tool Security & Confirmation

Alexia ensures safe and transparent operations:

- **Explicit Confirmation**: Every tool execution requires explicit user approval
- **Clear Prompts**: Understandable descriptions of requested actions
- **Visual Feedback**: Clear success/error messages for all operations
- **Session Persistence**: Maintains directory context across commands
- **Safe Execution**: Runs tools in a controlled environment

Example confirmation prompt:
```
⚠️  Confirmation Required
Change directory to: C:\Users\username\Documents
› Confirm? (y/n): 
```

## 🛠️ Project Structure

```
alexia/
├── alexia/                # Core Application
│   ├── core/             # Application Logic
│   │   ├── session.py    # Chat session management
│   │   └── config.py     # Configuration handling
│   ├── services/         # External Integrations
│   │   └── ollama_client.py # Ollama integration
│   ├── tools/           # Agentic Tools
│   │   ├── tool.py      # Base tool class
│   │   └── registry.py  # Tool registry
│   └── ui/              # User Interface
│       └── display.py   # Terminal UI components
├── tests/               # Test Suite
└── docs/               # Documentation
```

## 🤝 Contributing

1. **Fork Repository**
   - Click "Fork" on GitHub
   - Clone your fork locally

2. **Create Branch**
   ```bash
   git checkout -b feature/your-feature
   ```

3. **Make Changes**
   - Follow code standards
   - Add comprehensive tests
   - Update documentation
   - Run pre-commit hooks

4. **Submit Pull Request**
   - Reference relevant issues
   - Include clear descriptions
   - Add screenshots if applicable

### Code Standards
- **PEP 8 Compliance**: Strict adherence
- **Type Hints**: Required for public interfaces
- **Documentation**: Comprehensive docstrings
- **Testing**: Minimum 80% coverage
- **Linting**: Use pre-commit hooks
- **Branch Naming**: `feature/*`, `bugfix/*`, `hotfix/*`

## 📄 License & Credits

### License
- **MIT License**: See [LICENSE](LICENSE) for details

### Credits
- **Technology**: Built with Python and Rich
- **AI Platform**: Powered by Ollama
- **Inspiration**: Modern CLI design and agentic systems

### Support
- **Issues**: Open an issue on GitHub
- **Contributions**: Welcome pull requests
- **Community**: Join our Discord
- **Sponsor**: Support development via GitHub Sponsors or Patreon

### Security
- **Vulnerabilities**: Report security issues to security@alexia.ai
- **Updates**: Regular security audits and dependency updates

---

© 2025 Alexia AI. All rights reserved.

[Follow us on Twitter](https://twitter.com/alexia_ai)
[Join our Discord](https://discord.alexia.ai)
[Visit our Website](https://alexia.ai)
