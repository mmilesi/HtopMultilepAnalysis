import ROOT
from xAH_config import xAH_config
import sys, os

sys.path.insert(0, os.environ['ROOTCOREBIN']+"/user_scripts/HTopMultilepAnalysis/")

c = xAH_config()

# List the branches to be copied over and activated from the input TTree
#
eventweight_branches = ["mcWeightOrg","pileupEventWeight_090","MV2c20_77_EventWeight","JVT_EventWeight","lepSFTrigLoose","lepSFTrigTight","lepSFObjLoose","lepSFObjTight","tauSFTight","tauSFLoose"]
event_branches       = ["EventNumber","RunNumber","mc_channel_number","passEventCleaning","onelep_type","dilep_type","trilep_type","total_charge","total_leptons","nJets_OR_T","nJets_OR","nJets_OR_T_MV2c20_77","nJets_OR_MV2c20_77","nTaus_OR_Pt25","Mll01","Ptll01","DRll01","Mlll012","Mll02","Ptll02","DRll02","Mll12","Ptll12","DRll12","HT","HT_lep","HT_jets","MET_RefFinal_et","MET_RefFinal_phi","isBlinded"]
trigbits_branches    = ["HLT_e24_lhmedium_L1EM20VH","HLT_e24_lhmedium_L1EM18VH","HLT_e60_lhmedium","HLT_e120_lhloose","HLT_mu20_iloose_L1MU15","HLT_mu50"]
jet_branches         = ["lead_jetPt","lead_jetEta","lead_jetPhi","sublead_jetPt","sublead_jetEta","sublead_jetPhi"]
lep_branches         = ["lep_ID_0","lep_Index_0","lep_Pt_0","lep_E_0","lep_Eta_0","lep_Phi_0","lep_EtaBE2_0","lep_sigd0PV_0","lep_Z0SinTheta_0",
                        "lep_isTightLH_0","lep_isMediumLH_0","lep_isLooseLH_0","lep_isTight_0","lep_isMedium_0","lep_isLoose_0","lep_isolationLooseTrackOnly_0","lep_isolationLoose_0","lep_isolationFixedCutTight_0","lep_isolationFixedCutTightTrackOnly_0","lep_isolationFixedCutLoose_0",
                        "lep_isTrigMatch_0","lep_isPrompt_0","lep_isBremsElec_0","lep_isFakeLep_0",
                        "lep_SFIDLoose_0","lep_SFIDTight_0","lep_SFTrigLoose_0","lep_SFTrigTight_0","lep_SFIsoLoose_0","lep_SFIsoTight_0","lep_SFReco_0","lep_SFTTVA_0","lep_SFObjLoose_0","lep_SFObjTight_0",
                        "lep_ID_1","lep_Index_1","lep_Pt_1","lep_E_1","lep_Eta_1","lep_Phi_1","lep_EtaBE2_1","lep_sigd0PV_1","lep_Z0SinTheta_1",
                        "lep_isTightLH_1","lep_isMediumLH_1","lep_isLooseLH_1","lep_isTight_1","lep_isMedium_1","lep_isLoose_1","lep_isolationLooseTrackOnly_1","lep_isolationLoose_1","lep_isolationFixedCutTight_1","lep_isolationFixedCutTightTrackOnly_1","lep_isolationFixedCutLoose_1",
                        "lep_isTrigMatch_1","lep_isPrompt_1","lep_isBremsElec_1","lep_isFakeLep_1",
                        "lep_SFIDLoose_1","lep_SFIDTight_1","lep_SFTrigLoose_1","lep_SFTrigTight_1","lep_SFIsoLoose_1","lep_SFIsoTight_1","lep_SFReco_1","lep_SFTTVA_1","lep_SFObjLoose_1","lep_SFObjTight_1",
                        "lep_ID_2","lep_Index_2","lep_Pt_2","lep_E_2","lep_Eta_2","lep_Phi_2","lep_EtaBE2_2","lep_sigd0PV_2","lep_Z0SinTheta_2",
                        "lep_isTightLH_2","lep_isMediumLH_2","lep_isLooseLH_2","lep_isTight_2","lep_isMedium_2","lep_isLoose_2","lep_isolationLooseTrackOnly_2","lep_isolationLoose_2","lep_isolationFixedCutTight_2","lep_isolationFixedCutTightTrackOnly_2","lep_isolationFixedCutLoose_2",
                        "lep_isTrigMatch_2","lep_isPrompt_2","lep_isBremsElec_2","lep_isFakeLep_2",
                        "lep_SFIDLoose_2","lep_SFIDTight_2","lep_SFTrigLoose_2","lep_SFTrigTight_2","lep_SFIsoLoose_2","lep_SFIsoTight_2","lep_SFReco_2","lep_SFTTVA_2","lep_SFObjLoose_2","lep_SFObjTight_2"]
tau_branches         = ["tau_pt_0","tau_eta_0","tau_phi_0","tau_charge_0","tau_BDTJetScore_0","tau_JetBDTSigLoose_0","tau_JetBDTSigMedium_0","tau_JetBDTSigTight_0","tau_numTrack_0","tau_SFTight_0","tau_SFLoose_0"]

mc_truth_branches = ["m_truth_m","m_truth_pt","m_truth_eta","m_truth_phi","m_truth_e","m_truth_pdgId","m_truth_status","m_truth_barcode","m_truth_parents","m_truth_children","m_truth_jet_pt","m_truth_jet_eta","m_truth_jet_phi","m_truth_jet_e"]

branches_to_copy = eventweight_branches + event_branches + trigbits_branches + jet_branches + lep_branches + tau_branches + mc_truth_branches

# Trick to pass the list as a comma-separated string to the C++ algorithm
#
branches_to_copy_str = ",".join(branches_to_copy)

# Instantiate the main algorithm
#
HTopMultilepMiniNTupMakerDict = { "m_name"                 : "HTopMultilepMiniNTupMaker",
                                  "m_debug"                : False,
				  "m_outputNTupName"       : "physics",
                                  "m_outputNTupStreamName" : "output",
				  "m_inputBranches"        : branches_to_copy_str,
	                          "m_useAlgSelect"         : True,
				  "m_addStreamEventsHist"  : False,
                                }

# Instantiate the NTupleSvc algorithm
#
ntuplesvc = ROOT.EL.NTupleSvc(HTopMultilepMiniNTupMakerDict["m_outputNTupStreamName"])

# Set the branches to be copied over from the input TTree
#
print("Copying branches from input TTree:")
for branch in branches_to_copy:
   #print("\t{0}".format(branch))
   ntuplesvc.copyBranch(branch)

# Instantiate the AlgSelect algorithm to skim the input ntuple
#
algskim = ROOT.EL.AlgSelect(HTopMultilepMiniNTupMakerDict["m_outputNTupStreamName"])
#algskim.addCut ("passEventCleaning==1")
algskim.addCut ("HLT_e24_lhmedium_L1EM20VH||HLT_e24_lhmedium_L1EM18VH||HLT_e60_lhmedium||HLT_e120_lhloose||HLT_mu20_iloose_L1MU15||HLT_mu50")
algskim.addCut ("nJets_OR>=1") # temp
algskim.addCut("nJets_OR_MV2c20_77>=1") # temp
algskim.addCut ("dilep_type>0||trilep_type>0")
algskim.histName ("cutflow")

# Add the algorithms to the job.
#
# Here order matters!
#
c._algorithms.append(ntuplesvc)
if ( HTopMultilepMiniNTupMakerDict["m_useAlgSelect"] ):
  c._algorithms.append(algskim)
c.setalg("HTopMultilepMiniNTupMaker", HTopMultilepMiniNTupMakerDict)


