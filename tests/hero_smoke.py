"""Exercise the generated film/loop on localhost. Requires Playwright and Chrome."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("directory", type=Path, help="Output of diorama.py encode")
parser.add_argument("--chrome", help="Optional Chrome or Chromium executable")
args = parser.parse_args()
directory = args.directory.resolve(strict=True)
if not (directory / "index.html").is_file():
    parser.error("Missing index.html")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


with ThreadingHTTPServer(
    ("127.0.0.1", 0), partial(QuietHandler, directory=directory)
) as server:
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path=args.chrome)
            page = browser.new_page(reduced_motion="reduce")
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.add_init_script("""
                window.steps = [];
                document.addEventListener('playing', e => {
                    if (e.target.id) window.steps.push(e.target.id);
                }, true);
                let previous = 0;
                window.wraps = 0;
                function observe() {
                    const loop = document.querySelector('#loop');
                    if (loop) {
                        if (loop.currentTime + 0.001 < previous) window.wraps++;
                        previous = loop.currentTime;
                    }
                    requestAnimationFrame(observe);
                }
                requestAnimationFrame(observe);
            """)
            page.goto(f"http://127.0.0.1:{server.server_port}/")
            page.wait_for_function("document.getElementById('intro').paused")
            assert page.locator("#intro").evaluate(
                "v => v.currentSrc === '' && !!v.poster"
            )
            page.get_by_role("button", name="Lire").click()
            page.wait_for_function(
                "window.wraps >= 2 && getComputedStyle(loop).opacity === '1'",
                timeout=150000,
            )
            assert page.evaluate(
                "window.steps[0] === 'intro' && window.steps.includes('loop')"
            )
            page.get_by_role("button", name="Pause").click()
            page.wait_for_function("document.querySelector('#loop').paused")
            print(
                "Lecture et deux tours de boucle vérifiés.",
                page.locator("#loop").evaluate("v => v.currentSrc"),
            )
            page.emulate_media(reduced_motion="no-preference")
            page.reload()
            page.wait_for_function("window.steps.length > 0")
            assert page.evaluate("window.steps[0] === 'intro'")
            assert not errors, errors
            browser.close()
            print("Affiche, pause et redémarrage à l’introduction vérifiés.")
    finally:
        server.shutdown()
