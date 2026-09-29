import numpy as np
try:
    a = np.ones(2048, dtype=np.float32)
    b = np.hanning(2048) # float64
    c = np.empty(2048, dtype=np.float32)
    np.multiply(a, b, out=c, casting='same_kind')
    print("Same kind cast allowed")
except Exception as e:
    print("Same kind cast ERROR:", e)

try:
    np.multiply(a, b, out=c)
    print("Default cast allowed")
except Exception as e:
    print("Default cast ERROR:", e)
