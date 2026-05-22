from tools.config import Config
from tools.db_tool import initialize_database, insert_scheduled_message, get_due_messages, list_pending_messages
from schemas.models import ScheduledMessage, ParsedMessageCommand
from datetime import datetime, timedelta, timezone

def test_db():
    print("Testing DB Tool...")
    initialize_database()
    
    msg = ParsedMessageCommand(
        target="test_user",
        target_type="username",
        scheduled_time=datetime.now(timezone.utc) - timedelta(minutes=1),
        message="Hello Test!",
        confidence=1.0
    )
    
    msg_id = insert_scheduled_message(msg)
    print(f"Inserted message ID: {msg_id}")
    
    pending = list_pending_messages()
    print(f"Pending messages count: {len(pending)}")
    
    due = get_due_messages(datetime.now(timezone.utc))
    print(f"Due messages count: {len(due)}")
    
    assert len(pending) > 0
    assert len(due) > 0
    print("DB Tool tests passed!")

if __name__ == "__main__":
    test_db()
