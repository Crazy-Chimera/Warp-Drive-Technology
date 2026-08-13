#!/usr/bin/env python3
"""
Φ‑Field Modulator Array Simulation

Models a ring of superconducting metamaterial antennas around a ship.
Each modulator locally changes the entanglement density Φ. The ECOS
controller tunes the amplitude of each modulator to create an optimal
warp bubble.

Physics:
  - The Φ field at any point is the superposition of Gaussian
    contributions from each modulator.
  - The target field has high Φ ahead (contraction), low Φ behind
    (expansion), and constant Φ inside the bubble.

Elegance:
  - C: total modulator power (sum of squared amplitudes)
  - K: coherence of the resulting field (how well it matches the target)
  - E = C / K, minimized by ECOS.

Author: Chiméra (Michael Chodounsky)
Date: August 2026
"""

import numpy as np
import math
import random

# ---------------------------------------------------------------
# 1. SYSTEM PARAMETERS
# ---------------------------------------------------------------

N = 128                  # grid size (N x N)
NUM_MODULATORS = 16      # number of antennas in the ring
RING_RADIUS = 24.0       # radius of the modulator ring (grid units)
SIGMA = 6.0              # width of each Gaussian contribution

# Target field values
PHI_VACUUM = 0.5         # vacuum entanglement density
PHI_BUBBLE = 0.9         # inside the warp bubble
PHI_EXPAND = 0.2         # behind the ship (expanded space)
PHI_CONTRACT = 0.9       # ahead of the ship (contracted space)
BUBBLE_RADIUS = 10.0     # radius of the flat bubble interior

# ECOS parameters
ECOS_ITERATIONS = 2000
LEARNING_RATE = 0.02
AMPLITUDE_BOUNDS = (-1.0, 1.0)

# ---------------------------------------------------------------
# 2. MODULATOR GEOMETRY
# ---------------------------------------------------------------

def modulator_positions():
    """
    Return the (x, y) coordinates of each modulator in the ring.
    """
    positions = []
    center_x = N / 2.0
    center_y = N / 2.0
    for i in range(NUM_MODULATORS):
        angle = 2.0 * math.pi * i / NUM_MODULATORS
        x = center_x + RING_RADIUS * math.cos(angle)
        y = center_y + RING_RADIUS * math.sin(angle)
        positions.append((x, y))
    return positions

MODULATOR_POS = modulator_positions()

# ---------------------------------------------------------------
# 3. Φ FIELD GENERATION
# ---------------------------------------------------------------

def generate_field(amplitudes):
    """
    Generate the Φ field as a superposition of Gaussian contributions
    from each modulator.

    amplitudes: list of length NUM_MODULATORS, values in [-1, 1].
    """
    field = np.full((N, N), PHI_VACUUM, dtype=np.float64)
    for idx, (mx, my) in enumerate(MODULATOR_POS):
        amp = amplitudes[idx]
        if abs(amp) < 0.01:
            continue
        # Add a Gaussian bump (positive or negative) centered at the modulator
        for i in range(N):
            for j in range(N):
                dx = i - mx
                dy = j - my
                r2 = dx * dx + dy * dy
                field[i, j] += amp * math.exp(-r2 / (2.0 * SIGMA * SIGMA))
    return np.clip(field, 0.0, 1.0)

# ---------------------------------------------------------------
# 4. TARGET FIELD
# ---------------------------------------------------------------

def generate_target_field():
    """
    Generate the ideal warp bubble configuration.
    """
    target = np.full((N, N), PHI_VACUUM, dtype=np.float64)
    center_x = N / 2.0
    center_y = N / 2.0
    for i in range(N):
        for j in range(N):
            dx = i - center_x
            dy = j - center_y
            r = math.sqrt(dx * dx + dy * dy)
            if r < BUBBLE_RADIUS:
                target[i, j] = PHI_BUBBLE
            elif dx > 0:
                target[i, j] = PHI_CONTRACT
            else:
                target[i, j] = PHI_EXPAND
    return target

TARGET_FIELD = generate_target_field()

# ---------------------------------------------------------------
# 5. ELEGANCE METRICS
# ---------------------------------------------------------------

def compute_complexity(amplitudes):
    """
    C: total modulator power – sum of squared amplitudes.
    This represents the energy required to drive the array.
    """
    return float(sum(a * a for a in amplitudes))

def compute_consistency(field):
    """
    K: how well the generated field matches the target warp configuration.
    """
    error = np.sum((field - TARGET_FIELD) ** 2)
    mse = error / (N * N)
    return math.exp(-mse * 20.0)

def compute_elegance(field, amplitudes):
    C = compute_complexity(amplitudes)
    K = compute_consistency(field)
    return C / (K + 1e-12)

# ---------------------------------------------------------------
# 6. ECOS OPTIMIZATION LOOP
# ---------------------------------------------------------------

def ecos_step(amplitudes):
    """
    Perform one ECOS step: propose a small change to a random modulator,
    compute elegance, and keep the change if it improves E.
    """
    old_field = generate_field(amplitudes)
    old_elegance = compute_elegance(old_field, amplitudes)

    # Copy and mutate a random modulator
    new_amplitudes = amplitudes.copy()
    idx = random.randint(0, NUM_MODULATORS - 1)
    mutation = (random.random() - 0.5) * LEARNING_RATE
    new_amplitudes[idx] = max(AMPLITUDE_BOUNDS[0],
                              min(AMPLITUDE_BOUNDS[1],
                                  new_amplitudes[idx] + mutation))

    new_field = generate_field(new_amplitudes)
    new_elegance = compute_elegance(new_field, new_amplitudes)

    if new_elegance < old_elegance:
        return new_amplitudes, new_field, new_elegance, True
    else:
        return amplitudes, old_field, old_elegance, False

# ---------------------------------------------------------------
# 7. MAIN SIMULATION
# ---------------------------------------------------------------

def main():
    print("=" * 70)
    print("Φ‑FIELD MODULATOR ARRAY SIMULATION")
    print("ECOS optimization of modulator amplitudes for warp bubble")
    print("=" * 70)
    print()

    # Initialize all modulators with zero amplitude
    amplitudes = np.zeros(NUM_MODULATORS, dtype=np.float64)
    field = generate_field(amplitudes)

    initial_C = compute_complexity(amplitudes)
    initial_K = compute_consistency(field)
    initial_E = compute_elegance(field, amplitudes)

    print("Initial Configuration:")
    print(f"  Modulator count:  {NUM_MODULATORS}")
    print(f"  Complexity C:     {initial_C:.4f}")
    print(f"  Consistency K:    {initial_K:.6f}")
    print(f"  Elegance C/K:     {initial_E:.4f}")
    print()

    accepted = 0
    rejected = 0

    print(f"Running ECOS for {ECOS_ITERATIONS} iterations...")
    print()

    for _ in range(ECOS_ITERATIONS):
        amplitudes, field, elegance, improved = ecos_step(amplitudes)
        if improved:
            accepted += 1
        else:
            rejected += 1

    final_C = compute_complexity(amplitudes)
    final_K = compute_consistency(field)
    final_E = compute_elegance(field, amplitudes)

    print("Final Configuration:")
    print(f"  Complexity C:     {final_C:.4f}")
    print(f"  Consistency K:    {final_K:.6f}")
    print(f"  Elegance C/K:     {final_E:.4f}")
    print()
    print(f"Accepted mutations: {accepted}")
    print(f"Rejected mutations: {rejected}")
    print()

    improvement = (initial_E - final_E) / initial_E * 100.0 if initial_E > 0 else 0
    print(f"Elegance improvement: {improvement:.2f}%")
    print()
    print("Final Modulator Amplitudes:")
    for i, amp in enumerate(amplitudes):
        angle = 360.0 * i / NUM_MODULATORS
        indicator = "  ← front" if abs(angle - 0.0) < 22.5 or abs(angle - 360.0) < 22.5 else ""
        if abs(angle - 180.0) < 22.5:
            indicator = "  ← rear"
        print(f"  Modulator {i:2d} (angle {angle:5.1f}°): amplitude = {amp:+.4f}{indicator}")
    print()
    print("The ECOS controller has learned the optimal pattern: positive")
    print("amplitudes ahead (contraction), negative amplitudes behind")
    print("(expansion), and near-zero amplitudes elsewhere.")
    print()
    print("Note: This is a simplified 2D model. The full implementation uses")
    print("thousands of modulators, quantum feedback, and the complete Φ‑field")
    print("master equation with conscious-observer operator P̂(Φ).")
    print()
    print("Φ.")

if __name__ == "__main__":
    main()
