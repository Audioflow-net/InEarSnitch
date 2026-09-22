import os
import sys
import hashlib

VALID_CODE_HASHES = {
    "1828f2d5760d4cf839ca49453181698832d48e80f8c5a790333bd72d3783dbb2",
    "28c967ffdb947142ba96b211ac9b7a82d73e705ae4938b0048357842160ccca5",
    "467080d8304ae74587a8871d277301d6962350cc8d0adbdeacf164992306749e",
    "3340498b45cedd29a0f3e4bd16bc218e6642b2617966ac0bb992a4db2f643577",
    "752ec0de4e8783a1a9b6cea3727a875fce76fdc815c0188b53c42e090b6a6d49",
    "2d4daa3506a61e12f3e6bdcf812d381923313ce48c4c3261fe9eea85b48f8478",
    "fa19fa327ec49524a82509d8ece545cf599d41cbcedd120d94fa2fbe4ae67cf7",
    "2bd13e963d452a752e565da583a8e68055d2a98f106d1dd258a3ad795c177d0b",
    "9adb031d8be54cbf43003cc488add1f8f855e0dff40f6d4d02728107467c9bf7",
    "8329c956d34a3065c16c9fce051d318f48f59e3a168514ec118e784b2afd8aad",
    "bc688e2817772af9de241f6ccc18610c8ef7fb8804c27dd57ac360630dac498a",
    "a66191e82cd3095c357aaf3425269ca732e3f08e5fda033cc60a0af2a9b1cdf5",
    "766545bc887e483e9c41b204fbcf985763398ede9d7f731d6c17926cc094472c",
    "5903d43d01d796973d727dcf4914f654607428045aa0c4dddf44f8bc36ccc143",
    "25510b6e524bc19381508ebadde8a40e142dfd2db4f77b09170b92f87f724d2a",
    "0caec3efc96458f024248206516790cf9fd52aabb29cb4a5c9263d1bdaec0deb",
    "24bd2789b55de96bbf6a312680f6a1e282555eeb200b91b6d97d9290b548590c",
    "7d7f06121b54cdc34163f9c520f1a86d802c992580f515355a89a4e0bad75e42",
    "12fd82d9bfef2250bc8eca14a5578abf7db236a90fe779a495b4da8ad8bade28",
    "c433deca515974a48aa7d353482c57e5726e0f8830a0b5cd8401fc24ecef05bc",
    "f7180a263f1ca78f52bb304194a41d43ca9592591dfd9913f660a62c945b37e7",
    "ee7bd1d3904f1980bb93a778146265675321266cf12b34f213d111aa95b324e1",
    "7ea57abff314366f97a88d26cd1fe211432b463cc1b3bab5086e7c9d38a57584",
    "77f89e8a6ccad0efb0a93af8c55deba0b6bb8143e443c434086b5588a5d4c392",
    "02fdbd04dfa0b206c050030c0fde369c13b63826609b57629bc11eebc1b07953",
    "fb7bc08e304bc9f285deb479e7f2809f7878ed699571864663cd42a585712088",
    "5db52172b22bc0bb2839f3b6152db1ee40330259b061a97af317daef71f74cab",
    "c447ab57a79b5a0585c7fdea5bf960e6cad82504fc7d3779974c0ef6eff97cb8",
    "4f542e2e655cd4c549086585f1b35e4791a642dc48928b6678dbc61545daa06c",
    "9c5a61b5d71129cd60ad54432cf05bb51e197bcab379dfe3580298da4ac8405d",
    "b078f28b7df0f1309b46ff7f60f07dbf556de84e2f94d401f4cb76e735250ce1",
    "fe2fbfabd552d26935d42bab0363afea0fcf836e37cd5bf443fac45dcec2b301",
    "7ecb10814cce4353c5755321e58eaee1c7903517ec47ee1b7e885c74cbbb1eeb",
    "574ad449c2b3d44a819541c04f949b7da88726c88cdea706f3861c28c26eed75",
    "137648325202aa6877ef61d5a3676be21f6984d76825c228cd54cbeccbd1515a",
    "ee2cdd6fdac8c38e2407464045ae904bd3226744535961dfb62769f3644e5f2c",
    "144fb12c8c3153380ded932b955b1faf0eb630a0f92a5c9ad2b856ae128b7285",
    "b75abc7d948c7988501b6956ec5c73b2f3a7ba4331ff4625324056a12e8f827c",
    "f158ff3e0ffbb5cb70ec6ff3b5a9eeaf1c313aee6d74a0ad3c901db5becd96e0",
    "ff443743ef2e6039023ae4dc835a86a580287565c2d49f02734024cc9afee42b",
    "ad0e8d419b1647e5966034565f2494b646e4f1a36e1cbb807e9621ccf4249c7e",
    "4ed91365b766ec8fcd7a5cb4b34455255be226619a331b43062a78f704cb844b",
    "dbbb84b2101da22a25153e7fc97ceaa08592b28cfd32803c9068f85893633172",
    "07a30ae449aaec190e5307da93ddb1dc6d1c6c649e7f677e4f6be995f5a98a44",
    "8ca06be4b4c080a7343aafb358406adafe205581f7e4fd80680c78ef513ccba8",
    "3f43ab77a551d55e2d852c581d77fd1c6601ea961e747ced419027506a96d656",
    "49aff215aa8ed742bec2ebb5bdd7fe8d0b2ed4457e86f0be0c2c77209a3efe31",
    "f02975c34add7e5b646fda9731643b7af58216660cebf4d1e649f13d4f471e7b",
    "4d58450d5e89ab7d28ccd55a62d026034c8f1e10efa2b89347e1d2bd76237faa",
    "beb4fa70979bc164202352ec89574193cbdba08a5f2c6c5ff74088acd7600e7a",
}

def get_data_dir():
    """Get a safe, writable directory for application data."""
    home = os.path.expanduser("~")
    app_dir = os.path.join(home, "Documents", "InEarSnitch")
    if not os.path.exists(app_dir):
        try:
            os.makedirs(app_dir)
        except Exception:
            pass
    return app_dir

def get_db_path():
    """Get the absolute path to the SQLite database."""
    # If running from source (not frozen), we can just use the local directory
    # but to be safe and consistent, we'll use Documents/InEar Snitch/inearsnitch.db for frozen apps
    if getattr(sys, 'frozen', False):
        return os.path.join(get_data_dir(), "inearsnitch.db")
    else:
        # Development mode: use local db
        return "inearsnitch.db"

def is_prokit_unlocked() -> bool:
    """Return True if ProKit features are unlocked offline, False otherwise."""
    try:
        token_path = os.path.join(get_data_dir(), ".prokit_unlocked")
        return os.path.exists(token_path)
    except OSError:
        return False

def unlock_prokit(code: str) -> bool:
    """
    Attempt to unlock ProKit features with an offline code.
    Normalizes code by stripping whitespace and converting to uppercase.
    Writes hash to token file on success.
    Returns True if valid, False otherwise.
    """
    if not isinstance(code, str):
        return False
    normalized = code.strip().upper()
    if not normalized:
        return False
    code_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    if code_hash in VALID_CODE_HASHES:
        try:
            token_path = os.path.join(get_data_dir(), ".prokit_unlocked")
            with open(token_path, "w", encoding="utf-8") as f:
                f.write(code_hash + "\n")
            return True
        except OSError:
            return False
    return False

def revoke_prokit() -> bool:
    """
    Revoke ProKit features by removing the token file.
    Returns True on success or if already revoked.
    """
    try:
        token_path = os.path.join(get_data_dir(), ".prokit_unlocked")
        if os.path.exists(token_path):
            os.remove(token_path)
        return True
    except OSError:
        return False

