#ifndef HTopMultilepAnalysis_TagAndProbeTree_H
#define HTopMultilepAnalysis_TagAndProbeTree_H

// package include(s):
#include "xAODAnaHelpers/HelpTreeBase.h" 

// EDM include(s):
#include "xAODEventInfo/EventInfo.h"
#include "xAODMuon/Muon.h"
#include "xAODEgamma/Electron.h"
#include "xAODJet/Jet.h"

// Infrastructure include(s):
#include "xAODRootAccess/TEvent.h"

// ROOT include(s):
#include "TTree.h"
#include "TFile.h"

class TagAndProbeTree : public HelpTreeBase
{

  private:
    
    /* event variables*/
    int m_is_mc;
    int m_nBjetsMedium;
    int m_isDileptonOS;
    int m_isDileptonSS;
    int m_isNonTightEvent;
    int m_isProbeElEvent;
    int m_isProbeMuEvent;
    
    /* jet variables */
    std::vector<float> m_jet_m;    
    std::vector<int> m_jet_clean;
    
    /* muon variables */
    std::vector<int> m_muon_isTight; 
    std::vector<int> m_muon_isTrigMatched; 
    std::vector<int> m_muon_isTag; 
    std::vector<int> m_muon_isTruthMatched; 
    std::vector<int> m_muon_isTruthMatchedIso; 
    std::vector<int> m_muon_isTruthMatchedNonIso; 
    std::vector<int> m_muon_isTruthMatchedSecondary; 
    std::vector<int> m_muon_isTruthMatchedNoProdVtx; 
    std::vector<int> m_muon_isTruthMatchedOther; 
    std::vector<int> m_muon_isTruthMatchedUnknown;
    std::vector<int> m_muon_isChFlip; 
    std::vector<int> m_muon_isBrem;
    std::vector<int> m_muon_truthType;  
    std::vector<int> m_muon_truthOrigin; 
    std::vector<int> m_muon_truthStatus;  
    /* muon TAG variables */
    std::vector<float> m_muon_tag_pt;
    std::vector<float> m_muon_tag_eta;
    std::vector<int>   m_muon_tag_isTight; 
    std::vector<int>   m_muon_tag_isTruthMatched; 
    std::vector<int>   m_muon_tag_isTruthMatchedIso; 
    std::vector<int>   m_muon_tag_isTruthMatchedNonIso; 
    std::vector<int>   m_muon_tag_isTruthMatchedSecondary; 
    std::vector<int>   m_muon_tag_isTruthMatchedNoProdVtx; 
    std::vector<int>   m_muon_tag_isTruthMatchedOther; 
    std::vector<int>   m_muon_tag_isTruthMatchedUnknown;
    std::vector<int>   m_muon_tag_isChFlip; 
    std::vector<int>   m_muon_tag_isBrem;
    std::vector<int>   m_muon_tag_truthType;  
    std::vector<int>   m_muon_tag_truthOrigin; 
    std::vector<int>   m_muon_tag_truthStatus;  
    /* muon PROBE variables */
    std::vector<float> m_muon_probe_pt;
    std::vector<float> m_muon_probe_eta;
    std::vector<int>   m_muon_probe_isTight; 
    std::vector<int>   m_muon_probe_isTruthMatched; 
    std::vector<int>   m_muon_probe_isTruthMatchedIso; 
    std::vector<int>   m_muon_probe_isTruthMatchedNonIso; 
    std::vector<int>   m_muon_probe_isTruthMatchedSecondary; 
    std::vector<int>   m_muon_probe_isTruthMatchedNoProdVtx; 
    std::vector<int>   m_muon_probe_isTruthMatchedOther; 
    std::vector<int>   m_muon_probe_isTruthMatchedUnknown;
    std::vector<int>   m_muon_probe_isChFlip; 
    std::vector<int>   m_muon_probe_isBrem;
    std::vector<int>   m_muon_probe_truthType;  
    std::vector<int>   m_muon_probe_truthOrigin; 
    std::vector<int>   m_muon_probe_truthStatus;  
    
    /* electron variables */    
    std::vector<float> m_electron_calo_eta;   
    std::vector<int>   m_electron_crack;   
    std::vector<int>   m_electron_isTight; 
    std::vector<int>   m_electron_isTrigMatched; 
    std::vector<int>   m_electron_isTag; 
    std::vector<int>   m_electron_isTruthMatched; 
    std::vector<int>   m_electron_isTruthMatchedIso; 
    std::vector<int>   m_electron_isTruthMatchedNonIso; 
    std::vector<int>   m_electron_isTruthMatchedSecondary; 
    std::vector<int>   m_electron_isTruthMatchedNoProdVtx; 
    std::vector<int>   m_electron_isTruthMatchedOther; 
    std::vector<int>   m_electron_isTruthMatchedUnknown;
    std::vector<int>   m_electron_isChFlip; 
    std::vector<int>   m_electron_isBrem; 
    std::vector<int>   m_electron_truthType;
    std::vector<int>   m_electron_truthOrigin; 
    std::vector<int>   m_electron_truthStatus;
    /* electron TAG variables */
    std::vector<float> m_electron_tag_pt;
    std::vector<float> m_electron_tag_eta;
    std::vector<int>   m_electron_tag_isTight; 
    std::vector<int>   m_electron_tag_isChFlip;     
    std::vector<int>   m_electron_tag_isBrem;    
    std::vector<int>   m_electron_tag_isTruthMatchedIso; 
    /* electron PROBE variables */
    std::vector<float> m_electron_probe_pt;
    std::vector<float> m_electron_probe_eta;
    std::vector<int>   m_electron_probe_isTight; 
    std::vector<int>   m_electron_probe_isChFlip;     
    std::vector<int>   m_electron_probe_isBrem;    
    std::vector<int>   m_electron_probe_isTruthMatchedIso; 
       
  public:
    TagAndProbeTree(xAOD::TEvent * event, TTree* tree, TFile* file, const float units);
    ~TagAndProbeTree();

    void AddEventUser(const std::string detailStrUser = "");
    void AddMuonsUser(const std::string detailStrUser = "");
    void AddElectronsUser(const std::string detailStrUser = "");
    void AddJetsUser(const std::string detailStrUser = "");
    
    void ClearEventUser();      
    void ClearMuonsUser();   
    void ClearElectronsUser();  
    void ClearJetsUser();
         
    void FillEventUser( const xAOD::EventInfo* eventInfo );
    void FillMuonsUser( const xAOD::Muon* muon );
    void FillElectronsUser( const xAOD::Electron* electron );
    void FillJetsUser( const xAOD::Jet* jet );
    void FillFatJetsUser( const xAOD::Jet* fatJet );
};
#endif