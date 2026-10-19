# ==============================================================================
# STARVIOS OBS VOICE ASSISTANT v1.0
# Creado y Desarrollado por: CORNEJOXx
# Todos los derechos reservados (c) 2026 CORNEJOXx
#
# AVISO DE DERECHOS DE AUTOR Y LICENCIA DE USO:
# Este software y su código fuente han sido desarrollados por CORNEJOXx.
# Queda prohibida su distribución, copia o difusión pública o privada sin
# mantener de forma íntegra y visible el crédito de autoría a CORNEJOXx.
# ==============================================================================

AUTHOR = "CORNEJOXx"
APP_NAME = "Starvios OBS Voice Assistant"
COPYRIGHT = "© 2026 CORNEJOXx. Todos los derechos reservados."

import os
import sys

# Force UTF-8 encoding on Windows console
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


import json
import time
import queue
import ctypes
import asyncio
import tempfile
import edge_tts

import urllib.request
import urllib.error
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import pythoncom
import win32com.client

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "public")

default_config = {
    "token": "",
    "tts_enabled": True,
    "read_username": True,
    "filter_commands": True,
    "rate": 1,
    "volume": 100,
    "voice_name": "es-MX-DaliaNeural",
    "read_donations_first": True,
    "poll_interval": 1.5
}

def clean_token(value):
    """Accepts a bare token or a full overlay URL and returns only the token."""
    value = str(value or "").strip().split("?")[0].rstrip("/")
    return value.split("/")[-1].strip()

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                merged = {**default_config, **cfg}
                merged["token"] = clean_token(merged.get("token"))
                return merged
        except Exception as e:
            print(f"[!] Error leyendo config.json: {e}")
    return default_config.copy()

def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Error guardando config.json: {e}")

config = load_config()
config_lock = threading.Lock()

# State
state = {
    "connected": False,
    "is_live": False,
    "is_speaking": False,
    "current_speech": "",
    "messages": [],
    "voices": []
}
state_lock = threading.Lock()

speech_queue = queue.Queue()
sse_clients = []
sse_lock = threading.Lock()

def broadcast_event(event_type, data):
    payload = f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n".encode("utf-8")
    with sse_lock:
        to_remove = []
        for client in sse_clients:
            try:
                client.write(payload)
                client.flush()
            except Exception:
                to_remove.append(client)
        for client in to_remove:
            if client in sse_clients:
                sse_clients.remove(client)

# Neural voices (Microsoft Edge TTS)
NEURAL_VOICES = [
    {"id": "es-MX-DaliaNeural", "name": "Dalia - Mexico (mujer, natural)"},
    {"id": "es-MX-JorgeNeural", "name": "Jorge - Mexico (hombre)"},
    {"id": "es-ES-ElviraNeural", "name": "Elvira - Espana (mujer)"},
    {"id": "es-AR-ElenaNeural", "name": "Elena - Argentina (mujer)"},
    {"id": "es-CO-SalomeNeural", "name": "Salome - Colombia (mujer)"},
    {"id": "es-US-PalomaNeural", "name": "Paloma - EE.UU. (mujer)"},
]

winmm = ctypes.windll.winmm

def mci(cmd):
    buf = ctypes.create_unicode_buffer(255)
    winmm.mciSendStringW(cmd, buf, 254, 0)
    return buf.value

def play_mp3(path, volume):
    mci("close tts")
    mci(f'open "{path}" type mpegvideo alias tts')
    mci(f"setaudio tts volume to {max(0, min(100, volume)) * 10}")
    mci("play tts wait")
    mci("close tts")

async def _synth(text, voice, rate_pct, path):
    comm = edge_tts.Communicate(text, voice, rate=f"{rate_pct:+d}%")
    await comm.save(path)

def speak_neural(text, voice, rate, volume):
    path = os.path.join(tempfile.gettempdir(), "starvios_tts.mp3")
    asyncio.run(_synth(text, voice, rate * 10, path))
    play_mp3(path, volume)

# TTS Engine Worker
def tts_worker():
    pythoncom.CoInitialize()
    speaker = None  # SAPI fallback (offline), created lazily

    with state_lock:
        state["voices"] = NEURAL_VOICES

    print(f"[TTS] Voces neuronales listas ({len(NEURAL_VOICES)} disponibles).")

    while True:
        try:
            item = speech_queue.get()
            if item is None:
                break
            
            text, message_obj = item
            
            with config_lock:
                if not config.get("tts_enabled", True):
                    speech_queue.task_done()
                    continue
                rate = int(config.get("rate", 1))
                volume = int(config.get("volume", 100))
                voice_name = config.get("voice_name", "Sabina")

            if "Neural" not in voice_name:
                voice_name = "es-MX-DaliaNeural"

            # Notify UI speech started
            with state_lock:
                state["is_speaking"] = True
                state["current_speech"] = text
            broadcast_event("speech_start", {"text": text, "message": message_obj})

            # Speak synchronously in this worker thread
            try:
                speak_neural(text, voice_name, rate, volume)
            except Exception as e:
                print(f"[TTS] Voz neuronal fallo ({e}), usando voz de Windows")
                try:
                    if speaker is None:
                        speaker = win32com.client.Dispatch("SAPI.SpVoice")
                    speaker.Rate = max(-10, min(10, rate))
                    speaker.Volume = max(0, min(100, volume))
                    speaker.Speak(text, 0)
                except Exception as e2:
                    print(f"[TTS] Error al hablar: {e2}")

            # Notify UI speech finished
            with state_lock:
                state["is_speaking"] = False
                state["current_speech"] = ""
            broadcast_event("speech_end", {"text": text})

            time.sleep(0.15)
            speech_queue.task_done()
        except Exception as e:
            print(f"[TTS Worker] Error: {e}")
            time.sleep(0.5)

    pythoncom.CoUninitialize()

def safe_print(msg):
    try:
        print(msg)
    except Exception:
        try:
            print(str(msg).encode("ascii", "replace").decode("ascii"))
        except Exception:
            pass

# Starvios Chat Polling Worker
def starvios_poller():
    seen_ids = set()
    first_run = True

    safe_print("[Starvios] Iniciando escucha de chat en segundo plano...")

    while True:
        with config_lock:
            token = config.get("token", "").strip()
            poll_interval = float(config.get("poll_interval", 1.0))
            read_user = config.get("read_username", True)
            filter_cmd = config.get("filter_commands", True)
            tts_on = config.get("tts_enabled", True)

        if not token:
            with state_lock:
                state["connected"] = False
            time.sleep(2)
            continue

        url = f"https://starvios.com/api/public/obs-chat?token={token}&v=2"
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/json",
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache"
                }
            )
            # Starvios uses long-polling (~5.5 - 6.5s response time), so timeout must be generous (25s)
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                
                was_connected = state.get("connected", False)
                with state_lock:
                    state["connected"] = True
                    state["is_live"] = data.get("live", False)

                if not was_connected:
                    broadcast_event("status_update", {"connected": True, "is_live": state["is_live"]})

                raw_messages = data.get("messages", [])
                
                # If first run, load current messages into state so dashboard has history,
                # but don't read them all with TTS to avoid audio spam at startup
                if first_run:
                    initial_records = []
                    for m in raw_messages:
                        mid = m.get("id")
                        if mid:
                            seen_ids.add(mid)
                        name = m.get("name", "Anónimo")
                        body = m.get("body", "").strip()
                        coins = int(m.get("coins", 0) or 0)
                        msg_record = {
                            "id": mid,
                            "name": name,
                            "body": body,
                            "coins": coins,
                            "badges": m.get("badges", []),
                            "color": m.get("color", "#5CFF67"),
                            "time": time.strftime("%H:%M:%S")
                        }
                        initial_records.append(msg_record)
                    
                    with state_lock:
                        state["messages"] = initial_records[-100:]
                    first_run = False
                    safe_print(f"[Starvios] Conectado exitosamente. {len(initial_records)} mensajes cargados.")
                    broadcast_event("init_messages", state["messages"])
                else:
                    new_msgs = []
                    for m in raw_messages:
                        mid = m.get("id")
                        if mid and mid not in seen_ids:
                            seen_ids.add(mid)
                            new_msgs.append(m)

                    for m in new_msgs:
                        name = m.get("name", "Anónimo")
                        body = m.get("body", "").strip()
                        coins = int(m.get("coins", 0) or 0)
                        
                        # Add to state messages
                        msg_record = {
                            "id": m.get("id"),
                            "name": name,
                            "body": body,
                            "coins": coins,
                            "badges": m.get("badges", []),
                            "color": m.get("color", "#5CFF67"),
                            "time": time.strftime("%H:%M:%S")
                        }
                        with state_lock:
                            state["messages"].append(msg_record)
                            if len(state["messages"]) > 100:
                                state["messages"] = state["messages"][-100:]

                        safe_print(f"[Chat] {name}: {body}")
                        broadcast_event("new_message", msg_record)

                        # Determine if we should speak it
                        is_command = body.startswith("!") or body.startswith("/") or body.startswith(".")
                        if filter_cmd and is_command:
                            continue

                        # Build speech sentence
                        if coins > 0:
                            speech_text = f"¡{name} envió {coins} Starvies! {body}"
                        elif read_user:
                            speech_text = f"{name} dice: {body}"
                        else:
                            speech_text = body

                        if tts_on and speech_text:
                            speech_queue.put((speech_text, msg_record))

        except Exception as e:
            was_connected = state.get("connected", False)
            with state_lock:
                state["connected"] = False
            if was_connected:
                broadcast_event("status_update", {"connected": False, "is_live": state["is_live"]})

        time.sleep(poll_interval)

# HTTP Request Handler for Dashboard & API
class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Quiet logs

    def do_GET(self):
        parsed_path = self.path.split("?")[0]

        if parsed_path == "/api/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            with sse_lock:
                sse_clients.append(self.wfile)
            
            # Send initial state
            with state_lock:
                snapshot = dict(state)
            with config_lock:
                cfg_snapshot = dict(config)
            
            init_payload = f"event: init\ndata: {json.dumps({'state': snapshot, 'config': cfg_snapshot}, ensure_ascii=False)}\n\n".encode("utf-8")
            try:
                with sse_lock:
                    self.wfile.write(init_payload)
                    self.wfile.flush()
                # Keep thread waiting while connection is active
                while True:
                    time.sleep(15)
                    with sse_lock:
                        if self.wfile not in sse_clients:
                            break
                        self.wfile.write(b": ping\n\n")
                        self.wfile.flush()
            except Exception:
                pass
            finally:
                with sse_lock:
                    if self.wfile in sse_clients:
                        sse_clients.remove(self.wfile)
            return

        elif parsed_path == "/api/status":
            with state_lock:
                snap = dict(state)
            with config_lock:
                cfg = dict(config)
            
            data = {
                "state": snap,
                "config": cfg,
                "author": AUTHOR,
                "app_name": APP_NAME,
                "copyright": COPYRIGHT
            }
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # Serve static files from /public
        file_path = parsed_path.lstrip("/")
        if not file_path or file_path == "":
            file_path = "index.html"
        elif file_path == "overlay":
            file_path = "overlay.html"
        
        target = os.path.normpath(os.path.join(PUBLIC_DIR, file_path))
        if not target.startswith(PUBLIC_DIR) or not os.path.exists(target) or os.path.isdir(target):
            target = os.path.join(PUBLIC_DIR, "index.html")

        content_types = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".svg": "image/svg+xml",
            ".png": "image/png"
        }
        _, ext = os.path.splitext(target)
        c_type = content_types.get(ext, "application/octet-stream")

        try:
            with open(target, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", c_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error reading file: {e}")

    def do_POST(self):
        parsed_path = self.path.split("?")[0]
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        
        try:
            body_json = json.loads(post_body)
        except Exception:
            body_json = {}

        if parsed_path == "/api/settings":
            with config_lock:
                for k, v in body_json.items():
                    if k in default_config:
                        config[k] = clean_token(v) if k == "token" else v
                save_config(config)
            
            broadcast_event("config_updated", config)
            self.send_json_response({"status": "ok", "config": config})
            return

        elif parsed_path == "/api/test-voice":
            text = body_json.get("text", "Hola, soy el asistente de voz de Starvios. El lector de chat está listo para tu stream.")
            speech_queue.put((text, {"name": "Bot Asistente", "body": text, "coins": 0}))
            self.send_json_response({"status": "queued", "text": text})
            return

        elif parsed_path == "/api/clear":
            with state_lock:
                state["messages"] = []
            broadcast_event("cleared", {})
            self.send_json_response({"status": "ok"})
            return

        self.send_error(404, "Endpoint not found")

    def send_json_response(self, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def main():
    port = 7890
    print("=" * 64)
    print("      ⭐ STARVIOS OBS VOICE ASSISTANT v1.0 ⭐")
    print("        Creado y Desarrollado por: CORNEJOXx")
    print("        Todos los derechos reservados (C) 2026")
    token_str = str(config.get('token') or '').strip()
    token_display = token_str if token_str else "(Sin configurar - agrégalo en el panel web)"
    print(" [i] Aviso de Autor: Prohibida su difusion sin acreditar a CORNEJOXx")
    print(f" [*] Token del canal: {token_display}")
    print("=" * 64)

    # Start TTS Thread
    t_tts = threading.Thread(target=tts_worker, daemon=True)
    t_tts.start()

    # Start Poller Thread
    t_poller = threading.Thread(target=starvios_poller, daemon=True)
    t_poller.start()

    # Start Web Dashboard Server
    try:
        server = ThreadingHTTPServer(("127.0.0.1", port), DashboardHandler)
    except OSError:
        print(f"\n[!] El asistente ya está ejecutándose en http://localhost:{port}")
        try:
            import webbrowser
            webbrowser.open(f"http://localhost:{port}")
        except Exception:
            pass
        return

    print(f"\n[OK] Panel de Control en vivo: http://localhost:{port}")
    print(f"[OK] Overlay Local para OBS:        http://localhost:{port}/overlay.html")
    if token_str:
        print(f"[OK] Overlay Oficial Starvios:      https://starvios.com/overlay/chat/{token_str}")
    else:
        print("[i] Overlay Oficial Starvios:      (Configura tu token en el panel web)")
    print("\nPresiona Ctrl+C para salir.\n")

    # Optionally open browser
    try:
        import webbrowser
        webbrowser.open(f"http://localhost:{port}")
    except Exception:
        pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCerrando asistente...")
        server.server_close()
        speech_queue.put(None)
        sys.exit(0)

if __name__ == "__main__":
    main()
