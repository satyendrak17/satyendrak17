#!/usr/bin/env python3
"""
Quick Start Script for Radhe Jewellers
This script handles installation and startup automatically.
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages from requirements.txt"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_streamlit_directory():
    """Create .streamlit directory if it doesn't exist"""
    if not os.path.exists(".streamlit"):
        os.makedirs(".streamlit")
        print("📁 Created .streamlit directory")

def check_secrets_file():
    """Check if secrets.toml exists, if not, copy from example"""
    secrets_path = ".streamlit/secrets.toml"
    example_path = ".streamlit/secrets.toml.example"
    
    if not os.path.exists(secrets_path) and os.path.exists(example_path):
        import shutil
        shutil.copy(example_path, secrets_path)
        print("📋 Created secrets.toml from example")
        print("⚠️  Remember to add your WhatsApp API credentials to .streamlit/secrets.toml")

def run_streamlit():
    """Run the Streamlit application"""
    print("🚀 Starting Radhe Jewellers...")
    print("📱 Your application will open in the browser automatically")
    print("🌐 Access URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app_save_bill.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")

def main():
    """Main function"""
    print("💍 Radhe Jewellers - Quick Start")
    print("=" * 50)
    
    # Check if running in correct directory
    if not os.path.exists("app_save_bill.py"):
        print("❌ Error: app_save_bill.py not found. Please run this script from the project directory.")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Setup directories and files
    check_streamlit_directory()
    check_secrets_file()
    
    # Run the application
    run_streamlit()

if __name__ == "__main__":
    main() 