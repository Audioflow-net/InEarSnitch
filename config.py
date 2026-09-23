import os
import sys
import hashlib

VALID_CODE_HASHES = {
    "1995c01c1482b26dbea98699406a4138f23aebb126ff31b958d0faa03bf9df32",
    "68898a24be989f529afd169de801aee884717b01d9990c7ff7fa48c2d5ba1a28",
    "3e8b8d0dbbaf0fa3f578f6bec2979e3c1613f27f3e6577e2ca4b881b692ba3da",
    "012d86cae9aa24b7ef53dd6c39f6894da7238a6d4cfbf48d66ed7238eb84ff23",
    "4499427615757838e5ec8a5b1d8eb6b1d6f35d8faf4df19dafa89a2f46fb4c0b",
    "e8d7d7d99c6aa40bd8523a7fd6389408f7e8894c99d5d663601c398d0e9e35cf",
    "7228aca2309c956565cc8a1cc427daec95ad898948f5900d437ec762ffb44bfc",
    "8906afd6fe4aa0ebcb879dadcad71e9fe6d505f8d7e00cabdfc6603141302a25",
    "58d7a69c67da60189db57e5db3da6771fc184a0db58928cbdfb368637e460aa3",
    "25607ffce3528e61d9401256edc119fb7f4c425a640dfe4ebf47270c183e5822",
    "7423742fc0028928b353b3df599fcb134d9c8357f40b56b2cc47c472bb8686e1",
    "2a83b68c161931e7f7ab88c59cb166571a5fb948e48dd1e0d78a8d066b2de1d2",
    "f86a7c35ab8a3c2d89eb2f2565c131c47a42e44cb43eea52e7f2360d2c3aa795",
    "4ff168c046ad031e449d40fe7ae5b924cee59b18d25e11ba720058325c455661",
    "f2344b4ee49daf42626d1b606eb472bd112e4ae066036feb9535b6fd6d679ec1",
    "c4ff65d6c06d64f68013e6fdf9898e14e5e352ba65361c5adc29606ca7de5b62",
    "e53792d2243f43d8cc54d4c490e659ecf369116ff048a59172ad1d4d61b0ac86",
    "adf5c163d12fb250799c7c174761e31de97abe07c1ed094ab01cf8dfb807dddd",
    "bf849e995cd6de367df77f4261d35ced569b6ed40333ce7473c743ac3dc7947b",
    "eef9d5f834db464d25c8b497770b04dcf0f189667cc02b500309127e34b663b5",
    "f6b7a024afb0de1a07a8c2586cc190b7bb22518bbf76328c0997e5e94e6805a8",
    "8ccd894f34adc447266cf243c0d86410c13c966ec839b0a0777a9d2c98b8519b",
    "ccff392c6f742656823f27a4a7620acb4859342086b462f178a388723706774c",
    "025580c41839db9d87a8e508ade7fe8aa71e3aa8e1b7cbb44a0a1c825fab2b34",
    "afa6fa176e004a45ff0d3f4935606267337127bacaae215bf63d374414ca8b90",
    "4302099ea89cdd11a1c8e9e38a566378c863b3694c32c08873db3d8593025d23",
    "cf13a4a3259f3be159e410ee017c35f70a1a95cf328532f7c28bc25f5df508e0",
    "762073811eb0c34e0da33601f0c2ae3c174df2652ca7cda432ad27fb9f143658",
    "da34dd34ef71181b4a28f66cfaf06663e3f261659cb13a2965b8e2e3f38b3bed",
    "8957165554fdf8aab152dc8ea8a0d93e0aa935515ae9c9df76c18cd5dbd944c3",
    "2f214fe23e9b9faca81b0afcc9816d898ef8290b461e242bd5eb19380b5d41da",
    "a39e497c9504b1631ee30ee81af37619a8a457f3a6915d751450272c867852d3",
    "ef17381e38013a2689b0204971efa80508d40962571ca1a15f692957f3e66f8e",
    "21c953c0c10e789ce5eb2d9013be3eb78009bc7fe8653fcbc61ae4af3fecb67a",
    "6a0999d999564f4b4e2320262c60cbdd001bbd783ceb8aaf3ef4ba3a36927873",
    "321047073779b68964f72615d6802bab7f19157e078a4d44debcd7114964d3ac",
    "42d7f418c876767d7cadafd3de2a6844aefca30b045cc6b9c7764d08ef383453",
    "3def97fa1b47332748f6fe96402ffb89e71727d139520ca848789dee0a16e453",
    "cd9b9a4407da1cc8ae48ce7db24aac5cf5918112f77642f4c4bf70494a420e6b",
    "2113081134cc6f6399a2f1e86a41029379af468ef5629f662ac55d80beafd706",
    "fa1c68b43a17f782bf4fd5d3cbba95f031d1064717768407bb699b33d3cf8634",
    "c1303db819a29119d5278aa62868bf5bda8f728c4d5e1764fea59970084e199b",
    "1f1f00668657346d826ede79dcb19fd8536a18297a244fcd2d7676f30aba1a7b",
    "432cfbb0c5cb4ade835ea1eb321647a42ca2a1ee330eb3290047e6e9cea998dc",
    "b4ddc7007e0d2efe1ffb04ffca00a91997160cbb2e11e7e05080b691bb7172dd",
    "1d66ad4bda785c7da0ebff8c31c42fc62c91c7fa49185852f9ef6508f3b97219",
    "d472891c9639e28d23501ecf2302880171c615315bf0cd13a6a87da81f6bec38",
    "d62228630e2ca451566854730e745e86771665447cae2c6a0c1136d483dd18e2",
    "55ecc157b7a6209871e33e98bfcee0899add7027d3029496ea9d6cf62ba87e5f",
    "d6bde77f4dd5f4612757a4e2a4188536429f783f678cb0ad1c999cc0c31c96f5",
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

