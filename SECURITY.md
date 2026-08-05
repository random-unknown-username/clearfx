# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in ClearFX, please report it responsibly.

### How to Report

1. **Do NOT open a public GitHub issue** for security vulnerabilities.
2. Email security concerns to: security@clearfx.io
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Fix Timeline**: Depends on severity, typically within 2 weeks for critical issues

## Security Model

### Package Format Security

ClearFX community packages (`.clearfx` files) are designed to be safe by construction:

- **No executable Python code**: Community packages contain only declarative scene descriptions, validated metadata, and bounded mathematical expressions.
- **Expression sandboxing**: All expressions are parsed into an AST and validated against a strict allowlist. No `eval()`, `exec()`, or `import` is ever used.
- **Operation limits**: Expressions have operation-count and recursion-depth limits to prevent resource exhaustion.
- **Archive safety**: Packages are validated for path traversal, symlinks, ZIP bombs, oversized assets, and compression ratio attacks.
- **Checksums**: SHA-256 checksums verify package integrity.
- **Signatures**: Optional Ed25519 signatures verify package authenticity.

### Why No Arbitrary Python?

Running community-supplied Python code every time a user clears their terminal would create a severe supply-chain attack vector. A malicious animation could:

- Steal environment variables and secrets
- Modify shell configuration
- Install backdoors
- Exfiltrate data
- Corrupt the terminal

ClearFX's declarative format prevents all of these by design.

### Marketplace Security

- All packages are validated server-side before publication
- Content-addressed storage prevents tampering
- Version transitions are validated (no downgrades without explicit override)
- Simple authentication isolates upload permissions
- Packages can be reported and quarantined

### Terminal Safety

- ClearFX always restores terminal state on exit, crash, or signal
- Context managers and signal handlers ensure cursor visibility, alternate screen, colors, echo mode, and line wrapping are properly restored
- `CLEARFX_DISABLE=1` provides an emergency bypass
- Non-TTY output is handled safely (no escape sequences to files)
- Shell integration never overwrites existing configuration

### Threat Model

See `docs/threat_model.md` for a detailed threat analysis.

## Dependencies

ClearFX's core has minimal dependencies:
- `platformdirs` — platform-specific directory paths
- `wcwidth` — Unicode character width measurement

The marketplace server and optional features have additional dependencies, but these are isolated and never loaded during normal `clear` operation.
