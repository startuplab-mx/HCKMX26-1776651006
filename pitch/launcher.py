"""
NAHUAL Pitch Launcher — Tony Stark Mode v2

Detección mejorada:
  - Whisper con prompt bias para "Nahual" + fuzzy matching fonético
  - Aplausos por detección de transientes (picos súbitos vs ruido ambiente)
  - Wakeword "Vanguard" como backup (Whisper lo reconoce perfecto)

Uso:
    nahual_pitch.exe   (o python launcher.py)
"""

import os
import sys
import time
import wave
import struct
import subprocess
import webbrowser
import threading
import tempfile
import math
from pathlib import Path
from difflib import SequenceMatcher

# ══════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════

import os
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# NOTE: never hardcode API keys in source — set GROQ_API_KEY in your
# shell or .env before running. The previously hardcoded key has been
# rotated; pulling old commits will not give you a working key.

# Whisper prompt bias — le dice a Whisper qué vocabulario esperar
WHISPER_PROMPT = "Nahual, nagual, seguridad, ciberseguridad, Vanguard, activar escudo"

# Trigger words: exactas y fonéticas
# Whisper puede transcribir "nahual" como muchas variantes
TRIGGER_EXACT = [
    "nahual", "nagual", "nawal", "na wal", "na hual", "na cual",
    "nahúal", "nagúal", "nahual", "na gual", "nawual",
    "vanguard", "vanguardia",
    "activar escudo",
]

# Palabras que suenan parecido — fuzzy match con umbral
TRIGGER_FUZZY = [
    "nahual", "nagual", "nawal", "vanguard",
]
FUZZY_THRESHOLD = 0.6  # 60% similitud mínima por palabra

# ── Aplausos ──
CLAP_PEAK_THRESHOLD = 0.15     # Pico mínimo absoluto (bajo para captar aplausos suaves)
CLAP_SPIKE_RATIO = 4.0         # Pico debe ser N veces mayor que el ruido ambiente
CLAP_COUNT_TRIGGER = 2          # Aplausos necesarios
CLAP_WINDOW_SECONDS = 4         # Ventana para contar aplausos
CLAP_COOLDOWN = 0.3             # Segundos mínimos entre aplausos detectados
AMBIENT_HISTORY = 50            # Bloques de audio para calcular ruido ambiente

POPUP_DELAY = 1.8


def asset_path(relative):
    """Resolver ruta de assets — funciona como .py y como .exe (PyInstaller)."""
    if getattr(sys, 'frozen', False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent
    return base / relative


MUSIC_FILE = asset_path("assets/adventure.mp3")
VIDEO_FILE = asset_path("assets/nahual-demo.mp4")
PDF_FILE = asset_path("assets/NAH-2026-0042.pdf")


# ══════════════════════════════════════════
# FUZZY MATCHING FONÉTICO
# ══════════════════════════════════════════

def normalize_text(text):
    """Normalizar texto para comparación."""
    import unicodedata
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in text if not unicodedata.combining(c))
    return text.lower().strip()


def fuzzy_word_match(text, triggers, threshold):
    """Buscar si alguna palabra del texto se parece a un trigger."""
    text = normalize_text(text)
    words = text.split()

    # Comparar cada palabra individual
    for word in words:
        for trigger in triggers:
            ratio = SequenceMatcher(None, word, trigger).ratio()
            if ratio >= threshold:
                return trigger, word, ratio

    # Comparar bigramas (dos palabras juntas) — "na hual" → "nahual"
    for i in range(len(words) - 1):
        bigram = words[i] + words[i + 1]
        for trigger in triggers:
            ratio = SequenceMatcher(None, bigram, trigger).ratio()
            if ratio >= threshold:
                return trigger, bigram, ratio

    return None


def check_voice_trigger(text):
    """Verificar si el texto contiene un trigger por voz."""
    text_norm = normalize_text(text)

    # 1. Match exacto (substring)
    for trigger in TRIGGER_EXACT:
        if trigger in text_norm:
            return f"exacto: '{trigger}'"

    # 2. Fuzzy match por palabra
    result = fuzzy_word_match(text, TRIGGER_FUZZY, FUZZY_THRESHOLD)
    if result:
        trigger, matched, ratio = result
        return f"fuzzy: '{matched}' ≈ '{trigger}' ({ratio:.0%})"

    return None


# ══════════════════════════════════════════
# DETECCIÓN DE AUDIO
# ══════════════════════════════════════════

class AudioListener:
    """Escucha el micrófono con detección avanzada de voz y aplausos."""

    def __init__(self, on_trigger):
        self.on_trigger = on_trigger
        self.triggered = False
        self.sample_rate = 16000
        self.chunk_duration = 2  # chunks más cortos = respuesta más rápida
        self.recording = False
        self.audio_buffer = []
        self.buffer_lock = threading.Lock()

        # Estado de detección de aplausos
        self.clap_times = []
        self.last_clap_time = 0
        self.ambient_levels = []  # historial de niveles de ruido ambiente

    def start(self):
        import sounddevice as sd

        print("\n🎙️  Micrófono activo. Esperando trigger...")
        print(f"   🗣️  Di 'Nahual' o 'Vanguard' o 'Activar escudo'")
        print(f"   👏 Aplaude {CLAP_COUNT_TRIGGER} veces (detecta aplausos suaves)")
        print(f"   ⌨️  ENTER = trigger manual\n")

        # Thread para input manual
        threading.Thread(target=self._manual_trigger, daemon=True).start()

        # Calibrar ruido ambiente
        print("   📊 Calibrando ruido ambiente (2 seg)...")
        self._calibrate(sd)
        print("   📊 Calibración OK — escuchando...\n")

        # Stream de audio
        self.recording = True
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32',
            blocksize=int(self.sample_rate * 0.05),  # 50ms blocks (más resolución)
            callback=self._audio_callback
        ):
            while self.recording and not self.triggered:
                time.sleep(self.chunk_duration)
                if not self.triggered:
                    self._process_whisper()

    def _calibrate(self, sd):
        """Grabar 2 segundos de silencio para calibrar el nivel de ruido ambiente."""
        calibration = []
        duration = 2.0

        def cb(indata, frames, time_info, status):
            peak = max(abs(x) for x in indata[:, 0])
            calibration.append(peak)

        with sd.InputStream(
            samplerate=self.sample_rate, channels=1, dtype='float32',
            blocksize=int(self.sample_rate * 0.05), callback=cb
        ):
            time.sleep(duration)

        if calibration:
            # Usar el percentil 90 como baseline de ruido ambiente
            calibration.sort()
            idx = int(len(calibration) * 0.9)
            baseline = calibration[idx] if idx < len(calibration) else calibration[-1]
            self.ambient_levels = [baseline] * AMBIENT_HISTORY
            print(f"   📊 Ruido ambiente: {baseline:.4f} (peak p90)")

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback por cada bloque de 50ms."""
        if self.triggered:
            return

        samples = indata[:, 0]

        # Almacenar para Whisper
        with self.buffer_lock:
            self.audio_buffer.extend(samples.tolist())

        # ── Detección de aplausos por transientes ──
        peak = max(abs(x) for x in samples)

        # Actualizar nivel ambiente (media móvil, excluyendo picos)
        ambient = sum(self.ambient_levels) / len(self.ambient_levels) if self.ambient_levels else 0.01

        # Un pico que NO es aplauso contribuye al ruido ambiente
        if peak < ambient * 2:
            self.ambient_levels.append(peak)
            if len(self.ambient_levels) > AMBIENT_HISTORY:
                self.ambient_levels.pop(0)

        # Detectar aplauso: pico súbito sobre el ruido ambiente
        # Condiciones: pico absoluto suficiente AND pico relativo al ambiente
        spike_ratio = peak / max(ambient, 0.001)

        if peak > CLAP_PEAK_THRESHOLD and spike_ratio > CLAP_SPIKE_RATIO:
            now = time.time()

            # Cooldown para no contar el mismo aplauso dos veces
            if now - self.last_clap_time > CLAP_COOLDOWN:
                self.last_clap_time = now
                self.clap_times.append(now)
                # Limpiar aplausos viejos
                self.clap_times = [t for t in self.clap_times if now - t < CLAP_WINDOW_SECONDS]

                n = len(self.clap_times)
                print(f"   👏 Aplauso {n}/{CLAP_COUNT_TRIGGER} (peak={peak:.3f}, x{spike_ratio:.1f} sobre ambiente)")

                if n >= CLAP_COUNT_TRIGGER:
                    self._fire_trigger("clap")

    def _process_whisper(self):
        """Enviar audio a Groq Whisper con prompt bias."""
        with self.buffer_lock:
            if not self.audio_buffer or self.triggered:
                return
            # Tomar los últimos N segundos
            n_samples = self.sample_rate * self.chunk_duration
            audio_data = self.audio_buffer[-n_samples:]
            self.audio_buffer = []

        # Verificar que hay suficiente energía para transcribir (no enviar silencio)
        rms = math.sqrt(sum(x**2 for x in audio_data) / len(audio_data))
        if rms < 0.005:
            return  # Silencio, no gastar API call

        try:
            from groq import Groq

            # Crear WAV temporal
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name
                with wave.open(tmp_path, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(self.sample_rate)
                    int_data = [int(max(-1, min(1, s)) * 32767) for s in audio_data]
                    wf.writeframes(struct.pack(f'{len(int_data)}h', *int_data))

            # Transcribir con Groq Whisper + prompt bias
            client = Groq(api_key=GROQ_API_KEY)
            with open(tmp_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=("audio.wav", audio_file),
                    model="whisper-large-v3",
                    language="es",
                    prompt=WHISPER_PROMPT,  # ← CLAVE: bias hacia "Nahual"
                    response_format="text"
                )

            text = str(transcription).strip() if transcription else ""
            os.unlink(tmp_path)

            if not text or len(text) < 2:
                return

            print(f"   🎧 Escuché: \"{text}\"")

            # Verificar trigger
            match = check_voice_trigger(text)
            if match:
                print(f"   🎯 MATCH → {match}")
                self._fire_trigger("voice")

        except Exception as e:
            err = str(e).lower()
            if "rate" not in err and "too short" not in err:
                print(f"   ⚠️  Whisper: {e}")

    def _manual_trigger(self):
        input()
        if not self.triggered:
            print("⌨️  Trigger manual!")
            self._fire_trigger("manual")

    def _fire_trigger(self, source):
        if self.triggered:
            return
        self.triggered = True
        self.recording = False
        print(f"\n🚀 ACTIVADO por: {source}")
        self.on_trigger()


# ══════════════════════════════════════════
# SECUENCIA DE PRESENTACIÓN
# ══════════════════════════════════════════

def play_music(filepath):
    filepath = str(filepath)
    if not os.path.exists(filepath):
        print(f"   ⚠️  Música no encontrada: {filepath}")
        return
    try:
        if sys.platform == 'win32':
            os.startfile(filepath)
        elif sys.platform == 'darwin':
            subprocess.Popen(['afplay', filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(['xdg-open', filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("   🎵 Música reproduciendo")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")


def play_video(filepath):
    filepath = str(filepath)
    if not os.path.exists(filepath):
        print(f"   ⚠️  Video no encontrado: {filepath}")
        return
    try:
        if sys.platform == 'win32':
            vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
            if os.path.exists(vlc_path):
                subprocess.Popen([vlc_path, '--fullscreen', '--play-and-exit', filepath])
            else:
                os.startfile(filepath)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', '-a', 'QuickTime Player', filepath])
        else:
            subprocess.Popen(['xdg-open', filepath], stdout=subprocess.DEVNULL)
        print("   🎬 Video reproduciendo")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")


def open_pdf(filepath):
    filepath = str(filepath)
    if not os.path.exists(filepath):
        print(f"   ⚠️  PDF no encontrado: {filepath}")
        return
    try:
        if sys.platform == 'win32':
            os.startfile(filepath)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', filepath])
        else:
            subprocess.Popen(['xdg-open', filepath])
        print("   📄 PDF abierto")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")


def run_sequence():
    print("\n" + "="*60)
    print("  🛡️  N A H U A L — SECUENCIA ACTIVADA")
    print("="*60)

    print("\n[1/6] 🎵 Música...")
    play_music(MUSIC_FILE)
    time.sleep(1.5)

    print("[2/6] 💬 WhatsApp Web...")
    webbrowser.open("https://web.whatsapp.com")
    time.sleep(POPUP_DELAY)

    print("[3/6] 🌐 nahualsec.com...")
    webbrowser.open("https://nahualsec.com")
    time.sleep(POPUP_DELAY)

    print("[4/6] 📊 Panel de alertas...")
    webbrowser.open("http://159.223.187.6")
    time.sleep(POPUP_DELAY)

    print("[5/6] 📄 Reporte PDF...")
    open_pdf(PDF_FILE)
    time.sleep(POPUP_DELAY)

    print("[6/6] 🎬 Video demostrativo...")
    time.sleep(1)
    play_video(VIDEO_FILE)

    print("\n" + "="*60)
    print("  ✅ SECUENCIA COMPLETA — Pitch en curso")
    print("  Presiona Ctrl+C para terminar")
    print("="*60 + "\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛡️ Pitch finalizado. GG.")


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════

def main():
    print("""
    ╔══════════════════════════════════════════════╗
    ║  🛡️  NAHUAL — PITCH LAUNCHER  v2             ║
    ║  Tony Stark Mode                             ║
    ╠══════════════════════════════════════════════╣
    ║                                              ║
    ║  🗣️  Di "Nahual" o "Vanguard"                ║
    ║  👏 Aplaude 2 veces (detecta suaves)         ║
    ║  ⌨️  ENTER = activación manual               ║
    ║                                              ║
    ╚══════════════════════════════════════════════╝
    """)

    print("Verificando assets...")
    for label, f in [("Música", MUSIC_FILE), ("Video", VIDEO_FILE), ("PDF", PDF_FILE)]:
        status = "✅" if f.exists() else "❌ NO ENCONTRADO"
        print(f"  {status} {label}: {f.name}")

    print(f"  {'✅' if GROQ_API_KEY else '⚠️'} GROQ_API_KEY: {'OK' if GROQ_API_KEY else 'falta'}")
    print()

    listener = AudioListener(on_trigger=run_sequence)
    listener.start()


if __name__ == "__main__":
    main()
