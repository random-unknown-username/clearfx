# Contributing to ClearFX

Thank you for your interest in contributing to ClearFX! This document provides guidelines and information for contributors.

## Getting Started

### Development Setup

```bash
# Clone the repository
git clone https://github.com/clearfx/clearfx.git
cd clearfx

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with all extras
pip install -e ".[dev,client,recording]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
ruff check src/ tests/
mypy src/clearfx/
```

### Project Structure

```
src/clearfx/
├── cli/          # Command-line interface
├── core/         # Configuration, selection, registry, attribution
├── engine/       # Rendering engine (canvas, renderer, timeline, etc.)
├── animations/   # 36 built-in animations
├── formats/      # Package format, expressions, validation
├── compiler/     # Animation compiler and creator SDK
├── marketplace/  # Marketplace client and installer
├── recording/    # Animation recording
├── shell/        # Shell integration
└── resources/    # Static resources
```

## Contributing Animations

### Built-in Animations

Built-in animations are Python classes using the full engine API. To add a new built-in:

1. Create a new file in `src/clearfx/animations/`
2. Subclass `Animation` from `clearfx.engine.animation`
3. Implement `setup()`, `update()`, and `render()`
4. Add `AnimationMeta` with all required fields
5. Register in `src/clearfx/animations/__init__.py`
6. Add tests in `tests/unit/test_animations.py`

### Community Animations

Community animations use the Creator SDK and compile to the safe `.clearfx` format:

```bash
clearfx create my-animation
cd my-animation
# Edit src/design.py using the Creator SDK
clearfx preview .
clearfx validate .
clearfx pack .
```

See `docs/creator_sdk.md` for the full creator documentation.

## Code Standards

- **Type hints**: All public functions and methods must have type annotations
- **Docstrings**: All public classes, methods, and functions need docstrings
- **Testing**: New features need tests; bug fixes need regression tests
- **Linting**: Code must pass `ruff check` and `mypy`
- **Comments**: Only where they explain non-obvious behavior
- **No god classes**: Keep classes focused and modular

## Animation Guidelines

Each animation must:

- Have a unique visual concept (not a color variation of another)
- Support deterministic output with seeds
- Adapt to terminal dimensions
- Have ASCII fallback mode
- Support monochrome mode
- Support reduced motion mode
- Render correctly at 80×24, 120×30, and 160×45
- Degrade gracefully in small terminals
- Include metadata (title, creator, description, tags)
- Have at least one golden-frame or behavioral test

## Pull Request Process

1. Fork the repository and create a feature branch
2. Make your changes following the code standards
3. Add tests for new functionality
4. Run the full test suite: `pytest`
5. Run linting: `ruff check src/ tests/ && mypy src/clearfx/`
6. Update documentation if needed
7. Submit a pull request with a clear description

## Reporting Issues

- Use GitHub Issues for bug reports and feature requests
- For security vulnerabilities, see `SECURITY.md`
- Include terminal type, OS, Python version, and ClearFX version in bug reports

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Code of Conduct

Be respectful, constructive, and welcoming to all contributors regardless of experience level.

## Creator Attribution

Built-in animations use fictional creator handles (e.g., @mira, @echo, @flux) as project personas to demonstrate marketplace attribution. These are not real individuals. See the animation files for the complete list.
