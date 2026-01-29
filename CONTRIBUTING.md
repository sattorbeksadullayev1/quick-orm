# Contributing to Quick-ORM

Thank you for considering contributing to Quick-ORM!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/quick-orm.git
cd quick-orm
```

2. Create virtual environment:
```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
```

4. Run tests:
```bash
pytest tests/pytest/ -v
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Keep code clean and professional
- No comments unless absolutely necessary (self-documenting code preferred)
- Use meaningful variable and function names

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure nothing breaks
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for high test coverage

## Reporting Bugs

- Use GitHub Issues
- Provide detailed description
- Include code examples if possible
- Specify Python version and OS

## Feature Requests

- Use GitHub Issues with "enhancement" label
- Explain use case clearly
- Provide examples of desired behavior

## Code of Conduct

- Be respectful and professional
- Welcome newcomers
- Focus on constructive feedback
- No harassment or discrimination tolerated
