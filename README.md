<p align="center">
  <strong>ClearFX</strong><br>
  <em>because a blank screen is boring as fuck</em>
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

ngl i got so sick of watching my terminal just instantly vanish every time i ran `clear`, so i made this. ClearFX literally hijacks ur standard clear command (or `ls`, or whatever u want) and drops a crazy terminal animation before wiping the screen. u could be looking at some messy ass logs and one second later ur watching a tiny city shut off its lights or some ascii matrix rain.

it runs completely offline, uses a super safe sandboxed `.clearfx` package format so nobody can run malicious code on ur machine, and has a whole marketplace u can browse straight from the terminal.

## Installation

```bash
pip install clearfx
```
*(if u already have it, just do `pip install -U clearfx` to update)*

### Shell Integration

to actually make your `clear` command use this, u gotta set up the shell hooks:

```bash
clearfx setup-shell
```

it auto-detects what ur using (bash, zsh, fish, or powershell) and injects the hook. don't worry, it makes a backup of your config first just in case.

after that, just restart your shell or resource it:
```bash
source ~/.bashrc
```

and if u ever wanna wipe it completely from your machine:
```bash
clearfx reset
```

## Usage

### play a random animation
```bash
clearfx play
```

### wrap any command
want an animation to play every time you run `ls` or `git`?
```bash
clearfx wrap ls --anim aurora-fold
```

### list what we got
```bash
clearfx list
clearfx list --community
```

### tweak the playback
```bash
clearfx play --duration 700       # speed it up (ms)
clearfx play --fps 60             # buttery smooth
clearfx play --seed 42            # exact same output every time
clearfx play --ascii              # force ascii mode
clearfx play --monochrome         # no colors
clearfx play --reduced-motion     # accessibility mode (less crazy)
```

### emergency kill switch
if something breaks or u just want it off right now:
```bash
export CLEARFX_DISABLE=1
```

## Animations

i've built 36 built-in animations so far. they range from standard ascii art to full on rgb particle engines.

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

> note: built-in animations use fictional creator handles to demonstrate how marketplace attribution works.

## Configuration

all ur settings live in your platform's standard config directory (like `~/.config/clearfx/config.toml` on linux).

```bash
clearfx config                      # check current settings
clearfx config set duration_ms 900   # change something rq
```

example config:
```toml
enabled = true
duration_ms = 1100
fps = 30
reduced_motion = false
ascii_only = false
attribution_position = "auto"
```

## Accessibility

if ur terminal doesn't support crazy unicode or colors, u can force it:
```bash
clearfx config set ascii_only true
clearfx config set monochrome true
```

if u want simpler, gentler animations with fewer flashing lights:
```bash
clearfx config set reduced_motion true
```

## Marketplace

u can grab designs other people have made from the community catalog:

```bash
clearfx search "space"
clearfx install aurora-fold
clearfx update
```

## Creating Designs

i wanted to make it insanely easy to build ur own animations using python.

```bash
clearfx create my-animation
cd my-animation
# Edit src/design.py
clearfx preview .
clearfx validate .
clearfx pack .
```
*(check out `docs/CREATOR_SDK.md` for the full sdk tutorial on how to write these)*

### Security Model

running random python code every time u clear ur screen is a terrible fucking idea. 

so, community packages use a `.clearfx` file format. it's just a zip archive with a declarative JSON scene definition. there are ZERO `.py` files, ZERO arbitrary code execution, and ZERO network access when playing. it's completely sandboxed so u can install shit without worrying.

## Development Setup

wanna mess with the code?

```bash
git clone https://github.com/random-unknown-username/clearfx.git
cd clearfx
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,client,recording]"
```

to run the web marketplace locally for testing, the frontend code is included in the repo. just start it up!

## Troubleshooting

if things go weird:
1. run `clearfx doctor` to see wtf is wrong
2. if your terminal gets messed up (it shouldn't, but just in case), type `reset` and hit enter.

## License
MIT License. do whatever u want with it.
