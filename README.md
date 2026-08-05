<p align="center">
  <strong>✨ ClearFX</strong><br>
  <em>Replace terminal <code>clear</code> with stunning animations</em>
</p>

<p align="center">
  <a href="#installation">Install</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#animations">Animations</a> ·
  <a href="#creating-designs">Create</a> ·
  <a href="#marketplace">Marketplace</a> ·
  <a href="#configuration">Config</a>
</p>

---

ClearFX transforms the ordinary `clear` command into a brief, randomly selected terminal animation. Each time you clear your screen, a different piece of terminal art plays — from northern lights to firefly fields, fractal trees to tiny city shutdowns.

**36 built-in animations** · **Safe package format** · **Creator marketplace** · **Zero network during playback**

## Installation

```bash
pipx install clearfx
```

Or with pip:

```bash
pip install clearfx
```

### Shell Integration

After installing, set up your shell so `clear` triggers ClearFX:

```bash
clearfx setup-shell
```

This auto-detects your shell (Bash, Zsh, or Fish) and shows exactly what will be added before making changes. A backup of your config is created automatically.

To specify a shell explicitly:

```bash
clearfx setup-shell --shell zsh
```

After setup, restart your shell or source your config file. Now running `clear` plays a random animation!

### Removing Shell Integration

```bash
clearfx remove-shell
```

### Diagnostics

```bash
clearfx doctor
```

## Usage

### Play a random animation

```bash
clearfx play
```

### Play a specific animation

```bash
clearfx play aurora-fold
```

### List all available animations

```bash
clearfx list
clearfx list --builtin
clearfx list --community
clearfx list --favorites
```

### Get info about an animation

```bash
clearfx info aurora-fold
```

### Customize playback

```bash
clearfx play --duration 700       # Duration in ms
clearfx play --fps 24             # Frame rate
clearfx play --seed 42            # Deterministic selection
clearfx play --ascii              # ASCII-only mode
clearfx play --monochrome         # No colors
clearfx play --reduced-motion     # Accessibility mode
clearfx play --safe               # Built-in only, conservative features
```

### Favorites and blocks

```bash
clearfx favorite aurora-fold
clearfx unfavorite aurora-fold
clearfx block pixel-avalanche
clearfx unblock pixel-avalanche
```

### Emergency disable

```bash
export CLEARFX_DISABLE=1
```

When set, ClearFX bypasses animation entirely and performs a normal clear.

## Animations

ClearFX ships with 36 handcrafted animations, each with unique motion, geometry, and timing:

| # | Animation | Description |
|---|-----------|-------------|
| 1 | Aurora Fold | Smooth ribbons fold inward like northern lights |
| 2 | Black Hole Terminal | Characters orbit and collapse into a central void |
| 3 | Pixel Avalanche | Screen breaks into blocks that fall away |
| 4 | Neon Koi | Glowing fish circle each other |
| 5 | Gravity Well | A grid bends toward a moving point |
| 6 | Constellation Weaver | Stars connect into patterns and dissolve |
| 7 | Origami Crane | Lines fold into a crane and fly away |
| 8 | Cyber Shutter | Mechanical panels close with glowing seams |
| 9 | Ink in Water | Organic tendrils spread and fade |
| 10 | Signal Bloom | Radio waves expand into flower shapes |
| 11 | Terminal Rain Garden | Falling glyphs grow tiny plants |
| 12 | Wormhole | Tunnel of distorted rings |
| 13 | Glitch Cathedral | Symmetrical columns build, glitch, collapse |
| 14 | Comet Sweep | A comet wipes the terminal diagonally |
| 15 | Paper Burn | A burning edge turns content to ash |
| 16 | Liquid Mirror | Wave distortion flattens to clean |
| 17 | Circuit Pulse | Circuit paths grow with racing pulses |
| 18 | Moonlit Waves | Ocean waves beneath a reflected moon |
| 19 | Fractal Branch | A branching tree grows and retracts |
| 20 | Magnetic Sand | Particles organize along field lines |
| 21 | Portal Door | A portal opens, shows depth, closes |
| 22 | Retro Vector Horizon | 80s-style perspective grid |
| 23 | Glass Fracture | Cracks spread from an impact point |
| 24 | Clockwork Reset | Interlocking gears pull screen inward |
| 25 | Solar Flare | A sun emits curved flares |
| 26 | Data Serpent | A hex-digit snake slithers through |
| 27 | Rain on Window | Droplets descend, merge, leave trails |
| 28 | Quantum Split | Objects split into probability states |
| 29 | Snow Globe | Swirling snow in a shrinking globe |
| 30 | Typewriter Ghost | Text types itself and fades as ghosts |
| 31 | Mosaic Flip | Tiles flip in waves revealing blank space |
| 32 | Firefly Field | Warm points drift and communicate |
| 33 | Tidal Vortex | Opposing whirlpools create S-shaped flow |
| 34 | Laser Loom | Beams weave and cut geometric fabric |
| 35 | Mechanical Iris | Camera aperture blades close |
| 36 | Tiny City Shutdown | A skyline's windows turn off one by one |

All animations support:
- ✅ Deterministic seeds
- ✅ Terminal size adaptation
- ✅ ASCII fallback
- ✅ Monochrome mode
- ✅ Reduced motion mode

> **Note**: Built-in animations use fictional creator handles (@mira, @echo, @flux, etc.) as project personas for marketplace attribution demonstration. These are not real individuals.

## Configuration

Configuration is stored in your platform's config directory (`~/.config/clearfx/config.toml` on Linux).

```bash
clearfx config                      # Show current config
clearfx config set duration_ms 900   # Set a value
clearfx config set fps 24
```

### Example config

```toml
enabled = true
duration_ms = 1100
fps = 30
reduced_motion = false
ascii_only = false
attribution_position = "auto"
history_size = 8
source = "all"
skip_on_keypress = true
clear_after = true

[weights]
favorites = 2.0
newly_installed = 1.25
builtins = 1.0
community = 1.0
```

## Accessibility

### Reduced Motion

ClearFX respects accessibility needs:

```bash
clearfx play --reduced-motion
```

Or set it permanently:

```bash
clearfx config set reduced_motion true
```

Reduced-motion mode doesn't disable animations — it provides calm alternatives with gentle fades, slow movement, fewer particles, and no rapid effects.

### NO_COLOR

ClearFX respects the `NO_COLOR` environment variable. When set, animations render in monochrome.

### ASCII Mode

For terminals without Unicode support:

```bash
clearfx config set ascii_only true
```

## Marketplace

### Installing community designs

```bash
clearfx search "space"
clearfx install aurora-fold
clearfx install ./my-design.clearfx
```

### Updating designs

```bash
clearfx update              # Update all
clearfx update aurora-fold   # Update specific
```

### Syncing the index

```bash
clearfx marketplace sync
```

## Creating Designs

### Quick start

```bash
clearfx create my-animation
cd my-animation
# Edit src/design.py
clearfx preview .
clearfx validate .
clearfx pack .
```

### Package format

Community packages use the `.clearfx` format — a ZIP archive containing:

```
manifest.toml    # Metadata
design.json      # Declarative scene definition
assets/          # Text/ASCII art assets
previews/        # Preview images
CHECKSUMS        # SHA-256 checksums
SIGNATURE        # Optional Ed25519 signature
```

### Security model

**Community packages cannot contain executable Python code.** This is by design.

Running arbitrary community Python every time you clear your terminal would create a severe supply-chain vulnerability. Instead, ClearFX uses a safe declarative format:

- ✅ Validated metadata
- ✅ Declarative scene definitions
- ✅ Allowlisted animation opcodes
- ✅ Bounded mathematical expressions (parsed to AST, no eval)
- ✅ Text/ASCII assets
- ✅ Palettes
- ❌ No `.py` files
- ❌ No native libraries
- ❌ No shell scripts
- ❌ No dynamic imports
- ❌ No network calls
- ❌ No filesystem access

### Recording

```bash
clearfx record aurora-fold                    # Default format
clearfx record aurora-fold --format cast      # Asciinema
clearfx record aurora-fold --format svg       # SVG animation
clearfx record aurora-fold --format frames    # Text frames
clearfx record aurora-fold --format gif       # GIF (requires Pillow)
```

## Development

### Setup

```bash
git clone https://github.com/clearfx/clearfx.git
cd clearfx
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,client,recording]"
pre-commit install
```

### Running tests

```bash
pytest
pytest -m "not slow"
pytest tests/unit/
pytest tests/security/
```

### Linting

```bash
ruff check src/ tests/
mypy src/clearfx/
```

### Benchmarks

```bash
clearfx benchmark
```

Reports import time, startup time, frame render time, memory usage, and more.

### Marketplace server (development)

```bash
pip install -e ".[marketplace-server]"
cd marketplace_server
python run.py
```

### Architecture overview

```
src/clearfx/
├── cli/          # Argparse CLI with lazy imports
├── core/         # Config, selection, registry, attribution
├── engine/       # Canvas, renderer, timeline, particles, easing
├── animations/   # 36 built-in Python animations
├── formats/      # Package format, expressions, validation
├── compiler/     # Python → declarative compiler, creator SDK
├── marketplace/  # Client and installer
├── recording/    # Animation recording (SVG, cast, frames, GIF)
├── shell/        # Shell integration (Bash, Zsh, Fish)
└── resources/    # Static resources
```

## Troubleshooting

### Animation doesn't play

1. Check `clearfx doctor` for diagnostics
2. Ensure your terminal supports ANSI escape codes
3. Try `clearfx play --safe` for conservative mode
4. Set `CLEARFX_DISABLE=1` to bypass entirely

### Terminal corruption after Ctrl+C

This should never happen — ClearFX uses signal handlers and context managers to always restore terminal state. If it does:

```bash
reset  # Reset terminal
```

Please file a bug report with your terminal emulator name and version.

### Shell integration issues

```bash
clearfx remove-shell  # Remove integration
clearfx doctor        # Check for issues
clearfx setup-shell   # Re-add integration
```

## License

MIT License. See [LICENSE](LICENSE) for details.
