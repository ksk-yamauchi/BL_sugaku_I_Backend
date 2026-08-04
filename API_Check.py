import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
raw = os.environ.get('GEMINI_API_KEYS', '') or os.environ.get('GEMINI_API_KEY', '')
keys = [k.strip().strip('\'\"') for k in raw.split(',') if k.strip()]

print(f'🔍 検出されたキー数: {len(keys)} 件')
for idx, k in enumerate(keys, 1):
    try:
        client = genai.Client(api_key=k)
        res = client.models.generate_content(model='gemini-3.6-flash', contents='Hi')
        print(f'  ✅ Key [{idx}]: 正常動作 ({k[:8]}...)')
    except Exception as e:
        print(f'  ❌ Key [{idx}]: 無効なキー ({k[:8]}...) -> {e}')