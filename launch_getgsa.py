#!/usr/bin/env python3
"""
GetGSA System Launcher
Simple launcher to start the GetGSA web application
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path
import os

def main():
    """Launch the GetGSA system"""
    
    print("🚀 GetGSA System Launcher")
    print("=" * 30)
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print(f"📁 Working directory: {project_root}")
    
    # Check if virtual environment exists
    venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        print("❌ Virtual environment not found!")
        print(f"   Expected: {venv_python}")
        sys.exit(1)
    
    print("✅ Virtual environment found")
    
    # Start the server
    port = 8001
    host = "127.0.0.1"
    url = f"http://{host}:{port}"
    
    print(f"🌐 Starting GetGSA server at {url}")
    print("🔄 Please wait for initialization...")
    
    try:
        # Start uvicorn server
        cmd = [
            str(venv_python),
            "-m", "uvicorn",
            "main:app",
            "--host", host,
            "--port", str(port),
            "--reload"
        ]
        
        print(f"💻 Running: {' '.join(cmd)}")
        
        # Start the process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Monitor output and wait for server to be ready
        server_ready = False
        initialization_complete = False
        
        for line in iter(process.stdout.readline, ''):
            print(line.rstrip())
            
            if "Uvicorn running on" in line:
                server_ready = True
                print(f"✅ Server is running at {url}")
            
            if "GetGSA system initialized successfully" in line:
                initialization_complete = True
                print("✅ GetGSA system fully initialized!")
                
            if "Application startup complete" in line and server_ready:
                print("\n🎉 GetGSA System Ready!")
                print("=" * 30)
                print(f"🌐 Web Interface: {url}")
                print("📋 Features Available:")
                print("   • Document Upload & Analysis")
                print("   • GSA Compliance Checking") 
                print("   • AI-Powered Brief Generation")
                print("   • Professional Email Creation")
                print("   • Real-time Health Monitoring")
                print("\n💡 The web interface should open automatically.")
                print("   If not, manually navigate to:", url)
                
                # Try to open browser
                try:
                    time.sleep(2)  # Give server a moment
                    webbrowser.open(url)
                    print("🌐 Browser opened automatically")
                except Exception as e:
                    print(f"⚠️  Could not open browser automatically: {e}")
                
                break
        
        # Keep the process running
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down GetGSA system...")
            process.terminate()
            print("✅ GetGSA system stopped")
            
    except FileNotFoundError:
        print("❌ Python or uvicorn not found!")
        print("   Make sure the virtual environment is properly set up")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()