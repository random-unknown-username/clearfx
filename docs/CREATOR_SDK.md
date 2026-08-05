# ClearFX Creator SDK 

Alright so here is the whole ass documentation for the `CreatorAnimation` SDK so you can actually build some damn cool animations for the terminal. 

If u want to make a community package or use the Web Studio, u are gonna use this python lib. It compiles down to a sandboxed `design.json` payload, which means no one can run malicious code on ur machine when u install their designs.

## Getting Started

U js need to subclass `CreatorAnimation` and override the `design()` method. Dont touch `__init__`, dont touch `render()`, js write ur declarative layout in `design()`.

```python
from clearfx.compiler.creator_sdk import CreatorAnimation

class MyAnimation(CreatorAnimation):
    def design(self) -> None:
        # this is where all the magic happens
        pass
```

## Adding Shit to the Screen

Right now, it supports text (and soon lines, rects, circles, particles, and sprites). 

### `add_text(text, x, y, fg=None, bold=False)`

Drop some text on the screen. The coolest part is u dont have to hardcode coordinates. U can use expressions like `"w/2"` (width divided by 2) or `"h/2"` (height divided by 2) so it perfectly centers no matter how big the users fucking terminal window is.

```python
self.add_text(
    text="Terminal Magic.",
    x="w/2 - 7",    # center horizontally (offset by half string length)
    y="h/2",        # center vertically
    fg=(255, 0, 100), # rgb tuple
    bold=True
)
```

**Note:** Everything u add gets an auto-generated ID (like `text_0`, `text_1`, etc.) based on the order u add them. U will need this ID to animate it later.

## Animating Shit (Keyframes)

Static text is boring as fuck. U can animate properties by setting keyframes. The compiler handles all the tweening/interpolation for u between keyframes.

### `set_keyframe(target, property, time, value)`

- **target**: The ID of the element (e.g., `"text_0"`)
- **property**: What u want to change (right now, `"opacity"` is supported)
- **time**: A float from `0.0` to `1.0` (0 is the start of the animation, 1 is the end)
- **value**: The value at that time

Example: A fade-in and fade-out effect.

```python
# start invisible at 0%
self.set_keyframe(
    target="text_0",
    property="opacity",
    time=0.0,
    value=0.0,
)

# fully visible at 50%
self.set_keyframe(
    target="text_0",
    property="opacity",
    time=0.5,
    value=1.0,
)

# invisible again at 100%
self.set_keyframe(
    target="text_0",
    property="opacity",
    time=1.0,
    value=0.0,
)
```

## How to Test

1. Pop open the Web Studio.
2. Paste ur python code.
3. Hit **Execute** to run it live in the web terminal.
4. Hit **Publish** to push it straight into the catalog.
5. In ur terminal, run `clearfx install <slug>` and `clearfx wrap ls --anim <slug>` to see it every time u run `ls`.

Thats literally it. Go build sm cool shit.
