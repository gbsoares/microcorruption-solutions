#!/usr/bin/env python3
"""
Script to update the progress table in README.md
Usage: python3 update_progress.py "Challenge Name" "status"
Status options: "TODO" (not started), "WIP" (in progress), "DONE" (completed), "STUCK" (failed/stuck)
"""

import sys
import re

def update_progress(challenge_name, status):
    """Update the progress status for a given challenge."""
    
    # Read the README file
    try:
        with open('README.md', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: README.md not found!")
        return False
    
    # Find and replace the status for the given challenge
    pattern = rf'(\| \[{re.escape(challenge_name)}\].*?\| )TODO|WIP|DONE|STUCK( \|.*?\|.*?\|)'
    replacement = rf'\g<1>{status}\g<2>'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content == content:
        print(f"Warning: No changes made. Challenge '{challenge_name}' not found or already has status '{status}'")
        return False
    
    # Write back to file
    try:
        with open('README.md', 'w') as f:
            f.write(new_content)
        print(f"Successfully updated {challenge_name} status to {status}")
        return True
    except Exception as e:
        print(f"Error writing to README.md: {e}")
        return False

def show_usage():
    """Show usage information."""
    print("Usage: python3 update_progress.py \"Challenge Name\" \"status\"")
    print("\nStatus options:")
    print("  TODO   - Not Started")
    print("  WIP    - Work In Progress")  
    print("  DONE   - Completed")
    print("  STUCK  - Failed/Stuck")
    print("\nExample:")
    print("  python3 update_progress.py \"Tutorial\" \"DONE\"")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        show_usage()
        sys.exit(1)
    
    challenge_name = sys.argv[1]
    status = sys.argv[2]
    
    # Validate status
    valid_statuses = ["TODO", "WIP", "DONE", "STUCK"]
    if status not in valid_statuses:
        print(f"Error: Invalid status '{status}'")
        print(f"Valid statuses: {', '.join(valid_statuses)}")
        sys.exit(1)
    
    success = update_progress(challenge_name, status)
    sys.exit(0 if success else 1)