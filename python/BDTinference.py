import os

from analysis_tools.utils import import_root, randomize
from Base.Modules.baseModules import JetLepMetSyst

ROOT = import_root()

class L1DSBDTProducer(JetLepMetSyst):
    def __init__(self, *args, **kwargs):
        default_name = "bdt_l1ds"
        use_sigmoid = "false"
        #default_model_path = os.path.expandvars("$CMSSW_BASE/src/L1DS/Modules/data/XGB.json")

        # Regularisation to various degrees (note: these need sigmoid)
        default_model_path = os.path.expandvars("$CMSSW_BASE/src/L1DS/Modules/data/ICEBOOST_MI_0p1.json")
        #default_model_path = os.path.expandvars("$CMSSW_BASE/src/L1DS/Modules/data/ICEBOOST_MI_0p5.json")
        #default_model_path = os.path.expandvars("$CMSSW_BASE/src/L1DS/Modules/data/ICEBOOST_MI_1p0.json")

        if "MI" in default_model_path:
            use_sigmoid = "true"

        self.model_path = kwargs.pop("model_path", default_model_path)
        self.model = self.model_path.replace("/", "_").replace(".", "_")
        self.bdt_name = kwargs.pop("bdt_name", default_name)

        super(L1DSBDTProducer, self).__init__(*args, **kwargs)

        base = "{}/{}/src/L1DS/Modules".format(
            os.getenv("CMT_CMSSW_BASE"), os.getenv("CMT_CMSSW_VERSION"))

        if not os.getenv("_L1DSBDT"):
            os.environ["_L1DSBDT"] = "_L1DSBDT"

            ROOT.gSystem.Load("libL1DSModules.so")
            ROOT.gROOT.ProcessLine(".L {}/interface/BDTinference.h".format(base))

        if not os.getenv("_L1DSBDT_%s"%self.model):
            os.environ["_L1DSBDT_%s"%self.model] = "_L1DSBDT_%s"%self.model

            ROOT.gInterpreter.Declare("""
                auto bdt%s = BDTinference("%s", %s);
            """ % (self.model, self.model_path, use_sigmoid))

            ROOT.gInterpreter.Declare("""
                using Vfloat = ROOT::RVec<float>;
                std::vector<float> get_bdt_outputs_%s(
                    int nJet, float dijet_pt, float dijet_dphi, Vfloat Jet_eta, Vfloat Jet_phi, Vfloat Jet_scaled_pt, Vfloat Jet_pt){
                    std::vector<jet_t> jets(std::max(4, nJet), jet_t());
                    for(int i = 0; i < nJet; i++){
                        jets[i] = jet_t({Jet_pt[i], Jet_eta[i], Jet_phi[i], Jet_scaled_pt[i]});
                    }
                    //No need for sorting, the jets are already sorted in descending pT

                    return bdt%s.get_bdt_outputs(
                        {(float) nJet, dijet_pt, dijet_dphi, 
                        jets[0].eta, jets[1].eta, jets[2].eta, jets[3].eta,
                        jets[0].phi, jets[1].phi, jets[2].phi, jets[3].phi,
                        jets[0].scaled_pt, jets[1].scaled_pt, jets[2].scaled_pt, jets[3].scaled_pt}
                    );
                }
            """ % (self.model, self.model))
    
    def run(self, df):
        s = randomize("bdt")

        df = df.Define(s, f"""get_bdt_outputs_{self.model}(
            nJet, dijet_pt, dijet_dphi, Jet_eta, Jet_phi, Jet_scaled_pt, Jet_pt)
        """
        )

        p = [self.bdt_name]
        p = [str(param).replace(".", "p") for param in p]

        b_name = (f"{p[0]}{self.systs}")
        df = df.Define(b_name, " %s.at(0)" % s)

        return df, [b_name]

def L1DSBDT(*args, **kwargs):
    return lambda: L1DSBDTProducer(*args, **kwargs)
