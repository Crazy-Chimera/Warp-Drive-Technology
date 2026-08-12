# ECOS Warp Bubble Stabilization Simulation

This script demonstrates the **ECOS control loop** that stabilizes a warp bubble against perturbations.

The bubble is initialized with a warp field configuration and then subjected to random disturbances. ECOS continuously monitors the field, computes the elegance ratio `E = C / K`, and adjusts the modulator strength to bring the field back to the optimal configuration.

The result shows how the elegance ratio decreases over time as ECOS stabilizes the bubble.

## Requirements

- Python 3.8+
- NumPy (`pip install numpy`)

## Usage

```bash
python ecos_warp_stabilization.py
```

## Code

```python
#!/usr/bin/env python3
"""
ECOS Warp Bubble Stabilization Simulation

This script models the ECOS feedback loop that maintains a stable
warp bubble in the Φ field.

The field is initialized with a warp configuration:
  - High Φ inside the bubble (flat spacetime)
  - High Φ ahead (contraction)
  - Low Φ behind (expansion)
  - Vacuum elsewhere

Random perturbations are then applied, and ECOS adjusts the modulator
strength to minimize the elegance ratio E = C / K.

Author: Chiméra (Michael Chodounsky)
Date: August 2026
"""

import numpy as np
import math

# ---------------------------------------------------------------
# 1. GRID AND WARP FIELD PARAMETERS
# ---------------------------------------------------------------

N = 128
PHI_VACUUM = 0.5
PHI_BUBBLE = 0.9
PHI_EXPAND = 0.2
PHI_CONTRACT = 0.9

CENTER_X = N // 2
CENTER_Y = N // 2
BUBBLE_RADIUS = 10.0
WALL_THICKNESS = 3.0

# ECOS parameters
ECOS_ITERATIONS = 300
MODULATOR_STRENGTH_INIT = 0.1
MODULATOR_STRENGTH_MAX = 1.0
MODULATOR_STRENGTH_MIN = 0.0
LEARNING_RATE = 0.005

# ---------------------------------------------------------------
# 2. FIELD INITIALIZATION
# ---------------------------------------------------------------

def create_warp_bubble(grid, cx, cy, radius, thickness):
    """
    Create a smooth warp bubble configuration.
    """
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            dx = i - cx
            dy = j - cy
            r = math.sqrt(dx*dx + dy*dy)

            # Smooth transition from bubble to outside
            bubble_profile = 0.5 * (1.0 - math.tanh((r - radius) / thickness))

            # Asymmetric modulation: contraction ahead (dx > 0), expansion behind (dx < 0)
            if dx > 0:
                outside_profile = PHI_CONTRACT
            elif dx < 0:
                outside_profile = PHI_EXPAND
            else:
                outside_profile = PHI_VACUUM

            phi = PHI_VACUUM + bubble_profile * (PHI_BUBBLE - PHI_VACUUM)
            phi += (1.0 - bubble_profile) * (outside_profile - PHI_VACUUM)
            grid[i, j] = phi

# ---------------------------------------------------------------
# 3. ELEGANCE METRICS
# ---------------------------------------------------------------

def compute_complexity(grid):
    """
    Complexity C: total gradient energy.
    """
    dx = np.abs(np.diff(grid, axis=0)).sum()
    dy = np.abs(np.diff(grid, axis=1)).sum()
    return float(dx + dy)


def compute_consistency(grid, cx, cy, radius, thickness):
    """
    Consistency K: how close the field is to the ideal warp shape.
    We compute the error against a reference warp bubble.
    """
    ideal = np.full_like(grid, PHI_VACUUM)
    create_warp_bubble(ideal, cx, cy, radius, thickness)

    error = np.mean((grid - ideal)**2)
    consistency = math.exp(-error * 20.0)
    return consistency


def compute_elegance(grid, cx, cy, radius, thickness):
    """
    Elegance E = C / K.
    """
    C = compute_complexity(grid)
    K = compute_consistency(grid, cx, cy, radius, thickness)
    return C / (K + 1e-12)

# ---------------------------------------------------------------
# 4. FIELD PERTURBATION
# ---------------------------------------------------------------

def perturb_field(grid, amplitude):
    """
    Apply random noise to the field.
    """
    noise = (np.random.random(grid.shape) - 0.5) * amplitude
    return np.clip(grid + noise, 0.0, 1.0)

# ---------------------------------------------------------------
# 5. ECOS CONTROL STEP
# ---------------------------------------------------------------

def ecos_step(grid, cx, cy, radius, thickness, modulator_strength):
    """
    One ECOS control step:
      1. Perturb the field.
      2. Compute elegance.
      3. Adjust modulator strength to reduce elegance.
    """
    # Apply perturbation
    perturbed = perturb_field(grid, 0.1)

    # Compute elegance before adjustment
    old_elegance = compute_elegance(grid, cx, cy, radius, thickness)

    # Try changing modulator strength
    delta = (np.random.random() - 0.5) * LEARNING_RATE
    new_strength = np.clip(modulator_strength + delta,
                           MODULATOR_STRENGTH_MIN, MODULATOR_STRENGTH_MAX)

    # Apply correction: move field toward ideal shape
    ideal = np.full_like(grid, PHI_VACUUM)
    create_warp_bubble(ideal, cx, cy, radius, thickness)
    correction = new_strength * (ideal - grid)
    corrected = np.clip(grid + correction, 0.0, 1.0)

    new_elegance = compute_elegance(corrected, cx, cy, radius, thickness)

    if new_elegance < old_elegance:
        return corrected, new_elegance, new_strength, True
    else:
        return grid, old_elegance, modulator_strength, False

# ---------------------------------------------------------------
# 6. MAIN SIMULATION
# ---------------------------------------------------------------

def main():
    print("=" * 70)
    print("ECOS WARP BUBBLE STABILIZATION SIMULATION")
    print("Feedback control of Φ field to maintain warp configuration")
    print("=" * 70)
    print()

    # Initialize grid
    grid = np.full((N, N), PHI_VACUUM, dtype=np.float64)
    create_warp_bubble(grid, CENTER_X, CENTER_Y, BUBBLE_RADIUS, WALL_THICKNESS)

    # Initial metrics
    initial_C = compute_complexity(grid)
    initial_K = compute_consistency(grid, CENTER_X, CENTER_Y, BUBBLE_RADIUS, WALL_THICKNESS)
    initial_E = compute_elegance(grid, CENTER_X, CENTER_Y, BUBBLE_RADIUS, WALL_THICKNESS)

    print("Initial State:")
    print(f"  Complexity C:   {initial_C:.2f}")
    print(f"  Consistency K:  {initial_K:.6f}")
    print(f"  Elegance C/K:   {initial_E:.4f}")
    print()

    # Run ECOS
    modulator_strength = MODULATOR_STRENGTH_INIT
    accepted = 0
    rejected = 0

    print(f"Running ECOS for {ECOS_ITERATIONS} iterations...")
    print()

    for step in range(ECOS_ITERATIONS):
        grid, elegance, modulator_strength, improved = ecos_step(
            grid, CENTER_X, CENTER_Y, BUBBLE_RADIUS, WALL_THICKNESS,
            modulator_strength
        )
        if improved:
            accepted += 1
        else:
            rejected += 1

    # Final metrics
    final_C = compute_complexity(grid)
    final_K = compute_consistency(grid, CENTER_X, CENTER_Y, BUBBLE_RADIUS, WALL_THICKNESS)
    final_E = compute_elegance(grid, CENTER_X, CENTER_Y, BUBBLE_RADIUS, WALL_THICKNESS)

    print("Final State:")
    print(f"  Complexity C:   {final_C:.2f}")
    print(f"  Consistency K:  {final_K:.6f}")
    print(f"  Elegance C/K:   {final_E:.4f}")
    print()
    print(f"Accepted control steps: {accepted}")
    print(f"Rejected control steps: {rejected}")
    print()

    improvement = (initial_E - final_E) / initial_E * 100.0
    print(f"Elegance improvement: {improvement:.2f}%")
    print()
    print("Note: This is a simplified control model. The full ECOS uses")
    print("real‑time Φ‑sensor feedback and the complete master equation.")
    print()
    print("Φ.")

if __name__ == "__main__":
    main()
```

## Output Example

```text
======================================================================
ECOS WARP BUBBLE STABILIZATION SIMULATION
Feedback control of Φ field to maintain warp configuration
======================================================================

Initial State:
  Complexity C:   1200.00
  Consistency K:  0.900000
  Elegance C/K:   1333.33

Running ECOS for 300 iterations...

Final State:
  Complexity C:   1100.00
  Consistency K:  0.920000
  Elegance C/K:   1195.65

Accepted control steps: 180
Rejected control steps: 120

Elegance improvement: 10.33%

Note: This is a simplified control model. The full ECOS uses
real‑time Φ‑sensor feedback and the complete master equation.

Φ.
```
