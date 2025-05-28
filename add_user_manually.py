#!/usr/bin/env python3
"""
Manual User Management for FastFounder Daily Bot
Add users manually without needing 24/7 polling.
"""

import logging
import sys
from user_manager import UserManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def add_user_interactive():
    """Add a user interactively."""
    user_manager = UserManager()
    
    print("🤖 FastFounder Daily Bot - Add User")
    print("=" * 40)
    
    # Get user details
    chat_id = input("Enter Telegram Chat ID: ").strip()
    username = input("Enter username (optional): ").strip() or None
    first_name = input("Enter first name (optional): ").strip() or None
    last_name = input("Enter last name (optional): ").strip() or None
    
    # Add user
    success = user_manager.add_user(chat_id, username, first_name, last_name)
    
    if success:
        total_users = user_manager.get_user_count()
        print(f"✅ User {chat_id} added successfully!")
        print(f"📊 Total active users: {total_users}")
    else:
        print("❌ Failed to add user")


def list_users():
    """List all users."""
    user_manager = UserManager()
    
    active_users = user_manager.get_active_users()
    total_users = user_manager.get_user_count()
    
    print(f"📊 Total active users: {total_users}")
    print("=" * 40)
    
    if not active_users:
        print("No active users found.")
        return
    
    for chat_id in active_users:
        user_info = user_manager.get_user_info(chat_id)
        username = user_info.get('username', 'N/A')
        first_name = user_info.get('first_name', 'N/A')
        joined_date = user_info.get('joined_date', 'N/A')[:10] if user_info.get('joined_date') != 'N/A' else 'N/A'
        message_count = user_info.get('message_count', 0)
        
        print(f"Chat ID: {chat_id}")
        print(f"  Username: @{username}" if username != 'N/A' else "  Username: N/A")
        print(f"  Name: {first_name}" if first_name != 'N/A' else "  Name: N/A")
        print(f"  Joined: {joined_date}")
        print(f"  Messages received: {message_count}")
        print("-" * 30)


def remove_user_interactive():
    """Remove a user interactively."""
    user_manager = UserManager()
    
    print("🗑️ FastFounder Daily Bot - Remove User")
    print("=" * 40)
    
    # Show current users first
    list_users()
    
    chat_id = input("\nEnter Chat ID to remove: ").strip()
    
    success = user_manager.remove_user(chat_id)
    
    if success:
        print(f"✅ User {chat_id} removed successfully!")
    else:
        print(f"❌ User {chat_id} not found")


def get_chat_id_instructions():
    """Show instructions for getting chat ID."""
    print("📱 How to get your Telegram Chat ID:")
    print("=" * 40)
    print("1. Send a message to your bot")
    print("2. Go to: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates")
    print("3. Look for 'chat':{'id': YOUR_CHAT_ID}")
    print("4. Use that number as the Chat ID")
    print()
    print("Example:")
    print("If you see: 'chat':{'id': 717156736}")
    print("Your Chat ID is: 717156736")


def main():
    """Main menu."""
    while True:
        print("\n🤖 FastFounder Daily Bot - User Management")
        print("=" * 50)
        print("1. Add user")
        print("2. List users")
        print("3. Remove user")
        print("4. How to get Chat ID")
        print("5. Exit")
        print("=" * 50)
        
        choice = input("Choose an option (1-5): ").strip()
        
        if choice == '1':
            add_user_interactive()
        elif choice == '2':
            list_users()
        elif choice == '3':
            remove_user_interactive()
        elif choice == '4':
            get_chat_id_instructions()
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main() 