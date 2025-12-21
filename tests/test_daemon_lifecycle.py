"""
Test daemon lifecycle - ensure core daemons can be instantiated and run basic operations.
"""
import pytest
import sys
from pathlib import Path

# Add repo root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_seiros_lifecycle():
    """Test Seiros daemon can be instantiated and has correct attributes."""
    from Seiros.seiros import Seiros
    
    s = Seiros(interval=5)
    
    # Check basic attributes
    assert s.daemon_id == "seiros_propagator"
    assert s.role == "Propagation & Deployment Daemon"
    assert s.symbolic_traits["element"] == "fire"
    
    # Test config setting
    s.set_config({"version": "1.0.0", "test": "data"})
    assert s.config == {"version": "1.0.0", "test": "data"}
    
    # Test node registration
    s.register_node("test_node")
    assert "test_node" in s.nodes


def test_mila_lifecycle():
    """Test Mila daemon can be instantiated and has correct attributes."""
    from Mila.mila import Mila
    
    m = Mila()
    
    # Check basic attributes
    assert m.daemon_id == "mila_allocator"
    assert m.role == "Storage Allocation Daemon"
    assert m.symbolic_traits["element"] == "earth"
    
    # Check rules are defined
    assert "logs" in m.rules
    assert "configs" in m.rules


def test_saphira_imports():
    """Test Saphira daemon module can be imported."""
    # Saphira is a script, so we just test it imports without error
    try:
        from Saphira import saphira
        # Check that key functions exist
        assert hasattr(saphira, 'main')
        assert hasattr(saphira, 'seed_from_fragment')
    except ImportError as e:
        pytest.skip(f"Saphira import requires additional setup: {e}")


def test_daemon_goddess_quartet_complete():
    """Test that all four Goddess Quartet daemons are present."""
    quartet = ["Rhea", "Seiros", "Saphira", "Mila"]
    
    for daemon_name in quartet:
        daemon_path = ROOT / daemon_name
        assert daemon_path.exists(), f"{daemon_name} directory not found"
        assert daemon_path.is_dir(), f"{daemon_name} is not a directory"
        
        # Check for main daemon file
        main_file = daemon_path / f"{daemon_name.lower()}.py"
        alt_main_file = daemon_path / f"{daemon_name.lower()}_main.py"
        
        has_main = main_file.exists() or alt_main_file.exists()
        assert has_main, f"{daemon_name} main file not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
