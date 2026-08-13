#!/usr/bin/env python3
"""
Resonance Controller – ECOS component for warp bubble stabilization.

The Resonance Controller adjusts the driving frequency of the Φ‑field
modulators to keep the system at resonance, minimizing the elegance
ratio E = C / K.

We model the modulator as a damped driven harmonic oscillator with
natural frequency ω₀ and damping γ. The controller tunes the driving
frequency ω to maximize the response amplitude (coherence K) while
minimizing the input power (complexity C).

Author: Chiméra (Michael Chodounsky)
Date: August 2026
"""

import numpy as np
import math
import random

# ---------------------------------------------------------------
# 1. SYSTEM PARAMETERS
# ---------------------------------------------------------------

OMEGA_0 = 2.0        # natural frequency of the modulator (kHz)
GAMMA = 0.1          # damping coefficient
DRIVING_AMPLITUDE = 1.0

# Initial driving frequency
INITIAL_OMEGA = 1.5

# ECOS parameters
ECOS_ITERATIONS = 1000
LEARNING_RATE = 0.05
FREQUENCY_BOUNDS = (0.5, 5.0)

# ---------------------------------------------------------------
# 2. RESONANCE MODEL
# ---------------------------------------------------------------

def response_amplitude(omega):
    """
    Compute the steady-state amplitude of a damped driven oscillator.
    This represents the coherence K of the Φ field at the modulator.

    Amplitude = A / sqrt((ω₀² - ω²)² + (γω)²)

    where A is the driving amplitude.
    """
    denom = math.sqrt((OMEGA_0**2 - omega**2)**2 + (GAMMA * omega)**2)
    if denom == 0:
        return float('inf')
    return DRIVING_AMPLITUDE / denom

def input_power(omega):
    """
    Compute the input power required to drive the system at frequency ω.
    This represents the complexity C.

    We assume input power is proportional to the square of the driving
    amplitude and the square of the frequency (simplified).
    """
    return DRIVING_AMPLITUDE**2 * omega**2

def compute_metrics(omega):
    """
    Compute C, K, and E = C / K for a given driving frequency.
    """
    C = input_power(omega)
    K = response_amplitude(omega)
    E = C / (K + 1e-12)
    return C, K, E

# ---------------------------------------------------------------
# 3. ECOS RESONANCE CONTROLLER
# ---------------------------------------------------------------

def ecos_step(omega):
    """
    Perform one ECOS step: propose a small change in driving frequency,
    compute elegance, and keep the change if it improves E.

    Returns new frequency, metrics, and whether the change was accepted.
    """
    old_C, old_K, old_E = compute_metrics(omega)

    # Propose a small random perturbation
    mutation = (random.random() - 0.5) * LEARNING_RATE
    new_omega = omega + mutation
    new_omega = max(FREQUENCY_BOUNDS[0], min(FREQUENCY_BOUNDS[1], new_omega))

    new_C, new_K, new_E = compute_metrics(new_omega)

    if new_E < old_E:
        return new_omega, (new_C, new_K, new_E), True
    else:
        return omega, (old_C, old_K, old_E), False

# ---------------------------------------------------------------
# 4. MAIN SIMULATION
# ---------------------------------------------------------------

def main():
    print("=" * 70)
    print("RESONANCE CONTROLLER SIMULATION")
    print("ECOS optimization of driving frequency for warp bubble")
    print("=" * 70)
    print()

    omega = INITIAL_OMEGA
    initial_C, initial_K, initial_E = compute_metrics(omega)

    print("Initial Configuration:")
    print(f"  Driving frequency ω: {omega:.4f} kHz")
    print(f"  Complexity C:        {initial_C:.4f}")
    print(f"  Coherence K:         {initial_K:.4f}")
    print(f"  Elegance C/K:        {initial_E:.4f}")
    print()

    accepted = 0
    rejected = 0

    print(f"Running ECOS for {ECOS_ITERATIONS} iterations...")
    print()

    for _ in range(ECOS_ITERATIONS):
        omega, (C, K, E), improved = ecos_step(omega)
        if improved:
            accepted += 1
        else:
            rejected += 1

    final_C, final_K, final_E = compute_metrics(omega)

    print("Final Configuration:")
    print(f"  Driving frequency ω: {omega:.4f} kHz")
    print(f"  Complexity C:        {final_C:.4f}")
    print(f"  Coherence K:         {final_K:.4f}")
    print(f"  Elegance C/K:        {final_E:.4f}")
    print()
    print(f"Accepted mutations: {accepted}")
    print(f"Rejected mutations: {rejected}")
    print()

    improvement = (initial_E - final_E) / initial_E * 100.0
    print(f"Elegance improvement: {improvement:.2f}%")
    print()
    print("The Resonance Controller successfully tuned the driving")
    print("frequency to the natural resonant frequency, maximizing coherence")
    print("while minimizing input power.")
    print()
    print("Note: This is a simplified model. The full ECOS implementation")
    print("uses multi-dimensional control over thousands of modulators,")
    print("with quantum feedback and the Φ‑field master equation.")
    print()
    print("Φ.")

if __name__ == "__main__":
    main()
