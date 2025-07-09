//  src/core/cxx_sim.cpp  -----------------------------------------------------
//  C++17 fast Monte-Carlo replica of the full WC-2026 format
//  (12×4 groups  ➜  32-team knock-out bracket)

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <random>
#include <vector>
#include <string>
#include <array>
#include <tuple>
#include <algorithm>
#include <numeric>
#include <unordered_map>

namespace py = pybind11;

// ---------- utilities -------------------------------------------------------
static const double KFACT[] = {1,1,2,6,24,120,720,5040,40320};
inline double pois(int k,double l){return std::pow(l,k)*std::exp(-l)/KFACT[k];}
static const double MU = std::log(1.35);  // baseline log-rate

struct MatchRes {int gf, ga;};
MatchRes sample_match(double sA,double sB,std::mt19937& g){
    double lamA = std::exp(MU + sA - sB);
    double lamB = std::exp(MU + sB - sA);
    std::discrete_distribution<> dA({
        pois(0,lamA),pois(1,lamA),pois(2,lamA),pois(3,lamA),
        pois(4,lamA),pois(5,lamA),pois(6,lamA),pois(7,lamA),pois(8,lamA)});
    std::discrete_distribution<> dB({
        pois(0,lamB),pois(1,lamB),pois(2,lamB),pois(3,lamB),
        pois(4,lamB),pois(5,lamB),pois(6,lamB),pois(7,lamB),pois(8,lamB)});
    return {dA(g), dB(g)};
}
double win_prob(double sA,double sB){
    double lamA = std::exp(MU + sA - sB);
    double lamB = std::exp(MU + sB - sA);
    double pA=0,pB=0,pD=0;
    for(int i=0;i<=8;++i){double pi=pois(i,lamA);
      for(int j=0;j<=8;++j){double pj=pois(j,lamB);
        if(i>j) pA+=pi*pj; else if(i<j) pB+=pi*pj; else pD+=pi*pj;}}
    return pA + .5*pD;         // penalties 50-50
}
// ---------- group stage -----------------------------------------------------
struct TeamStat{int id;int pts=0,gd=0,gf=0;};
// comparator *without* randomness -- we shuffle first to break ties randomly
bool rank_cmp(const TeamStat&a,const TeamStat&b){
    if(a.pts!=b.pts) return a.pts>b.pts;
    if(a.gd !=b.gd ) return a.gd >b.gd;
    if(a.gf !=b.gf ) return a.gf >b.gf;
    return a.id<b.id;         // arbitrary but deterministic
}
void play_group(const std::vector<double>& s,
                const std::array<int,4>& idx,
                std::vector<int>& top2,
                TeamStat& third,
                std::mt19937& rng)
{
    std::array<TeamStat,4> st;
    for(int k=0;k<4;++k){st[k].id=idx[k];}
    // six matches
    for(int a=0;a<4;++a)for(int b=a+1;b<4;++b){
        auto m = sample_match(s[idx[a]], s[idx[b]], rng);
        st[a].gf+=m.gf; st[a].gd+=m.gf-m.ga;
        st[b].gf+=m.ga; st[b].gd+=m.ga-m.gf;
        if   (m.gf>m.ga){st[a].pts+=3;}
        else if(m.gf<m.ga){st[b].pts+=3;}
        else{st[a].pts+=1; st[b].pts+=1;}
    }
    std::shuffle(st.begin(),st.end(),rng);        // random tie-break root
    std::stable_sort(st.begin(),st.end(), rank_cmp);
    top2.push_back(st[0].id);
    top2.push_back(st[1].id);
    third = st[2];                                // candidate for “best 3rd”
}
// ---------- knock-out bracket (32 teams) ------------------------------------
int play_knock(const std::vector<double>& s,
               std::vector<int> teams,
               std::mt19937& rng)
{
    while(teams.size()>1){
        std::vector<int> nxt;
        for(size_t i=0;i<teams.size();i+=2){
            double pA = win_prob(s[teams[i]], s[teams[i+1]]);
            nxt.push_back( std::generate_canonical<double,10>(rng)<pA ? teams[i]
                                                                     : teams[i+1] );
        }
        teams.swap(nxt);
    }
    return teams[0];
}
// ---------- main simulator ---------------------------------------------------
std::string simulate_tournament_once(const std::vector<double>& s,
                                     std::mt19937& rng)
{
    // assume len(teams)==48  (pass in exactly 48 lambdas/teams)
    std::array<int,48> id{};
    std::iota(id.begin(), id.end(), 0);
    std::shuffle(id.begin(), id.end(), rng); 
    // ---- group stage
    std::vector<int>  ko32;
    std::vector<TeamStat> thirds;
    for(int g=0; g<12; ++g){
        std::array<int,4> idx{ id[4*g], id[4*g+1], id[4*g+2], id[4*g+3] };
        TeamStat third;
        play_group(s, idx, ko32, third, rng);
        thirds.push_back(third);
    }
    // select best 8 thirds
    std::shuffle(thirds.begin(),thirds.end(),rng);
    std::stable_sort(thirds.begin(),thirds.end(), rank_cmp);
    for(int k=0;k<8;++k) ko32.push_back(thirds[k].id);

    // ---- fixed bracket (simple seed: ko32 order)
    return std::to_string( play_knock(s, ko32, rng) ); // returns id as string
}
// ---------- bulk Monte-Carlo wrapper ----------------------------------------
py::dict simulate_many(const std::vector<std::string>& teams,
                       const std::vector<double>&    strengths,
                       int                           n_runs = 20000,
                       unsigned                      seed   = 0)
{
    std::vector<int> wins(teams.size());
    std::mt19937 rng(seed);
    for(int r=0;r<n_runs;++r){
        int champ = std::stoi( simulate_tournament_once(strengths, rng) );
        ++wins[champ];
    }
    py::dict d;
    for(size_t i=0;i<teams.size();++i)
        d[py::str(teams[i])] = double(wins[i])/n_runs;
    return d;
}
// ----------------------------------------------------------------------------
/* … existing code … */

PYBIND11_MODULE(cxx_sim, m) {
    m.doc() = "C++17 fast Poisson helpers for world-cup-sim";

    // expose the single-match helper so Python can call it
    m.def("win_prob", &win_prob,
          py::arg("strength_a"), py::arg("strength_b"));

    // the naive tournament we tried before – you can keep it or drop it
    m.def("simulate_many", &simulate_many,
          py::arg("teams"), py::arg("strengths"),
          py::arg("n_runs") = 20'000, py::arg("seed") = 0U);
}

