# Contributing to ClearFX

Thanks for checking out the project! I'm pretty open to pull requests, whether it's bug fixes, new features, or just adding a cool new built-in animation.

## Getting Setup

It's a standard Python project:

```bash
git clone https://github.com/random-unknown-username/clearfx.git
cd clearfx
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,client,recording]"
```

Run tests with `pytest`.
Check typing/linting with `ruff check src/ tests/` and `mypy src/clearfx/`.

## Adding Built-in Animations

If you've got an idea for a built-in animation, go for it! Built-ins use the raw Python engine API (unlike the restricted community packages). 
Just take a look at `src/clearfx/animations/` to see how the existing ones work, subclass `Animation`, and make sure it handles resizing gracefully.

If you run into any issues, just open a draft PR and I'll try to help.
