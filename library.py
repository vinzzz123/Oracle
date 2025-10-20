"""
PROJECT ORACLE - AUTOMATIC LIBRARY INSTALLER
Installs all required Python libraries for Project Oracle

File: library.py
Usage: python library.py
"""

import subprocess
import sys
import importlib
from typing import List, Tuple

# ==============================================================================
# REQUIRED LIBRARIES
# ==============================================================================

REQUIRED_LIBRARIES = [
    ('yfinance', 'yfinance>=0.2.28'),
    ('pandas', 'pandas>=1.5.0'),
    ('numpy', 'numpy>=1.23.0'),
    ('sklearn', 'scikit-learn>=1.2.0'),
    ('investpy', 'investpy'),
    ('openpyxl', 'openpyxl'),
]

OPTIONAL_LIBRARIES = [
    ('matplotlib', 'matplotlib>=3.6.0'),
    ('scipy', 'scipy>=1.10.0'),
]


# ==============================================================================
# INSTALLATION FUNCTIONS
# ==============================================================================

def check_library(package_name: str) -> bool:
    """Check if a library is already installed"""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False


def install_library(pip_name: str) -> Tuple[bool, str]:
    """Install a library using pip"""
    try:
        print(f"  Installing {pip_name}...", end=' ')
        
        # Run pip install
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', pip_name],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print("✅ SUCCESS")
            return True, "Installed successfully"
        else:
            print("❌ FAILED")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT")
        return False, "Installation timed out"
    except Exception as e:
        print(f"❌ ERROR")
        return False, str(e)


def upgrade_pip():
    """Upgrade pip to latest version"""
    print("📦 Upgrading pip to latest version...")
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
            capture_output=True,
            timeout=120
        )
        print("✅ pip upgraded successfully\n")
    except Exception as e:
        print(f"⚠️  Warning: Could not upgrade pip: {e}\n")


# ==============================================================================
# MAIN INSTALLATION PROCESS
# ==============================================================================

def main():
    """Main installation function"""
    
    print("\n" + "="*80)
    print("🔮 PROJECT ORACLE - LIBRARY INSTALLER")
    print("="*80)
    print("\nThis script will install all required libraries for Project Oracle")
    print("Estimated time: 2-5 minutes depending on your internet connection\n")
    
    # Check Python version
    print(f"Python Version: {sys.version}")
    
    if sys.version_info < (3, 7):
        print("\n❌ ERROR: Python 3.7 or higher is required")
        print("Please upgrade your Python installation")
        sys.exit(1)
    
    print("✅ Python version is compatible\n")
    
    # Upgrade pip first
    upgrade_pip()
    
    # Track installation results
    installed = []
    already_installed = []
    failed = []
    
    # Install required libraries
    print("="*80)
    print("📚 INSTALLING REQUIRED LIBRARIES")
    print("="*80 + "\n")
    
    for package_name, pip_name in REQUIRED_LIBRARIES:
        print(f"📦 {package_name}")
        
        # Check if already installed
        if check_library(package_name):
            print(f"  Already installed ✓")
            already_installed.append(package_name)
        else:
            # Install the library
            success, message = install_library(pip_name)
            
            if success:
                installed.append(package_name)
            else:
                failed.append((package_name, message))
        
        print()  # Empty line
    
    # Install optional libraries
    print("\n" + "="*80)
    print("📚 INSTALLING OPTIONAL LIBRARIES")
    print("="*80 + "\n")
    
    for package_name, pip_name in OPTIONAL_LIBRARIES:
        print(f"📦 {package_name} (optional)")
        
        if check_library(package_name):
            print(f"  Already installed ✓")
            already_installed.append(package_name)
        else:
            success, message = install_library(pip_name)
            if success:
                installed.append(package_name)
            # Don't add to failed list for optional libraries
        
        print()
    
    # Print summary
    print("\n" + "="*80)
    print("📊 INSTALLATION SUMMARY")
    print("="*80 + "\n")
    
    if installed:
        print(f"✅ Newly Installed ({len(installed)}):")
        for lib in installed:
            print(f"   • {lib}")
        print()
    
    if already_installed:
        print(f"✓ Already Installed ({len(already_installed)}):")
        for lib in already_installed:
            print(f"   • {lib}")
        print()
    
    if failed:
        print(f"❌ Failed to Install ({len(failed)}):")
        for lib, error in failed:
            print(f"   • {lib}")
            print(f"     Error: {error[:100]}...")
        print()
    
    # Verify installation
    print("="*80)
    print("🔍 VERIFYING INSTALLATION")
    print("="*80 + "\n")
    
    all_working = True
    
    for package_name, _ in REQUIRED_LIBRARIES:
        if check_library(package_name):
            print(f"✅ {package_name:20} - OK")
        else:
            print(f"❌ {package_name:20} - MISSING")
            all_working = False
    
    print("\n" + "="*80)
    
    if all_working and not failed:
        print("✅ ALL LIBRARIES INSTALLED SUCCESSFULLY!")
        print("="*80)
        print("\n🎉 You're ready to use Project Oracle!")
        print("\nNext steps:")
        print("  1. Run: python main.py")
        print("  2. Or: python market_scanner.py")
        print("\n" + "="*80 + "\n")
    elif failed:
        print("⚠️  INSTALLATION COMPLETED WITH ERRORS")
        print("="*80)
        print("\nSome libraries failed to install.")
        print("\nTry manual installation:")
        for lib, _ in failed:
            pip_name = next(p for n, p in REQUIRED_LIBRARIES if n == lib)
            print(f"  pip install {pip_name}")
        print("\n" + "="*80 + "\n")
    else:
        print("⚠️  SOME LIBRARIES ARE MISSING")
        print("="*80)
        print("\nPlease run this script again or install manually:")
        print("  pip install -r requirements.txt")
        print("\n" + "="*80 + "\n")


# ==============================================================================
# ALTERNATIVE INSTALLATION METHODS
# ==============================================================================

def install_from_requirements():
    """Install from requirements.txt file"""
    print("\n📦 Installing from requirements.txt...")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("✅ All libraries installed from requirements.txt")
            return True
        else:
            print("❌ Failed to install from requirements.txt")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("⚠️  requirements.txt not found")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def create_requirements_file():
    """Create requirements.txt file"""
    print("\n📝 Creating requirements.txt...")
    
    requirements_content = """# Project Oracle - Required Libraries

# Core libraries
yfinance>=0.2.28
pandas>=1.5.0
numpy>=1.23.0
scikit-learn>=1.2.0

# Market data
investpy

# Excel export
openpyxl

# Optional (for visualization)
matplotlib>=3.6.0
scipy>=1.10.0
"""
    
    try:
        with open('requirements.txt', 'w') as f:
            f.write(requirements_content)
        print("✅ requirements.txt created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create requirements.txt: {e}")
        return False


# ==============================================================================
# INTERACTIVE MENU
# ==============================================================================

def interactive_menu():
    """Interactive installation menu"""
    
    print("\n" + "="*80)
    print("🔮 PROJECT ORACLE - LIBRARY INSTALLER")
    print("="*80)
    print("\nInstallation Options:")
    print("1. Automatic Installation (Recommended)")
    print("2. Install from requirements.txt")
    print("3. Create requirements.txt file")
    print("4. Check installed libraries")
    print("5. Exit")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == '1':
        main()
    elif choice == '2':
        install_from_requirements()
    elif choice == '3':
        create_requirements_file()
        print("\nYou can now run: pip install -r requirements.txt")
    elif choice == '4':
        print("\n" + "="*80)
        print("📋 CHECKING INSTALLED LIBRARIES")
        print("="*80 + "\n")
        
        for package_name, pip_name in REQUIRED_LIBRARIES:
            if check_library(package_name):
                print(f"✅ {package_name:20} - Installed")
            else:
                print(f"❌ {package_name:20} - Not installed")
        
        print("\nOptional libraries:")
        for package_name, pip_name in OPTIONAL_LIBRARIES:
            if check_library(package_name):
                print(f"✅ {package_name:20} - Installed")
            else:
                print(f"⚠️  {package_name:20} - Not installed (optional)")
        
        print()
    elif choice == '5':
        print("\n👋 Goodbye!")
        return
    else:
        print("\n❌ Invalid option")


# ==============================================================================
# RUN INSTALLER
# ==============================================================================

if __name__ == "__main__":
    try:
        # Check if running with command line argument
        if len(sys.argv) > 1:
            if sys.argv[1] == '--auto':
                main()
            elif sys.argv[1] == '--requirements':
                install_from_requirements()
            elif sys.argv[1] == '--create-req':
                create_requirements_file()
            elif sys.argv[1] == '--check':
                for package_name, _ in REQUIRED_LIBRARIES:
                    status = "✅" if check_library(package_name) else "❌"
                    print(f"{status} {package_name}")
            else:
                print("Usage:")
                print("  python library.py              - Interactive menu")
                print("  python library.py --auto        - Automatic installation")
                print("  python library.py --requirements - Install from requirements.txt")
                print("  python library.py --create-req  - Create requirements.txt")
                print("  python library.py --check       - Check installed libraries")
        else:
            # Run interactive menu by default
            interactive_menu()
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)