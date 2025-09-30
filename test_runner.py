"""
Simple test runner for GetGSA system
"""

import asyncio
import sys
import os

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tests.test_getgsa import run_all_tests

if __name__ == "__main__":
    print("🚀 GetGSA Test Runner")
    print("=" * 50)
    
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test runner failed: {e}")
        sys.exit(1)