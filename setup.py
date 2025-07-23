"""
Setup script for LEGO BrickEconomy Professional Scraper
"""
import os
import sys
import subprocess
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def create_env_file():
    """Create .env file from template"""
    env_path = Path(".env")
    example_path = Path(".env.example")
    
    if env_path.exists():
        print("✅ .env file already exists")
        return True
    
    if not example_path.exists():
        print("❌ .env.example file not found")
        return False
    
    try:
        # Copy example to .env
        with open(example_path, 'r') as src, open(env_path, 'w') as dst:
            dst.write(src.read())
        
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your BrickEconomy credentials!")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def create_output_directory():
    """Create output directory"""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    print("✅ Created output directory")

def main():
    """Main setup function"""
    print("🚀 Setting up LEGO BrickEconomy Professional Scraper")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Create output directory
    create_output_directory()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit the .env file with your BrickEconomy credentials")
    print("2. Run: python demo.py (for interactive demonstration)")
    print("3. Run: python main.py --codes \"3920\" (for command-line usage)")
    print("\nAvailable commands:")
    print("  python demo.py           # Interactive demonstration")
    print("  python main.py --help    # Command-line help")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
