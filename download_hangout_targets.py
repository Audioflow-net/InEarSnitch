import urllib.request, ssl, os

targets = [
    "IEF_Preference_2025",
    "PopAvg-DF (JM-1 Delta)",
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
out_dir = "reference_targets/Pro_Live_IEMs"

for t in targets:
    for suffix in [".txt", "_Target.txt", " Target.txt", ""]:
        safe_name = urllib.parse.quote(t + suffix)
        url = f"https://graph.hangout.audio/iem/711/data/{safe_name}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
            resp = urllib.request.urlopen(req, context=ctx).read().decode('utf-8')
            if "forbidden" not in resp.lower() and "not found" not in resp.lower():
                print(f"Erfolg: {t} ({suffix}) - {resp[:30]}")
                break
        except Exception as e:
            print(f"Failed {url}: {e}")
