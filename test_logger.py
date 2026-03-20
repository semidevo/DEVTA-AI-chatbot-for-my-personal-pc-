#!/usr/bin/env python
"""Test script to verify logger functionality"""

from logger import get_logger
import os

logger = get_logger('test')
logger.info('Test log entry from verification script')
logger.warning('This is a warning test')

print('✓ Logs directory created:', os.path.exists("logs"))
print('✓ Log file exists:', os.path.exists("logs/devta.log"))

# Show last few log entries
if os.path.exists("logs/devta.log"):
    with open("logs/devta.log", "r") as f:
        lines = f.readlines()
        print('✓ Log entries (last 5 lines):')
        for line in lines[-5:]:
            print(f'  {line.strip()}')

print('\n✓ Logger verification complete!')
