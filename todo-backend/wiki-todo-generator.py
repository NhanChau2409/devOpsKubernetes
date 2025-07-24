#!/usr/bin/env python3
"""
Wiki Todo Generator - CronJob script
Generates a new todo with a random Wikipedia article URL every hour
"""

import requests
import os
import sys
from datetime import datetime


def get_random_wikipedia_url():
    """Get a random Wikipedia article URL"""
    try:
        # Make request to Wikipedia random page
        response = requests.get(
            "https://en.wikipedia.org/wiki/Special:Random",
            allow_redirects=True,
            timeout=10,
        )

        if response.status_code == 302:
            # Extract the final URL from Location header
            final_url = response.headers.get("Location")
            if final_url:
                return final_url
            else:
                print("❌ No Location header found in redirect")
                return None
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Error getting random Wikipedia URL: {e}")
        return None


def create_todo(todo_text, api_url):
    """Create a new todo via the API"""
    try:
        payload = {"text": todo_text}
        response = requests.post(f"{api_url}/todos", json=payload, timeout=10)

        if response.status_code == 201:
            todo_data = response.json()
            print(f"✅ Todo created successfully: {todo_data['id']}")
            return True
        else:
            print(f"❌ Failed to create todo: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error creating todo: {e}")
        return False


def main():
    """Main function"""
    print(f"🕐 Wiki Todo Generator started at {datetime.now()}")

    # Get API URL from environment variable
    api_url = os.environ.get("TODO_API_URL", "http://todo-backend:8080")

    # Get random Wikipedia URL
    wiki_url = get_random_wikipedia_url()
    if not wiki_url:
        print("❌ Failed to get random Wikipedia URL")
        sys.exit(1)

    # Create todo text
    todo_text = f"Read {wiki_url}"
    print(f"📚 Generated todo: {todo_text}")

    # Create the todo
    success = create_todo(todo_text, api_url)

    if success:
        print("✅ Wiki todo generator completed successfully")
        sys.exit(0)
    else:
        print("❌ Wiki todo generator failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
