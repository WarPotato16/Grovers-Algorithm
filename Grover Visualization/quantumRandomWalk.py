import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import expm

# Parameters
N = 101           # Number of sites in the cycle (choose an odd number to center nicely)
gamma = 1.0       # Hopping rate
T = 10.0          # Total simulation time
dt = 1.0          # Larger time step for sampling fewer snapshots
time_steps = np.arange(0, T+dt, dt)

# Construct the Hamiltonian for a cycle (periodic boundary conditions)
# Each site is connected to its two neighbors.
H = np.zeros((N, N), dtype=complex)
for i in range(N):
    H[i, (i + 1) % N] = 1
    H[i, (i - 1) % N] = 1
H = -gamma * H  # The minus sign is conventional for the hopping term

# Initial state: a localized state at the center of the lattice
psi0 = np.zeros(N, dtype=complex)
psi0[N // 2] = 1.0

# We'll store the probability distributions at each sampled time
prob_snapshots = []

for t in time_steps:
    U = expm(-1j * H * t)   # Time evolution operator U(t) = exp(-i H t)
    psi_t = U.dot(psi0)
    prob = np.abs(psi_t)**2
    prob_snapshots.append(prob)

# Convert to a NumPy array for convenience (optional)
prob_snapshots = np.array(prob_snapshots)

# We'll shift the site indices so that 0 is in the middle (for a more symmetric plot)
# This is optional, but often makes wavefunction plots clearer.
sites = np.arange(N) - (N // 2)

# Plot the probability distribution for each time on the same figure
plt.figure(figsize=(8, 6))
for i, t in enumerate(time_steps):
    plt.plot(sites, prob_snapshots[i], label=f"t = {t:.1f}")

plt.xlabel("Position (x)")
plt.ylabel("Probability P(x)")
plt.title("Snapshots of a Continuous-Time Quantum Walk on a Cycle")
plt.legend()
plt.grid(True)
plt.show()