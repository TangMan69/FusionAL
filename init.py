#!/usr/bin/env python3
"""
FusionAL Initialization Script

Sets up environment, checks dependencies, and initializes Docker/Claude configuration.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def check_docker():
    """Verify Docker is installed and running."""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker:", result.stdout.strip())
            return True
        else:
            print("❌ Docker not found")
            return False
    except FileNotFoundError:
        print("❌ Docker not installed")
        return False


def check_python():
    """Verify Python version."""
    import sys
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} (requires 3.11+)")
        return False


def check_dependencies():
    """Verify Python dependencies."""
    try:
        import fastapi
        import uvicorn
        import dotenv
        print("✅ Core dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: pip install -r core/requirements.txt")
        return False


def setup_docker_mcp():
    """Set up Docker MCP directory structure."""
    home = Path.home()
    mcp_dir = home / ".docker" / "mcp"
    
    try:
        mcp_dir.mkdir(parents=True, exist_ok=True)
        (mcp_dir / "catalogs").mkdir(exist_ok=True)
        print(f"✅ Docker MCP directory: {mcp_dir}")
        return True
    except Exception as e:
        print(f"❌ Failed to create Docker MCP directory: {e}")
        return False


def main():
    print("\n" + "="*60)
    print("🚀 FusionAL Initialization")
    print("="*60 + "\n")
    
    checks = [
        ("Docker", check_docker),
        ("Python", check_python),
        ("Dependencies", check_dependencies),
        ("Docker MCP Setup", setup_docker_mcp),
    ]
    
    results = []
    for name, check in checks:
        print(f"\nChecking {name}...")
        try:
            result = check()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append((name, False))
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n{passed}/{total} checks passed\n")
    
    if passed == total:
        print("🎉 FusionAL is ready! Next steps:")
        print("   1. cd core")
        print("   2. python -m uvicorn main:app --reload")
        print("   3. Visit http://localhost:8009/docs")
        return 0
    else:
        print("⚠️  Please fix the above issues and try again")
        return 1


if __name__ == "__main__":
    sys.exit(main())
