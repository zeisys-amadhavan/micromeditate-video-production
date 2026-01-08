from elevenlabs.client import ElevenLabs
from elevenlabs.play import play  # (kept as-is, though not used below)

from io import BytesIO
from pydub import AudioSegment
from pydub.silence import detect_nonsilent  # NEW

client = ElevenLabs(
    api_key="sk_63d2ae7382d0221c03844d5e37aeff53c563d000c7948142"
)

# ONLY Brian
voices = [
    ("Brian", "nPczCjzI2devNBz1zQrb"),
]

SPEECH_MS = 4000
SILENCE_MS = 4000
EXHALE_PHASE_MS = 8000  # exhale + pause2 must not exceed this

chants = [
    ("Om namo", "śivāya namaḥ"),
    ("Om namo", "maheśvarāya namaḥ"),
    ("Om namo", "śambhave namaḥ"),
    ("Om namo", "pinākine namaḥ"),
    ("Om namo", "śaśi-śekharāya namaḥ"),
    ("Om namo", "vāma-devāya namaḥ"),
    ("Om namo", "virūpākṣāya namaḥ"),
    ("Om namo", "kapardine namaḥ"),
    ("Om namo", "nīla-lohitāya namaḥ"),
    ("Om namo", "śāṅkarāya namaḥ"),
    ("Om namo", "śūla-pāṇaye namaḥ"),
    ("Om namo", "khaṭvāṅgine namaḥ"),
    ("Om namo", "viṣṇu-vallabhāya namaḥ"),
    ("Om namo", "śipi-viṣṭāya namaḥ"),
    ("Om namo", "ambikā-nāthāya namaḥ"),
    ("Om namo", "śrī-kaṇṭhāya namaḥ"),
    ("Om namo", "bhakta-vatsalāya namaḥ"),
    ("Om namo", "bhavāya namaḥ"),
    ("Om namo", "śarvāya namaḥ"),
    ("Om namo", "trilokeśāya namaḥ"),
    ("Om namo", "śita-kaṇṭhāya namaḥ"),
    ("Om namo", "śivā-priyāya namaḥ"),
    ("Om namo", "ugrāya namaḥ"),
    ("Om namo", "kapāline namaḥ"),
    ("Om namo", "kāmaraye namaḥ"),
    ("Om namo", "andhakāsura sūdanāya namaḥ"),
    ("Om namo", "gaṅgā-dharāya namaḥ"),
    ("Om namo", "lalāṭākṣāya namaḥ"),
    ("Om namo", "kalakalāya namaḥ"),
    ("Om namo", "kṛpa-nidhaye namaḥ"),
    ("Om namo", "bhīmāya namaḥ"),
    ("Om namo", "paraśu-hastāya namaḥ"),
    ("Om namo", "mṛga-pānaye namaḥ"),
    ("Om namo", "jaṭā-dharāya namaḥ"),
    ("Om namo", "kailāsa-vāsine namaḥ"),
    ("Om namo", "kavachine namaḥ"),
    ("Om namo", "kaṭhorāya namaḥ"),
    ("Om namo", "tripurāntakāya namaḥ"),
    ("Om namo", "vṛṣāṅkāya namaḥ"),
    ("Om namo", "vṛṣabhā rūḍhāya namaḥ"),
    ("Om namo", "bhasmo-dhūlita vigrahāya namaḥ"),
    ("Om namo", "sāma-priyāya namaḥ"),
    ("Om namo", "svara-mayāya namaḥ"),
    ("Om namo", "trayī-mūrtaye namaḥ"),
    ("Om namo", "an-īśvarāya namaḥ"),
    ("Om namo", "sarva-jñāya namaḥ"),
    ("Om namo", "paramātmane namaḥ"),
    ("Om namo", "soma-sūryāgni-lochanāya namaḥ"),
    ("Om namo", "haviṣe namaḥ"),
    ("Om namo", "yajña-mayāya namaḥ"),
    ("Om namo", "somāya namaḥ"),
    ("Om namo", "pañcha-vaktrāya namaḥ"),
    ("Om namo", "sadā-śivāya namaḥ"),
    ("Om namo", "viśveśvarāya namaḥ"),
    ("Om namo", "vīra-bhadrāya namaḥ"),
    ("Om namo", "gaṇa-nāthāya namaḥ"),
    ("Om namo", "prajā-pataye namaḥ"),
    ("Om namo", "hiraṇya-retase namaḥ"),
    ("Om namo", "durdharṣāya namaḥ"),
    ("Om namo", "girīśāya namaḥ"),
    ("Om namo", "giri-śāya namaḥ"),
    ("Om namo", "an-aghāya namaḥ"),
    ("Om namo", "bhujaṅga-bhūṣaṇāya namaḥ"),
    ("Om namo", "bhargāya namaḥ"),
    ("Om namo", "giri-dhanvane namaḥ"),
    ("Om namo", "giri-priyāya namaḥ"),
    ("Om namo", "kṛtti-vāsase namaḥ"),
    ("Om namo", "purā-rātaye namaḥ"),
    ("Om namo", "bhagavate namaḥ"),
    ("Om namo", "pramathādhipāya namaḥ"),
    ("Om namo", "mṛtyuñ-jayāya namaḥ"),
    ("Om namo", "sūkṣma-tanave namaḥ"),
    ("Om namo", "jagad-vyāpine namaḥ"),
    ("Om namo", "jagad-gurave namaḥ"),
    ("Om namo", "vyoma-keśāya namaḥ"),
    ("Om namo", "mahāsena-janakāya namaḥ"),
    ("Om namo", "chāru-vikramāya namaḥ"),
    ("Om namo", "rudrāya namaḥ"),
    ("Om namo", "bhūta-pataye namaḥ"),
    ("Om namo", "sthāṇave namaḥ"),
    ("Om namo", "ahirbudhnyāya namaḥ"),
    ("Om namo", "dig-ambarāya namaḥ"),
    ("Om namo", "aṣṭa-mūrtaye namaḥ"),
    ("Om namo", "anekātmane namaḥ"),
    ("Om namo", "sāttvikāya namaḥ"),
    ("Om namo", "śuddha vigrahāya namaḥ"),
    ("Om namo", "śāśvatāya namaḥ"),
    ("Om namo", "khaṇḍa-paraśave namaḥ"),
    ("Om namo", "a-jāya namaḥ"),
    ("Om namo", "pāśa-vimochanāya namaḥ"),
    ("Om namo", "mṛḍāya namaḥ"),
    ("Om namo", "paśu-pataye namaḥ"),
    ("Om namo", "devāya namaḥ"),
    ("Om namo", "mahā-devāya namaḥ"),
    ("Om namo", "a-vyayāya namaḥ"),
    ("Om namo", "harāye namaḥ"),
    ("Om namo", "pūṣa-danta-bhide namaḥ"),
    ("Om namo", "a-vyagrāya namaḥ"),
    ("Om namo", "dakṣā-dhvara harāya namaḥ"),
    ("Om namo", "harāye namaḥ"),
    ("Om namo", "bhaga netra-bhide namaḥ"),
    ("Om namo", "a-vyaktāya namaḥ"),
    ("Om namo", "sahasrākṣāya namaḥ"),
    ("Om namo", "sahasra-pade namaḥ"),
    ("Om namo", "apavarga pradāya namaḥ"),
    ("Om namo", "an-antāya namaḥ"),
    ("Om namo", "tārakāya namaḥ"),
    ("Om namo", "parameśvarāya namaḥ"),
]




def clean_tts_tail(seg: AudioSegment, label: str = "") -> AudioSegment:
    """
    Trim junk/noise after the spoken content.
    Keeps audio up to the last detected non-silent region, then fades out to true silence.
    """
    if len(seg) == 0:
        return seg

    # Dynamic threshold: treat anything ~20dB quieter than average as "silence"
    # (clamped so we don't get too aggressive)
    silence_thresh = max(-45, seg.dBFS - 20)

    ranges = detect_nonsilent(seg, min_silence_len=180, silence_thresh=silence_thresh)

    if not ranges:
        # If it thinks it's all silence/noise, just return a tiny silence segment
        return AudioSegment.silent(duration=0)

    # End at the last non-silent chunk + a tiny cushion
    end_ms = min(len(seg), ranges[-1][1] + 60)

    cleaned = seg[:end_ms]

    # Kill clicks + force a clean drop to zero
    cleaned = cleaned.fade_out(120)

    return cleaned

def tts_mp3_segment(text: str, voice_id: str) -> AudioSegment:
    audio_iter = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        language_code="hi",
        output_format="mp3_44100_128",
        apply_text_normalization="off",  # if your SDK errors, delete this line

        # NEW: reduce hallucinated tails / garbage syllables
        # If your SDK errors on this param, remove this block.
        voice_settings={
            "stability": 0.90,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True,
        },
    )
    mp3_bytes = b"".join(chunk for chunk in audio_iter if chunk)
    seg = AudioSegment.from_file(BytesIO(mp3_bytes), format="mp3")
    return clean_tts_tail(seg, label=text)  # NEW

def fit_to(seg: AudioSegment, target_ms: int, label: str = "") -> AudioSegment:
    if len(seg) > target_ms:
        print(f"WARNING: '{label}' was {len(seg)}ms > {target_ms}ms, trimming.")
        return seg[:target_ms]
    return seg + AudioSegment.silent(duration=(target_ms - len(seg)))

def exhale_and_pause(seg: AudioSegment, label: str = ""):
    if len(seg) >= EXHALE_PHASE_MS:
        print(f"WARNING: exhale '{label}' was {len(seg)}ms >= {EXHALE_PHASE_MS}ms, trimming to fit.")
        return seg[:EXHALE_PHASE_MS], AudioSegment.silent(duration=0)

    pause2_ms = EXHALE_PHASE_MS - len(seg)
    return seg, AudioSegment.silent(duration=pause2_ms)

for name, voice_id in voices:
    out = AudioSegment.silent(duration=0)

    for inhale_text, exhale_text in chants:
        inhale = fit_to(tts_mp3_segment(inhale_text, voice_id), SPEECH_MS, label=inhale_text)
        pause1 = AudioSegment.silent(duration=SILENCE_MS)

        exhale_raw = tts_mp3_segment(exhale_text, voice_id)
        exhale, pause2 = exhale_and_pause(exhale_raw, label=exhale_text)

        out += inhale + pause1 + exhale + pause2

    output_path = f"{name}_timed.mp3"
    out.export(output_path, format="mp3", bitrate="128k")
    print(f"Saved: {output_path}  (duration_ms={len(out)})")
