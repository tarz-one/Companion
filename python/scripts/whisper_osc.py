#!/usr/bin/env python3
"""
Real-time Speech-to-Text with OSC output for TouchDesigner
Uses faster-whisper for transcription and sends OSC messages on keyword detection
"""

import sys
import queue
import threading
import time
from pathlib import Path
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from pythonosc import udp_client
from pythonosc.osc_message_builder import OscMessageBuilder
import argparse

class WhisperOSC:
    def __init__(self, 
                 model_size="base",
                 osc_ip="127.0.0.1", 
                 osc_port=9000,
                 device_id=None,
                 sample_rate=16000,
                 channels=1,
                 blocksize=1024):
        
        # Initialize Whisper model
        print(f"Loading Whisper model '{model_size}'...")
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        print("Model loaded!")
        
        # OSC client
        self.osc_client = udp_client.SimpleUDPClient(osc_ip, osc_port)
        print(f"OSC client configured: {osc_ip}:{osc_port}")
        
        # Audio parameters
        self.sample_rate = sample_rate
        self.channels = channels
        self.blocksize = blocksize
        self.device_id = device_id
        
        # Audio queue and buffer
        self.audio_queue = queue.Queue()
        self.audio_buffer = []
        self.buffer_duration = 3.0  # Process audio in 3-second chunks
        self.buffer_size = int(self.sample_rate * self.buffer_duration)
        
        # Keywords to detect (lowercase)
        self.keywords = {
            "love": "/keyword/love",
            "hate": "/keyword/hate",
            "stop": "/keyword/stop",
            "light": "/keyword/light",
            "dark": "/keyword/dark",
            "move": "/keyword/move",
            "fast": "/keyword/fast",
            "slow": "/keyword/slow",
            "red": "/keyword/red",
            "blue": "/keyword/blue",
            "green": "/keyword/green"
        }
        
        # Thread control
        self.running = False
        self.processing_thread = None
        
    def audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream - adds audio to queue"""
        if status:
            print(f"Audio callback status: {status}", file=sys.stderr)
        self.audio_queue.put(indata.copy())
    
    def process_audio(self):
        """Process audio from queue and transcribe"""
        print("Starting audio processing...")
        
        while self.running:
            try:
                # Collect audio chunks into buffer
                while not self.audio_queue.empty() and len(self.audio_buffer) < self.buffer_size:
                    chunk = self.audio_queue.get(timeout=0.1)
                    self.audio_buffer.extend(chunk[:, 0])  # Use first channel
                
                # Process when buffer is full
                if len(self.audio_buffer) >= self.buffer_size:
                    # Convert to numpy array
                    audio_np = np.array(self.audio_buffer[:self.buffer_size], dtype=np.float32)
                    
                    # Clear processed audio from buffer
                    self.audio_buffer = self.audio_buffer[self.buffer_size//2:]  # Keep half for overlap
                    
                    # Transcribe
                    segments, _ = self.model.transcribe(
                        audio_np,
                        beam_size=5,
                        language="en",
                        vad_filter=True,
                        vad_parameters=dict(min_silence_duration_ms=500)
                    )
                    
                    # Process transcription
                    for segment in segments:
                        text = segment.text.strip()
                        if text:
                            print(f"Transcribed: {text}")
                            self.detect_keywords(text)
                            
                            # Send full text as OSC
                            self.osc_client.send_message("/transcription/text", text)
                            
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Processing error: {e}", file=sys.stderr)
                time.sleep(0.1)
    
    def detect_keywords(self, text):
        """Detect keywords in transcribed text and send OSC messages"""
        text_lower = text.lower()
        
        for keyword, osc_address in self.keywords.items():
            if keyword in text_lower:
                print(f"  → Keyword detected: '{keyword}' → OSC: {osc_address}")
                # Send trigger (1.0) followed by reset (0.0) after short delay
                self.osc_client.send_message(osc_address, 1.0)
                # Schedule reset in separate thread to avoid blocking
                threading.Timer(0.1, lambda addr=osc_address: self.osc_client.send_message(addr, 0.0)).start()
    
    def list_audio_devices(self):
        """List available audio input devices"""
        print("\nAvailable audio input devices:")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                marker = " (DEFAULT)" if i == sd.default.device[0] else ""
                print(f"  {i}: {device['name']} [{device['max_input_channels']} channels]{marker}")
    
    def start(self):
        """Start audio stream and processing"""
        self.running = True
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self.process_audio)
        self.processing_thread.start()
        
        # Start audio stream
        print(f"\nStarting audio stream (device: {self.device_id or 'default'})...")
        print(f"Listening for keywords: {', '.join(self.keywords.keys())}")
        print("Press Ctrl+C to stop\n")
        
        try:
            with sd.InputStream(
                device=self.device_id,
                samplerate=self.sample_rate,
                channels=self.channels,
                blocksize=self.blocksize,
                callback=self.audio_callback
            ):
                # Keep main thread alive
                while self.running:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\nStopping...")
        except Exception as e:
            print(f"Stream error: {e}", file=sys.stderr)
        finally:
            self.stop()
    
    def stop(self):
        """Stop audio stream and processing"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=2)
        print("Stopped.")

def main():
    parser = argparse.ArgumentParser(description="Whisper STT → OSC for TouchDesigner")
    parser.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper model size (default: base)")
    parser.add_argument("--ip", default="127.0.0.1", help="OSC IP address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=9000, help="OSC port (default: 9000)")
    parser.add_argument("--device", type=int, help="Audio input device ID")
    parser.add_argument("--list-devices", action="store_true", help="List audio devices and exit")
    
    args = parser.parse_args()
    
    # Create processor
    processor = WhisperOSC(
        model_size=args.model,
        osc_ip=args.ip,
        osc_port=args.port,
        device_id=args.device
    )
    
    # List devices if requested
    if args.list_devices:
        processor.list_audio_devices()
        return
    
    # Start processing
    processor.start()

if __name__ == "__main__":
    main()
