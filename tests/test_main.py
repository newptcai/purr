# Tests for __main__.py
import sys
from unittest.mock import patch


def test_main_execution():
    """Test that __main__.py can be imported and executes app()."""
    # Use a dummy module and set __name__ to '__main__'
    with patch("kitten_cli.cli.app") as mock_app:
        # Mock sys.argv to avoid Typer trying to parse pytest arguments
        with patch.object(sys, "argv", ["purr", "--help"]):
            # Trigger the execution by setting __name__ correctly
            import kitten_cli.__main__
            
            # Since we just imported it, and it has `if __name__ == "__main__":`
            # we need to execute the code manually if we want to test the block
            # or use a different approach.
            
            # Re-running the module with __name__ == "__main__"
            # This is a bit hacky but covers the lines
            import runpy
            runpy.run_module("kitten_cli.__main__", run_name="__main__")
            
            mock_app.assert_called()
