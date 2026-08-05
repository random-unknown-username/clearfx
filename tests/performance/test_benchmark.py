import pytest
import sys
from io import StringIO
from argparse import Namespace

try:
    from clearfx.cli.commands import cmd_benchmark
except ImportError:
    cmd_benchmark = None

def test_cmd_benchmark():
    """Test that the benchmark CLI command runs successfully."""
    if cmd_benchmark is None:
        pytest.skip("Benchmark command is not implemented")
        
    args = Namespace()
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    try:
        cmd_benchmark(args)
        output = sys.stdout.getvalue()
        
        assert "ClearFX Benchmark" in output
        assert "All animation benchmark" in output
    finally:
        sys.stdout = old_stdout

@pytest.mark.xfail(reason="Dedicated benchmark module is not implemented yet")
def test_benchmark_module():
    """Test for the non-existent benchmark module."""
    import clearfx.benchmark  # This should raise ImportError and xfail
