import numpy as np
x = np.array([1+2j, 3+4j])
power_abs = np.sum(np.abs(x)**2)
power_vdot = np.vdot(x, x).real
print("Abs:", power_abs)
print("Vdot:", power_vdot)
