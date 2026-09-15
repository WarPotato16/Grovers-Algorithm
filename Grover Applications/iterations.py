# pip install qiskit qiskit-aer matplotlib

import numpy as np
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit_aer.primitives import Sampler as AerSampler

from qiskit.quantum_info import Statevector

from qiskit.visualization import plot_histogram
from qiskit.circuit.library import GroverOperator

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

def grover_success_prob_over_iters(n, marked_int, max_iters=10):
    oracle = phase_oracle_mark_state(n, marked_int)
    grover_op = GroverOperator(oracle)

    probs = []
    marked_bits = format(marked_int, f"0{n}b")

    base = QuantumCircuit(n)
    base.h(range(n))

    for k in range(max_iters + 1):
        qc = base.copy()
        for _ in range(k):
            qc.append(grover_op, range(n))

        sv = Statevector.from_instruction(qc)
        # Qiskit uses little-endian ordering in many displays;
        # We'll compute probabilities over computational basis as returned.
        prob_dict = sv.probabilities_dict()
        probs.append(prob_dict.get(marked_bits, 0.0))

    return probs

n = 3
marked = 5
probs = grover_success_prob_over_iters(n, marked, max_iters=12)

plt.figure()
plt.plot(range(len(probs)), probs, marker="o")
plt.xlabel("Grover iterations")
plt.ylabel("P(measure marked state)")
plt.title("Amplitude amplification curve (Grover)")
plt.ylim(0, 1)
plt.grid(True)
plt.show()

# Run + visualize

sampler = AerSampler()
job = sampler.run([qc], shots=2000)
result = job.result()
counts = result.quasi_dists[0].binary_probabilities()

plot_histogram(counts)
plt.title("Grover search measurement histogram")
plt.show()