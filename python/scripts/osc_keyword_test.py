#!/usr/bin/env python3
"""
OSC Keyword Test - Initialize all channels in TouchDesigner
Sends a pulse to every keyword address so they appear in OSC In CHOP
"""

import time
from pythonosc import udp_client
import argparse

def get_all_keywords():
    """Return the complete keyword mapping with synonyms"""
    return {
                 # LOVE / AFFECTION
    "love": "/keyword/love",
    "adore": "/keyword/love",
    "cherish": "/keyword/love",
    "enjoy": "/keyword/love",
    "appreciate": "/keyword/love",
    "treasure": "/keyword/love",
    
    # HATE / NEGATIVITY
    "hate": "/keyword/hate",
    "despise": "/keyword/hate",
    "detest": "/keyword/hate",
    "loathe": "/keyword/hate",
    "dislike": "/keyword/hate",
    
    # STOP / END
    "stop": "/keyword/stop",
    "halt": "/keyword/stop",
    "cease": "/keyword/stop",
    "end": "/keyword/stop",
    "quit": "/keyword/stop",
    "pause": "/keyword/stop",
    
    # DEATH / DYING
    "die": "/keyword/die",
    "death": "/keyword/die",
    "dead": "/keyword/die",
    "kill": "/keyword/die",
    "killed": "/keyword/die",
    "dying": "/keyword/die",
    
    # LIGHT / BRIGHTNESS
    "light": "/keyword/light",
    "bright": "/keyword/light",
    "shine": "/keyword/light",
    "glow": "/keyword/light",
    "illuminate": "/keyword/light",
    "sunny": "/keyword/light",
    "radiant": "/keyword/light",
    
    # DARK / DARKNESS
    "dark": "/keyword/dark",
    "darkness": "/keyword/dark",
    "shadow": "/keyword/dark",
    "black": "/keyword/dark",
    "dim": "/keyword/dark",
    "night": "/keyword/dark",
    
    
    # SPEED - SLOW
    "slow": "/keyword/slow",
    "slowly": "/keyword/slow",
    
 
    # EMOTIONS - HAPPY
    "happy": "/keyword/happy",
    "joy": "/keyword/happy",
    "joyful": "/keyword/happy",
    "glad": "/keyword/happy",
    "delighted": "/keyword/happy",
    "pleased": "/keyword/happy",
    "cheerful": "/keyword/happy",
    
    # EMOTIONS - SAD
    "sad": "/keyword/sad",
    "sorrow": "/keyword/sad",
    "grief": "/keyword/sad",
    "melancholy": "/keyword/sad",
    "unhappy": "/keyword/sad",
    "depressed": "/keyword/sad",
    
    # EMOTIONS - ANGRY
    "angry": "/keyword/angry",
    "anger": "/keyword/angry",
    "mad": "/keyword/angry",
    "furious": "/keyword/angry",
    "rage": "/keyword/angry",
    "upset": "/keyword/angry",
    
    # EMOTIONS - FEAR
    "fear": "/keyword/fear",
    "afraid": "/keyword/fear",
    "scared": "/keyword/fear",
    "terror": "/keyword/fear",
    "frightened": "/keyword/fear",
    "anxiety": "/keyword/fear",
    
    }

def initialize_channels(ip="127.0.0.1", port=9000, pulse_duration=0.1):
    """Send pulses to all unique OSC addresses to create channels"""
    
    client = udp_client.SimpleUDPClient(ip, port)
    keywords = get_all_keywords()
    
    # Get unique OSC addresses
    unique_addresses = sorted(set(keywords.values()))
    
    print("=" * 60)
    print(f"OSC KEYWORD CHANNEL INITIALIZER")
    print(f"Target: {ip}:{port}")
    print("=" * 60)
    print(f"\nInitializing {len(unique_addresses)} unique channels...")
    print("(These will appear in your TouchDesigner OSC In CHOP)\n")
    
    try:
        # Send startup signal
        client.send_message("/system/init_start", 1.0)
        time.sleep(0.5)
        
        # Pulse each unique address
        for i, address in enumerate(unique_addresses, 1):
            channel_name = address.split('/')[-1]  # Get last part of address
            
            # Send pulse (ON)
            client.send_message(address, 1.0)
            print(f"[{i:2d}/{len(unique_addresses)}] ✓ {address:25s} → keyword_{channel_name}")
            
            time.sleep(pulse_duration)
            
            # Send reset (OFF)
            client.send_message(address, 0.0)
            
            time.sleep(0.05)
        
        # Send completion signal
        client.send_message("/system/init_complete", 1.0)
        time.sleep(0.1)
        client.send_message("/system/init_complete", 0.0)
        
        print("\n" + "=" * 60)
        print("✅ INITIALIZATION COMPLETE!")
        print("=" * 60)
        print("\nExpected channels in TouchDesigner OSC In CHOP:")
        print("-" * 60)
        for address in unique_addresses:
            channel_name = address.split('/')[-1]
            print(f"  • keyword_{channel_name}")
        print("\nPlus:")
        print("  • system_init_start")
        print("  • system_init_complete")
        print("  • transcription_text (created during speech recognition)")
        
        print("\n" + "=" * 60)
        print("KEYWORD MAPPINGS (synonyms → OSC address):")
        print("=" * 60)
        
        # Group keywords by OSC address
        address_to_words = {}
        for word, addr in keywords.items():
            if addr not in address_to_words:
                address_to_words[addr] = []
            address_to_words[addr].append(word)
        
        for address in sorted(address_to_words.keys()):
            channel_name = address.split('/')[-1]
            words = sorted(address_to_words[address])
            print(f"\n{address} (keyword_{channel_name}):")
            print(f"  → {', '.join(words)}")
        
        print("\n" + "=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nInitialization interrupted.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure TouchDesigner is running with OSC In CHOP configured!")

def test_specific_keyword(keyword, ip="127.0.0.1", port=9000):
    """Test a specific keyword trigger"""
    keywords = get_all_keywords()
    
    if keyword.lower() not in keywords:
        print(f"❌ Keyword '{keyword}' not found!")
        print(f"\nAvailable keywords: {', '.join(sorted(keywords.keys()))}")
        return
    
    client = udp_client.SimpleUDPClient(ip, port)
    address = keywords[keyword.lower()]
    
    print(f"Testing keyword: '{keyword}' → {address}")
    
    for i in range(3):
        client.send_message(address, 1.0)
        print(f"  Pulse {i+1}: ON")
        time.sleep(0.2)
        client.send_message(address, 0.0)
        print(f"  Pulse {i+1}: OFF")
        time.sleep(0.5)
    
    print("✓ Test complete!")

def main():
    parser = argparse.ArgumentParser(
        description="Initialize OSC channels for all keywords in TouchDesigner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize all channels
  python osc_keyword_test.py
  
  # Initialize on custom IP/port
  python osc_keyword_test.py --ip 192.168.1.100 --port 8000
  
  # Test specific keyword
  python osc_keyword_test.py --test love
  
  # Slower pulse for visualization
  python osc_keyword_test.py --duration 0.5
        """
    )
    parser.add_argument("--ip", default="127.0.0.1", 
                        help="OSC IP address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=9000, 
                        help="OSC port (default: 9000)")
    parser.add_argument("--duration", type=float, default=0.1,
                        help="Pulse duration in seconds (default: 0.1)")
    parser.add_argument("--test", type=str,
                        help="Test a specific keyword (e.g., 'love', 'angry')")
    
    args = parser.parse_args()
    
    if args.test:
        test_specific_keyword(args.test, args.ip, args.port)
    else:
        initialize_channels(args.ip, args.port, args.duration)

if __name__ == "__main__":
    main()
