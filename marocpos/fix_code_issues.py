#!/usr/bin/env python3
"""
This script fixes the remaining issues with row access in the code
and cleans up cached Python files to ensure changes take effect.
"""

import os
import re
import sys
import shutil

def clean_pycache():
    """Delete all __pycache__ directories to force Python to recompile modules"""
    pycache_count = 0
    
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                pycache_count += 1
                print(f"Removed: {pycache_path}")
            except Exception as e:
                print(f"Error removing {pycache_path}: {e}")
    
    return pycache_count

def fix_user_module():
    """Fix any remaining row access issues in the user module"""
    user_module_path = os.path.join('models', 'user.py')
    if not os.path.exists(user_module_path):
        print(f"Error: Cannot find {user_module_path}")
        return 0
        
    with open(user_module_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace all instances of row[0], row[1], etc. with row['id'], row['username'], etc.
    pattern = r"row\[(\d+)\]"
    column_map = {
        '0': 'id', 
        '1': 'username', 
        '2': 'password', 
        '3': 'role', 
        '4': 'active'
    }
    
    def replace_index(match):
        index = match.group(1)
        if index in column_map:
            return f"row['{column_map[index]}']"
        return match.group(0)
    
    new_content = re.sub(pattern, replace_index, content)
    
    # Check if we made any changes
    changes = new_content != content
    
    if changes:
        with open(user_module_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed row access issues in {user_module_path}")
    else:
        print(f"No issues found in {user_module_path}")
    
    return 1 if changes else 0

def fix_count_queries():
    """Fix COUNT(*) queries to use aliases"""
    files_to_check = []
    for root, dirs, files in os.walk('models'):
        for file in files:
            if file.endswith('.py'):
                files_to_check.append(os.path.join(root, file))
    
    fixed_count = 0
    
    for file_path in files_to_check:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for COUNT(*) without 'as count'
        count_pattern = r"SELECT\s+COUNT\(\*\)\s+FROM"
        new_content = re.sub(count_pattern, "SELECT COUNT(*) as count FROM", content)
        
        # Look for fetchone()[0] patterns
        fetchone_pattern = r"fetchone\(\)\[(\d+)\]"
        new_content = re.sub(fetchone_pattern, r"fetchone()['count']", new_content)
        
        # Save changes if any were made
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed COUNT queries in {file_path}")
            fixed_count += 1
    
    return fixed_count

def fix_database_connection():
    """Ensure database connection uses dict_factory for row_factory"""
    db_path = 'database.py'
    if not os.path.exists(db_path):
        print(f"Error: Cannot find {db_path}")
        return False
        
    with open(db_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if dict_factory is already set
    if 'dict_factory' in content and 'row_factory = dict_factory' in content:
        print("Database connection already uses dict_factory")
        return False
    
    # If not, add it
    conn_pattern = r"conn = sqlite3\.connect\(cls\.DB_PATH\)"
    if re.search(conn_pattern, content):
        new_content = re.sub(conn_pattern, 
            "conn = sqlite3.connect(cls.DB_PATH)\n            \n"
            "            # Configure row_factory to return dictionaries\n"
            "            def dict_factory(cursor, row):\n"
            "                d = {}\n"
            "                for idx, col in enumerate(cursor.description):\n"
            "                    d[col[0]] = row[idx]\n"
            "                return d\n"
            "                \n"
            "            # Use our dict_factory instead of sqlite3.Row\n"
            "            conn.row_factory = dict_factory", 
            content)
        
        with open(db_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Added dict_factory to database connection")
        return True
    
    return False

def main():
    print("=== MarocPOS Code Fixer ===")
    print("This script will fix common issues with the code.")
    
    # Ensure we're in the right directory
    if not os.path.exists('main.py'):
        if os.path.exists(os.path.join('marocpos', 'main.py')):
            os.chdir('marocpos')
        else:
            print("Error: Cannot find main.py. Please run this script from the project root directory.")
            sys.exit(1)
    
    print("\n1. Cleaning Python cache files...")
    cache_count = clean_pycache()
    print(f"   {cache_count} __pycache__ directories removed")
    
    print("\n2. Fixing User module row access...")
    user_fixed = fix_user_module()
    print(f"   {'Changes made' if user_fixed else 'No changes needed'}")
    
    print("\n3. Fixing COUNT(*) queries...")
    count_fixed = fix_count_queries()
    print(f"   Fixed {count_fixed} files")
    
    print("\n4. Checking database connection...")
    db_fixed = fix_database_connection()
    print(f"   {'Configuration updated' if db_fixed else 'No changes needed'}")
    
    print("\n=== Fixes Complete ===")
    if cache_count or user_fixed or count_fixed or db_fixed:
        print("Changes were made to your code. Please restart your application.")
    else:
        print("No issues found. If you're still experiencing problems, please contact support.")

if __name__ == "__main__":
    main()
