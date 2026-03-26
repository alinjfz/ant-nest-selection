"""
Ant Nest Selection Simulation
==============================
Extended model based on Robinson et al. (2011), incorporating:
  - Pheromone dynamics (positive & negative feedback with exponential decay)
  - Memory mechanisms (ants retain the last N visited sites)
  - Capacity constraints (nests become unattractive once full)

Reference: Robinson et al. (2011) PLOS ONE 6(5): e19981
"""

import time

import matplotlib.pyplot as plt
import numpy as np

import PlotSummaryDataRobinson as psdr


# ---------------------------------------------------------------------------
# Core Simulation
# ---------------------------------------------------------------------------

def simulate_ants(
    n,
    quals,
    probs,
    threshold_mean,
    threshold_stddev,
    qual_stddev,
    time_means,
    time_stddevs,
    pheromone_decay_rate,
    memory_span,
    nest_capacities,
    positive_feedback_constant=2.0,
    negative_feedback_constant=0.3,
    steps=100,
):
    """
    Simulate ant nest-site selection with pheromone feedback, memory, and capacity constraints.

    Parameters
    ----------
    n : int
        Number of ants in the colony.
    quals : list
        Quality of each nest site. Use -inf for the home (starting) site.
    probs : np.ndarray
        Square transition probability matrix (sites x sites).
    threshold_mean : float
        Mean of the normal distribution used to sample individual ant thresholds.
    threshold_stddev : float
        Standard deviation of the threshold distribution.
    qual_stddev : list
        Per-site standard deviation for perceived quality sampling.
    time_means : np.ndarray
        Mean travel times between sites (sites x sites).
    time_stddevs : np.ndarray
        Standard deviations of travel times (sites x sites).
    pheromone_decay_rate : float
        Exponential decay constant applied to pheromone levels each step.
    memory_span : int
        Maximum number of recently visited sites an ant remembers.
    nest_capacities : list
        Maximum occupancy for each nest (0 means the site is never selected).
    positive_feedback_constant : float
        Pheromone boost when an ant accepts a site.
    negative_feedback_constant : float
        Pheromone penalty when an ant moves to a lower-quality site.
    steps : int
        Total number of simulation time steps.

    Returns
    -------
    pheromone_levels : np.ndarray
        Final pheromone levels at each site.
    ant_paths : list of list of int
        Sequence of sites visited by each ant.
    pheromone_history : list of np.ndarray
        Pheromone levels recorded at every time step.
    discovers : np.ndarray
        First discovery time of each site for each ant (sites x ants).
    visits : np.ndarray
        Total visit count for each site by each ant (sites x ants).
    """
    num_sites = len(quals)
    pheromone_levels = np.zeros(num_sites)
    pheromone_history = []
    nest_occupancy = np.zeros(num_sites)
    discovers = np.zeros((num_sites, n))
    visits = np.zeros((num_sites, n))

    np.random.seed(int(time.time()))

    ants = [
        {
            "threshold": np.random.normal(threshold_mean, threshold_stddev),
            "memory": [],
            "current_site": 1,
            "selected": False,
            "path": [],
        }
        for _ in range(n)
    ]

    for step in range(steps):
        for i, ant in enumerate(ants):
            ant["index"] = i

            if ant["selected"]:
                continue

            current_site = ant["current_site"]
            perceived_quality = np.random.normal(quals[current_site], qual_stddev[current_site])

            # Scale perceived quality by how full the nest currently is
            if nest_capacities[current_site] != 0:
                occupancy_factor = 1 - (nest_occupancy[current_site] / nest_capacities[current_site])
            else:
                occupancy_factor = 0

            perceived_quality *= max(occupancy_factor, 0)

            # Home site (site 0) is never accepted
            if current_site == 0:
                perceived_quality = -np.inf

            # Accept site if it clears the ant's threshold and still has space
            if (
                perceived_quality >= ant["threshold"]
                and nest_occupancy[current_site] < nest_capacities[current_site]
            ):
                ant["selected"] = True
                pheromone_levels[current_site] += positive_feedback_constant
                nest_occupancy[current_site] += 1
                ant["path"].append(current_site)
                continue

            # Update rolling memory (capped at memory_span)
            ant["memory"].append((current_site, perceived_quality))
            if len(ant["memory"]) > memory_span:
                ant["memory"].pop(0)

            # Record the step on which this site was first discovered
            if visits[current_site, i] == 0:
                discovers[current_site, i] = step

            visits[current_site, i] += 1

            # Probabilistic move — home site is excluded from choices
            next_site_probs = probs[:, current_site].copy()
            next_site_probs[0] = 0

            if next_site_probs.sum() == 0:
                next_site_probs = np.ones(num_sites) / num_sites
            else:
                next_site_probs /= next_site_probs.sum()

            next_site = np.random.choice(num_sites, p=next_site_probs)

            # Negative pheromone feedback when the ant moves to a worse site
            if quals[current_site] > quals[next_site]:
                pheromone_levels[current_site] = max(
                    pheromone_levels[current_site] - negative_feedback_constant, 0.01
                )

            ant["current_site"] = next_site
            ant["path"].append(current_site)

        # Exponential pheromone decay after every step
        pheromone_levels = np.maximum(pheromone_levels * (1 - pheromone_decay_rate), 0.01)
        pheromone_history.append(pheromone_levels.copy())

    return (
        pheromone_levels,
        [ant["path"] for ant in ants],
        pheromone_history,
        discovers,
        visits,
    )


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

SITE_COLORS = ["#f50537", "#00aeef", "#2a5934", "#ffb900"]


def plot_results(pheromone_history, ant_paths, nest_positions, nest_qualities, nest_capacities):
    """Generate and display all simulation result plots."""
    pheromone_history = np.array(pheromone_history)
    num_sites = len(nest_positions)
    colors = (SITE_COLORS * ((num_sites // len(SITE_COLORS)) + 1))[:num_sites]

    # Pheromone levels over time
    fig, ax = plt.subplots(figsize=(9, 6))
    for site in range(num_sites):
        ax.plot(pheromone_history[:, site], label=f"Site {site}", color=colors[site])
    ax.set_title("Pheromone Levels Over Time (With Decay)")
    ax.set_xlabel("Time Step")
    ax.set_ylabel("Pheromone Level")
    ax.legend()
    plt.tight_layout()
    plt.show()

    print(f"Positive feedback led to a max pheromone level of {pheromone_history.max():.2f}.")
    print(f"Negative feedback reduced pheromone level to a min of {pheromone_history.min():.2f}.")

    # Sample ant paths and nest spatial map
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))

    for path in [p for p in ant_paths[8:12] if p]:
        axes[0].plot(range(len(path)), path, marker="o", alpha=0.5)
    axes[0].set_title("Sample Ant Paths with Memory Retention")
    axes[0].set_xlabel("Step")
    axes[0].set_ylabel("Site")
    axes[0].set_yticks(range(num_sites))

    for i, (pos, qual, cap) in enumerate(zip(nest_positions, nest_qualities, nest_capacities)):
        axes[1].scatter(
            pos[0], pos[1],
            s=cap + 100,
            label=f"Nest {i}: Qual={qual}, Cap={cap}",
            alpha=0.8,
        )
    axes[1].set_title("Nest Positions, Qualities, and Capacities")
    axes[1].set_xlabel("X Coordinate")
    axes[1].set_ylabel("Y Coordinate")
    axes[1].legend()
    axes[1].grid(True)
    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------------------------
# Simulation Parameters
# ---------------------------------------------------------------------------

N_ANTS = 200

# Nest 0 = home site (never selected); Nests 1–3 are candidate sites
NEST_QUALITIES = [-np.inf, 4, 8, 6]
NEST_CAPACITIES = [0, 50, 110, 350]
NEST_POSITIONS = [(0, 0), (30, 0), (0, 30), (26, 28)]

# Row i, column j: probability of moving from site j to site i
TRANSITION_PROBS = np.array([
    [0.7, 0.1, 0.1, 0.1],
    [0.1, 0.6, 0.2, 0.1],
    [0.1, 0.2, 0.6, 0.1],
    [0.1, 0.1, 0.2, 0.6],
])

TRAVEL_TIME_MEANS = np.array([
    [ 1, 30, 30, 50],
    [30,  1, 25, 25],
    [30, 25,  1, 40],
    [50, 25, 40,  1],
])
TRAVEL_TIME_STDDEVS = TRAVEL_TIME_MEANS / 4

QUALITY_STDDEV    = [1, 1, 1, 1]
THRESHOLD_MEAN    = 5
THRESHOLD_STDDEV  = 1
MEMORY_SPAN       = 5
PHEROMONE_DECAY   = 0.001   # Slow decay promotes exploration without locking in early
POSITIVE_FEEDBACK = 1
NEGATIVE_FEEDBACK = 0.2
STEPS             = 1000


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pheromone_levels, ant_paths, pheromone_history, discovers, visits = simulate_ants(
        n=N_ANTS,
        quals=NEST_QUALITIES,
        probs=TRANSITION_PROBS,
        threshold_mean=THRESHOLD_MEAN,
        threshold_stddev=THRESHOLD_STDDEV,
        qual_stddev=QUALITY_STDDEV,
        time_means=TRAVEL_TIME_MEANS,
        time_stddevs=TRAVEL_TIME_STDDEVS,
        pheromone_decay_rate=PHEROMONE_DECAY,
        memory_span=MEMORY_SPAN,
        nest_capacities=NEST_CAPACITIES,
        positive_feedback_constant=POSITIVE_FEEDBACK,
        negative_feedback_constant=NEGATIVE_FEEDBACK,
        steps=STEPS,
    )

    plot_results(pheromone_history, ant_paths, NEST_POSITIONS, NEST_QUALITIES, NEST_CAPACITIES)

    current_time  = max(len(path) for path in ant_paths)
    accepts       = [path[-1] if path else -1 for path in ant_paths]
    ants_summary  = [{"path": path, "selected": len(path) > 0} for path in ant_paths]

    psdr.PlotSummaryDataRobinson(current_time, accepts, discovers, visits, ants_summary)
