# Contributing to AI Resume Builder

Thank you for your interest in contributing to AI Resume Builder! 🎉

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- A clear title and description
- Steps to reproduce the bug
- Expected vs actual behavior
- Screenshots (if applicable)
- Your environment details (OS, Python version, etc.)

### Suggesting Features

We welcome feature suggestions! Please create an issue with:
- A clear description of the feature
- Use cases and benefits
- Any implementation ideas you have

### Code Contributions

1. **Fork the repository**
   ```bash
   git clone https://github.com/kiruuuuuuu/ai-resume-builder-v2.git
   cd ai-resume-builder-v2
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Copy environment file
   cp .env.example .env
   # Edit .env with your settings
   
   # Run migrations
   python manage.py migrate
   ```

4. **Make your changes**
   - Follow PEP 8 style guidelines
   - Write tests for new features
   - Update documentation as needed

5. **Test your changes**
   ```bash
   python manage.py test
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: Description of your changes"
   ```

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**
   - Provide a clear description of your changes
   - Reference any related issues
   - Add screenshots if UI changes are involved

## Code Style

- Follow PEP 8 Python style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Write clear commit messages

## Testing

Please ensure all tests pass before submitting a PR:
```bash
python manage.py test
```

## Questions?

Feel free to open an issue for any questions or clarifications!

Thank you for contributing! 🙏

