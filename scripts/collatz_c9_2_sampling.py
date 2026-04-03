import numpy as np
import matplotlib.pyplot as plt

# Configuration
num_samples = 1000
max_iter = 1e5

# Collatz function

def collatz(n):
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1

# Sampling
samples = []
for _ in range(num_samples):
    n = np.random.randint(1, 10000)
    count = 0
    while n != 1 and count < max_iter:
        n = collatz(n)
        count += 1
    samples.append(count)

# Plotting
plt.hist(samples, bins=30, edgecolor='black')
plt.xlabel('Steps to reach 1')
plt.ylabel('Frequency')
plt.title('Collatz Sampling')
plt.show()