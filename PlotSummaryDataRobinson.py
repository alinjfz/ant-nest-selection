"""
PlotSummaryDataRobinson
========================
Adapted from the plotting utilities in Robinson et al. (2011) — PLOS ONE 6(5): e19981.

Generates a four-panel summary figure showing:
  1. Distribution of final nest choices across the colony.
  2. Time-to-decision distribution (how long each ant took to commit).
  3. Mean first-discovery time per site.
  4. Mean number of visits per site.
"""

import matplotlib.pyplot as plt
import numpy as np


def PlotSummaryDataRobinson(current_time, accepts, discovers, visits, Ants):
    """
    Plot a four-panel summary of one simulation run.

    Parameters
    ----------
    current_time : int
        The maximum time step reached in the simulation.
    accepts : list of int
        Final nest site chosen by each ant (-1 if the ant never committed).
    discovers : np.ndarray, shape (num_sites, n_ants)
        Step at which each ant first visited each site (0 means never visited).
    visits : np.ndarray, shape (num_sites, n_ants)
        Total number of times each ant visited each site.
    Ants : list of dict
        Ant state dicts — each must contain ``path`` (list of ints) and
        ``selected`` (bool).
    """
    num_sites = discovers.shape[0]

    decision_times = [len(ant["path"]) for ant in Ants if ant["selected"]]

    # Mean discovery time per site, ignoring sites never visited (stored as 0)
    mean_discovery = [
        np.mean(discovers[s, discovers[s] > 0]) if np.any(discovers[s] > 0) else 0
        for s in range(num_sites)
    ]

    mean_visits = [np.mean(visits[s]) for s in range(num_sites)]

    site_labels = [f"Site {i}" for i in range(num_sites)]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "Simulation Summary — Robinson et al. (2011) Extended Model",
        fontsize=14,
        fontweight="bold",
    )

    ax1, ax2, ax3, ax4 = axes.flatten()

    # Panel 1 — final site distribution
    # Bin edges extended to four sites (0–3) to accommodate the expanded model
    ax1.hist(accepts, bins=[-0.5, 0.5, 1.5, 2.5, 3.5], edgecolor="black", color="#00aeef")
    ax1.set_title("Final Site Distribution")
    ax1.set_xlabel("Final Site")
    ax1.set_ylabel("Number of Ants")
    ax1.set_xticks(range(num_sites))
    ax1.set_xticklabels(site_labels)

    # Panel 2 — time-to-decision histogram
    ax2.hist(decision_times, bins=20, edgecolor="black", color="#2a5934")
    ax2.set_title("Time Till Final Decision")
    ax2.set_xlabel("Decision Time (steps)")
    ax2.set_ylabel("Number of Ants")

    # Panel 3 — mean discovery time per site
    ax3.bar(range(num_sites), mean_discovery, edgecolor="black", color="#ffb900")
    ax3.set_title("Mean Discovery Time per Site")
    ax3.set_xlabel("Site")
    ax3.set_ylabel("Mean Time Step")
    ax3.set_xticks(range(num_sites))
    ax3.set_xticklabels(site_labels)

    # Panel 4 — mean number of visits per site
    ax4.bar(range(num_sites), mean_visits, edgecolor="black", color="#f50537")
    ax4.set_title("Mean Number of Visits per Site")
    ax4.set_xlabel("Site")
    ax4.set_ylabel("Mean Visits")
    ax4.set_xticks(range(num_sites))
    ax4.set_xticklabels(site_labels)

    plt.tight_layout()
    plt.show()
