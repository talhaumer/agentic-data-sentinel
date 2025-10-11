# Contributing to Data Sentinel

First off, thank you for considering contributing to Data Sentinel! It's people like you that make Data Sentinel such a great tool.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community](#community)

## 📜 Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to support@datasentinel.ai.

## 🤝 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Bug Report Template:**
- **Description**: Clear description of the bug
- **Steps to Reproduce**: Step-by-step instructions
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: OS, Python version, Docker version
- **Logs**: Relevant error messages or logs
- **Screenshots**: If applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title** and description
- **Use case**: Why this enhancement would be useful
- **Proposed solution**: How you think it should work
- **Alternative solutions**: Other approaches you've considered
- **Additional context**: Screenshots, mockups, or examples

### Pull Requests

We actively welcome your pull requests! Here's how to contribute code:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write or update tests
5. Update documentation
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to your branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 🛠️ Development Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized development)
- Git

### Local Development Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/agentic-data-sentinel.git
cd agentic-data-sentinel

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r server/requirements.txt
pip install -r client/requirements.txt
pip install -r requirements-dev.txt

# 4. Copy environment configuration
cp server/env.example server/.env
# Edit server/.env with your configuration

# 5. Run tests to verify setup
pytest tests/

# 6. Start development servers
python run.py
```

### Docker Development Setup

```bash
# Start development environment
docker-compose --profile dev up -d

# View logs
docker-compose logs -f

# Run tests in container
docker-compose exec data-sentinel-dev pytest
```

## 🔄 Pull Request Process

### Before Submitting

1. **Update Documentation**: Ensure README and relevant docs are updated
2. **Write Tests**: Add tests for new features or bug fixes
3. **Run Linters**: Ensure code passes all linting checks
4. **Run Tests**: All tests must pass
5. **Update CHANGELOG**: Add entry describing your changes

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated and passing
- [ ] No new warnings generated
- [ ] CHANGELOG.md updated
- [ ] Commits follow conventional commit format

### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

**Examples:**
```bash
feat: add support for PostgreSQL database
fix: resolve memory leak in anomaly detection agent
docs: update Docker deployment guide
test: add unit tests for validation agent
```

## 📏 Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some project-specific conventions:

- **Line Length**: Maximum 100 characters
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings
- **Imports**: Organized with `isort`
- **Formatting**: Automated with `black`
- **Type Hints**: Required for all functions

### Code Quality Tools

```bash
# Format code
black server/ client/

# Sort imports
isort server/ client/

# Lint code
flake8 server/ client/

# Type checking
mypy server/ client/

# Security check
bandit -r server/ client/
```

### Pre-commit Hooks

Install pre-commit hooks to automatically check your code:

```bash
pip install pre-commit
pre-commit install
```

## 🧪 Testing Guidelines

### Writing Tests

- Write tests for all new features
- Update tests when modifying existing code
- Aim for >80% code coverage
- Use descriptive test names
- Follow AAA pattern: Arrange, Act, Assert

### Test Structure

```python
def test_feature_name():
    """Test description of what is being tested."""
    # Arrange: Set up test data and conditions
    data = create_test_data()
    
    # Act: Execute the code being tested
    result = function_under_test(data)
    
    # Assert: Verify the results
    assert result.status == "success"
    assert len(result.items) > 0
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_agents.py

# Run with coverage
pytest --cov=server --cov=client --cov-report=html

# Run specific test
pytest tests/unit/test_agents.py::test_anomaly_detection
```

## 📚 Documentation

### Documentation Standards

- **Code Comments**: Explain "why", not "what"
- **Docstrings**: Required for all public functions/classes
- **README**: Keep updated with new features
- **API Docs**: Update OpenAPI/Swagger documentation
- **Examples**: Provide code examples for new features

### Docstring Format

We use Google-style docstrings:

```python
def process_data(data: pd.DataFrame, threshold: float = 0.5) -> dict:
    """Process data and detect anomalies.
    
    Args:
        data: Input DataFrame containing the data to process
        threshold: Detection threshold (default: 0.5)
        
    Returns:
        Dictionary containing processed results and anomalies
        
    Raises:
        ValueError: If data is empty or invalid
        
    Examples:
        >>> result = process_data(df, threshold=0.7)
        >>> print(result['anomaly_count'])
        5
    """
    pass
```

## 🏗️ Architecture Guidelines

### Agent Development

When creating new agents:

1. Inherit from `BaseAgent`
2. Implement required methods: `initialize()`, `execute()`, `validate()`
3. Add comprehensive error handling
4. Include logging for debugging
5. Write unit and integration tests

### API Development

When adding new API endpoints:

1. Add endpoint to `server/app/api/endpoints.py`
2. Create Pydantic schemas in `server/app/api/schemas.py`
3. Update OpenAPI documentation
4. Add request/response examples
5. Implement rate limiting if needed
6. Write API tests

## 🚀 Release Process

1. Update version in relevant files
2. Update CHANGELOG.md with release notes
3. Create GitHub release with tag
4. Update Docker images
5. Announce release

## 🤝 Community

### Getting Help

- 💬 **Discord**: [Join our Discord](https://discord.gg/datasentinel)
- 📧 **Email**: support@datasentinel.ai
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/agentic-data-sentinel/issues)
- 📖 **Wiki**: [GitHub Wiki](https://github.com/your-username/agentic-data-sentinel/wiki)

### Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- Project website

## 📝 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Data Sentinel! 🎉**

Your contributions help make data quality monitoring better for everyone.

