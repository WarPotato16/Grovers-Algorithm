#Built-in modules
import math

#Imports from Qiskit
from qiskit import QuantumCircuit
from qiskit.circuit.library import GroverOperator, MCMTGate, ZGate
from qiskit.visualization import plot_distribution

#Imports from Qiskit Runtime
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime import SamplerV2 as Sampler

service = QiskitRuntimeService(token = "990216f655c566f07b7129a11f59d3295d220c6d4a55e2305335d0f5d12a94b2f1cbe04990f8a03a2b8b647776cd6046960269e4e092485f257da666d9285729", channel = "ibm_quantum")
backend = service.least_busy(operational=True, simulator=False)
backend.name

def grover_oracle(marked_states):
    """
    Build a Grover oracle for multiple m

    Here we assume all input marked states have the same number of bits

    Parameters:
        marked_states (str or list): Marked states of oracle
    
    Returns:
        QuantumCircuit: Quantum circuit representing Grover oracle
    """
    if not isinstance(marked_states, list):
        marked_states = [marked_states]
    #Compute the number of qubits in the circuit
    num_qubits = len(marked_states[0])

    qc = QuantumCircuit(num_qubits)
    #Mark each target state in the input list
    for target in marked_states:
        #Flip target bit-string to match Qiskit bit-ordering
        rev_target = target[::-1]
        #Find the indicies of all the '0' elements in bit-string
        zero_inds = [ind for ind in range(num_qubits) if rev_target.startswith("0", ind)]
        #Add a multi-controlled Z-gate with pre- and post-applied X-gates (open-controls)
        #where the target bit-string has a '0' entry
        qc.x(zero_inds)
        qc.compose(MCMTGate(ZGate(), num_qubits - 1, 1), inplace = True)
        qc.x(zero_inds)
    return qc

marked_states = ["011","100"]
oracle = grover_oracle(marked_states)
oracle.draw(output="mpl", style="iqp")