#!/usr/bin/env python3
"""
Quick Start Script for LEGO BrickEconomy Scraper
==============================================

This script automatically sets up everything you need to get started.

Usage: python quick_start.py
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python 3.13 is available"""
    print("🔍 Checking Python 3.13 availability...")
    try:
        result = subprocess.run("py -3.13 --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Found Python 3.13: {result.stdout.strip()}")
            return True
        else:
            print("❌ Python 3.13 not found")
            return False
    except Exception as e:
        print(f"❌ Error checking Python 3.13: {e}")
        return False

def create_virtual_environment():
    """Create Python 3.13 virtual environment"""
    if os.path.exists("venv_py313"):
        print("✅ Virtual environment already exists")
        return True
    
    return run_command("py -3.13 -m venv venv_py313", "Creating Python 3.13 virtual environment")

def install_dependencies():
    """Install required dependencies"""
    pip_cmd = "venv_py313\\Scripts\\pip.exe" if os.name == 'nt' else "venv_py313/bin/pip"
    return run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies")

def create_env_file():
    """Create .env file if it doesn't exist"""
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return True
    
    print("📝 Creating .env file...")
    try:
        with open('.env', 'w') as f:
            f.write("""# Environment variables for the LEGO BrickEconomy Scraper
BRICKECONOMY_USERNAME=your_username_here
BRICKECONOMY_PASSWORD=your_password_here
CHROME_HEADLESS=false
SCRAPING_DELAY=2
OUTPUT_FORMAT=xlsx
""")
        print("✅ .env file created successfully!")
        print("⚠️  Please edit .env with your BrickEconomy credentials!")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_installation():
    """Test that everything works"""
    python_cmd = "venv_py313\\Scripts\\python.exe" if os.name == 'nt' else "venv_py313/bin/python"
    return run_command(f"{python_cmd} test_imports.py", "Testing installation")

def main():
    """Main setup function"""
    print("🎉 LEGO BrickEconomy Scraper - Quick Start Setup")
    print("=" * 50)
    print("This script will set up everything you need to get started!\n")
    
    steps = [
        ("Checking Python 3.13", check_python_version),
        ("Creating virtual environment", create_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Creating .env file", create_env_file),
        ("Testing installation", test_installation)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n📋 Step: {step_name}")
        print("-" * 30)
        
        if not step_func():
            failed_steps.append(step_name)
    
    print("\n" + "=" * 50)
    print("📊 SETUP SUMMARY")
    print("=" * 50)
    
    if not failed_steps:
        print("🎉 Setup completed successfully!")
        print("\n🚀 Next steps:")
        print("1. Edit the .env file with your BrickEconomy credentials")
        print("2. Run the demo: python demo.py")
        print("3. Or use command line: python main.py --help")
        
        print("\n💻 To activate the environment:")
        print("Windows: .\\activate_env.bat")
        print("PowerShell: .\\activate_env.ps1")
        print("Manual: .\\venv_py313\\Scripts\\activate")
        
    else:
        print(f"⚠️  Setup completed with {len(failed_steps)} issues:")
        for step in failed_steps:
            print(f"   ❌ {step}")
        print("\nPlease resolve these issues and run the script again.")
    
    return len(failed_steps) == 0

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)
