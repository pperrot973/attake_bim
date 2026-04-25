"""Serveur HTTP minimal — bibliothèque standard Python uniquement."""
import http.server
import webbrowser
import threading
import os
import sys

PORT = 8000
HOST = '0.0.0.0'

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Headers CORS pour les appels API depuis le navigateur
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def log_message(self, fmt, *args):
        print(f"  {args[0]}  {args[1]}")


def open_browser():
    import time
    time.sleep(0.8)
    webbrowser.open(f'http://localhost:{PORT}/index.html')


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    threading.Thread(target=open_browser, daemon=True).start()

    print(f"\n  API Bâtiment — Réseau EDF Guyane")
    print(f"  Serveur démarré sur http://localhost:{PORT}")
    print(f"  → Fiche bâtiment : http://localhost:{PORT}/index.html")
    print(f"  → Carte réseau   : http://localhost:{PORT}/carte-reseau.html")
    print(f"\n  Ctrl+C pour arrêter\n")

    try:
        with http.server.HTTPServer((HOST, PORT), Handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Serveur arrêté.")
    except OSError as e:
        print(f"\n  Erreur : port {PORT} déjà utilisé. Fermez l'autre instance et relancez.")
        sys.exit(1)
