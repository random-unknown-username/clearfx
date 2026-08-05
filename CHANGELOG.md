# Changelog

All notable changes to ClearFX will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-01

### Added
- Initial release of ClearFX
- 36 built-in terminal animations
- Terminal rendering engine with double buffering and frame diffing
- Shell integration for Bash, Zsh, and Fish
- Safe declarative animation package format (.clearfx)
- Expression evaluator with AST validation
- Package signing with Ed25519
- Animation compilation from Python to safe format
- Creator SDK for community animation design
- Marketplace MVP server (FastAPI + SQLite)
- Marketplace client with security verification
- Animation recording (SVG, asciinema cast, frame sequences)
- Configuration system with platformdirs
- Random selection with history, favorites, and filtering
- Attribution overlay system
- Reduced motion mode
- ASCII and monochrome fallbacks
- Terminal resize handling
- Benchmark command
- Doctor command for diagnostics
- Complete test suite
