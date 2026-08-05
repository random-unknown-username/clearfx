<p align="center">
  <strong>ClearFX</strong><br>
  <em>Because a blank screen is boring</em>
</p>

<!-- TODO: add demo gif -->

<p align="center">
  <a href="#installation">Install</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#animations">Animations</a> ·
  <a href="#creating-designs">Create</a> ·
  <a href="#configuration">Config</a>
</p>

---

I got tired of just seeing my terminal text vanish instantly when I ran `clear`, so I built ClearFX. It swaps out the standard `clear` command for a quick, random terminal animation. One second you're clearing some messy logs, and the next you're watching a tiny city shut off its lights or some ASCII birds fly away. 

It runs completely offline during playback, has a declarative package format so you can safely run community animations, and has a marketplace you can browse right from your terminal.

## Installation

```bash
pip install clearfx
```

### Shell Integration

To make your regular `clear` command actually use ClearFX, run:

```bash
clearfx setup-shell
```

It'll auto-detect what you're using (Bash, Zsh, or Fish) and show you exactly what it's adding before it does anything. It automatically backs up your config too, just in case.

If you need to force a specific shell:

```bash
clearfx setup-shell --shell zsh
```

Restart your shell or source your config file, and you're good to go!

If you ever want to go back to normal:

```bash
clearfx remove-shell
```

## Usage

### Play a random animation
```bash
clearfx play
```

### Play a specific one
```bash
clearfx play aurora-fold
```

### List what's available
```bash
clearfx list
clearfx list --builtin
clearfx list --community
```

### Tweak the playback
```bash
clearfx play --duration 700       # Speed it up (ms)
clearfx play --fps 24             # Change frame rate
clearfx play --seed 42            # Get the exact same animation output
clearfx play --ascii              # Force ASCII mode
clearfx play --monochrome         # No colors
clearfx play --reduced-motion     # Accessibility mode
```

### Emergency disable

If something goes wrong or you just need it off right now:
```bash
export CLEARFX_DISABLE=1
```
It'll completely bypass the animation and run a standard clear.

## Animations

I've built 36 animations so far. Here's what's included:

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

> Note: Built-in animations use fictional creator handles to demonstrate how marketplace attribution works.

## Configuration

Settings live in your platform's standard config directory (like `~/.config/clearfx/config.toml` on Linux).

```bash
clearfx config                      # Check current settings
clearfx config set duration_ms 900   # Change something
```

Example config:
```toml
enabled = true
duration_ms = 1100
fps = 30
reduced_motion = false
ascii_only = false
attribution_position = "auto"
```

## Accessibility

ClearFX respects `NO_COLOR` for monochrome mode out of the box.

If you want simpler, gentler animations with fewer particles and no rapid flashing:
```bash
clearfx config set reduced_motion true
```

If your terminal doesn't like Unicode:
```bash
clearfx config set ascii_only true
```

## Marketplace

You can grab designs other people have made:

```bash
clearfx search "space"
clearfx install aurora-fold
clearfx update
```

## Creating Designs

I wanted to make it easy to build your own.

```bash
clearfx create my-animation
cd my-animation
# Edit src/design.py
clearfx preview .
clearfx validate .
clearfx pack .
```

### Security Model

Running some random python code every time you clear your screen is a terrible idea. So, community packages use a `.clearfx` file format. It's just a ZIP archive with a declarative JSON scene definition.

There are no `.py` files, no arbitrary code execution, no shell scripts, and zero network access when playing. It's completely sandboxed.

## Development Setup

If you want to poke around the code:

```bash
git clone https://github.com/random-unknown-username/clearfx.git
cd clearfx
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,client,recording]"
pre-commit install
```

To run the web marketplace locally for testing, the frontend code is included in the repo. Just start it up!

## Troubleshooting

If things go weird:
1. Run `clearfx doctor`
2. If your terminal gets messed up if you hit Ctrl+C at the wrong time (it shouldn't, but just in case), type `reset` and hit enter.

## License
MIT License.
