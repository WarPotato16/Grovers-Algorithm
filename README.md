# Grover's Algorithm: Theory and Applications

Author: Alexander Bousman

This repository is an educational exploration of Grover's quantum search algorithm. Its central resource is a pedagogical Jupyter notebook that develops the algorithm from classical linear search.

The project began as the final paper I wrote for my PHYS 265 class at Washington and Lee University. The notebook reorganizes that work into an interactive lesson with runnable simulations, conceptual checkpoints, derivations, and experiments based on the accompanying Python scripts in the repository.

**To start**: Open `Grover_Search_Interactive.ipynb` and run the cells in order. Then experiment with the additional files in the `Grover Applications` and `Grover Visualization` folders.

## Repository Contents

| File | Purpose |
| --- | --- |
| `Grover_Search_Interactive.ipynb` | Main interactive lesson and recommended entry point |
| `linearSearch.py` | Animated classical linear-search demonstration |
| `quantumRandomWalk.py` | Continuous-time quantum walk on a cycle |
| `groverSearch.py` | Qiskit oracle construction for one or more marked bitstrings | 
| `lookup.py` | Small gate-level Grover search and measurement example |
| `iterations.py` | Target probability as a function of Grover iterations | 
| `groverPIN.py` | Toy 14-qubit PIN-verifier demonstration | 

## Installation

Python 3.10 or newer is recommended. 

```bash
git clone <https://github.com/WarPotato16/Grovers-Algorithm.git>
cd <Grovers-Algorithm>

python -m venv .venv
```

Activate the environment on macOS or Linux:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies needed by the notebook:

```bash
python -m pip install jupyter numpy matplotlib scipy
```

Then launch Jupyter:

```bash
jupyter notebook Grover_Search_Interactive.ipynb
```

## Optional Qiskit scripts

The main notebook does not require Qiskit. To run the accompanying circuit and simulator scripts, install:

```bash
python -m pip install qiskit qiskit-aer qiskit-ibm-runtime
```

Qiskit APIs change over time, so scripts written against one release may require small import or sampler updates under another release.

The hardware-oriented example also requires an IBM Quantum account. Keep credentials outside source code and version control. Do not commit API tokens to a public repository; use Qiskit's account configuration or an environment variable instead.

