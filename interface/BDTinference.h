#ifndef bdtinference_h
#define bdtinference_h

// Standard libraries
#include <vector>
#include <string>
#include <cmath>
#include <iostream>

#include <xgboost/c_api.h> 

float sigmoid (float x) {
  return (1. / (1 + std::exp(-1. * x)));
}

struct jet_t{
    float pt = -999.;
    float eta = -999.;
    float phi = -999.;
    float scaled_pt = -999.;
};

bool jet_sort(const jet_t &a, const jet_t &b) {
    return (a.pt > b.pt);
}

class BDTinference {
    public:
        BDTinference ();
        BDTinference (std::string filename, bool use_sigmoid);
        ~BDTinference ();
        std::vector<float> get_bdt_outputs(std::vector<float> inputs);

    private:
        BoosterHandle booster_;
        bool use_sigmoid_;
};

#endif