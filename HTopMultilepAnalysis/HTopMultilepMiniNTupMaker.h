/**
 * @file   HTopMultilepMiniNTupMaker.h
 * @author Marco Milesi <marco.milesi@cern.ch>
 * @brief  EventLoop algorithm to skim/slim/augment HTop group ntuples
 *
 */

#ifndef HTopMultilepAnalysis_HTopMultilepMiniNTupMaker_H
#define HTopMultilepAnalysis_HTopMultilepMiniNTupMaker_H

// algorithm wrapper
#include "xAODAnaHelpers/Algorithm.h"

// EL include(s):
#include <EventLoopAlgs/NTupleSvc.h>
#include <EventLoopAlgs/AlgSelect.h>
#include <EventLoop/Worker.h>
#include <EventLoop/Algorithm.h>
#include <EventLoop/Job.h>
#include <EventLoop/OutputStream.h>

// ROOT include(s):
#include "TTree.h"
#include "TFile.h"
#include "TH1F.h"
#include "TRandom3.h"

namespace MiniNTupMaker {

  struct Branch_Types {
      float f;
      char c;
      int i;
      std::vector<float> vec_f;
      std::vector<char> vec_c;
      std::vector<int> vec_i;
  };

  class eventObj {

  public:
    eventObj():
      isSS01(0), isSS12(0),
      dilep(0), trilep(0),
      dilep_type(0),
      nbjets(0),
      isBadTPEvent_SLT(1), /** Be pesimistic */
      weight_event(1.0),
      weight_event_trig_SLT(1.0),
      weight_event_lep(1.0),
      weight_lep_tag(1.0),weight_lep_probe(1.0),
      weight_trig_tag(1.0),weight_trig_probe(1.0)
    { };

    char isSS01;
    char isSS12;
    char dilep;
    char trilep;
    int  dilep_type;
    int  nbjets;

    char isBadTPEvent_SLT; /** No T&TM (SLT) leptons found */

    float weight_event;
    float weight_event_trig_SLT;
    float weight_event_lep;

    float weight_lep_tag;
    float weight_lep_probe;
    float weight_trig_tag;
    float weight_trig_probe;

  };

  class bjetObj {
  public:
    bjetObj():
      pt(-1.0),eta(-999.0),phi(-999.0)
      { };

      float pt;
      float eta;
      float phi;
  };

  class leptonObj {

  public:
    leptonObj():
      pt(-1.0),eta(-999.0),etaBE2(-999.0),phi(-999.0),ID(0.0),flavour(0),charge(-999.0),d0sig(-999.0),z0sintheta(-999.0),
      pid(0),isolated(0),trackisooverpt(-1.0),caloisooverpt(-1.0),
      ptVarcone20(-1.0),ptVarcone30(-1.0),topoEtcone20(-1.0),
      tight(0),
      trigmatched(0),trigmatched_SLT(0),trigmatched_DLT(0),
      prompt(0),fake(0),brems(0),qmisid(0),convph(0),
      truthType(0),truthOrigin(0),
      tag_SLT(0),tag_DLT(0),
      deltaRClosestBJet(-1.0),massClosestBJet(-1.0),
      SFIDLoose(1.0),
      SFIDTight(1.0),
      SFTrigLoose(1.0),
      SFTrigTight(1.0),
      EffTrigLoose(0.0),
      EffTrigTight(0.0),
      SFIsoLoose(1.0),
      SFIsoTight(1.0),
      SFReco(1.0),
      SFTTVA(1.0),
      SFObjLoose(1.0),
      SFObjTight(1.0)
    { };

    float pt;
    float eta;
    float etaBE2;
    float phi;
    int ID;
    int flavour;
    float charge;
    float d0sig;
    float z0sintheta;
    char pid;
    char isolated;
    float trackisooverpt;
    float caloisooverpt;
    float ptVarcone20;
    float ptVarcone30;
    float topoEtcone20;
    char tight;
    char trigmatched;
    char trigmatched_SLT;
    char trigmatched_DLT;
    char prompt;
    char fake;
    char brems;
    char qmisid;
    char convph;
    int  truthType;
    int  truthOrigin;
    char tag_SLT;
    char tag_DLT;
    float deltaRClosestBJet;
    float massClosestBJet;

    float SFIDLoose;
    float SFIDTight;
    float SFTrigLoose;
    float SFTrigTight;
    float EffTrigLoose;
    float EffTrigTight;
    float SFIsoLoose;
    float SFIsoTight;
    float SFReco;
    float SFTTVA;
    float SFObjLoose;
    float SFObjTight;

  };

  struct SorterEta {
    bool operator() ( const std::shared_ptr<leptonObj>& lep0, const std::shared_ptr<leptonObj>& lep1 ) const {
       return  fabs(lep0.get()->eta) > fabs(lep1.get()->eta); /* sort in descending order of |eta| */
    }
  };

  struct SorterPt {
    bool operator() ( const std::shared_ptr<leptonObj>& lep0, const std::shared_ptr<leptonObj>& lep1 ) const {
       return  lep0.get()->pt > lep1.get()->pt; /* sort in descending order of pT (get highest pT first) */
    }
  };

  struct SorterTrackIsoOverPt {
    bool operator() ( const std::shared_ptr<leptonObj>& lep0, const std::shared_ptr<leptonObj>& lep1 ) const {
       if ( lep0.get()->trackisooverpt == lep1.get()->trackisooverpt ) { /* if they have same iso (aka 0 ), use pT as criterion */
         return lep0.get()->pt > lep1.get()->pt;
       }
       return  lep0.get()->trackisooverpt < lep1.get()->trackisooverpt; /* sort in ascending order of trackisooverpt (get more isolated first) */
    }
  };

  struct SorterDistanceClosestBJet {
    bool operator() ( const std::shared_ptr<leptonObj>& lep0, const std::shared_ptr<leptonObj>& lep1 ) const {
       return  lep0.get()->deltaRClosestBJet > lep1.get()->deltaRClosestBJet; /* sort in descending order of DeltaR(lep, closest bjet) (get lep w/ maximal distance first) */
    }
  };

  struct SorterMassClosestBJet {
    bool operator() ( const std::shared_ptr<leptonObj>& lep0, const std::shared_ptr<leptonObj>& lep1 ) const {
       return  lep0.get()->massClosestBJet > lep1.get()->massClosestBJet; /* sort in descending order of M(lep, closest bjet) (get lep w/ maximal mass w/ closest bjet first --> assume it's less likely to be fake) */
    }
  };

}



class HTopMultilepMiniNTupMaker : public xAH::Algorithm
{
  // put your configuration variables here as public variables.
  // that way they can be set directly from CINT and python.
public:

  /** The name of the output TTree */
  std::string m_outputNTupName;

  std::string m_outputNTupStreamName;

  /** A comma-separated list of input branches to be activated */
  std::string m_inputBranches;

  /** Perform event skimming through an EL::AlgSelect svc, or do it manually */
  bool         m_useAlgSelect;

  /** Add an output stream (aka, directory) for the histogram containing the total number of generated raw/weighted events */
  bool         m_addStreamEventsHist;

  /** Activate if want to define T&P leptons based on truth matching (NB: do this only on TTBar!)  */
  bool m_useTruthTP;

  /** Activate if want to define T&P leptons as in SUSY SS analysis (different treatment of ambiguous case where both leptons are T & T.M.  */
  bool m_useSUSYSSTP;

  /** Choose which criterion to use to solve ambiguous case of both T (TM) leptons in T&P Fake SS CR */
  std::string m_ambiSolvingCrit;

private:

  /** Input TTree */

  TTree*          m_inputNTuple;

  /** Input TTree with the sum of weights */

  TTree*          m_sumWeightsTree;

  /** Histogram containing the total number of generated raw/weighted events */

  TH1F*           m_sumGenEventsHist;

  /** Output TTree (svc) */

  EL::NTupleSvc*  m_outputNTuple;

  /** Input TTree branches which need to be used by the algorithm */

  ULong64_t       m_EventNumber;
  UInt_t          m_RunNumber;
  Int_t           m_RunYear;
  Bool_t          m_passEventCleaning;
  UInt_t          m_mc_channel_number; /** for DATA, mc_channel_number=0 */

  Double_t        m_mcWeightOrg;
  Double_t	  m_pileupEventWeight_090;
  Double_t	  m_MV2c10_70_EventWeight;
  Double_t	  m_JVT_EventWeight;

  Int_t 	  m_dilep_type;
  Int_t 	  m_trilep_type;

  Int_t           m_nJets_OR;
  Int_t           m_nJets_OR_MV2c10_70;
  Int_t           m_nJets_OR_T;
  Int_t           m_nJets_OR_T_MV2c10_70;

  Float_t	  m_lep_ID_0;
  Float_t	  m_lep_Pt_0;
  Float_t	  m_lep_E_0;
  Float_t	  m_lep_Eta_0;
  Float_t	  m_lep_Phi_0;
  Float_t	  m_lep_EtaBE2_0;
  Float_t	  m_lep_sigd0PV_0;
  Float_t	  m_lep_Z0SinTheta_0;
  Char_t	  m_lep_isTightLH_0;
  Char_t	  m_lep_isMediumLH_0;
  Char_t	  m_lep_isLooseLH_0;
  Char_t	  m_lep_isTight_0;
  Char_t	  m_lep_isMedium_0;
  Char_t	  m_lep_isLoose_0;
  Int_t 	  m_lep_isolationLooseTrackOnly_0;
  Int_t 	  m_lep_isolationLoose_0;
  Int_t 	  m_lep_isolationFixedCutTight_0;
  Int_t 	  m_lep_isolationFixedCutTightTrackOnly_0;
  Int_t 	  m_lep_isolationFixedCutLoose_0;
  Float_t	  m_lep_topoEtcone20_0;
  Float_t	  m_lep_ptVarcone20_0;
  Float_t	  m_lep_ptVarcone30_0;
  Char_t	  m_lep_isTrigMatch_0;
  Char_t	  m_lep_isTrigMatchDLT_0;
  Char_t	  m_lep_isPrompt_0;
  Char_t	  m_lep_isBrems_0;
  Char_t	  m_lep_isFakeLep_0;
  Char_t	  m_lep_isQMisID_0;
  Char_t	  m_lep_isConvPh_0;
  Int_t	          m_lep_truthType_0;
  Int_t	          m_lep_truthOrigin_0;
  Float_t	  m_lep_SFIDLoose_0;
  Float_t	  m_lep_SFIDTight_0;
  Float_t	  m_lep_SFTrigLoose_0;
  Float_t	  m_lep_SFTrigTight_0;
  Float_t         m_lep_EffTrigLoose_0;
  Float_t         m_lep_EffTrigTight_0;
  Float_t	  m_lep_SFIsoLoose_0;
  Float_t	  m_lep_SFIsoTight_0;
  Float_t	  m_lep_SFReco_0;
  Float_t	  m_lep_SFTTVA_0;
  Float_t	  m_lep_SFObjLoose_0;
  Float_t	  m_lep_SFObjTight_0;

  Float_t	  m_lep_ID_1;
  Float_t	  m_lep_Pt_1;
  Float_t	  m_lep_E_1;
  Float_t	  m_lep_Eta_1;
  Float_t	  m_lep_Phi_1;
  Float_t	  m_lep_EtaBE2_1;
  Float_t	  m_lep_sigd0PV_1;
  Float_t	  m_lep_Z0SinTheta_1;
  Char_t	  m_lep_isTightLH_1;
  Char_t	  m_lep_isMediumLH_1;
  Char_t	  m_lep_isLooseLH_1;
  Char_t	  m_lep_isTight_1;
  Char_t	  m_lep_isMedium_1;
  Char_t	  m_lep_isLoose_1;
  Int_t 	  m_lep_isolationLooseTrackOnly_1;
  Int_t 	  m_lep_isolationLoose_1;
  Int_t 	  m_lep_isolationFixedCutTight_1;
  Int_t 	  m_lep_isolationFixedCutTightTrackOnly_1;
  Int_t 	  m_lep_isolationFixedCutLoose_1;
  Float_t	  m_lep_topoEtcone20_1;
  Float_t	  m_lep_ptVarcone20_1;
  Float_t	  m_lep_ptVarcone30_1;
  Char_t	  m_lep_isTrigMatch_1;
  Char_t	  m_lep_isTrigMatchDLT_1;
  Char_t	  m_lep_isPrompt_1;
  Char_t	  m_lep_isBrems_1;
  Char_t	  m_lep_isFakeLep_1;
  Char_t	  m_lep_isQMisID_1;
  Char_t	  m_lep_isConvPh_1;
  Int_t	          m_lep_truthType_1;
  Int_t	          m_lep_truthOrigin_1;
  Float_t	  m_lep_SFIDLoose_1;
  Float_t	  m_lep_SFIDTight_1;
  Float_t	  m_lep_SFTrigLoose_1;
  Float_t	  m_lep_SFTrigTight_1;
  Float_t         m_lep_EffTrigLoose_1;
  Float_t         m_lep_EffTrigTight_1;
  Float_t	  m_lep_SFIsoLoose_1;
  Float_t	  m_lep_SFIsoTight_1;
  Float_t	  m_lep_SFReco_1;
  Float_t	  m_lep_SFTTVA_1;
  Float_t	  m_lep_SFObjLoose_1;
  Float_t	  m_lep_SFObjTight_1;

  Float_t	  m_lep_ID_2;
  Float_t	  m_lep_Pt_2;
  Float_t	  m_lep_E_2;
  Float_t	  m_lep_Eta_2;
  Float_t	  m_lep_Phi_2;
  Float_t	  m_lep_EtaBE2_2;
  Float_t	  m_lep_sigd0PV_2;
  Float_t	  m_lep_Z0SinTheta_2;
  Char_t	  m_lep_isTightLH_2;
  Char_t	  m_lep_isMediumLH_2;
  Char_t	  m_lep_isLooseLH_2;
  Char_t	  m_lep_isTight_2;
  Char_t	  m_lep_isMedium_2;
  Char_t	  m_lep_isLoose_2;
  Int_t 	  m_lep_isolationLooseTrackOnly_2;
  Int_t 	  m_lep_isolationLoose_2;
  Int_t 	  m_lep_isolationFixedCutTight_2;
  Int_t 	  m_lep_isolationFixedCutTightTrackOnly_2;
  Int_t 	  m_lep_isolationFixedCutLoose_2;
  Float_t	  m_lep_topoEtcone20_2;
  Float_t	  m_lep_ptVarcone20_2;
  Float_t	  m_lep_ptVarcone30_2;
  Char_t	  m_lep_isTrigMatch_2;
  Char_t	  m_lep_isTrigMatchDLT_2;
  Char_t	  m_lep_isPrompt_2;
  Char_t	  m_lep_isBrems_2;
  Char_t	  m_lep_isFakeLep_2;
  Char_t	  m_lep_isQMisID_2;
  Char_t	  m_lep_isConvPh_2;
  Int_t	          m_lep_truthType_2;
  Int_t	          m_lep_truthOrigin_2;
  Float_t	  m_lep_SFIDLoose_2;
  Float_t	  m_lep_SFIDTight_2;
  Float_t	  m_lep_SFTrigLoose_2;
  Float_t	  m_lep_SFTrigTight_2;
  Float_t         m_lep_EffTrigLoose_2;
  Float_t         m_lep_EffTrigTight_2;
  Float_t	  m_lep_SFIsoLoose_2;
  Float_t	  m_lep_SFIsoTight_2;
  Float_t	  m_lep_SFReco_2;
  Float_t	  m_lep_SFTTVA_2;
  Float_t	  m_lep_SFObjLoose_2;
  Float_t	  m_lep_SFObjTight_2;

  ULong64_t       m_totalEvents;
  Float_t         m_totalEventsWeighted;

  /** Trigger match decision per-lepton (for each chain) - BEFORE overlap removal! */

  // 2015

  std::vector<int> *m_electron_match_HLT_e24_lhmedium_L1EM20VH        = nullptr; //!
  std::vector<int> *m_electron_match_HLT_e60_lhmedium                 = nullptr; //!
  std::vector<int> *m_electron_match_HLT_e120_lhloose                 = nullptr; //!
  std::vector<int> *m_electron_match_HLT_2e12_lhloose_L12EM10VH       = nullptr; //!
  std::vector<int> *m_electron_match_HLT_e24_medium_L1EM20VHI_mu8noL1 = nullptr; //!
  std::vector<int> *m_electron_match_HLT_e7_medium_mu24               = nullptr; //!
  std::vector<int> *m_muon_match_HLT_mu20_iloose_L1MU15               = nullptr; //!
  std::vector<int> *m_muon_match_HLT_mu18_mu8noL1                     = nullptr; //!
  std::vector<int> *m_muon_match_HLT_e24_medium_L1EM20VHI_mu8noL1     = nullptr; //!
  std::vector<int> *m_muon_match_HLT_e7_medium_mu24                   = nullptr; //!

  // 2016

  std::vector<int> *m_electron_match_HLT_e26_lhtight_nod0_ivarloose = nullptr; //!
  std::vector<int> *m_electron_match_HLT_e60_lhmedium_nod0          = nullptr; //!
  std::vector<int> *m_electron_match_HLT_e140_lhloose_nod0          = nullptr; //!
  std::vector<int> *m_electron_match_HLT_2e17_lhvloose_nod0         = nullptr; //!
  std::vector<int> *m_electron_match_HLT_e17_lhloose_mu14           = nullptr; //!
  std::vector<int> *m_electron_match_HLT_e17_lhloose_nod0_mu14      = nullptr; //!
  std::vector<int> *m_electron_match_HLT_e7_lhmedium_mu24           = nullptr; //!
  std::vector<int> *m_muon_match_HLT_mu26_ivarmedium                = nullptr; //!
  std::vector<int> *m_muon_match_HLT_mu22_mu8noL1                   = nullptr; //!
  std::vector<int> *m_muon_match_HLT_e17_lhloose_mu14               = nullptr; //!
  std::vector<int> *m_muon_match_HLT_e17_lhloose_nod0_mu14          = nullptr; //!

  // 2015 & 2016

  std::vector<int> *m_muon_match_HLT_mu50 = nullptr; //!

  /** Index of leptons which passed the overlap removal */

  std::vector<char> *m_electron_passOR = nullptr; //!
  std::vector<char> *m_muon_passOR     = nullptr; //!

  /** Some other lepton vector branches */

  std::vector<float> *m_electron_pt	      = nullptr; //!
  std::vector<float> *m_electron_eta	      = nullptr; //!
  std::vector<float> *m_electron_EtaBE2       = nullptr; //!
  std::vector<float> *m_electron_phi	      = nullptr; //!
  std::vector<float> *m_electron_E	      = nullptr; //!
  std::vector<float> *m_electron_sigd0PV      = nullptr; //!
  std::vector<float> *m_electron_z0SinTheta   = nullptr; //!
  std::vector<float> *m_electron_topoetcone20 = nullptr; //!
  std::vector<float> *m_electron_ptvarcone20  = nullptr; //!
  std::vector<int>   *m_electron_truthType    = nullptr; //!
  std::vector<int>   *m_electron_truthOrigin  = nullptr; //!
  std::vector<float> *m_muon_pt	              = nullptr; //!
  std::vector<float> *m_muon_eta	      = nullptr; //!
  std::vector<float> *m_muon_phi	      = nullptr; //!
  std::vector<float> *m_muon_sigd0PV	      = nullptr; //!
  std::vector<float> *m_muon_z0SinTheta       = nullptr; //!
  std::vector<float> *m_muon_ptvarcone30      = nullptr; //!
  std::vector<int>   *m_muon_truthType        = nullptr; //!
  std::vector<int>   *m_muon_truthOrigin      = nullptr; //!

  /** Reco jets BEFORE overlap removal */

  std::vector<float>   *m_jet_pt = nullptr;  //!
  std::vector<float>   *m_jet_eta = nullptr; //!
  std::vector<float>   *m_jet_phi = nullptr; //!
  std::vector<float>   *m_jet_E = nullptr;   //!
  std::vector<float>   *m_jet_flavor_weight_MV2c10 = nullptr;     //!
  std::vector<int>     *m_jet_flavor_truth_label = nullptr;       //!
  std::vector<int>     *m_jet_flavor_truth_label_ghost = nullptr; //!

  /** Indexes of jets that pass overlap removal */

  std::vector<short>   *m_selected_jets   = nullptr;  //!
  std::vector<short>   *m_selected_jets_T = nullptr;  //!

  /** Truth jets */

  std::vector<float>   *m_truth_jet_pt  = nullptr;  //!
  std::vector<float>   *m_truth_jet_eta = nullptr;  //!
  std::vector<float>   *m_truth_jet_phi = nullptr;  //!
  std::vector<float>   *m_truth_jet_e   = nullptr;  //!

  /** Extra branches to be stored in output TTree */

  float     m_weight_event;
  float     m_weight_event_trig_SLT;
  float     m_weight_event_lep;

  float     m_weight_lep_tag;
  float     m_weight_trig_tag;
  float     m_weight_lep_probe;
  float     m_weight_trig_probe;

  char	    m_isSS01;
  char	    m_isSS12;

  char	    m_is_T_T;
  char	    m_is_T_AntiT;
  char	    m_is_AntiT_T;
  char	    m_is_AntiT_AntiT;
  char      m_is_Tel_AntiTmu;
  char      m_is_Tmu_AntiTel;
  char      m_is_AntiTel_Tmu;
  char      m_is_AntiTmu_Tel;

  int       m_nmuons;
  int       m_nelectrons;
  int       m_nleptons;

  char	    m_lep_isTightSelected_0;
  char	    m_lep_isTightSelected_1;
  char	    m_lep_isTightSelected_2;

  float     m_lep_deltaRClosestBJet_0;
  float     m_lep_deltaRClosestBJet_1;
  float     m_lep_deltaRClosestBJet_2;

  char	    m_lep_isTrigMatch_SLT_0;
  char	    m_lep_isTrigMatch_SLT_1;
  char	    m_lep_isTrigMatch_DLT_0;
  char	    m_lep_isTrigMatch_DLT_1;

  char	    m_event_isTrigMatch_DLT;

  /** Some vector branches for leptons after OLR (pT-ordered) */

  std::vector<std::string> m_EL_VEC_VARS  = { "pt/F", "eta/F", "EtaBE2/F", "phi/F", "isTightSelected/B", "sigd0PV/F", "z0SinTheta/F", "deltaRClosestBJet/F", "ptvarcone20/F", "topoetcone20/F", "truthType/I", "truthOrigin/I" };
  std::vector<std::string> m_MU_VEC_VARS  = { "pt/F", "eta/F", "phi/F", "isTightSelected/B", "sigd0PV/F", "z0SinTheta/F", "deltaRClosestBJet/F", "ptvarcone30/F", "truthType/I", "truthOrigin/I" };
  std::vector<std::string> m_LEP_VEC_VARS  = { "Pt/F", "Eta/F", "EtaBE2/F", "deltaRClosestBJet/F"};

  std::map< std::string, MiniNTupMaker::Branch_Types > m_electron_OR_branches;
  std::map< std::string, MiniNTupMaker::Branch_Types > m_muon_OR_branches;
  std::map< std::string, MiniNTupMaker::Branch_Types > m_lep_OR_branches;

  /** Tag & Probe vector branches */

  std::vector<std::string> m_TPS      = { "Tag", "Probe" };
  std::vector<std::string> m_TRIGS    = { "SLT" /*, "DLT"*/ };
  std::vector<std::string> m_TP_VARS  = { "Pt/F", "Pt/VECF", "Eta/F", "Eta/VECF", "EtaBE2/F", "EtaBE2/VECF", "ptVarcone20/F", "ptVarcone30/F", "topoEtcone20/F", "sigd0PV/F", "Z0SinTheta/F", "ID/F", "deltaRClosestBJet/F", "deltaRClosestBJet/VECF", "massClosestBJet/F", "isTrigMatch/B", "isTightSelected/B", "isPrompt/B", "isBrems/B", "isFakeLep/B", "isQMisID/B", "isConvPh/B", "truthType/I", "truthType/VECI", "truthOrigin/I", "truthOrigin/VECI" };

  char m_isBadTPEvent_SLT; /** No T&TM (SLT) leptons found */

  std::map< std::string, MiniNTupMaker::Branch_Types > m_TagProbe_branches;

  /** Jets AFTER overlap removal */

  std::vector<float> m_jet_OR_Pt;
  std::vector<float> m_jet_OR_Eta;
  std::vector<float> m_jet_OR_Phi;
  std::vector<float> m_jet_OR_E;
  std::vector<float> m_jet_OR_truthMatch_Pt;
  std::vector<float> m_jet_OR_truthMatch_Eta;
  std::vector<float> m_jet_OR_truthMatch_Phi;
  std::vector<float> m_jet_OR_truthMatch_E;
  std::vector<char>  m_jet_OR_truthMatch_isBJet;
  std::vector<char>  m_jet_OR_truthMatch_isCJet;
  std::vector<char>  m_jet_OR_truthMatch_isLFJet;
  std::vector<char>  m_jet_OR_truthMatch_isGluonJet;

  // variables that don't get filled at submission time should be
  // protected from being send from the submission node to the worker
  // node (done by the //!)

  /** Other private members */

  unsigned int m_effectiveTotEntries;  //!
  int          m_numEntry;             //!
  float        m_sumGenEvents;         //!
  float        m_sumGenEventsWeighted; //!

  std::shared_ptr<MiniNTupMaker::eventObj>                 m_event;   //!
  std::vector< std::shared_ptr<MiniNTupMaker::leptonObj> > m_leptons; //!
  std::vector< std::shared_ptr<MiniNTupMaker::bjetObj> >   m_bjets;   //!

  TRandom3* m_rand; //!

public:

  // this is a standard constructor
  HTopMultilepMiniNTupMaker (std::string className = "HTopMultilepMiniNTupMaker");

  // these are the functions inherited from Algorithm
  virtual EL::StatusCode setupJob (EL::Job& job);
  virtual EL::StatusCode fileExecute ();
  virtual EL::StatusCode histInitialize ();
  virtual EL::StatusCode changeInput (bool firstFile);
  virtual EL::StatusCode initialize ();
  virtual EL::StatusCode execute ();
  virtual EL::StatusCode postExecute ();
  virtual EL::StatusCode finalize ();
  virtual EL::StatusCode histFinalize ();

  // this is needed to distribute the algorithm to the workers
  ClassDef(HTopMultilepMiniNTupMaker, 1);

private:

  EL::StatusCode enableSelectedBranches ();
  EL::StatusCode checkIsTightLep( std::shared_ptr<MiniNTupMaker::leptonObj> lep );
  EL::StatusCode decorateEvent ();
  EL::StatusCode decorateWeights ();

  EL::StatusCode getPostOLRIndex( int& idx, const unsigned int& pos, const std::string& lep_type );
  EL::StatusCode triggerMatching ();
  EL::StatusCode findClosestBJetLep ();

  /**
    * @brief  Set which lepton is tag and which is probe for the r/f efficiency measurement
    *
  */
  EL::StatusCode defineTagAndProbe ();

  EL::StatusCode fillTPFlatBranches ( std::shared_ptr<MiniNTupMaker::leptonObj> lep, const std::string& trig );
  EL::StatusCode storeLeptonBranches ();
  EL::StatusCode setOutputBranches ();
  EL::StatusCode clearBranches ( const std::string& type );

  EL::StatusCode jetTruthMatching();

};

#endif
