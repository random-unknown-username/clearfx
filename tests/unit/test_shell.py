import pytest
from pathlib import Path
from clearfx.shell.integration import ShellIntegration

def test_detect_shell(monkeypatch):
    integration = ShellIntegration()
    
    monkeypatch.setenv("SHELL", "/bin/zsh")
    assert integration.detect_shell() == "zsh"
    
    monkeypatch.setenv("SHELL", "/usr/bin/fish")
    assert integration.detect_shell() == "fish"
    
    monkeypatch.setenv("SHELL", "/bin/bash")
    assert integration.detect_shell() == "bash"

def test_setup_and_remove_bash(tmp_path, monkeypatch):
    integration = ShellIntegration()
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    
    bashrc = tmp_path / ".bashrc"
    
    # Test setup
    integration.setup(shell="bash")
    assert bashrc.exists()
    content = bashrc.read_text()
    assert ShellIntegration.BLOCK_START in content
    assert "clearfx play --clear-after" in content
    assert ShellIntegration.BLOCK_END in content
    
    # Test setup when already configured (idempotency)
    integration.setup(shell="bash")
    content_idempotent = bashrc.read_text()
    assert content_idempotent.count(ShellIntegration.BLOCK_START) == 1
    
    # Test remove
    integration.remove(shell="bash")
    content_after = bashrc.read_text()
    assert ShellIntegration.BLOCK_START not in content_after
    assert ShellIntegration.BLOCK_END not in content_after

def test_setup_dry_run(tmp_path, monkeypatch, capsys):
    integration = ShellIntegration()
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    
    integration.setup(shell="zsh", dry_run=True)
    zshrc = tmp_path / ".zshrc"
    
    assert not zshrc.exists()
    
    captured = capsys.readouterr()
    assert "Would append to" in captured.out
    assert "clearfx play" in captured.out
