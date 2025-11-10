#!/usr/bin/env python3
"""
Simple OSC Test Script for TouchDesigner
Sends test messages to verify OSC communication
"""

import time
import random
from pythonosc import udp_client
import argparse

def test_osc(ip="127.0.0.1", port=9000):
    """Send test OSC messages to TouchDesigner"""
    
    # Create OSC client
    client = udp_client.SimpleUDPClient(ip, port)
    print(f"OSC Test Client → {ip}:{port}")
    print("-" * 40)
    
    # Test messages
    keywords = ["love", "hate", "stop", "light", "dark", "move", "red", "blue", "green"]
    
    print("Sending test messages...")
    print("(Watch your TouchDesigner OSC In CHOP)\n")
    
    try:
        # Send a startup message
        client.send_message("/test/started", 1.0)
        print("✓ Sent: /test/started = 1.0")
        time.sleep(1)
        
        # Test each keyword
        for keyword in keywords:
            address = f"/keyword/{keyword}"
            
            # Send trigger (1.0)
            client.send_message(address, 1.0)
            print(f"✓ Sent: {address} = 1.0 (ON)")
            time.sleep(0.5)
            
            # Send reset (0.0)
            client.send_message(address, 0.0)
            print(f"  Sent: {address} = 0.0 (OFF)")
            time.sleep(0.5)
        
        # Send some random values
        print("\nSending random values...")
        for i in range(5):
            value = random.random()
            client.send_message("/test/random", value)
            print(f"✓ Sent: /test/random = {value:.3f}")
            time.sleep(0.5)
        
        # Send a bundle test
        print("\nSending multiple values at once...")
        client.send_message("/test/x", 0.5)
        client.send_message("/test/y", 0.75)
        client.send_message("/test/z", 0.25)
        print("✓ Sent: /test/x=0.5, /test/y=0.75, /test/z=0.25")
        
        # Send completion message
        time.sleep(1)
        client.send_message("/test/completed", 1.0)
        print("\n✓ Test completed!")
        print("\nExpected channels in TouchDesigner OSC In CHOP:")
        print("  - keyword_love, keyword_hate, keyword_stop, etc.")
        print("  - test_started, test_random, test_x, test_y, test_z, test_completed")
        
    except KeyboardInterrupt:
        print("\nTest interrupted.")
    except Exception as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="OSC Test for TouchDesigner")
    parser.add_argument("--ip", default="127.0.0.1", help="OSC IP address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=9000, help="OSC port (default: 9000)")
    
    args = parser.parse_args()
    test_osc(args.ip, args.port)

if __name__ == "__main__":
    main()
