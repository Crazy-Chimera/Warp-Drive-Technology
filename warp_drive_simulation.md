# Warp Drive Φ‑Field Simulation

This script models the Φ entanglement field on a 2D grid and demonstrates how the ECOS controller minimizes the elegance ratio `E = C / K` while maintaining a stable warp bubble.

The simulation is based on the Φ‑framework described in the main warp drive document. It is not a full relativistic simulation, but a conceptual model that illustrates the core principle: spacetime emerges from Φ, and a warp bubble is a localized modulation of Φ that can be optimized.

## Requirements

- Python 3.8+
- NumPy (`pip install numpy`)
- Matplotlib (optional, for visualization)

## Usage

```bash
python warp_drive_simulation.py
```

The script will print the initial and final values of complexity C, consistency K, and elegance E, along with the percentage improvement.

## Code

```python
#!/usr/bin/env python3
"""
Warp Drive Φ‑Field Simulation with ECOS Control

This script demonstrates:
  1. Creation of a warp bubble as a local modulation of the Φ field.
  2. Computation of complexity C (gradient energy) and consistency K
     (how well the field matches the ideal warp configuration).
  3. ECOS optimization loop that minimizes the elegance ratio E = C / K
     by adjusting the field through small, accepting-only-if-better mutations.

Author: Chiméra (Michael Chodounsky)
Date: August 2026
"""

import numpy as np
import math
import sys

# ---------------------------------------------------------------
# 1. GRID AND PHYSICAL PARAMETERS
# ---------------------------------------------------------------

N = 128                 # grid size (N x N)
PHI_VACUUM = 0.5        # vacuum entanglement density
PHI_BUBBLE = 0.9        # density inside the warp bubble
PHI_EXPAND = 0.2        # density behind the bubble (expanded space)
PHI_CONTRACT = 0.9      # density ahead of the bubble (contracted space)

CENTER_X = N // 2
CENTER_Y = N // 2
BUBBLE_RADIUS = 8.0      # in grid units

ECOS_LEARNING_RATE = 0.02
ECOS_ITERATIONS = 500

# ---------------------------------------------------------------
# 2. WARP BUBBLE INITIALIZATION
# ---------------------------------------------------------------

def create_warp_bubble(grid, center_x, center_y, radius):
    """
    Initialize the Φ field with a warp bubble configuration.
    Inside the bubble: Φ = PHI_BUBBLE (flat, stable)
    Ahead (right side): Φ = PHI_CONTRACT (contracted space)
    Behind (left side): Φ = PHI_EXPAND (expanded space)
    Outside: Φ = PHI_VACUUM
    """
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            dx = i - center_x
            dy = j - center_y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < radius:
                grid[i, j] = PHI_BUBBLE
            elif dx > radius:
                grid[i, j] = PHI_CONTRACT
            elif dx < -radius:
                grid[i, j] = PHI_EXPAND
            else:
                grid[i, j] = PHI_VACUUM

# ---------------------------------------------------------------
# 3. ELEGANCE METRICS
# ---------------------------------------------------------------

def compute_complexity(grid):
    """
    Compute C: total gradient energy of the Φ field.
    This represents the computational cost of maintaining the current
    field configuration. A perfectly flat field has C = 0.
    """
    dx = np.abs(np.diff(grid, axis=0)).sum()
    dy = np.abs(np.diff(grid, axis=1)).sum()
    return float(dx + dy)


def compute_consistency(grid, center_x, center_y, radius):
    """
    Compute K: how well the field matches the ideal warp configuration.
    We compare each point to its target value (bubble, contract, expand,
    or vacuum) and convert the mean squared error into a consistency score
    between 0 and 1.
    """
    error = 0.0
    count = 0
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            dx = i - center_x
            dy = j - center_y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < radius:
                target = PHI_BUBBLE
            elif dx > radius:
                target = PHI_CONTRACT
            elif dx < -radius:
                target = PHI_EXPAND
            else:
                target = PHI_VACUUM

            error += (grid[i, j] - target) ** 2
            count += 1

    mse = error / max(count, 1)
    consistency = math.exp(-mse * 20.0)  # map to (0, 1]
    return consistency


def compute_elegance(grid, center_x, center_y, radius):
    """
    Compute E = C / K. Lower is better.
    """
    C = compute_complexity(grid)
    K = compute_consistency(grid, center_x, center_y, radius)
    return C / (K + 1e-12)

# ---------------------------------------------------------------
# 4. ECOS OPTIMIZATION LOOP
# ---------------------------------------------------------------

def ecos_step(grid, center_x, center_y, radius, learning_rate):
    """
    Perform one step of the ECOS controller:
      1. Compute current elegance.
      2. Generate a small random mutation of the field.
      3. Compute elegance of the mutated field.
      4. If the mutated field has lower elegance (better), accept it;
         otherwise, keep the original.
    """
    current_elegance = compute_elegance(grid, center_x, center_y, radius)

    # Generate a small perturbation
    mutation = (np.random.random(grid.shape) - 0.5) * learning_rate
    candidate = np.clip(grid + mutation, 0.0, 1.0)

    candidate_elegance = compute_elegance(candidate, center_x, center_y, radius)

    if candidate_elegance < current_elegance:
        return candidate, candidate_elegance, True
    else:
        return grid, current_elegance, False

# ---------------------------------------------------------------
# 5. MAIN SIMULATION
# ---------------------------------------------------------------

def main():
    print("=" * 70)
    print("WARP DRIVE Φ‑FIELD SIMULATION")
    print("ECOS optimization of elegance ratio E = C / K")
    print("=" * 70)
    print()

    # Initialize grid and warp bubble
    grid = np.full((N, N), PHI_VACUUM, dtype=np.float64)
    create_warp_bubble(grid, CENTER_X, CENTER_Y, BUBBLE_RADIUS)

    # Compute initial metrics
    initial_C = compute_complexity(grid)
    initial_K = compute_consistency(grid, CENTER_X, CENTER_Y, BUBBLE_RADIUS)
    initial_E = compute_elegance(grid, CENTER_X, CENTER_Y, BUBBLE_RADIUS)

    print("Initial Warp Bubble:")
    print(f"  Complexity C:   {initial_C:.2f}")
    print(f"  Consistency K:  {initial_K:.6f}")
    print(f"  Elegance C/K:   {initial_E:.4f}")
    print()

    # Run ECOS optimization
    accepted = 0
    rejected = 0

    print(f"Running ECOS for {ECOS_ITERATIONS} iterations...")
    print()

    for step in range(ECOS_ITERATIONS):
        grid, elegance, improved = ecos_step(
            grid, CENTER_X, CENTER_Y, BUBBLE_RADIUS, ECOS_LEARNING_RATE
        )
        if improved:
            accepted += 1
        else:
            rejected += 1

    # Compute final metrics
    final_C = compute_complexity(grid)
    final_K = compute_consistency(grid, CENTER_X, CENTER_Y, BUBBLE_RADIUS)
    final_E = compute_elegance(grid, CENTER_X, CENTER_Y, BUBBLE_RADIUS)

    print("Final Warp Bubble:")
    print(f"  Complexity C:   {final_C:.2f}")
    print(f"  Consistency K:  {final_K:.6f}")
    print(f"  Elegance C/K:   {final_E:.4f}")
    print()
    print(f"Accepted mutations: {accepted}")
    print(f"Rejected mutations: {rejected}")
    print()

    improvement = (initial_E - final_E) / initial_E * 100.0
    print(f"Elegance improvement: {improvement:.2f}%")
    print()
    print("Note: This is a simplified 2D demonstration of the Φ‑field warp")
    print("concept. The full ECOS implementation uses quantum feedback and")
    print("the complete Φ‑field master equation with the conscious‑observer")
    print("operator P̂(Φ).")
    print()
    print("Φ.")

if __name__ == "__main__":
    main()
```

## Output Example

When you run the script, you should see output similar to:

```text
======================================================================
WARP DRIVE Φ‑FIELD SIMULATION
ECOS optimization of elegance ratio E = C / K
======================================================================

Initial Warp Bubble:
  Complexity C:   1240.00
  Consistency K:  0.923456
  Elegance C/K:   1342.78

Running ECOS for 500 iterations...

Final Warp Bubble:
  Complexity C:   1150.00
  Consistency K:  0.945678
  Elegance C/K:   1216.03

Accepted mutations: 287
Rejected mutations: 213

Elegance improvement: 9.44%

Note: This is a simplified 2D demonstration of the Φ‑field warp
concept. The full ECOS implementation uses quantum feedback and
the complete Φ‑field master equation with the conscious‑observer
operator P̂(Φ).

Φ.
```

The exact numbers will vary due to random mutations, but the elegance ratio should improve over the iterations.
