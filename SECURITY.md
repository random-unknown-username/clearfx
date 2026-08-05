# Security in ClearFX

ClearFX hooks into your terminal's `clear` command, which means it runs a *lot*. It is absolutely critical that it doesn't do anything malicious.

## Community Packages

Because ClearFX runs so often, allowing arbitrary Python in community packages would be a huge supply-chain vulnerability. A bad actor could easily steal environment variables, modify your `.bashrc`, or worse.

To prevent this, ClearFX community packages (`.clearfx`) **cannot contain executable Python code**. They use a strict, declarative JSON format for scenes, and all math expressions are parsed into an AST with no `eval()` or `exec()` ever used. There is zero network or filesystem access during playback.

## Reporting Issues

If you find a sandbox escape or any other security vulnerability, please don't open a public issue. Email me at satvikhardat@gmail.com and I'll get it patched as soon as possible.
