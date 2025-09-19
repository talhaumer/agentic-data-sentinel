#!/usr/bin/env python3
"""
Simple syntax checker for Python files
Alternative to mypy when mypy is not available
"""

import ast
import sys
from pathlib import Path

def check_file_syntax(file_path):
    """Check syntax of a single Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the file to check for syntax errors
        ast.parse(content, filename=str(file_path))
        print(f"✅ {file_path} - Syntax OK")
        return True
        
    except SyntaxError as e:
        print(f"❌ {file_path} - Syntax Error:")
        print(f"   Line {e.lineno}: {e.text}")
        print(f"   Error: {e.msg}")
        return False
        
    except Exception as e:
        print(f"❌ {file_path} - Error: {e}")
        return False

def check_directory_syntax(directory):
    """Check syntax of all Python files in a directory."""
    directory = Path(directory)
    python_files = list(directory.rglob("*.py"))
    
    if not python_files:
        print(f"No Python files found in {directory}")
        return True
    
    print(f"🔍 Checking syntax for {len(python_files)} Python files...")
    print("=" * 50)
    
    passed = 0
    total = len(python_files)
    
    for file_path in python_files:
        if check_file_syntax(file_path):
            passed += 1
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} files passed syntax check")
    
    if passed == total:
        print("🎉 All files have valid syntax!")
        return True
    else:
        print("❌ Some files have syntax errors.")
        return False

def main():
    """Main function."""
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = "app/"
    
    print(f"🚀 Checking syntax for: {target}")
    print()
    
    success = check_directory_syntax(target)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
