"""ClearFX CLI command implementations.

Each command uses lazy imports to keep startup fast.
"""
from __future__ import annotations

import argparse
import sys
import os
import time
from pathlib import Path


def cmd_play(args: argparse.Namespace) -> None:
    """Play an animation."""
    from clearfx.core.config import load_config
    from clearfx.core.registry import AnimationRegistry
    from clearfx.core.selector import AnimationSelector
    from clearfx.core.fallback import fallback_clear
    from clearfx.engine.terminal import TerminalSession, detect_capabilities
    from clearfx.engine.player import AnimationPlayer

    try:
        config = load_config()

        # Apply CLI overrides
        if args.duration_ms is not None:
            config.duration_ms = args.duration_ms
        if args.fps is not None:
            config.fps = args.fps
        if args.ascii_only:
            config.ascii_only = True
        if args.monochrome:
            config.monochrome = True
        if args.reduced_motion:
            config.reduced_motion = True
        if getattr(args, "keep_screen", False):
            clear_after = False
        elif args.clear_after:
            clear_after = True
        else:
            clear_after = config.clear_after

        registry = AnimationRegistry()

        # Select animation
        anim_class = None
        if args.design:
            if os.path.isdir(args.design):
                from clearfx.formats.interpreter import DesignInterpreter
                try:
                    d = os.path.abspath(args.design)
                    if os.path.exists(os.path.join(d, "src", "design.py")) or os.path.exists(os.path.join(d, "design.py")):
                        # It's a raw project, we need to compile it to memory first to get elements
                        from clearfx.compiler.compiler import AnimationCompiler
                        import tempfile
                        import zipfile
                        
                        compiler = AnimationCompiler()
                        # compiler.pack creates a zip file
                        out_zip = compiler.pack(d)
                        
                        # Extract it to a temp dir so DesignInterpreter can read design.json
                        temp_dir = tempfile.mkdtemp()
                        with zipfile.ZipFile(out_zip, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)
                            
                        interpreter = DesignInterpreter()
                        anim_class = interpreter.load(temp_dir)
                    elif os.path.exists(os.path.join(d, "design.json")):
                        # It's an extracted package
                        interpreter = DesignInterpreter()
                        anim_class = interpreter.load(d)
                    else:
                        raise ValueError("Directory does not contain a valid ClearFX project or package")
                except Exception as e:
                    print(f"Error loading design from {args.design}: {e}", file=sys.stderr)
                    fallback_clear()
                    return
            else:
                anim_class = registry.get_animation(args.design)
            if anim_class is None:
                print(f"Unknown animation: {args.design}", file=sys.stderr)
                fallback_clear()
                return
        else:
            selector = AnimationSelector(config, registry)
            anim_class = selector.select(seed=getattr(args, "seed", None))

        if anim_class is None:
            fallback_clear()
            return

        anim = anim_class()

        # Play with terminal session
        caps = detect_capabilities()
        keep_screen = getattr(args, "keep_screen", False)
        with TerminalSession(caps, keep_screen=keep_screen) as session:
            player = AnimationPlayer(
                animation=anim,
                session=session,
                config=config,
                seed=getattr(args, "seed", None),
                loop=getattr(args, "loop", False),
            )
            player.play()

        if clear_after:
            fallback_clear()

    except KeyboardInterrupt:
        fallback_clear()
    except Exception as exc:
        if getattr(args, "debug", False):
            import traceback
            traceback.print_exc()
        fallback_clear()


def cmd_preview(args: argparse.Namespace) -> None:
    """Preview an animation (same as play for now)."""
    args.clear_after = False
    args.safe = False
    args.debug = True
    if not hasattr(args, "seed"):
        args.seed = None
    if not hasattr(args, "duration_ms"):
        args.duration_ms = None
    if not hasattr(args, "fps"):
        args.fps = None
    if not hasattr(args, "ascii_only"):
        args.ascii_only = False
    if not hasattr(args, "monochrome"):
        args.monochrome = False
    if not hasattr(args, "reduced_motion"):
        args.reduced_motion = False
    args.keep_screen = True
    args.loop = True
    cmd_play(args)


def cmd_list(args: argparse.Namespace) -> None:
    """List available animations."""
    from clearfx.core.registry import AnimationRegistry
    from clearfx.core.config import load_config

    registry = AnimationRegistry()
    config = load_config()
    animations = registry.list_animations()

    # Filter
    if getattr(args, "builtin", False):
        animations = [a for a in animations if a.get("source") == "builtin"]
    if getattr(args, "community", False):
        animations = [a for a in animations if a.get("source") == "community"]
    if getattr(args, "favorites", False):
        animations = [a for a in animations if a["slug"] in config.favorites]

    if not animations:
        print("No animations found.")
        return

    # Header
    print(f"\n{'Slug':<25} {'Name':<25} {'Author':<15} {'Tags'}")
    print("─" * 80)
    for info in animations:
        slug = info.get("slug", "?")
        name = info.get("name", "?")
        author = info.get("author_handle", "?")
        tags = ", ".join(info.get("tags", []))
        fav = "★" if slug in config.favorites else " "
        print(f" {fav} {slug:<23} {name:<25} {author:<15} {tags}")
    print(f"\n  {len(animations)} animation(s)")


def cmd_info(args: argparse.Namespace) -> None:
    """Show animation details."""
    from clearfx.core.registry import AnimationRegistry

    registry = AnimationRegistry()
    anim_cls = registry.get_animation(args.design)
    if anim_cls is None:
        print(f"Unknown animation: {args.design}", file=sys.stderr)
        sys.exit(1)

    m = anim_cls.meta
    print(f"\n  {m.name}")
    print(f"  by {m.author_handle} ({m.author_name})")
    print(f"  ─{'─' * 40}")
    print(f"  ID:              {m.id}")
    print(f"  Slug:            {m.slug}")
    print(f"  Description:     {m.description}")
    print(f"  Tags:            {', '.join(m.tags)}")
    print(f"  Version:         {m.version}")
    print(f"  Min size:        {m.min_width}×{m.min_height}")
    print(f"  Duration:        {m.recommended_duration_ms}ms")
    print(f"  ASCII support:   {'yes' if m.supports_ascii else 'no'}")
    print(f"  Mono support:    {'yes' if m.supports_monochrome else 'no'}")
    print()


def cmd_favorite(args: argparse.Namespace) -> None:
    """Add animation to favorites."""
    from clearfx.core.config import load_config, save_config

    config = load_config()
    slug = args.design
    if slug not in config.favorites:
        config.favorites.append(slug)
        save_config(config)
        print(f"★ Added '{slug}' to favorites")
    else:
        print(f"'{slug}' is already a favorite")


def cmd_unfavorite(args: argparse.Namespace) -> None:
    """Remove animation from favorites."""
    from clearfx.core.config import load_config, save_config

    config = load_config()
    slug = args.design
    if slug in config.favorites:
        config.favorites.remove(slug)
        save_config(config)
        print(f"Removed '{slug}' from favorites")
    else:
        print(f"'{slug}' is not a favorite")


def cmd_block(args: argparse.Namespace) -> None:
    """Block an animation."""
    from clearfx.core.config import load_config, save_config

    config = load_config()
    slug = args.design
    if slug not in config.blocked:
        config.blocked.append(slug)
        save_config(config)
        print(f"Blocked '{slug}'")
    else:
        print(f"'{slug}' is already blocked")


def cmd_unblock(args: argparse.Namespace) -> None:
    """Unblock an animation."""
    from clearfx.core.config import load_config, save_config

    config = load_config()
    slug = args.design
    if slug in config.blocked:
        config.blocked.remove(slug)
        save_config(config)
        print(f"Unblocked '{slug}'")
    else:
        print(f"'{slug}' is not blocked")


def cmd_install(args: argparse.Namespace) -> None:
    """Install a .clearfx package."""
    from clearfx.marketplace.installer import install_package

    source = args.source
    try:
        result = install_package(source)
        if result.success:
            print(f"✓ Installed '{result.slug}' v{result.version}")
        else:
            print(f"✗ Installation failed: {result.error}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"✗ Installation failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_uninstall(args: argparse.Namespace) -> None:
    """Uninstall a design."""
    from clearfx.marketplace.installer import uninstall_package

    try:
        uninstall_package(args.design)
        print(f"✓ Uninstalled '{args.design}'")
    except Exception as e:
        print(f"✗ Uninstall failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_update(args: argparse.Namespace) -> None:
    """Update designs from marketplace."""
    print("Checking for updates...")
    try:
        from clearfx.marketplace.installer import install_package, list_installed
        
        if args.design:
            res = install_package(args.design)
            if res.success:
                print(f"✓ Updated '{args.design}' to v{res.version}")
            else:
                print(f"✗ Failed to update '{args.design}': {res.error}", file=sys.stderr)
        else:
            installed = list_installed()
            if not installed:
                print("No community packages installed.")
                return
                
            for pkg in installed:
                res = install_package(pkg.slug)
                if res.success:
                    print(f"✓ Updated '{pkg.slug}' to v{res.version}")
                else:
                    print(f"✗ Failed to update '{pkg.slug}': {res.error}", file=sys.stderr)
            print("✓ All designs up to date")
    except Exception as e:
        print(f"Could not check for updates: {e}", file=sys.stderr)


def cmd_search(args: argparse.Namespace) -> None:
    """Search designs."""
    from clearfx.core.registry import AnimationRegistry

    registry = AnimationRegistry()
    query = args.query.lower()
    results = []
    for info in registry.list_animations():
        name = info.get("name", "").lower()
        desc = info.get("description", "").lower()
        tags = [t.lower() for t in info.get("tags", [])]
        if query in name or query in desc or query in tags:
            results.append(info)

    if not results:
        print(f"No animations matching '{args.query}'")
        return

    print(f"\nSearch results for '{args.query}':")
    print(f"{'Slug':<25} {'Name':<25} {'Author':<15}")
    print("─" * 65)
    for info in results:
        print(f"  {info['slug']:<23} {info['name']:<25} {info.get('author_handle', '?')}")
    print(f"\n  {len(results)} result(s)")


def cmd_validate(args: argparse.Namespace) -> None:
    """Validate a .clearfx package."""
    from clearfx.formats.validator import validate_package

    result = validate_package(args.path)
    if result.is_valid:
        print(f"✓ Package is valid")
        if result.warnings:
            for w in result.warnings:
                print(f"  ⚠ {w}")
    else:
        print(f"✗ Package validation failed:")
        for err in result.errors:
            print(f"  ✗ {err}")
        sys.exit(1)


def cmd_pack(args: argparse.Namespace) -> None:
    """Pack a design directory into a .clearfx package."""
    from clearfx.compiler.compiler import AnimationCompiler

    try:
        compiler = AnimationCompiler()
        output = compiler.pack(args.directory)
        print(f"✓ Created {output}")
    except Exception as e:
        print(f"✗ Pack failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_unpack(args: argparse.Namespace) -> None:
    """Unpack a .clearfx file."""
    from clearfx.formats.package import PackageReader

    try:
        reader = PackageReader(args.path)
        output_dir = Path(args.path).stem
        reader.extract_to(output_dir)
        print(f"✓ Unpacked to {output_dir}/")
    except Exception as e:
        print(f"✗ Unpack failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_create(args: argparse.Namespace) -> None:
    """Create a new animation project."""
    name = args.name
    slug = name.lower().replace(" ", "-").replace("_", "-")
    project_dir = Path(name)

    if project_dir.exists():
        print(f"✗ Directory '{name}' already exists", file=sys.stderr)
        sys.exit(1)

    project_dir.mkdir(parents=True)
    (project_dir / "src").mkdir()
    (project_dir / "assets").mkdir()
    (project_dir / "tests").mkdir()

    # Create manifest
    manifest = f'''format_version = 1
id = "io.clearfx.community.{slug}"
slug = "{slug}"
name = "{name.replace('-', ' ').title()}"
version = "1.0.0"
author_name = "Your Name"
author_handle = "@yourhandle"
license = "MIT"
description = "A custom ClearFX animation."
entry_scene = "main"
minimum_width = 40
minimum_height = 12
recommended_duration_ms = 1200
supports_ascii = true
supports_monochrome = true
tags = ["custom"]
'''
    (project_dir / "manifest.toml").write_text(manifest)

    # Create design.py
    design_py = '''"""Custom ClearFX animation.

This file uses the Creator SDK to define your animation.
Run `clearfx pack .` to compile it into a .clearfx package.
"""
from clearfx.compiler.creator_sdk import CreatorAnimation


class MyAnimation(CreatorAnimation):
    def design(self) -> None:
        """Define your animation here."""
        # Add a text element
        self.add_text(
            text="Hello ClearFX!",
            x="w/2 - 7",
            y="h/2",
            fg=(255, 255, 255),
        )

        # Add a simple transition
        self.set_keyframe(
            target="text_0",
            property="opacity",
            time=0.0,
            value=0.0,
        )
        self.set_keyframe(
            target="text_0",
            property="opacity",
            time=0.5,
            value=1.0,
        )
        self.set_keyframe(
            target="text_0",
            property="opacity",
            time=1.0,
            value=0.0,
        )
'''
    (project_dir / "src" / "design.py").write_text(design_py)

    # Create README
    readme = f"""# {name.replace('-', ' ').title()}

A custom ClearFX animation.

## Development

```bash
clearfx preview .
clearfx validate .
clearfx pack .
```

## Publishing

1. Create an account on the ClearFX marketplace
2. Run `clearfx pack .` to create a .clearfx package
3. Upload the package through the marketplace web interface
"""
    (project_dir / "README.md").write_text(readme)

    print(f"✓ Created animation project in {project_dir}/")
    print(f"  Edit {project_dir}/src/design.py to create your animation")
    print(f"  Run 'clearfx preview {project_dir}/' to preview")
    print(f"  Run 'clearfx pack {project_dir}/' to package")


def cmd_record(args: argparse.Namespace) -> None:
    """Record an animation."""
    from clearfx.recording.recorder import AnimationRecorder
    from clearfx.core.registry import AnimationRegistry

    registry = AnimationRegistry()
    anim_cls = registry.get_animation(args.design)
    if anim_cls is None:
        print(f"Unknown animation: {args.design}", file=sys.stderr)
        sys.exit(1)

    output = args.output
    fmt = args.fmt

    try:
        recorder = AnimationRecorder()
        if fmt == "cast":
            output = output or f"{args.design}.cast"
            recorder.record_cast(anim_cls(), output)
        elif fmt == "svg":
            output = output or f"{args.design}.svg"
            recorder.record_svg(anim_cls(), output)
        elif fmt == "frames":
            output = output or f"{args.design}_frames"
            recorder.record_frames(anim_cls(), output)
        elif fmt == "gif":
            output = output or f"{args.design}.gif"
            recorder.record_gif(anim_cls(), output)
        print(f"✓ Recorded to {output}")
    except Exception as e:
        print(f"✗ Recording failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_config(args: argparse.Namespace) -> None:
    """Show or set configuration."""
    from clearfx.core.config import load_config, save_config, get_config_path

    config = load_config()

    if args.action is None:
        # Show current config
        print(f"\nClearFX Configuration ({get_config_path()})")
        print("─" * 50)
        for field in [
            "enabled", "duration_ms", "fps", "reduced_motion", "ascii_only",
            "monochrome", "attribution_position", "history_size", "source",
            "skip_on_keypress", "clear_after", "marketplace_url", "debug",
        ]:
            val = getattr(config, field, "?")
            print(f"  {field:<25} {val}")
        if config.favorites:
            print(f"  {'favorites':<25} {', '.join(config.favorites)}")
        if config.blocked:
            print(f"  {'blocked':<25} {', '.join(config.blocked)}")
        print()
    elif args.action == "set":
        if not args.key or args.value is None:
            print("Usage: clearfx config set <key> <value>", file=sys.stderr)
            sys.exit(1)
        key = args.key
        value = args.value
        # Type coercion
        if hasattr(config, key):
            current = getattr(config, key)
            if isinstance(current, bool):
                value = value.lower() in ("true", "1", "yes")
            elif isinstance(current, int):
                value = int(value)
            elif isinstance(current, float):
                value = float(value)
            setattr(config, key, value)
            save_config(config)
            print(f"Set {key} = {value}")
        else:
            print(f"Unknown config key: {key}", file=sys.stderr)
            sys.exit(1)
    elif args.action == "get":
        if not args.key:
            print("Usage: clearfx config get <key>", file=sys.stderr)
            sys.exit(1)
        if hasattr(config, args.key):
            print(getattr(config, args.key))
        else:
            print(f"Unknown config key: {args.key}", file=sys.stderr)
            sys.exit(1)


def cmd_marketplace_sync(args: argparse.Namespace) -> None:
    """Sync marketplace index."""
    print("Syncing marketplace index...")
    try:
        from clearfx.marketplace.client import MarketplaceClient
        client = MarketplaceClient()
        client.sync_index()
        print("✓ Index updated")
    except Exception as e:
        print(f"Could not sync: {e}")


def cmd_wrap(args: argparse.Namespace) -> None:
    """Wrap a command to run with ClearFX."""
    from clearfx.core.config import load_config, save_config
    from clearfx.shell.integration import ShellIntegration
    
    config = load_config()
    cmd = args.cmd
    
    if cmd not in config.wrapped_commands or config.wrapped_commands[cmd] != args.anim:
        config.wrapped_commands[cmd] = args.anim
        save_config(config)
        print(f"✓ Configured to wrap '{cmd}'")
        
        # Automatically update shell config
        integration = ShellIntegration()
        integration.setup(wrapped_commands=config.wrapped_commands)
        print("Please restart your shell or re-source your config to apply changes.")
    else:
        anim_text = f" with animation '{args.anim}'" if args.anim else ""
        print(f"Command '{cmd}' is already wrapped{anim_text}.")


def cmd_unwrap(args: argparse.Namespace) -> None:
    """Unwrap a command."""
    from clearfx.core.config import load_config, save_config
    from clearfx.shell.integration import ShellIntegration
    
    config = load_config()
    cmd = args.cmd
    
    if cmd in config.wrapped_commands:
        del config.wrapped_commands[cmd]
        save_config(config)
        print(f"✓ Removed wrap for '{cmd}'")
        
        # Automatically update shell config
        integration = ShellIntegration()
        integration.setup(wrapped_commands=config.wrapped_commands)
        print("Please restart your shell or re-source your config to apply changes.")
    else:
        print(f"Command '{cmd}' is not wrapped.")

def cmd_reset(args: argparse.Namespace) -> None:
    """Remove all community animations and reset config."""
    from clearfx.core.config import get_config_path
    from clearfx.shell.integration import ShellIntegration
    import shutil

    # 1. Remove shell integration blocks from bashrc/zshrc/fish
    integration = ShellIntegration()
    integration.remove()

    # 2. Delete the entire clearfx config directory
    config_dir = get_config_path().parent
    if config_dir.exists():
        try:
            shutil.rmtree(config_dir)
            print("✓ Removed all community animations, wrappers, and config")
        except Exception as e:
            print(f"✗ Failed to remove config directory: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("✓ No config directory found, nothing to remove")
    
    print("Please restart your shell or re-source your config to apply changes.")

def cmd_setup_shell(args: argparse.Namespace) -> None:
    """Set up shell integration."""
    from clearfx.shell.integration import ShellIntegration

    integration = ShellIntegration()
    integration.setup(
        shell=getattr(args, "shell", None),
        dry_run=getattr(args, "dry_run", False),
    )


def cmd_remove_shell(args: argparse.Namespace) -> None:
    """Remove shell integration."""
    from clearfx.shell.integration import ShellIntegration

    integration = ShellIntegration()
    integration.remove(shell=getattr(args, "shell", None))


def cmd_doctor(args: argparse.Namespace) -> None:
    """Run diagnostics."""
    from clearfx.shell.integration import ShellIntegration
    from clearfx.engine.terminal import detect_capabilities
    from clearfx.core.config import load_config, get_config_path
    from clearfx.core.registry import AnimationRegistry

    print("\n  ClearFX Doctor")
    print("  " + "─" * 40)

    # Check Python version
    import platform
    print(f"  Python:          {platform.python_version()}")
    print(f"  Platform:        {platform.system()} {platform.machine()}")

    # Check terminal
    caps = detect_capabilities()
    print(f"  Terminal size:   {caps.width}×{caps.height}")
    print(f"  Color support:   {caps.colors}")
    print(f"  Unicode:         {'yes' if caps.unicode_support else 'no'}")
    print(f"  Alt screen:      {'yes' if caps.alternate_screen_support else 'no'}")

    # Check config
    config_path = get_config_path()
    print(f"  Config file:     {config_path}")
    print(f"  Config exists:   {'yes' if config_path.exists() else 'no'}")

    # Check animations
    registry = AnimationRegistry()
    anims = registry.list_animations()
    print(f"  Animations:      {len(anims)}")

    # Check shell integration
    integration = ShellIntegration()
    shell = integration.detect_shell()
    print(f"  Current shell:   {shell or 'unknown'}")
    if shell:
        config_file = integration.get_config_file(shell)
        has_block = integration._has_managed_block(config_file) if config_file and config_file.exists() else False
        print(f"  Shell config:    {config_file}")
        print(f"  Integration:     {'installed' if has_block else 'not installed'}")

    # Check TTY
    print(f"  Is TTY:          {'yes' if sys.stdout.isatty() else 'no'}")
    print(f"  CLEARFX_DISABLE: {os.environ.get('CLEARFX_DISABLE', 'not set')}")
    print(f"  NO_COLOR:        {os.environ.get('NO_COLOR', 'not set')}")
    print()


def cmd_benchmark(args: argparse.Namespace) -> None:
    """Run performance benchmarks."""
    import time
    import resource

    print("\n  ClearFX Benchmark")
    print("  " + "─" * 40)

    # Import time
    t0 = time.perf_counter()
    from clearfx.engine.canvas import Canvas
    from clearfx.engine.animation import AnimationContext
    from clearfx.engine.framebuffer import FrameBuffer
    from clearfx.engine.renderer import DiffRenderer
    t1 = time.perf_counter()
    print(f"  Engine import:   {(t1 - t0) * 1000:.1f}ms")

    # Animation import time
    t0 = time.perf_counter()
    from clearfx.animations import BUILTIN_ANIMATIONS
    t1 = time.perf_counter()
    print(f"  Anim import:     {(t1 - t0) * 1000:.1f}ms")

    # Frame render time
    canvas = Canvas(80, 24)
    anim_cls = BUILTIN_ANIMATIONS[0]
    anim = anim_cls()
    ctx = AnimationContext(
        width=80, height=24, capabilities=None,
        duration_ms=1000, fps=30, seed=42,
        reduced_motion=False, ascii_only=False, monochrome=False,
        progress=0.0, elapsed_ms=0, dt=33.3, frame_number=0,
    )
    anim.setup(ctx)

    frame_times = []
    for i in range(60):
        ctx = AnimationContext(
            width=80, height=24, capabilities=None,
            duration_ms=1000, fps=30, seed=42,
            reduced_motion=False, ascii_only=False, monochrome=False,
            progress=i / 60.0, elapsed_ms=i * 16, dt=16.6, frame_number=i,
        )
        t0 = time.perf_counter()
        anim.update(ctx)
        canvas.clear()
        anim.render(ctx, canvas)
        t1 = time.perf_counter()
        frame_times.append((t1 - t0) * 1000)

    avg_frame = sum(frame_times) / len(frame_times)
    max_frame = max(frame_times)
    print(f"  Avg frame:       {avg_frame:.2f}ms")
    print(f"  Max frame:       {max_frame:.2f}ms")
    print(f"  Target budget:   {1000 / 30:.1f}ms (30fps)")

    # Memory
    try:
        usage = resource.getrusage(resource.RUSAGE_SELF)
        print(f"  Memory (RSS):    {usage.ru_maxrss / 1024:.1f}MB")
    except Exception:
        pass

    # All animations
    print(f"\n  All animation benchmark (5 frames each):")
    print(f"  {'Slug':<25} {'Avg ms':<10} {'Status'}")
    print("  " + "─" * 50)
    for anim_cls in BUILTIN_ANIMATIONS:
        try:
            anim = anim_cls()
            ctx0 = AnimationContext(
                width=80, height=24, capabilities=None,
                duration_ms=1000, fps=30, seed=42,
                reduced_motion=False, ascii_only=False, monochrome=False,
                progress=0.0, elapsed_ms=0, dt=33.3, frame_number=0,
            )
            anim.setup(ctx0)
            times = []
            for i in range(5):
                ctx = AnimationContext(
                    width=80, height=24, capabilities=None,
                    duration_ms=1000, fps=30, seed=42,
                    reduced_motion=False, ascii_only=False, monochrome=False,
                    progress=i / 15.0, elapsed_ms=i * 33, dt=33.3, frame_number=i,
                )
                t0 = time.perf_counter()
                anim.update(ctx)
                c = Canvas(80, 24)
                anim.render(ctx, c)
                t1 = time.perf_counter()
                times.append((t1 - t0) * 1000)
            avg = sum(times) / len(times)
            status = "✓" if avg < 33 else "⚠ slow"
            print(f"  {anim_cls.meta.slug:<25} {avg:<10.2f} {status}")
        except Exception as e:
            print(f"  {anim_cls.meta.slug:<25} {'error':<10} ✗ {e}")
    print()
