import numpy as np
indata = np.ones(1024, dtype=np.float32)
window = np.hanning(1024) # float64
out = np.empty(1024, dtype=np.float32)
try:
    np.multiply(indata, window, out=out)
    print("Multiplication succeeded")
except Exception as e:
    print("Error:", e)
