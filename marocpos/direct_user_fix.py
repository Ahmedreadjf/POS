#!/usr/bin/env python3
"""
Direct fix for the User module to resolve KeyError issues
"""

import os
import sys

def fix_user_module():
    """Replace all row[index] with the appropriate row['name'] in user.py"""
    user_path = os.path.join('models', 'user.py')
    
    if not os.path.exists(user_path):
        if os.path.exists(os.path.join('marocpos', 'models', 'user.py')):
            user_path = os.path.join('marocpos', 'models', 'user.py')
        else:
            print(f"Error: Could not find user.py in {os.getcwd()}")
            print("Please run this script from the project root directory.")
            return False
    
    print(f"Found user.py at: {user_path}")
    
    # Read the file
    try:
        with open(user_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Replace row access patterns
    replacements = [
        ("row[0]", "row['id']"),
        ("row[1]", "row['username']"),
        ("row[2]", "row['password']"),
        ("row[3]", "row['role']"),
        ("row[4]", "row['active']"),
        ("row[5]", "row['email']"),
        ("row[6]", "row['phone']"),
        ("SELECT COUNT(*) FROM", "SELECT COUNT(*) as count FROM"),
        ("fetchone()[0]", "fetchone()['count']"),
    ]
    
    new_content = content
    for old, new in replacements:
        new_content = new_content.replace(old, new)
    
    # Write the file if changes were made
    if new_content != content:
        try:
            with open(user_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Successfully updated {user_path}")
            print("The file has been updated to use named column access.")
            return True
        except Exception as e:
            print(f"Error writing file: {e}")
            return False
    else:
        print("⚠️ No changes were needed or the file was already fixed.")
        return False

def remove_pycache():
    """Remove __pycache__ directories to force Python to reload modules"""
    pycache_dirs = []
    
    # Find __pycache__ directories
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_dirs.append(os.path.join(root, '__pycache__'))
    
    # Remove each directory
    removed = 0
    for pycache_dir in pycache_dirs:
        try:
            import shutil
            shutil.rmtree(pycache_dir)
            print(f"Removed: {pycache_dir}")
            removed += 1
        except Exception as e:
            print(f"Could not remove {pycache_dir}: {e}")
    
    print(f"Removed {removed} __pycache__ directories")
    return removed > 0

if __name__ == "__main__":
    print("\n=== MarocPOS User Module Direct Fix ===\n")
    
    # Make a backup of the file first
    user_path = os.path.join('models', 'user.py')
    if os.path.exists(user_path):
        backup_path = user_path + '.backup'
        try:
            import shutil
            shutil.copy2(user_path, backup_path)
            print(f"✅ Created backup: {backup_path}")
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
    
    # Fix the user module
    fixed = fix_user_module()
    
    # Remove __pycache__ directories
    print("\nRemoving Python cache files...")
    removed = remove_pycache()
    
    print("\n=== Fix Complete ===")
    if fixed or removed:
        print("Changes were made. Please restart your application.\n")
    else:
        print("No changes were needed. If you're still having issues, please contact support.\n")
