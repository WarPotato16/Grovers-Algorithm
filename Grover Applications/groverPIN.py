"""
grover_pin_demo.py

Ethical, toy "password cracking" (PIN recovery) demo with Grover's algorithm.
- Uses Qiskit Aer SamplerV2 (Aer >= 0.15)
- Visualizes:
  1) Measurement histogram (top outcomes)
  2) Success probability vs Grover iterations (amplitude amplification curve)
  3) Classical vs Grover query scaling plot (O(N) vs O(sqrt(N)))

Run:
  python grover_pin_demo.py

Optional args:
  python grover_pin_demo.py --pin 0420 --shots 4000 --max-iters-curve 60 --topk 32

Notes:
- This is a classroom/lab-style demo. It does NOT crack real passwords or systems.
- The "oracle" marks the correct PIN state (models a verifier).
"""

import argparse
import math
from typing import Dict, List, Tuple

import numpy as np
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit
from qiskit.circuit.library import GroverOperator
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram
from qiskit_aer.primitives import SamplerV2

from qiskit import transpile
from qiskit_aer import AerSimulator

def phase_oracle_mark_int(n: int, marked_int: int) -> QuantumCircuit:
    """
    Construct a phase oracle that flips the phase of |marked_int> on n qubits.

    Implementation:
      - Map |marked> -> |11..1> by X on 0-bits
      - Apply multi-controlled Z via H - MCX - H on the last qubit
      - Unmap back
    """
    if marked_int < 0 or marked_int >= 2**n:
        raise ValueError("marked_int must satisfy 0 <= marked_int < 2^n")

    bits = format(marked_int, f"0{n}b")  # MSB..LSB
    qc = QuantumCircuit(n, name=f"Oracle({marked_int})")

    for i, b in enumerate(reversed(bits)):  # i=0 -> qubit 0
        if b == "0":
            qc.x(i)

    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)  # multi-controlled X acts as Z with surrounding H
    qc.h(n - 1)

    for i, b in enumerate(reversed(bits)):
        if b == "0":
            qc.x(i)

    return qc


def build_grover_circuit(n: int, grover_op: GroverOperator, iters: int) -> QuantumCircuit:
    """Build a full Grover circuit with Hadamards, iters Grover iterations, then measure."""
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for _ in range(iters):
        qc.append(grover_op, range(n))
    qc.measure_all()
    return qc


def run_sampler_counts(qc: QuantumCircuit, shots: int) -> Dict[str, int]:
    """
    Run circuit on Aer simulator and return measurement counts.
    Fixes GroverOperator 'Q' instruction issue.
    """

    # Break GroverOperator into basic gates
    qc2 = qc.decompose(reps=10)

    backend = AerSimulator()

    # Convert circuit to backend-supported gates
    qc2 = transpile(qc2, backend)

    job = backend.run(qc2, shots=shots)
    result = job.result()

    return result.get_counts()


def topk_counts(counts: Dict[str, int], k: int) -> Dict[str, int]:
    """Return a dict of the top-k bitstrings by counts."""
    items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:k]
    return dict(items)


def bitstring_to_int(bitstring: str) -> int:
    """Convert MSB..LSB bitstring to integer."""
    return int(bitstring, 2)


def make_pin_label(v: int) -> str:
    """Format an integer as a 4-digit PIN if in range; otherwise plain int."""
    if 0 <= v <= 9999:
        return f"{v:04d}"
    return str(v)

def plot_top_histogram(counts: Dict[str, int], topk: int, title: str) -> None:
    """Plot histogram for top-k counts."""
    tk = topk_counts(counts, topk)
    plt.figure()
    plot_histogram(tk)
    plt.title(title)
    plt.show()


def print_top_candidates(counts: Dict[str, int], limit: int = 10) -> None:
    """Print the top candidate states as integers (and 4-digit PIN labels where relevant)."""
    items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:limit]
    total = sum(counts.values())
    print("\nTop candidates:")
    for b, c in items:
        v = bitstring_to_int(b)
        p = c / total if total else 0.0
        print(f"  state={b}  int={v:5d}  pin={make_pin_label(v):>4}  counts={c:5d}  prob≈{p:.3f}")


def success_prob_curve(n: int, secret_int: int, grover_op: GroverOperator, max_iters: int) -> List[float]:
    """
    Compute P(measure secret) vs iteration count using statevector simulation (exact).
    This is feasible for n=14 (2^14=16384) on most machines.
    """
    secret_bits = format(secret_int, f"0{n}b")
    base = QuantumCircuit(n)
    base.h(range(n))

    probs: List[float] = []
    for k in range(max_iters + 1):
        qc = base.copy()
        for _ in range(k):
            qc.append(grover_op, range(n))
        sv = Statevector.from_instruction(qc)
        probs.append(sv.probabilities_dict().get(secret_bits, 0.0))

    return probs


def plot_success_curve(probs: List[float], title: str) -> None:
    """Plot success probability vs Grover iterations."""
    plt.figure()
    plt.plot(range(len(probs)), probs, marker="o")
    plt.xlabel("Grover iterations")
    plt.ylabel("P(measure secret)")
    plt.title(title)
    plt.ylim(0, 1)
    plt.grid(True)
    plt.show()


def plot_scaling_comparison(max_digits: int = 8) -> None:
    """
    Plot classical brute force queries vs Grover queries for d-digit PIN spaces.
      N = 10^d
      Classical expected queries ~ N/2
      Grover optimal iterations ~ floor(pi/4 * sqrt(N))  (for one marked item)
    """
    digits = np.arange(1, max_digits + 1)
    N = 10 ** digits.astype(float)

    classical = N / 2.0
    grover = (np.pi / 4.0) * np.sqrt(N)

    plt.figure()
    plt.loglog(digits, classical, marker="o", label="Classical expected queries ~ N/2")
    plt.loglog(digits, grover, marker="o", label="Grover iterations ~ (π/4)√N")
    plt.xticks(digits, [str(d) for d in digits])
    plt.xlabel("PIN digits (d)")
    plt.ylabel("Queries / iterations (log scale)")
    plt.title("Search cost scaling: classical vs Grover")
    plt.grid(True, which="both")
    plt.legend()
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Grover toy PIN recovery demo (SamplerV2 + visualizations).")
    parser.add_argument("--pin", type=str, default="0420", help="4-digit PIN to 'recover' (toy secret).")
    parser.add_argument("--shots", type=int, default=4000, help="Measurement shots for the sampler.")
    parser.add_argument("--topk", type=int, default=32, help="How many outcomes to show in histogram.")
    parser.add_argument("--max-iters-curve", type=int, default=60, help="Max iterations for success-prob curve.")
    parser.add_argument("--max-digits-scaling", type=int, default=8, help="Max digits for scaling plot.")
    args = parser.parse_args()

    # Validate PIN
    if not args.pin.isdigit() or len(args.pin) != 4:
        raise ValueError("Please provide a 4-digit PIN like 0420.")
    secret = int(args.pin)
    if secret < 0 or secret > 9999:
        raise ValueError("PIN must be between 0000 and 9999 inclusive.")

    # Build search space n = ceil(log2(10000)) = 14
    n = int(math.ceil(math.log2(10000)))

    # Oracle + Grover operator
    oracle = phase_oracle_mark_int(n, secret)
    grover_op = GroverOperator(oracle)

    # Use standard single-solution estimate for optimal iterations in full 2^n space
    N = 2**n
    iters = int(math.floor((math.pi / 4.0) * math.sqrt(10000)))

    print("=== Grover Toy PIN Recovery Demo ===")
    print(f"Secret PIN: {args.pin} (int={secret})")
    print(f"Qubits: {n} (search space size 2^n = {N})")
    print(f"Grover iterations (standard estimate): {iters}")
    print(f"Shots: {args.shots}")

    # Build and run circuit
    qc = build_grover_circuit(n, grover_op, iters)
    counts = run_sampler_counts(qc, shots=args.shots)

    # --- Figure 1: histogram of VALID pins only ---
    def filter_valid_pins(counts: dict, max_pin: int = 9999) -> dict:
        """Keep only outcomes whose integer value is <= max_pin."""
        out = {}
        for b, c in counts.items():
            v = int(b, 2)
            if v <= max_pin:
                out[b] = c
        return out
    
    valid_counts = filter_valid_pins(counts)

    print("Total shots:", sum(counts.values()))
    print("Valid-pin shots:", sum(valid_counts.values()))
    print("Invalid-pin shots:", sum(counts.values()) - sum(valid_counts.values()))

    if len(valid_counts) > 0:

        k = min(args.topk, len(valid_counts))

        tk = dict(
            sorted(valid_counts.items(), key=lambda kv: kv[1], reverse=True)[:k]
        )

        plt.figure()
        plot_histogram(tk)
        plt.title("Figure 1: Grover PIN recovery (valid PINs only)")
        plt.tight_layout()
        plt.show(block=True)

    else:
        print("No valid PINs to plot.")

    # Print top candidates (existing code)
    print_top_candidates(counts, limit=10)
    plot_top_histogram(counts, topk=args.topk, title="Grover PIN recovery (top outcomes)")

    # Success probability curve via exact statevector
    probs = success_prob_curve(n, secret, grover_op, max_iters=args.max_iters_curve)
    plot_success_curve(probs, title="Amplitude amplification curve (PIN demo)")

    # Scaling comparison plot
    plot_scaling_comparison(max_digits=args.max_digits_scaling)


if __name__ == "__main__":
    main()