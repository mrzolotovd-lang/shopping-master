#!/usr/bin/env python3
"""Demo script for Chat Interface."""

from src.database.connection import DatabaseConnection
from src.interfaces.chat import ChatInterface


def main():
    """Run chat interface demo."""
    print("=" * 70)
    print("🛒 SHOPPING MASTER - Chat Interface Demo")
    print("=" * 70)
    print()

    # Initialize
    db = DatabaseConnection(DatabaseConnection.get_sqlite_url("./data/shopping.db"))
    chat = ChatInterface(db)

    # Demo commands
    demo_commands = [
        # Set user
        ("user", "Привет, я Александр!"),
        
        # Status queries
        ("что есть дома?", None),
        ("список покупок", None),
        ("статус молоко", None),
        
        # Purchase commands
        ("купил молоко 2 литра", None),
        ("купил 5 йогуртов", None),
        
        # Update commands
        ("молока осталось половина", None),
        ("кефир почти закончился", None),
        
        # Unknown command
        ("абракадабра", None),
    ]

    for command, _ in demo_commands:
        print(f"👤 Вы: {command}")
        print("-" * 70)
        
        if command == "user":
            response = chat.set_user(1, "Александр")
        else:
            response = chat.process_message(command)
        
        print(f"🤖 Агент: {response}")
        print()
        print()

    # Show final status
    print("=" * 70)
    print("📊 FINAL STATUS")
    print("=" * 70)
    print()
    
    print(chat.process_message("что есть дома"))
    print()
    print(chat.process_message("список покупок"))
    print()


if __name__ == "__main__":
    main()
