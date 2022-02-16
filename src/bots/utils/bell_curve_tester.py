##############################################################
## Helper file to check how therequired bell curve looks like.
##############################################################

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Create range of x-values from --x to x in increments of .001
x = np.arange(-2.2, 2.2, 0.001)
y = norm.pdf(x, 0, 1.6)

# Define plot
fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(x, y)

# Choose plot style and display the bell curve.
plt.style.use('fivethirtyeight')
plt.show()
