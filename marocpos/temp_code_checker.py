import os
import inspect
from models.user import User

def check_code():
    # Get the file path of the user module
    user_module_path = inspect.getfile(User)
    print(f"User module location: {user_module_path}")
    
    # Try to read the get_user_by_username method to see what it contains
    try:
        with open(user_module_path, 'r') as f:
            content = f.read()
            
        # Find the get_user_by_username function
        start_index = content.find("def get_user_by_username")
        if start_index == -1:
            print("Could not find get_user_by_username function in the file!")
            return
            
        # Extract a portion of the function to check
        function_content = content[start_index:start_index+500]  # Get approximately 500 chars after function start
        print("\nContent of get_user_by_username function:")
        print("-" * 50)
        print(function_content)
        print("-" * 50)
        
        # Check if the function is using row[0] or row['id']
        if "row[0]" in function_content:
            print("\n⚠️ WARNING: Your code is still using numeric indexes like row[0]!")
            print("This is the old version of the code that causes errors.")
        elif "row['id']" in function_content:
            print("\n✅ GOOD: Your code is using named keys like row['id'].")
            print("This is the updated version that should work correctly.")
        else:
            print("\n❓ UNCLEAR: Could not determine the access method being used.")
            
        # Check for other key problems
        print("\nChecking for other potential issues:")
        if "row_factory = dict_factory" not in content and "row_factory = sqlite3.Row" not in content:
            print("⚠️ No row_factory setting found in the database connection code!")
        
    except Exception as e:
        print(f"Error while checking code: {e}")
        
    print("\n=== Recommendations ===")
    print("1. Make sure you've pulled the latest changes from GitHub")
    print("2. Try deleting any __pycache__ directories: find . -name __pycache__ -type d -exec rm -rf {} +")
    print("3. Check if you're running the right copy of the code")

if __name__ == "__main__":
    print("Checking code configuration...")
    check_code()
