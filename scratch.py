import sounddevice as sd
try:
    raise sd.CallbackStop
except Exception as e:
    print(f"Caught by Exception: {type(e)}")
