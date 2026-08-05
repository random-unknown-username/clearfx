import os
from pathlib import Path
from typing import Optional, Tuple

class ShellIntegration:
    BLOCK_START = "# >>> clearfx managed block >>>"
    BLOCK_END = "# <<< clearfx managed block <<<"

    def detect_shell(self) -> str:
        shell = os.environ.get("SHELL", "").lower()
        if "zsh" in shell:
            return "zsh"
        elif "fish" in shell:
            return "fish"
        elif "pwsh" in shell or "powershell" in shell:
            return "powershell"
            
        if os.name == "nt":
            return "powershell"
            
        return "bash"

    def get_config_file(self, shell: str) -> Path:
        home = Path.home()
        if shell == "zsh":
            return home / ".zshrc"
        elif shell == "fish":
            return home / ".config" / "fish" / "config.fish"
        elif shell == "powershell":
            if os.name == "nt":
                return home / "Documents" / "PowerShell" / "Microsoft.PowerShell_profile.ps1"
            else:
                return home / ".config" / "powershell" / "Microsoft.PowerShell_profile.ps1"
        return home / ".bashrc"

    def get_managed_block(self, shell: str, wrapped_commands: dict[str, str] = None) -> str:
        wrapped = wrapped_commands or {}
        blocks = []
        blocks.append(f"{self.BLOCK_START}\n# DO NOT EDIT - managed by clearfx setup-shell")
        
        if shell in ("bash", "zsh"):
            blocks.append("if command -v clearfx &>/dev/null; then")
            blocks.append("  function clear {\n    command clearfx play --clear-after\n  }")
            for cmd, anim in wrapped.items():
                anim_arg = f" {anim}" if anim else ""
                blocks.append(f"  function {cmd} {{\n    command clearfx play{anim_arg}\n    command {cmd} \"$@\"\n  }}")
            blocks.append("fi")
        elif shell == "fish":
            blocks.append("if type -q clearfx")
            blocks.append("  function clear\n    command clearfx play --clear-after\n  end")
            for cmd, anim in wrapped.items():
                anim_arg = f" {anim}" if anim else ""
                blocks.append(f"  function {cmd}\n    command clearfx play{anim_arg}\n    command {cmd} $argv\n  end")
            blocks.append("end")
        elif shell == "powershell":
            blocks.append("if (Get-Command clearfx -ErrorAction SilentlyContinue) {")
            blocks.append("  function clearfx_clear {\n    clearfx play --clear-after\n  }")
            blocks.append("  Set-Alias clear clearfx_clear -Force -Option AllScope -ErrorAction SilentlyContinue")
            for cmd, anim in wrapped.items():
                anim_arg = f" {anim}" if anim else ""
                blocks.append(f"  function clearfx_{cmd} {{\n    clearfx play{anim_arg}\n    if ('{cmd}' -eq 'ls' -and (Get-Command Get-ChildItem -ErrorAction SilentlyContinue)) {{\n      Get-ChildItem @args\n    }} else {{\n      $c = Get-Command {cmd} -CommandType Application,Cmdlet,ExternalScript -ErrorAction SilentlyContinue | Select-Object -First 1\n      if ($c) {{ & $c @args }} else {{ Write-Host \"Command {cmd} not found\" -ForegroundColor Red }}\n    }}\n  }}")
                blocks.append(f"  Set-Alias {cmd} clearfx_{cmd} -Force -Option AllScope -ErrorAction SilentlyContinue")
            blocks.append("}")
            
        blocks.append(self.BLOCK_END)
        return "\n".join(blocks)

    def setup(self, shell: Optional[str] = None, dry_run: bool = False, wrapped_commands: dict[str, str] = None) -> None:
        if wrapped_commands is None:
            try:
                from clearfx.core.config import load_config
                wrapped_commands = load_config().wrapped_commands
            except Exception:
                wrapped_commands = {}
                
        shell = shell or self.detect_shell()
        config_file = self.get_config_file(shell)
        block = self.get_managed_block(shell, wrapped_commands)

        if not block:
            print(f"Unsupported shell: {shell}")
            return

        if dry_run:
            print(f"Would append to {config_file}:\n{block}")
            return

        if config_file.exists():
            content = config_file.read_text()
            if self.BLOCK_START in content:
                # Remove the old block first so we can cleanly replace it
                self.remove(shell)
                content = config_file.read_text()
            # Create backup
            backup_file = config_file.with_suffix(config_file.suffix + ".clearfx.bak")
            backup_file.write_text(content)
            
            with open(config_file, "a") as f:
                f.write(f"\n{block}\n")
        else:
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, "w") as f:
                f.write(f"{block}\n")
        print(f"Successfully configured ClearFX for {shell}.")

    def remove(self, shell: Optional[str] = None) -> None:
        shell = shell or self.detect_shell()
        config_file = self.get_config_file(shell)

        if not config_file.exists():
            print("Config file not found.")
            return

        content = config_file.read_text()
        if self.BLOCK_START not in content:
            print("ClearFX block not found in config.")
            return

        lines = content.splitlines()
        new_lines = []
        in_block = False
        for line in lines:
            if line.strip() == self.BLOCK_START:
                in_block = True
                continue
            if line.strip() == self.BLOCK_END:
                in_block = False
                continue
            if not in_block:
                new_lines.append(line)

        config_file.write_text("\n".join(new_lines) + "\n")
        print(f"Removed ClearFX configuration from {shell}.")

    def doctor(self) -> None:
        shell = self.detect_shell()
        config_file = self.get_config_file(shell)
        print(f"Detected shell: {shell}")
        print(f"Config file: {config_file} (exists: {config_file.exists()})")
        if config_file.exists():
            content = config_file.read_text()
            print(f"Integration installed: {self.BLOCK_START in content}")
