# pip install qiskit qiskit-aer matplotlib

import numpy as np
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit_aer.primitives import Sampler as AerSampler

from qiskit.quantum_info import Statevector

from qiskit.visualization import plot_histogram
from qiskit.circuit.library import GroverOperator

#lookup.py code

def phase_oracle_mark_state(n, marked_int):
    """Phase oracle that flips the phase of |marked>."""
    marked_bits = format(marked_int, f"0{n}b")
    qc = QuantumCircuit(n)
    # Convert |marked> to |111...1> via X on 0-bits
    for i, b in enumerate(reversed(marked_bits)):  # qiskit uses q0 as LSB in this mapping
        if b == "0":
            qc.x(i)
    # Multi-controlled Z via H-MCX-H on the last qubit
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    # Undo X
    for i, b in enumerate(reversed(marked_bits)):
        if b == "0":
            qc.x(i)
    qc.name = f"Oracle(|{marked_bits}>)"
    return qc

n = 3
marked = 5  # 101
oracle = phase_oracle_mark_state(n, marked)

grover_op = GroverOperator(oracle)  # includes oracle + diffusion :contentReference[oaicite:2]{index=2}

# Build a Grover circuit with ~floor(pi/4 * sqrt(N)) iterations for 1 marked item
N = 2**n
iters = int(np.floor(np.pi/4 * np.sqrt(N)))
qc = QuantumCircuit(n)
qc.h(range(n))
for _ in range(iters):
    qc.append(grover_op, range(n))
qc.measure_all()

print("Grover iterations:", iters)
print(qc.draw("text"))

# Run + visualize

sampler = AerSampler()
job = sampler.run([qc], shots=2000)
result = job.result()
counts = result.quasi_dists[0].binary_probabilities()

plot_histogram(counts)
plt.title("Grover search measurement histogram")
plt.show()