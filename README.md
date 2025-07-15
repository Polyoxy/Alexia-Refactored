### # Alexia - Agentic AI CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A modern, agentic command-line interface for interacting with Ollama's AI models, featuring tool-driven capabilities and a polished terminal experience.

## 🚀 Features

- 🤖 Tool-driven AI interactions with intelligent tool invocation
- 🎨 Rich terminal UI with markdown support and styled output
- 🔄 Asynchronous tool execution with progress indicators
- 🛡️ Secure tool permission system with user confirmation
- 📚 Modular architecture for easy extension
- 📄 Built-in file reading capabilities
- 🔄 Graceful error handling and session management

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Ollama running locally (default: http://localhost:11434)

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/Polyoxy/Alexia-Refactored.git
cd Alexia-Refactored

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m alexia.ui.__main__
```

## 📋 Usage

### Basic Interaction

1. Start the application:
   ```bash
   python -m alexia.ui.__main__
   ```

2. Type your questions or commands:
   - Use natural language to interact with the AI
   - The AI will automatically detect when to use tools
   - Confirm tool usage when prompted

3. Exit the application:
   - Type `/exit` or `/quit`
   - Press Ctrl+C

### Tool Usage

- The AI can automatically invoke tools based on context
- Tools include:
  - `read_file`: Read and process local files
  - More tools coming soon!
- Tool usage requires user confirmation for security

## 🛠️ Development

### Project Structure

```
alexia/
├── alexia/                # Source code
│   ├── core/             # Core application logic
│   ├── services/         # External service integrations
│   ├── tools/           # Agentic tools and registry
│   └── ui/              # User interface components
├── tests/               # Test files
└── docs/               # Documentation
```

### Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

Please make sure to:
- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation
- Maintain backward compatibility

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ using Python and Rich for terminal UI
- Special thanks to the Ollama team for their amazing AI platform
- Inspired by modern CLI tooling and agentic AI systems

## 📱 Contact

For support, questions, or contributions, please open an issue or submit a pull request.

---

Made with ❤️ by the Alexia development team 🚀
