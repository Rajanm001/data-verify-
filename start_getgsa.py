#!/usr/bin/env python3
"""
🚀 GetGSA Quick Start Script
Automatically finds available port and starts the system
Created by: Rajan Mishra
"""

import socket
import subprocess
import webbrowser
import time
import sys
import os
from pathlib import Path

def find_free_port(start_port=8001):
    """Find the first available port starting from start_port"""
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None

def start_getgsa_server():
    """Start GetGSA server on available port"""
    print("🚀 Starting GetGSA: AI + RAG System")
    print("="*50)
    
    # Check if virtual environment exists
    venv_python = Path(r"C:\Users\Rajan mishra Ji\abhi\.venv\Scripts\python.exe")
    if not venv_python.exists():
        print("❌ Virtual environment not found!")
        print("Please run: python -m venv .venv && .venv\\Scripts\\activate && pip install -r requirements.txt")
        return False
    
    # Find available port
    print("🔍 Finding available port...")
    port = find_free_port(8001)
    if not port:
        print("❌ No available ports found in range 8001-8100")
        return False
    
    print(f"✅ Using port {port}")
    
    # Start the server
    print("🌐 Starting FastAPI server...")
    try:
        # Start server in background
        process = subprocess.Popen([
            str(venv_python), "-m", "uvicorn", "main:app", 
            "--host", "127.0.0.1", "--port", str(port), "--reload"
        ], cwd=r"C:\Users\Rajan mishra Ji\abhi")
        
        # Wait for server to start
        print("⏳ Waiting for server to initialize...")
        time.sleep(5)
        
        # Check if server is running
        try:
            import requests
            response = requests.get(f"http://127.0.0.1:{port}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server started successfully!")
                print(f"🌐 Access your GetGSA system at: http://127.0.0.1:{port}")
                print(f"📚 API Documentation: http://127.0.0.1:{port}/docs")
                print(f"❤️ Health Check: http://127.0.0.1:{port}/health")
                
                # Open browser
                print("🖥️ Opening browser...")
                webbrowser.open(f"http://127.0.0.1:{port}")
                
                print("\n🎯 System is ready for demonstration!")
                print("Press Ctrl+C to stop the server")
                
                # Keep running
                try:
                    process.wait()
                except KeyboardInterrupt:
                    print("\n\n⏹️ Stopping server...")
                    process.terminate()
                    print("✅ Server stopped successfully")
                
                return True
            else:
                print(f"⚠️ Server responded with status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"⚠️ Could not verify server health: {e}")
            print(f"🌐 Try accessing: http://127.0.0.1:{port}")
            
            # Keep server running anyway
            try:
                # Open browser anyway
                webbrowser.open(f"http://127.0.0.1:{port}")
                process.wait()
            except KeyboardInterrupt:
                print("\n\n⏹️ Stopping server...")
                process.terminate()
                print("✅ Server stopped successfully")
            
            return True
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def main():
    """Main function"""
    print("🎯 GetGSA System - Quick Start")
    print("Developed by: Rajan Mishra")
    print("Enterprise AI Solutions Architect")
    print()
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ main.py not found in current directory")
        print("Please run this script from the GetGSA project directory")
        return
    
    # Start the system
    success = start_getgsa_server()
    
    if success:
        print("\n🎉 GetGSA system started successfully!")
    else:
        print("\n❌ Failed to start GetGSA system")
        print("Please check the error messages above")

if __name__ == "__main__":
    main()