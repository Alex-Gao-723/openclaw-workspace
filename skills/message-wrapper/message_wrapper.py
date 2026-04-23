#!/usr/bin/env python3
"""
Message Delivery Wrapper - Robust message sending with retry logic
Fixes the '⚠️ ✉️ Message failed' issue in cron jobs
"""

import subprocess
import json
import sys
import time
import os
from typing import Optional, Dict, Any

# Configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def send_message(
    target: str,
    message: str,
    channel: str = "kimi-claw",
    retries: int = MAX_RETRIES,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Send a message with retry logic and proper error handling
    
    Args:
        target: Target recipient (open_id for kimi-claw)
        message: Message content
        channel: Channel to use (default: kimi-claw)
        retries: Number of retry attempts
        dry_run: If True, just print what would be sent
    
    Returns:
        Dict with 'success', 'message_id', and 'error' keys
    """
    result = {
        "success": False,
        "message_id": None,
        "error": None,
        "attempts": 0
    }
    
    if dry_run:
        print(f"[DRY RUN] Would send to {target} via {channel}:")
        print(f"Message: {message[:200]}...")
        result["success"] = True
        return result
    
    for attempt in range(1, retries + 1):
        result["attempts"] = attempt
        
        try:
            # Build the OpenClaw command
            cmd = [
                "openclaw", "message", "send",
                "--target", target,
                "--message", message,
                "--channel", channel
            ]
            
            # Execute with timeout
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Check output for success indicators
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
            combined = stdout + stderr
            
            # Ignore config warnings - they are not actual message errors
            cleaned_stderr = stderr
            if "Config warnings:" in stderr:
                # Remove config warning lines for error checking
                lines = stderr.split('\n')
                cleaned_lines = [l for l in lines if not l.strip().startswith('- plugins.') and 'Config warnings' not in l]
                cleaned_stderr = '\n'.join(cleaned_lines)
            
            # Success indicators (various possible outputs)
            success_indicators = [
                "messageId" in combined,
                "delivered" in combined.lower(),
                "Message delivered" in combined,
                proc.returncode == 0 and "Message failed" not in combined
            ]
            
            # Error indicators (real message failures, not config warnings)
            error_indicators = [
                "Message failed" in combined,
                "error" in cleaned_stderr.lower() and "delivered" not in combined.lower(),
                proc.returncode != 0 and "delivered" not in combined.lower() and not "Config warnings" in stderr
            ]
            
            if any(success_indicators) and not any(error_indicators):
                result["success"] = True
                # Try to extract message ID
                if "messageId:" in combined:
                    try:
                        result["message_id"] = combined.split("messageId:")[1].split()[0].strip()
                    except:
                        pass
                return result
            
            # If we get here, there was an issue
            error_msg = stderr if stderr else stdout
            result["error"] = f"Attempt {attempt}: {error_msg[:200]}"
            
            # Don't retry on certain fatal errors
            if "not found" in error_msg.lower() or "invalid" in error_msg.lower():
                break
                
        except subprocess.TimeoutExpired:
            result["error"] = f"Attempt {attempt}: Timeout after 30s"
        except Exception as e:
            result["error"] = f"Attempt {attempt}: {str(e)}"
        
        # Wait before retry
        if attempt < retries:
            time.sleep(RETRY_DELAY)
    
    return result


def send_to_master(
    message: str,
    channel: str = "kimi-claw",
    master_id: str = "ou_1f6604399e414700d963393e24420570",
    **kwargs
) -> Dict[str, Any]:
    """Convenience function to send message to Master"""
    return send_message(
        target=master_id,
        message=message,
        channel=channel,
        **kwargs
    )


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Robust message delivery wrapper")
    parser.add_argument("target", help="Target recipient (open_id)")
    parser.add_argument("message", help="Message content (or @file to read from file)")
    parser.add_argument("--channel", default="kimi-claw", help="Channel to use")
    parser.add_argument("--retries", type=int, default=MAX_RETRIES, help="Number of retries")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be sent without sending")
    
    args = parser.parse_args()
    
    # Handle file input
    message = args.message
    if message.startswith("@"):
        file_path = message[1:]
        try:
            with open(file_path, 'r') as f:
                message = f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    
    result = send_message(
        target=args.target,
        message=message,
        channel=args.channel,
        retries=args.retries,
        dry_run=args.dry_run
    )
    
    # Output result as JSON
    print(json.dumps(result, indent=2))
    
    # Exit with appropriate code
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
