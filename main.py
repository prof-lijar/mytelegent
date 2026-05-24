from __future__ import annotations

import argparse
import sys
import asyncio
from datetime import datetime
from typing import Optional

from tools.db_tool import initialize_database, insert_scheduled_message, list_pending_messages, cancel_message
from tools.logging_tool import get_logger
from agents.parsing_agent import ParsingAgent
from schemas.models import ParsedMessageCommand

# Import the scheduler main logic
from run_scheduler import main as scheduler_main

logger = get_logger('main_cli')

def handle_schedule(args: argparse.Namespace, parser: ParsingAgent) -> None:
    '''Handle the scheduling of a message.'''
    user_input = args.message
    logger.info(f'User input received via CLI: {user_input}')
    
    # 1. Parse the command
    parsed_command = parser.parse_command(user_input)
    
    if parsed_command is None:
        print('❌ I couldn\'t understand that command. Please try rephrasing it.')
        logger.warning(f'Failed to parse user input: {user_input}')
        return

    # 2. Present for confirmation
    print('\n--- Proposed Schedule ---')
    print(f'Recipient: {parsed_command.target} ({parsed_command.target_type})')
    print(f'Message:   {parsed_command.message}')
    
    # Avoid backslashes in f-string expressions (Python < 3.12)
    time_str = parsed_command.scheduled_time.strftime('%Y-%m-%d %H:%M %Z')
    print(f'Time:      {time_str}')
    print(f'Confidence: {parsed_command.confidence:.2f}')
    print('------------------------')
    
    try:
        confirm = input('Confirm scheduling? (y/n): ').strip().lower()
    except EOFError:
        print('\nConfirmation required. Please run the command in an interactive terminal.')
        return
    
    if confirm == 'y':
        # 3. Save to database
        msg_id = insert_scheduled_message(parsed_command)
        print(f'✅ Success! Message scheduled with ID: {msg_id}')
        logger.info(f'Successfully scheduled message {msg_id} for {parsed_command.target}')
    else:
        print('👎 Scheduling cancelled.')
        logger.info('User cancelled the scheduling request.')

def handle_list() -> None:
    '''List all pending messages.'''
    messages = list_pending_messages()
    if not messages:
        print('No pending messages found.')
        return

    print(f'\n{"ID":<5} {"Recipient":<20} {"Scheduled Time":<25} {"Message":<30}')
    print('-' * 80)
    for msg in messages:
        # Truncate message for display
        msg_text = (msg.message[:27] + '...') if len(msg.message) > 30 else msg.message
        
        # Avoid backslashes in f-string expressions
        time_str = msg.scheduled_time.strftime('%Y-%m-%d %H:%M')
        print(f'{msg.id:<5} {msg.target:<20} {time_str:<25} {msg_text:<30}')
    print('-' * 80)
    print(f'Total pending: {len(messages)}\n')

def handle_cancel(args: argparse.Namespace) -> None:
    '''Cancel a scheduled message by ID.'''
    success = cancel_message(args.id)
    if success:
        print(f'✅ Message {args.id} has been cancelled.')
        logger.info(f'Cancelled message {args.id}')
    else:
        print(f'❌ Message {args.id} not found or could not be cancelled.')
        logger.warning(f'Failed to cancel message {args.id}')

def main() -> None:
    # Initialize system
    try:
        initialize_database()
    except Exception as e:
        logger.error(f'Critical error initializing database: {e}')
        print(f'Error: Could not initialize database. See logs/errors.log for details.')
        sys.exit(1)

    parser = argparse.ArgumentParser(description='tiny-jarvis: AI Telegram Scheduler CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Schedule command
    sched_parser = subparsers.add_parser('schedule', help='Schedule a new message')
    sched_parser.add_argument('message', type=str, help='The natural language command to schedule')

    # List command
    subparsers.add_parser('list', help='List all pending messages')

    # Cancel command
    cancel_parser = subparsers.add_parser('cancel', help='Cancel a scheduled message')
    cancel_parser.add_argument('id', type=int, help='The ID of the message to cancel')

    # Run-scheduler command
    subparsers.add_parser('run-scheduler', help='Start the background scheduler process')

    args = parser.parse_args()

    if args.command == 'schedule':
        parsing_agent = ParsingAgent()
        handle_schedule(args, parsing_agent)
    elif args.command == 'list':
        handle_list()
    elif args.command == 'cancel':
        handle_cancel(args)
    elif args.command == 'run-scheduler':
        try:
            asyncio.run(scheduler_main())
        except KeyboardInterrupt:
            print('\nStopping scheduler...')
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
