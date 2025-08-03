#!/usr/bin/env python3
"""
Command-line utility for viewing and filtering structured logs.

Usage:
    python log_viewer.py [options] [log_file]

Options:
    --level LEVEL         Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    --category CATEGORY   Filter by error category
    --request-id ID       Filter by request ID
    --user-id ID          Filter by user ID
    --operation TYPE      Filter by operation type
    --service NAME        Filter by service name
    --start-time TIME     Filter logs after this time (ISO format)
    --end-time TIME       Filter logs before this time (ISO format)
    --format FORMAT       Output format (pretty, json, compact)
    --tail N              Show only the last N logs
    --follow              Follow log file (like tail -f)
    --help                Show this help message

Examples:
    python log_viewer.py logs/app.log --level ERROR
    python log_viewer.py logs/app.log --category database --format pretty
    python log_viewer.py logs/app.log --request-id abc-123 --format json
    python log_viewer.py --follow --level WARNING
"""

import os
import sys
import json
import time
import argparse
import datetime
from typing import Dict, Any, List, Optional, TextIO
import re
import signal


# ANSI color codes for pretty printing
COLORS = {
    "DEBUG": "\033[36m",     # Cyan
    "INFO": "\033[32m",      # Green
    "WARNING": "\033[33m",   # Yellow
    "ERROR": "\033[31m",     # Red
    "CRITICAL": "\033[35m",  # Magenta
    "RESET": "\033[0m"       # Reset
}


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="View and filter structured logs")
    
    parser.add_argument("log_file", nargs="?", default="-", 
                        help="Log file to process (default: stdin)")
    
    parser.add_argument("--level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Filter by log level")
    
    parser.add_argument("--category", help="Filter by error category")
    
    parser.add_argument("--request-id", help="Filter by request ID")
    
    parser.add_argument("--user-id", help="Filter by user ID")
    
    parser.add_argument("--operation", help="Filter by operation type")
    
    parser.add_argument("--service", help="Filter by service name")
    
    parser.add_argument("--start-time", help="Filter logs after this time (ISO format)")
    
    parser.add_argument("--end-time", help="Filter logs before this time (ISO format)")
    
    parser.add_argument("--format", choices=["pretty", "json", "compact"], default="pretty",
                        help="Output format (default: pretty)")
    
    parser.add_argument("--tail", type=int, help="Show only the last N logs")
    
    parser.add_argument("--follow", action="store_true", 
                        help="Follow log file (like tail -f)")
    
    return parser.parse_args()


def parse_log_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse a JSON log line."""
    line = line.strip()
    if not line:
        return None
    
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None


def should_include_log(log: Dict[str, Any], args) -> bool:
    """Check if log entry matches filter criteria."""
    # Filter by log level
    if args.level and log.get("level") != args.level:
        return False
    
    # Filter by error category
    if args.category and log.get("error_category") != args.category:
        return False
    
    # Filter by request ID
    if args.request_id and log.get("request_id") != args.request_id:
        return False
    
    # Filter by user ID
    if args.user_id and str(log.get("user_id")) != args.user_id:
        return False
    
    # Filter by operation type
    if args.operation and log.get("operation") != args.operation:
        return False
    
    # Filter by service name
    if args.service and log.get("service") != args.service:
        return False
    
    # Filter by start time
    if args.start_time:
        try:
            start_time = datetime.datetime.fromisoformat(args.start_time.replace("Z", "+00:00"))
            log_time = datetime.datetime.fromisoformat(log.get("timestamp", "").replace("Z", "+00:00"))
            if log_time < start_time:
                return False
        except (ValueError, TypeError):
            pass
    
    # Filter by end time
    if args.end_time:
        try:
            end_time = datetime.datetime.fromisoformat(args.end_time.replace("Z", "+00:00"))
            log_time = datetime.datetime.fromisoformat(log.get("timestamp", "").replace("Z", "+00:00"))
            if log_time > end_time:
                return False
        except (ValueError, TypeError):
            pass
    
    return True


def format_log_pretty(log: Dict[str, Any]) -> str:
    """Format log entry in pretty format."""
    level = log.get("level", "INFO")
    timestamp = log.get("timestamp", "")
    message = log.get("message", "")
    
    # Basic log line
    log_line = f"{COLORS[level]}{timestamp} [{level}]{COLORS['RESET']} {message}"
    
    # Add request ID if available
    if "request_id" in log:
        log_line += f" (request_id: {log['request_id']})"
    
    # Add error category if available
    if "error_category" in log:
        log_line += f" (category: {log['error_category']})"
    
    # Add operation if available
    if "operation" in log:
        log_line += f" (operation: {log['operation']})"
    
    # Add exception if available
    if "exception" in log:
        exception = log["exception"]
        log_line += f"\n  Exception: {exception.get('type')}: {exception.get('message')}"
    
    return log_line


def format_log_compact(log: Dict[str, Any]) -> str:
    """Format log entry in compact format."""
    level = log.get("level", "INFO")
    timestamp = log.get("timestamp", "").split("T")[1].split(".")[0]  # Just time part
    message = log.get("message", "")
    
    # Basic log line
    log_line = f"{timestamp} [{level[0]}] {message}"
    
    # Add request ID if available (shortened)
    if "request_id" in log:
        request_id = log["request_id"]
        if len(request_id) > 8:
            request_id = request_id[:8]
        log_line += f" ({request_id})"
    
    return log_line


def process_logs(file_obj: TextIO, args):
    """Process and filter log entries."""
    # For tail mode, buffer logs
    if args.tail:
        buffer = []
        for line in file_obj:
            log = parse_log_line(line)
            if log and should_include_log(log, args):
                buffer.append(log)
                if len(buffer) > args.tail:
                    buffer.pop(0)
        
        # Output buffered logs
        for log in buffer:
            output_log(log, args)
    
    # For normal mode, process logs sequentially
    else:
        for line in file_obj:
            log = parse_log_line(line)
            if log and should_include_log(log, args):
                output_log(log, args)


def follow_logs(file_obj: TextIO, args):
    """Follow log file and process new entries."""
    # Go to end of file
    file_obj.seek(0, os.SEEK_END)
    
    # Process new lines as they are added
    while True:
        line = file_obj.readline()
        if line:
            log = parse_log_line(line)
            if log and should_include_log(log, args):
                output_log(log, args)
        else:
            time.sleep(0.1)


def output_log(log: Dict[str, Any], args):
    """Output log entry in specified format."""
    if args.format == "json":
        print(json.dumps(log))
    elif args.format == "compact":
        print(format_log_compact(log))
    else:  # pretty
        print(format_log_pretty(log))


def main():
    """Main entry point."""
    args = parse_args()
    
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    
    # Open log file or use stdin
    if args.log_file == "-":
        if args.follow:
            print("Cannot follow stdin, use a file instead", file=sys.stderr)
            sys.exit(1)
        process_logs(sys.stdin, args)
    else:
        try:
            with open(args.log_file, "r") as file_obj:
                if args.follow:
                    follow_logs(file_obj, args)
                else:
                    process_logs(file_obj, args)
        except FileNotFoundError:
            print(f"Error: Log file '{args.log_file}' not found", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()