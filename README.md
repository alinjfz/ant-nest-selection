# Ant Nest Selection — Extended Robinson et al. (2011) Model

A Python simulation of collective nest-site decision-making in ant colonies, extending the threshold-based model from Robinson et al. (2011) with three biologically grounded mechanisms: **pheromone dynamics**, **memory**, and **capacity constraints**.

---

## Background

Ant colonies relocate to new nest sites through a decentralised process — no single ant directs the move. Each individual evaluates sites independently and signals its preference by laying pheromone trails. A quorum forms when enough ants commit to one site, triggering the colony to follow.

Robinson et al. (2011) formalised this with a simple threshold rule: an ant accepts a site when its perceived quality exceeds an internal threshold. This project extends that model to explore how pheromone feedback, individual memory, and physical nest capacity alter collective outcomes.

The species modelled is *Temnothorax albipennis*, a rock ant widely used in collective behaviour research.

---

## Model Extensions

### Pheromone Dynamics
Ants deposit pheromone when they accept a site (positive feedback), increasing its attractiveness for future recruits. When an ant moves to a lower-quality site, pheromone at the previous site is reduced (negative feedback). All pheromone levels decay exponentially at each time step, preventing long-term lock-in to suboptimal sites.

### Memory
Each ant maintains a rolling memory of the last *N* sites it has visited (default: 5). This models the empirically observed ability of *Temnothorax* ants to revisit known sites, which reduces oscillatory behaviour and improves decision accuracy.

### Capacity Constraints
Each candidate site has a fixed maximum occupancy. As a site fills up, its perceived quality degrades proportionally. Once at capacity, the site becomes effectively unavailable, redirecting further recruitment toward alternatives.

---

## Simulation Setup

| Parameter | Value |
|---|---|
| Ants | 200 |
| Time steps | 1 000 |
| Candidate sites | 3 (+ home) |
| Site qualities | −∞ (home), 4, 8, 6 |
| Site capacities | 0 (home), 50, 110, 350 |
| Pheromone decay rate | 0.001 |
| Memory span | 5 sites |
| Positive feedback | 1.0 |
| Negative feedback | 0.2 |

Ant thresholds are sampled from a normal distribution (mean = 5, σ = 1). Movement between sites follows a Markov process governed by a fixed transition probability matrix.

---

## Results

Pheromone dynamics significantly accelerated recruitment to the highest-quality site (quality = 8). Negative feedback prevented early overcommitment to the nearest but lower-quality site (quality = 4). Memory reduced oscillatory movement, with memory-equipped ants reaching a committed site ~22% faster on average. Capacity constraints produced a balanced colony distribution once the best site filled, echoing natural resource-partitioning behaviour.

---

## Installation

```bash
git clone https://github.com/your-username/ant-nest-selection.git
cd ant-nest-selection
pip install -r requirements.txt
```

## Usage

```bash
python simulation.py
```

The script runs the full simulation and opens four plots:

1. **Pheromone levels over time** — tracks positive and negative feedback dynamics across all sites.
2. **Sample ant paths** — visualises individual movement histories with memory retention.
3. **Nest map** — spatial layout of sites, scaled by quality and capacity.
4. **Summary panel** — final site distribution, decision times, mean discovery times, and mean visit counts (Robinson et al. style).

---

## File Structure

```
.
├── simulation.py                # Simulation logic, plotting, and entry point
├── PlotSummaryDataRobinson.py   # Four-panel summary plot (adapted from Robinson et al.)
├── requirements.txt
└── README.md
```

---

## References

1. Robinson, E.J.H., et al. *A Simple Threshold Rule Is Sufficient to Explain Sophisticated Collective Decision-Making.* PLOS ONE, 2011. 6(5): e19981.
2. Czaczkes, T.J. and Heinze, J. *Ants adjust their pheromone deposition to a changing environment.* Proceedings of the Royal Society B, 2015. 282(1810): 20150679.
3. Garnier, S., et al. *Do Ants Need to Estimate the Geometrical Properties of Trail Bifurcations to Find an Efficient Route?* PLOS Computational Biology, 2013. 9(3): e1002903.
4. Czaczkes, T., Grüter, C., and Ratnieks, F. *Negative feedback in ants: Crowding results in less trail pheromone deposition.* Journal of the Royal Society Interface, 2013. 10: 20121009.
5. Chang, J., et al. *Nest choice in arboreal ants is an emergent consequence of network creation under spatial constraints.* Swarm Intelligence, 2021. 15(1): 7–30.
