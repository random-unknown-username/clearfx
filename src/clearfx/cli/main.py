"""ClearFX CLI entry point.

Uses argparse for fast startup. All heavy imports are deferred.
"""
import argparse
import sys
import os


def main() -> None:
    """Main CLI entry point."""
    # Emergency disable
    if os.environ.get("CLEARFX_DISABLE"):
        _fallback_clear()
        return

    parser = argparse.ArgumentParser(
        prog="clearfx",
        description="ClearFX — Replace terminal clear with stunning animations",
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- play ---
    play_p = subparsers.add_parser("play", help="Play an animation")
    play_p.add_argument("design", nargs="?", default=None, help="Animation slug")
    play_p.add_argument("--random", action="store_true", help="Random animation")
    play_p.add_argument("--seed", type=int, default=None, help="Random seed")
    play_p.add_argument("--duration", dest="duration_ms", type=int, default=None)
    play_p.add_argument("--fps", type=int, default=None)
    play_p.add_argument("--ascii", dest="ascii_only", action="store_true")
    play_p.add_argument("--monochrome", action="store_true")
    play_p.add_argument("--reduced-motion", dest="reduced_motion", action="store_true")
    play_p.add_argument("--clear-after", dest="clear_after", action="store_true")
    play_p.add_argument("--keep-screen", dest="keep_screen", action="store_true", help="Do not clear screen after animation")
    play_p.add_argument("--loop", action="store_true", help="Loop the animation indefinitely")
    play_p.add_argument("--safe", action="store_true", help="Built-in only, conservative")
    play_p.add_argument("--debug", action="store_true")

    # --- preview ---
    preview_p = subparsers.add_parser("preview", help="Preview an animation")
    preview_p.add_argument("design", help="Animation slug or directory")

    # --- list ---
    list_p = subparsers.add_parser("list", help="List animations")
    list_p.add_argument("--installed", action="store_true")
    list_p.add_argument("--builtin", action="store_true")
    list_p.add_argument("--community", action="store_true")
    list_p.add_argument("--favorites", action="store_true")

    # --- info ---
    info_p = subparsers.add_parser("info", help="Show animation details")
    info_p.add_argument("design", help="Animation slug")

    # --- favorite / unfavorite ---
    fav_p = subparsers.add_parser("favorite", help="Add to favorites")
    fav_p.add_argument("design", help="Animation slug")
    unfav_p = subparsers.add_parser("unfavorite", help="Remove from favorites")
    unfav_p.add_argument("design", help="Animation slug")

    # --- block / unblock ---
    block_p = subparsers.add_parser("block", help="Block an animation")
    block_p.add_argument("design", help="Animation slug")
    unblock_p = subparsers.add_parser("unblock", help="Unblock an animation")
    unblock_p.add_argument("design", help="Animation slug")

    # --- install / uninstall ---
    inst_p = subparsers.add_parser("install", help="Install a .clearfx package")
    inst_p.add_argument("source", help="Path to .clearfx file or slug")
    uninst_p = subparsers.add_parser("uninstall", help="Uninstall a design")
    uninst_p.add_argument("design", help="Animation slug")

    # --- update ---
    update_p = subparsers.add_parser("update", help="Update designs")
    update_p.add_argument("design", nargs="?", default=None, help="Specific slug")

    # --- search ---
    search_p = subparsers.add_parser("search", help="Search designs")
    search_p.add_argument("query", help="Search query")

    # --- validate ---
    validate_p = subparsers.add_parser("validate", help="Validate a .clearfx package")
    validate_p.add_argument("path", help="Path to package or directory")

    # --- pack ---
    pack_p = subparsers.add_parser("pack", help="Pack a design into .clearfx")
    pack_p.add_argument("directory", help="Source directory")

    # --- unpack ---
    unpack_p = subparsers.add_parser("unpack", help="Unpack a .clearfx file")
    unpack_p.add_argument("path", help="Path to .clearfx file")

    # --- create ---
    create_p = subparsers.add_parser("create", help="Create a new animation project")
    create_p.add_argument("name", help="Animation name")

    # --- record ---
    record_p = subparsers.add_parser("record", help="Record an animation")
    record_p.add_argument("design", help="Animation slug")
    record_p.add_argument("--format", dest="fmt", default="cast",
                          choices=["svg", "cast", "frames", "gif"])
    record_p.add_argument("--output", "-o", default=None)

    # --- config ---
    config_p = subparsers.add_parser("config", help="Show or set configuration")
    config_p.add_argument("action", nargs="?", default=None, choices=["set", "get"])
    config_p.add_argument("key", nargs="?", default=None)
    config_p.add_argument("value", nargs="?", default=None)

    # --- wrap / unwrap ---
    wrap_p = subparsers.add_parser("wrap", help="Wrap a command with ClearFX animations")
    wrap_p.add_argument("cmd", help="Command to wrap")
    wrap_p.add_argument("--anim", help="Specific animation to play when command is run", default="")
    unwrap_p = subparsers.add_parser("unwrap", help="Unwrap a command")
    unwrap_p.add_argument("cmd", help="Command to unwrap")

    # --- setup-shell ---
    setup_p = subparsers.add_parser("setup-shell", help="Set up shell integration")
    setup_p.add_argument("--shell", choices=["bash", "zsh", "fish"])
    setup_p.add_argument("--dry-run", action="store_true")

    # --- remove-shell ---
    remove_p = subparsers.add_parser("remove-shell", help="Remove shell integration")
    remove_p.add_argument("--shell", choices=["bash", "zsh", "fish"])

    # --- doctor ---
    subparsers.add_parser("doctor", help="Check ClearFX installation")

    # --- benchmark ---
    subparsers.add_parser("benchmark", help="Run performance benchmarks")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return

    try:
        _dispatch(args)
    except KeyboardInterrupt:
        _fallback_clear()
    except Exception as exc:
        if getattr(args, "debug", False):
            import traceback
            traceback.print_exc()
        _fallback_clear()


def _dispatch(args: argparse.Namespace) -> None:
    """Route to the appropriate command handler."""
    from clearfx.cli.commands import (
        cmd_play, cmd_list, cmd_info, cmd_favorite, cmd_unfavorite,
        cmd_block, cmd_unblock, cmd_install, cmd_uninstall, cmd_update,
        cmd_search, cmd_validate, cmd_pack, cmd_unpack, cmd_create,
        cmd_record, cmd_config, cmd_marketplace_sync, cmd_setup_shell,
        cmd_remove_shell, cmd_doctor, cmd_benchmark, cmd_preview,
        cmd_wrap, cmd_unwrap
    )

    handlers = {
        "play": cmd_play,
        "preview": cmd_preview,
        "list": cmd_list,
        "info": cmd_info,
        "favorite": cmd_favorite,
        "unfavorite": cmd_unfavorite,
        "block": cmd_block,
        "unblock": cmd_unblock,
        "install": cmd_install,
        "uninstall": cmd_uninstall,
        "update": cmd_update,
        "search": cmd_search,
        "validate": cmd_validate,
        "pack": cmd_pack,
        "unpack": cmd_unpack,
        "create": cmd_create,
        "record": cmd_record,
        "config": cmd_config,
        "marketplace": cmd_marketplace_sync,
        "wrap": cmd_wrap,
        "unwrap": cmd_unwrap,
        "setup-shell": cmd_setup_shell,
        "remove-shell": cmd_remove_shell,
        "doctor": cmd_doctor,
        "benchmark": cmd_benchmark,
    }

    handler = handlers.get(args.command)
    if handler:
        handler(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)


def _fallback_clear() -> None:
    """Perform a plain terminal clear as safety fallback."""
    if sys.platform == "win32":
        os.system("cls")
    else:
        sys.stdout.write("\033[H\033[2J\033[3J")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
