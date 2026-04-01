#!/usr/bin/env python3
"""
未返信メール 返信不要ボタン UI サーバー
Usage: python server.py
"""
import json
import http.server
import sys
import webbrowser

STATE_FILE = r"C:\Users\yinagaki\.claude\skills\unreplied-emails\state.json"
PORT = 8766


def read_state():
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def generate_html(emails):
    cards = ""
    for email in emails:
        body_html = esc(email.get('body', '')).replace('\n', '<br>')
        received = email.get('received_at', '')[:10]
        thread_id = email.get('thread_id', '')
        # message_idがあればそのメッセージを直接開く、なければスレッドを開く
        gmail_id = email.get('message_id') or thread_id
        no = email['no']
        cards += f"""
        <div class="email-card" id="card-{no}">
            <div class="email-header">
                <button class="no-btn" onclick="openGmail('{esc(gmail_id)}')">No.{no} ↗</button>
                <button class="delete-btn" onclick="deleteEmail({no})">✕ 返信不要</button>
            </div>
            <div class="email-field"><strong>送信者</strong>{esc(email.get('sender', ''))}</div>
            <div class="email-field"><strong>件名</strong>{esc(email.get('subject', ''))}</div>
            <div class="email-field"><strong>受信日</strong>{received}</div>
            <div class="email-body">{body_html}</div>
        </div>
        """

    if not emails:
        cards = '<p class="no-emails">✓ 未返信メールはありません</p>'

    count = len(emails)
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>未返信メール</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic", sans-serif;
    background: #f0f2f5;
    padding: 32px 20px;
  }}
  .container {{ max-width: 800px; margin: 0 auto; }}
  h1 {{
    font-size: 1.3em;
    color: #1a1a2e;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .count-badge {{
    background: #e74c3c;
    color: white;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.78em;
    font-weight: 700;
  }}
  .email-card {{
    background: white;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    transition: opacity 0.4s, transform 0.4s;
  }}
  .email-card.removing {{
    opacity: 0;
    transform: translateX(40px);
  }}
  .email-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f0f0f0;
  }}
  .no-btn {{
    font-size: 1em;
    font-weight: 700;
    color: #3498db;
    background: #eaf4fd;
    padding: 4px 10px;
    border-radius: 6px;
    border: none;
    cursor: pointer;
    transition: background 0.2s;
  }}
  .no-btn:hover {{ background: #c5e3f7; }}
  .delete-btn {{
    background: #e74c3c;
    color: white;
    border: none;
    padding: 7px 14px;
    border-radius: 7px;
    cursor: pointer;
    font-size: 0.85em;
    font-weight: 600;
    transition: background 0.2s, transform 0.1s;
  }}
  .delete-btn:hover {{ background: #c0392b; transform: scale(1.03); }}
  .delete-btn:active {{ transform: scale(0.97); }}
  .email-field {{
    margin: 4px 0;
    color: #444;
    font-size: 0.9em;
    line-height: 1.5;
    display: flex;
    gap: 8px;
  }}
  .email-field strong {{
    color: #aaa;
    font-weight: 600;
    min-width: 46px;
    flex-shrink: 0;
  }}
  .email-body {{
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #f5f5f5;
    color: #555;
    font-size: 0.87em;
    line-height: 1.8;
  }}
  .no-emails {{
    text-align: center;
    color: #27ae60;
    padding: 60px;
    font-size: 1.05em;
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  }}
  .toast {{
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: #2c3e50;
    color: white;
    padding: 11px 18px;
    border-radius: 8px;
    font-size: 0.88em;
    opacity: 0;
    transition: opacity 0.3s;
    pointer-events: none;
    z-index: 9999;
  }}
  .toast.show {{ opacity: 1; }}
</style>
</head>
<body>
<div class="container">
  <h1>📬 未返信メール <span class="count-badge" id="count-badge">{count}件</span></h1>
  <div id="email-list">
{cards}
  </div>
</div>
<div class="toast" id="toast"></div>
<script>
function showToast(msg) {{
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2000);
}}

async function openGmail(threadId) {{
  await fetch('/open-gmail', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{thread_id: threadId}})
  }});
  showToast('Gmailを開きました');
}}

async function deleteEmail(no) {{
  const card = document.getElementById('card-' + no);
  card.classList.add('removing');
  try {{
    const resp = await fetch('/delete', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{no: no}})
    }});
    if (resp.ok) {{
      setTimeout(() => {{
        card.remove();
        const remaining = document.querySelectorAll('.email-card').length;
        document.getElementById('count-badge').textContent = remaining + '件';
        if (remaining === 0) {{
          document.getElementById('email-list').innerHTML = '<p class="no-emails">✓ 未返信メールはありません</p>';
        }}
        showToast('No.' + no + ' を削除しました');
      }}, 400);
    }}
  }} catch(e) {{
    card.classList.remove('removing');
  }}
}}
</script>
</body>
</html>"""


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        state = read_state()
        html = generate_html(state.get('unreplied_emails', []))
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length))

        if self.path == '/open-gmail':
            thread_id = body.get('thread_id', '')
            gmail_url = f"https://mail.google.com/mail/u/0/#inbox/{thread_id}"
            webbrowser.open(gmail_url)
            self._json_ok()

        elif self.path == '/delete':
            no = body.get('no')
            state = read_state()
            state['unreplied_emails'] = [e for e in state['unreplied_emails'] if e['no'] != no]
            write_state(state)
            self._json_ok()

    def _json_ok(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(b'{"ok": true}')

    def log_message(self, format, *args):
        pass


if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"http://localhost:{PORT} で起動しました", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
