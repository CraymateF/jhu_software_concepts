#!/usr/bin/env python3
"""
Setup script to create and populate both databases with their respective datasets
"""
import subprocess

from dotenv import load_dotenv
from load_data import load_data

# Load environment variables
load_dotenv()

def run_command(cmd):
    """Run a shell command and return success status"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=False
        )
        if result.returncode != 0 and "already exists" not in result.stderr:
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(f"Error running command: {exc}")
        return False

def main():
    """Create and populate both GradCafe databases with their respective datasets"""
    print("=" * 70)
    print("Setting up GradCafe databases...")
    print("=" * 70)

    # Create databases
    print("\n1. Creating databases...")
    print("   - Creating gradcafe database...")
    run_command("createdb gradcafe 2>&1")

    print("   - Creating gradcafe_sample database...")
    run_command("createdb gradcafe_sample 2>&1")

    # Load data into gradcafe database
    print("\n2. Loading full dataset into gradcafe database...")
    print("   Source: module_2/llm_extend_applicant_data.json")
    try:
        load_data(dbname='gradcafe', file_path='module_2/llm_extend_applicant_data.json')
        print("   ✓ Successfully loaded full dataset")
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(f"   ✗ Error loading full dataset: {exc}")

    # Load data into gradcafe_sample database
    print("\n3. Loading sample dataset into gradcafe_sample database...")
    print("   Source: module_3/sample_data/llm_extend_applicant_data.json")
    try:
        load_data(
            dbname='gradcafe_sample',
            file_path='module_3/sample_data/llm_extend_applicant_data.json'
        )
        print("   ✓ Successfully loaded sample dataset")
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(f"   ✗ Error loading sample dataset: {exc}")

    print("\n" + "=" * 70)
    print("Setup complete! You can now:")
    print("  1. Run: python module_3/app.py")
    print("  2. Visit: http://127.0.0.1:8080")
    print("  3. Use the 'Switch Database' button to toggle between datasets")
    print("=" * 70)

if __name__ == "__main__":
    main()
