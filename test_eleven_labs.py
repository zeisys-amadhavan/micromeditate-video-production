from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
import argparse


parser = argparse.ArgumentParser(description="Minimal ElevenLabs TTS test")

parser.add_argument("--api-key", required=True, help="ElevenLabs API key")
parser.add_argument("--text", required=True, help="Text to speak")
parser.add_argument("--voice-id", required=True, help="ElevenLabs voice ID")
parser.add_argument("--model-id", required=True, help="Model ID (e.g. eleven_multilingual_v2)")
parser.add_argument("--output-format", required=True, help="Output format (e.g. mp3_44100_128)")

args = parser.parse_args()


client = ElevenLabs(
    api_key=args.api_key
)

audio = client.text_to_speech.convert(
    text=args.text,
    voice_id=args.voice_id,
    model_id=args.model_id,
    output_format=args.output_format,
)

play(audio)
