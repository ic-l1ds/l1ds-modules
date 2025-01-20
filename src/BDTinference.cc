#include "L1DS/Modules/interface/BDTinference.h"

BDTinference::BDTinference (std::string filename, bool use_sigmoid) {
    XGBoosterCreate(NULL, 0, &booster_);
    XGBoosterLoadModel(booster_, filename.c_str()); // second argument should be a const char *.
    use_sigmoid_ = use_sigmoid;
    //bst_ulong out_len;
    //const char **out_dump_array;
    //XGBoosterDumpModel(booster_, "", 0, &out_len, &out_dump_array);
    ////std::cout << "Dumping" << std::endl;
    //FILE *file = fopen("filename", "w");
    //for (int i=0; i < (int) out_len; i++)
        //fputs(out_dump_array[i], file);
    //fclose(file);
}

// Destructor
BDTinference::~BDTinference() {}

std::vector<float> BDTinference::get_bdt_outputs (std::vector<float> inputs) {

    float values[1][inputs.size()];
    int ivar=0;

    for(auto& var : inputs)
    {
        // std::cout << var << std::endl;
        values[0][ivar] = var;
        ++ivar;
    }
    DMatrixHandle dvalues;
    XGDMatrixCreateFromMat(reinterpret_cast<float*>(values), 1, inputs.size(), -9999., &dvalues);

    // Dimension of output prediction
    bst_ulong out_dim;

    float const* out_result = NULL;

    auto ret = XGBoosterPredict(
        booster_, dvalues, 0, 0, 0, &out_dim, &out_result);

    XGDMatrixFree(dvalues);

    std::vector<float> results;
    if(ret==0)
    {
        for(unsigned int ic=0; ic < out_dim; ++ic) {
            //std::cout << "Score: " << out_result[ic] << std::endl;
            if (!use_sigmoid_)
                results.push_back(out_result[ic]);
            else
                results.push_back(sigmoid(out_result[ic]));
        }
    }

    return results;
}