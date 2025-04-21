#!/usr/bin/env python
"""
Simple script to test Gmail API connectivity.
Run with: uv run python scripts/test_gmail_setup.py
"""
import gmail


def test_gmail_connection():
    """Tests connection to Gmail API and prints labels to verify access."""
    print("Starting Gmail API test...")

    # Use the gmail module with the MODIFY scope for testing
    service = gmail.get_gmail_service(scopes=gmail.GMAIL_MODIFY_SCOPE)
    print("Authentication successful!")

    # Attempt to get a few recent messages as additional verification
    print("\nChecking for recent messages...")
    messages = gmail.list_messages(service, max_results=3)
    if messages:
        print(f"Found {len(messages)} recent messages!")
        print("\n✅ SUCCESS: Your Gmail API setup is working correctly!")
    else:
        print("No messages found. This is unusual but might be normal for a new account.")

    print("\nAPI access test completed.")


if __name__ == "__main__":
    test_gmail_connection()
