#!/usr/bin/env python3

from agents.parsing_agent import parse_command
from agents.scheduler_agent import schedule_message

if __name__ == "__main__":
    user_input = input("Enter command: ")
    parsed = parse_command(user_input)
    schedule_message(parsed)