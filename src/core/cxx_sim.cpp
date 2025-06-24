// minimal, self-contained Monte-Carlo core -------------------------------
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <random>
#include <unordered_map>
#include <vector>
#include <string>

namespace py  = pybind11;

// simple Poisson pmf (λ^k e^-λ / k!) for k ≤ 8 – inline table of factorials
static const double KFACT[] = {1, 1, 2, 6, 24, 120, 720, 5040, 40320};

inline double poisson_pmf(int k, double lambda) {
    return std::pow(lambda, k) * std::exp(-lambda) / KFACT[k];
}

// probability that team A beats team B in a single match
double win_prob(double lamA, double lamB) {
    double pA = 0.0, pB = 0.0, pDraw = 0.0;
    for (int i = 0; i <= 8; ++i) {
        double pi = poisson_pmf(i, lamA);
        for (int j = 0; j <= 8; ++j) {
            double pj = poisson_pmf(j, lamB);
            if (i > j)       pA    += pi * pj;
            else if (i < j)  pB    += pi * pj;
            else             pDraw += pi * pj;
        }
    }
    // FIFA knock-outs decide draws with penalties ⇒ add half draw prob
    return pA + 0.5 * pDraw;
}

// ------------------------------------------------------------------------
py::str simulate_once(const std::vector<std::string>& teams,
                      const std::vector<double>&    lambdas,
                      std::mt19937&                 rng)
{
    // round-robin strength: λ = base * strength
    std::uniform_int_distribution<> pick(0, static_cast<int>(teams.size() - 1));

    // naive “draw”: pick two distinct teams until one wins
    while (true) {
        int ia = pick(rng), ib = pick(rng);
        if (ia == ib) continue;
        double pA = win_prob(lambdas[ia], lambdas[ib]);
        if (std::generate_canonical<double, 10>(rng) < pA)
            return py::str(teams[ia]);
        else
            return py::str(teams[ib]);
    }
}

// exposed bulk Monte-Carlo ------------------------------------------------
py::dict simulate_many(const std::vector<std::string>& teams,
                       const std::vector<double>&    lambdas,
                       int                           n_runs,
                       unsigned                      seed)
{
    std::unordered_map<std::string, int> win_count;
    for (const auto& t : teams) win_count[t] = 0;

    std::mt19937 rng(seed);
    for (int r = 0; r < n_runs; ++r) {
        py::str champ = simulate_once(teams, lambdas, rng);
        ++win_count[champ];
    }

    py::dict out;
    for (const auto& kv : win_count)
        out[kv.first.c_str()] = static_cast<double>(kv.second) / n_runs;
    return out;
}

PYBIND11_MODULE(cxx_sim, m) {
    m.doc() = "C++17 fast Monte-Carlo core for world-cup-sim";
    m.def("simulate_many", &simulate_many,
          py::arg("teams"), py::arg("lambdas"),
          py::arg("n_runs") = 20000, py::arg("seed") = 0U);
}
