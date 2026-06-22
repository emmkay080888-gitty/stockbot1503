#!/usr/bin/env python3
"""Seed the admin user into the users database.

Run this script once to create the admin account:
    python seed_admin.py

You can customize credentials via environment variables or command line args.
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is in path
ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.auth import seed_admin

def main():
    parser = argparse.ArgumentParser(description="Seed the admin user")
    parser.add_argument("--password", default="admin123", help="Admin password (default: admin123)")
    parser.add_argument("--email", default="admin@stockbot.local", help="Admin email")
    parser.add_argument("--question", default="What is your favorite book?", help="Secret question")
    parser.add_argument("--answer", default="admin", help="Secret answer")
    args = parser.parse_args()

    success, msg = seed_admin(
        password=args.password,
        email=args.email,
        secret_question=args.question,
        secret_answer=args.answer,
    )
    print(f"✅ {msg}")
    if success:
        print(f"\nYou can now log in with:")
        print(f"  Username: admin")
        print(f"  Password: {args.password}")

if __name__ == "__main__":
    main()
