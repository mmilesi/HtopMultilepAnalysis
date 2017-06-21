import os, glob, subprocess, shutil

# ID,category,xsection,kfactor,efficiency,name,group,subgroup
samplelist = [
["","Data","","","","physics_Main","Data","physics_Main"],
["","Data","","","","fakes_mm","Data","fakes_mm"],
["343365","Signal","0.05343","1.0","1.0","aMcAtNloPythia8EvtGen_A14_NNPDF23_NNPDF30ME_ttH125_dilep","ttH","ttH_dil_Pythia8"],
["343366","Signal","0.22276","1.0","1.0","aMcAtNloPythia8EvtGen_A14_NNPDF23_NNPDF30ME_ttH125_semilep","ttH","ttH_semilep_Pythia8"],
["343367","Signal","0.23082","1.0","1.0","aMcAtNloPythia8EvtGen_A14_NNPDF23_NNPDF30ME_ttH125_allhad","ttH","ttH_allhad_Pythia8"],
["304014","Background","0.0016398","1","1.0","Pythia8_3top_SM","tops","3top"],
["341998","Background","5.7e-05","1","1.0","tWH125_gamgam_yt_plus1","tWH","gamgam"],
["342001","Background","0.007615","1","1.0","tWH125_lep_yt_plus1","tWH","lep"],
["342004","Background","0.014425","1","1.0","tWH125_bbbar_yt_plus1","tWH","bbbar"],
["342284","Background","1.1021","1","1.0","Pythia8EvtGen_WH_inc","VH","WH_inc"],
["342285","Background","0.60072","1","1.0","Pythia8EvtGen_ZH_inc","VH","ZH_inc"],
["343267","Background","0.00012335","1","1.0","MadGraphPythia8_tHjb125_gamgam","tHbj","gamgam"],
["343270","Background","0.031216","1","1.0","MadGraphPythia8_tHjb125_bbbar","tHbj","bbbar"],
["343273","Background","0.016479","1","1.0","MadGraphPythia8_tHjb125_lep","tHbj","lep"],
["361063","Background","12.805","0.91","1.0","Sherpa_CT10_llll","Diboson","llll"],
["361064","Background","1.8446","0.91","1.0","Sherpa_CT10_lllvSFMinus","Diboson","lllvSFMinus"],
["361065","Background","3.6235","0.91","1.0","Sherpa_CT10_lllvOFMinus","Diboson","lllvOFMinus"],
["361066","Background","2.5656","0.91","1.0","Sherpa_CT10_lllvSFPlus","Diboson","lllvSFPlus"],
["361067","Background","5.0169","0.91","1.0","Sherpa_CT10_lllvOFPlus","Diboson","lllvOFPlus"],
["361068","Background","14.022","0.91","1.0","Sherpa_CT10_llvv","Diboson","llvv"],
["361069","Background","0.02575","0.91","1.0","Sherpa_CT10_llvvjj_ss_EW4","Diboson","llvvjj_ss_EW4"],
["361070","Background","0.043375","0.91","1.0","Sherpa_CT10_llvvjj_ss_EW6","Diboson","EWllssnunujj"],
["361071","Background","0.042017","0.91","1.0","Sherpa_CT10_lllvjj_EW6","Diboson","lllvjj_EW6"],
["361072","Background","0.031496","0.91","1.0","Sherpa_CT10_lllljj_EW6","Diboson","lllljj_EW6"],
["361073","Background","0.02095","0.91","1.0","Sherpa_CT10_ggllll","Diboson","ggllll"],
["361077","Background","0.85492","0.91","1.0","Sherpa_CT10_ggllvv","Diboson","ggllvv"],
["361091","Background","24.885","0.91","1.0","Sherpa_CT10_WplvWmqq_SHv21_improved","Diboson","WW_SHv21_improved"],
["361092","Background","24.857","0.91","1.0","Sherpa_CT10_WpqqWmlv_SHv21_improved","Diboson","WW_SHv21_improved"],
["361093","Background","11.494","0.91","1.0","Sherpa_CT10_WlvZqq_SHv21_improved","Diboson","WZ_SHv21_improved"],
["361094","Background","3.4234","0.91","1.0","Sherpa_CT10_WqqZll_SHv21_improved","Diboson","WZ_SHv21_improved"],
["361095","Background","6.7770","0.91","1.0","Sherpa_CT10_WqqZvv_SHv21_improved","Diboson","WZ_SHv21_improved"],
["361096","Background","2.35832","0.91","1.0","Sherpa_CT10_ZqqZll_SHv21_improved","Diboson","ZZ_SHv21_improved"],
["361097","Background","4.64178","0.91","1.0","Sherpa_CT10_ZqqZvv_SHv21_improved","Diboson","ZZ_SHv21_improved"],
["361620","Background","1","0.008343","1.0","Sherpa_WWW_3l3v","Triboson","WWW_3l3v"],
["361621","Background","1","0.001734","1.0","Sherpa_WWZ_4l2v","Triboson","WWZ_4l2v"],
["361622","Background","1","0.0034299","1.0","Sherpa_WWZ_2l4v","Triboson","WWZ_2l4v"],
["361623","Background","1","0.00021783","1.0","Sherpa_WZZ_5l1v","Triboson","WZZ_5l1v"],
["361624","Background","1","0.000855458","1.0","Sherpa_WZZ_3l3v","Triboson","WZZ_3l3v"],
["361625","Background","1","1.7059e-05","1.0","Sherpa_ZZZ_6l0v","Triboson","ZZZ_6l0v"],
["361626","Background","1","9.9467e-05","1.0","Sherpa_ZZZ_4l2v","Triboson","ZZZ_4l2v"],
["361627","Background","1","0.000199561","1.0","Sherpa_ZZZ_2l4v","Triboson","ZZZ_2l4v"],
["364100","Background","1630.22","0.9751","1.0","Sherpa221_Zmumu_MAXHTPTV0_70_CVetoBVeto","Z+jetsCVetoBVeto","mumu"],
["364101","Background","223.717","0.9751","1.0","Sherpa221_Zmumu_MAXHTPTV0_70_CFilterBVeto","Z+jetsCFilterBVeto","mumu"],
["364102","Background","127.18","0.9751","1.0","Sherpa221_Zmumu_MAXHTPTV0_70_BFilter","Z+jetsBFilter","mumu"],
["364103","Background","75.0165","0.9751","1.0","Sherpa221_Zmumu_MAXHTPTV70_140_CVetoBVeto","Z+jetsCVetoBVeto","mumu"],
["364104","Background","20.3477","0.9751","1.0","Sherpa221_Zmumu_MAXHTPTV70_140_CFilterBVeto","Z+jetsCFilterBVeto","mumu"],
["364105","Background","12.3885","0.9751","1.0","Sherpa221_Zmumu_MAXHTPTV70_140_BFilter","Z+jetsBFilter","mumu"],
["364106","Background","24.2853","0.9751","1.0","Sherpa221_Zmumu_MAXHTPTV140_280_CVetoBVeto","Z+jetsCVetoBVeto","mumu"],
["364107","Background","9.27542","0.9751","1.0","Sherpa221_Zmumu_MAXHTPTV140_280_CFilterBVeto","Z+jetsCFilterBVeto","mumu"],
["364108","Background","6.01361","0.9751","1.0","Sherpa221_Zmumu_MAXHTPTV140_280_BFilter","Z+jetsBFilter","mumu"],
["364109","Background","4.77297","0.9751","1.0","Sherpa221_Zmumu_MAXHTPTV280_500_CVetoBVeto","Z+jetsCVetoBVeto","mumu"],
["364110","Background","2.26557","0.9751","1.0","Sherpa221_Zmumu_MAXHTPTV280_500_CFilterBVeto","Z+jetsCFilterBVeto","mumu"],
["364111","Background","1.49132","0.9751","1.0","Sherpa221_Zmumu_MAXHTPTV280_500_BFilter","Z+jetsBFilter","mumu"],
["364112","Background","1.7881","0.9751","1.0","Sherpa221_Zmumu_MAXHTPTV500_1000","Z+jets_HighZPt","mumu"],
["364113","Background","0.14769","0.9751","1.0","Sherpa221_Zmumu_MAXHTPTV1000_E_CMS","Z+jets_HighZPt","mumu"],
["364114","Background","1627.18","0.9751","1.0","Sherpa221_Zee_MAXHTPTV0_70_CVetoBVeto","Z+jetsCVetoBVeto","ee"],
["364115","Background","223.731","0.9751","1.0","Sherpa221_Zee_MAXHTPTV0_70_CFilterBVeto","Z+jetsCFilterBVeto","ee"],
["364116","Background","126.45","0.9751","1.0","Sherpa221_Zee_MAXHTPTV0_70_BFilter","Z+jetsBFilter","ee"],
["364117","Background","76.2925","0.9751","1.0","Sherpa221_Zee_MAXHTPTV70_140_CVetoBVeto","Z+jetsCVetoBVeto","ee"],
["364118","Background","20.336","0.9751","1.0","Sherpa221_Zee_MAXHTPTV70_140_CFilterBVeto","Z+jetsCFilterBVeto","ee"],
["364119","Background","12.6228","0.9751","1.0","Sherpa221_Zee_MAXHTPTV70_140_BFilter","Z+jetsBFilter","ee"],
["364120","Background","25.03","0.9751","1.0","Sherpa221_Zee_MAXHTPTV140_280_CVetoBVeto","Z+jetsCVetoBVeto","ee"],
["364121","Background","9.37199","0.9751","1.0","Sherpa221_Zee_MAXHTPTV140_280_CFilterBVeto","Z+jetsCFilterBVeto","ee"],
["364122","Background","6.08263","0.9751","1.0","Sherpa221_Zee_MAXHTPTV140_280_BFilter","Z+jetsBFilter","ee"],
["364123","Background","4.86923","0.9751","1.0","Sherpa221_Zee_MAXHTPTV280_500_CVetoBVeto","Z+jetsCVetoBVeto","ee"],
["364124","Background","2.27998","0.9751","1.0","Sherpa221_Zee_MAXHTPTV280_500_CFilterBVeto","Z+jetsCFilterBVeto","ee"],
["364125","Background","1.49437","0.9751","1.0","Sherpa221_Zee_MAXHTPTV280_500_BFilter","Z+jetsBFilter","ee"],
["364126","Background","1.8081","0.9751","1.0","Sherpa221_Zee_MAXHTPTV500_1000","Z+jets_HighZPt","ee"],
["364127","Background","0.14857","0.9751","1.0","Sherpa221_Zee_MAXHTPTV1000_E_CMS","Z+jets_HighZPt","ee"],
["364128","Background","1627.73","0.9751","1.0","Sherpa221_Ztautau_MAXHTPTV0_70_CVetoBVeto","Z+jetsCVetoBVeto","tautau"],
["364129","Background","223.881","0.9751","1.0","Sherpa221_Ztautau_MAXHTPTV0_70_CFilterBVeto","Z+jetsCFilterBVeto","tautau"],
["364130","Background","127.733","0.9751","1.0","Sherpa221_Ztautau_MAXHTPTV0_70_BFilter","Z+jetsBFilter","tautau"],
["364131","Background","76.0262","0.9751","1.0","Sherpa221_Ztautau_MAXHTPTV70_140_CVetoBVeto","Z+jetsCVetoBVeto","tautau"],
["364132","Background","20.2123","0.9751","1.0","Sherpa221_Ztautau_MAXHTPTV70_140_CFilterBVeto","Z+jetsCFilterBVeto","tautau"],
["364133","Background","12.2939","0.9751","1.0","Sherpa221_Ztautau_MAXHTPTV70_140_BFilter","Z+jetsBFilter","tautau"],
["364134","Background","24.8034","0.9751","1.0","Sherpa221_Ztautau_MAXHTPTV140_280_CVetoBVeto","Z+jetsCVetoBVeto","tautau"],
["364135","Background","9.32824","0.9751","1.0","Sherpa221_Ztautau_MAXHTPTV140_280_CFilterBVeto","Z+jetsCFilterBVeto","tautau"],
["364136","Background","5.47909","0.9751","1.0","Sherpa221_Ztautau_MAXHTPTV140_280_BFilter","Z+jetsBFilter","tautau"],
["364137","Background","4.79119","0.9751","1.0","Sherpa221_Ztautau_MAXHTPTV280_500_CVetoBVeto","Z+jetsCVetoBVeto","tautau"],
["364138","Background","2.27563","0.9751","1.0","Sherpa221_Ztautau_MAXHTPTV280_500_CFilterBVeto","Z+jetsCFilterBVeto","tautau"],
["364139","Background","1.50284","0.9751","1.0","Sherpa221_Ztautau_MAXHTPTV280_500_BFilter","Z+jetsBFilter","tautau"],
["364140","Background","1.8096","0.9751","1.0","Sherpa221_Ztautau_MAXHTPTV500_1000","Z+jets_HighZPt","tautau"],
["364141","Background","0.14834","0.9751","1.0","Sherpa221_Ztautau_MAXHTPTV1000_E_CMS","Z+jets_HighZPt","tautau"],
["364156","Background","15770","0.9702","1.0","Sherpa221_Wmunu_MAXHTPTV0_70_CVetoBVeto","W+jetsCVetoBVeto","munu"],
["364157","Background","2493.38","0.9702","1.0","Sherpa221_Wmunu_MAXHTPTV0_70_CFilterBVeto","W+jetsCFilterBVeto","munu"],
["364158","Background","844.198","0.9702","1.0","Sherpa221_Wmunu_MAXHTPTV0_70_BFilter","W+jetsBFilter","munu"],
["364159","Background","637.424","0.9702","1.0","Sherpa221_Wmunu_MAXHTPTV70_140_CVetoBVeto","W+jetsCVetoBVeto","munu"],
["364160","Background","219.966","0.9702","1.0","Sherpa221_Wmunu_MAXHTPTV70_140_CFilterBVeto","W+jetsCFilterBVeto","munu"],
["364161","Background","71.4594","0.9702","1.0","Sherpa221_Wmunu_MAXHTPTV70_140_BFilter","W+jetsBFilter","munu"],
["364162","Background","212.555","0.9702","1.0","Sherpa221_Wmunu_MAXHTPTV140_280_CVetoBVeto","W+jetsCVetoBVeto","munu"],
["364163","Background","98.4372","0.9702","1.0","Sherpa221_Wmunu_MAXHTPTV140_280_CFilterBVeto","W+jetsCFilterBVeto","munu"],
["364164","Background","36.9148","0.9702","1.0","Sherpa221_Wmunu_MAXHTPTV140_280_BFilter","W+jetsBFilter","munu"],
["364165","Background","39.3825","0.9702","1.0","Sherpa221_Wmunu_MAXHTPTV280_500_CVetoBVeto","W+jetsCVetoBVeto","munu"],
["364166","Background","22.9178","0.9702","1.0","Sherpa221_Wmunu_MAXHTPTV280_500_CFilterBVeto","W+jetsCFilterBVeto","munu"],
["364167","Background","9.60864","0.9702","1.0","Sherpa221_Wmunu_MAXHTPTV280_500_BFilter","W+jetsBFilter","munu"],
["364168","Background","15.01","0.9702","1.0","Sherpa221_Wmunu_MAXHTPTV500_1000","W+jets_HighWPt","munu"],
["364169","Background","1.2344","0.9702","1.0","Sherpa221_Wmunu_MAXHTPTV1000_E_CMS","W+jets_HighWPt","munu"],
["364170","Background","15769.6","0.9702","1.0","Sherpa221_Wenu_MAXHTPTV0_70_CVetoBVeto","W+jetsCVetoBVeto","enu"],
["364171","Background","2492.64","0.9702","1.0","Sherpa221_Wenu_MAXHTPTV0_70_CFilterBVeto","W+jetsCFilterBVeto","enu"],
["364172","Background","844.638","0.9702","1.0","Sherpa221_Wenu_MAXHTPTV0_70_BFilter","W+jetsBFilter","enu"],
["364173","Background","630.322","0.9702","1.0","Sherpa221_Wenu_MAXHTPTV70_140_CVetoBVeto","W+jetsCVetoBVeto","enu"],
["364174","Background","215.49","0.9702","1.0","Sherpa221_Wenu_MAXHTPTV70_140_CFilterBVeto","W+jetsCFilterBVeto","enu"],
["364175","Background","97.738","0.9702","1.0","Sherpa221_Wenu_MAXHTPTV70_140_BFilter","W+jetsBFilter","enu"],
["364176","Background","202.836","0.9702","1.0","Sherpa221_Wenu_MAXHTPTV140_280_CVetoBVeto","W+jetsCVetoBVeto","enu"],
["364177","Background","98.4433","0.9702","1.0","Sherpa221_Wenu_MAXHTPTV140_280_CFilterBVeto","W+jetsCFilterBVeto","enu"],
["364178","Background","36.9965","0.9702","1.0","Sherpa221_Wenu_MAXHTPTV140_280_BFilter","W+jetsBFilter","enu"],
["364179","Background","39.2433","0.9702","1.0","Sherpa221_Wenu_MAXHTPTV280_500_CVetoBVeto","W+jetsCVetoBVeto","enu"],
["364180","Background","22.8465","0.9702","1.0","Sherpa221_Wenu_MAXHTPTV280_500_CFilterBVeto","W+jetsCFilterBVeto","enu"],
["364181","Background","9.65665","0.9702","1.0","Sherpa221_Wenu_MAXHTPTV280_500_BFilter","W+jetsBFilter","enu"],
["364182","Background","15.224","0.9702","1.0","Sherpa221_Wenu_MAXHTPTV500_1000","W+jets_HighWPt","enu"],
["364183","Background","1.2334","0.9702","1.0","Sherpa221_Wenu_MAXHTPTV1000_E_CMS","W+jets_HighWPt","enu"],
["364184","Background","15799.4","0.9702","1.0","Sherpa221_Wtaunu_MAXHTPTV0_70_CVetoBVeto","W+jetsCVetoBVeto","taunu"],
["364185","Background","2477.25","0.9702","1.0","Sherpa221_Wtaunu_MAXHTPTV0_70_CFilterBVeto","W+jetsCFilterBVeto","taunu"],
["364186","Background","854.555","0.9702","1.0","Sherpa221_Wtaunu_MAXHTPTV0_70_BFilter","W+jetsBFilter","taunu"],
["364187","Background","638.546","0.9702","1.0","Sherpa221_Wtaunu_MAXHTPTV70_140_CVetoBVeto","W+jetsCVetoBVeto","taunu"],
["364188","Background","210.382","0.9702","1.0","Sherpa221_Wtaunu_MAXHTPTV70_140_CFilterBVeto","W+jetsCFilterBVeto","taunu"],
["364189","Background","98.0183","0.9702","1.0","Sherpa221_Wtaunu_MAXHTPTV70_140_BFilter","W+jetsBFilter","taunu"],
["364190","Background","202.333","0.9702","1.0","Sherpa221_Wtaunu_MAXHTPTV140_280_CVetoBVeto","W+jetsCVetoBVeto","taunu"],
["364191","Background","98.5776","0.9702","1.0","Sherpa221_Wtaunu_MAXHTPTV140_280_CFilterBVeto","W+jetsCFilterBVeto","taunu"],
["364192","Background","40.0623","0.9702","1.0","Sherpa221_Wtaunu_MAXHTPTV140_280_BFilter","W+jetsBFilter","taunu"],
["364193","Background","39.3251","0.9702","1.0","Sherpa221_Wtaunu_MAXHTPTV280_500_CVetoBVeto","W+jetsCVetoBVeto","taunu"],
["364194","Background","22.779","0.9702","1.0","Sherpa221_Wtaunu_MAXHTPTV280_500_CFilterBVeto","W+jetsCFilterBVeto","taunu"],
["364195","Background","9.67021","0.9702","1.0","Sherpa221_Wtaunu_MAXHTPTV280_500_BFilter","W+jetsBFilter","taunu"],
["364196","Background","15.046","0.9702","1.0","Sherpa221_Wtaunu_MAXHTPTV500_1000","W+jets_HighWPt","taunu"],
["364197","Background","1.2339","0.9702","1.0","Sherpa221_Wtaunu_MAXHTPTV1000_E_CMS","W+jets_HighWPt","taunu"],
["364198","Background","2330.19","0.9751","1.0","Zmm_Mll10_40_MAXHTPTV0_70_BVeto","Z+jetsLowMllBVeto","mumu"],
["364199","Background","82.2568","0.9751","1.0","Zmm_Mll10_40_MAXHTPTV0_70_BFilter","Z+jetsLowMllBFilter","mumu"],
["364200","Background","44.8791","0.9751","1.0","Zmm_Mll10_40_MAXHTPTV70_280_BVeto","Z+jetsLowMllBVeto","mumu"],
["364201","Background","5.11499","0.9751","1.0","Zmm_Mll10_40_MAXHTPTV70_280_BFilter","Z+jetsLowMllBFilter","mumu"],
["364202","Background","2.75978","0.9751","1.0","Zmm_Mll10_40_MAXHTPTV280_E_CMS_BVeto","Z+jetsLowMllBVeto","mumu"],
["364203","Background","0.472156","0.9751","1.0","Zmm_Mll10_40_MAXHTPTV280_E_CMS_BFilter","Z+jetsLowMllBFilter","mumu"],
["364204","Background","2331.22","0.9751","1.0","Zee_Mll10_40_MAXHTPTV0_70_BVeto","Z+jetsLowMllBVeto","ee"],
["364205","Background","81.3577","0.9751","1.0","Zee_Mll10_40_MAXHTPTV0_70_BFilter","Z+jetsLowMllBFilter","ee"],
["364206","Background","44.9714","0.9751","1.0","Zee_Mll10_40_MAXHTPTV70_280_BVeto","Z+jetsLowMllBVeto","ee"],
["364207","Background","5.48142","0.9751","1.0","Zee_Mll10_40_MAXHTPTV70_280_BFilter","Z+jetsLowMllBFilter","ee"],
["364208","Background","2.77741","0.9751","1.0","Zee_Mll10_40_MAXHTPTV280_E_CMS_BVeto","Z+jetsLowMllBVeto","ee"],
["364209","Background","0.473086","0.9751","1.0","Zee_Mll10_40_MAXHTPTV280_E_CMS_BFilter","Z+jetsLowMllBFilter","ee"],
["364210","Background","2333.93","0.9751","1.0","Ztt_Mll10_40_MAXHTPTV0_70_BVeto","Z+jetsLowMllBVeto","tautau"],
["364211","Background","81.1026","0.9751","1.0","Ztt_Mll10_40_MAXHTPTV0_70_BFilter","Z+jetsLowMllBFilter","tautau"],
["364212","Background","44.8369","0.9751","1.0","Ztt_Mll10_40_MAXHTPTV70_280_BVeto","Z+jetsLowMllBVeto","tautau"],
["364213","Background","5.54094","0.9751","1.0","Ztt_Mll10_40_MAXHTPTV70_280_BFilter","Z+jetsLowMllBFilter","tautau"],
["364214","Background","2.79355","0.9751","1.0","Ztt_Mll10_40_MAXHTPTV280_E_CMS_BVeto","Z+jetsLowMllBVeto","tautau"],
["364215","Background","0.469721","0.9751","1.0","Ztt_Mll10_40_MAXHTPTV280_E_CMS_BFilter","Z+jetsLowMllBFilter","tautau"],
["410000","Background","696.12","1.1949","0.543","PowhegPythiaEvtGen_P2012_ttbar_hdamp172p5_nonallhad","tops","ttbar_nonallhad"],
["410011","Background","43.739","1.0","1.0094","PowhegPythiaEvtGen_P2012_singletop_tchan_lept_top","tops","singlet"],
["410012","Background","25.778","1.0","1.0193","PowhegPythiaEvtGen_P2012_singletop_tchan_lept_antitop","tops","singlet"],
["410013","Background","34.009","1.0","1.054","PowhegPythiaEvtGen_P2012_Wt_inclusive_top","tops","tW"],
["410014","Background","33.989","1.0","1.054","PowhegPythiaEvtGen_P2012_Wt_inclusive_antitop","tops","tW"],
["410025","Background","2.0517","1.005","1.0","PowhegPythiaEvtGen_P2012_SingleTopSchan_noAllHad_top","tops","SingleTopSchan_noAllHad"],
["410026","Background","1.2615","1.022","1.0","PowhegPythiaEvtGen_P2012_SingleTopSchan_noAllHad_antitop","tops","SingleTopSchan_noAllHad"],
["410050","Background","0.24013","1","1.0","MadGraphPythia_tZ_4fl_tchan_noAllHad","tops","tZ"],
["410080","Background","0.0091622","1.0042","1.0","MadGraphPythia8EvtGen_A14NNPDF23_4topSM","tops","4top"],
["410081","Background","0.0080975","1.2231","1.0","MadGraphPythia8EvtGen_A14NNPDF23_ttbarWW","tops","ttWW"],
["410082","Background","2.982","1.47","1.0","MadGraphPythia8EvtGen_A14NNPDF23LO_ttgamma_noallhad","tops","ttgamma"],
["410155","Background","0.548300","1.10","1.0","aMcAtNloPythia8EvtGen_MEN30NLO_A14N23LO_ttW","tops","ttW_aMcAtNlo"],
["410156","Background","0.154990","1.11","1.0","aMcAtNloPythia8EvtGen_MEN30NLO_A14N23LO_ttZnunu","tops","ttZnunu_aMcAtNlo"],
["410157","Background","0.527710","1.11","1.0","aMcAtNloPythia8EvtGen_MEN30NLO_A14N23LO_ttZqq","tops","ttZqq_aMcAtNlo"],
["410215","Background","0.015558","1.0","1.0","aMcAtNloPythia8EvtGen_A14_NNPDF23LO_260000_tWZDR","tops","tWZDR"],
["410218","Background","0.036888","1.12","1.0","aMcAtNloPythia8EvtGen_MEN30NLO_A14N23LO_ttee","tops","ttee_aMcAtNlo"],
["410219","Background","0.036895","1.12","1.0","aMcAtNloPythia8EvtGen_MEN30NLO_A14N23LO_ttmumu","tops","ttmumu_aMcAtNlo"],
["410220","Background","0.036599","1.12","1.0","aMcAtNloPythia8EvtGen_MEN30NLO_A14N23LO_tttautau","tops","tttautau_aMcAtNlo"],
["410501","Background","396.49","1.1391","1.0","PowhegPythia8EvtGen_A14_ttbar_hdamp258p75_nonallhad","tops","ttbar_nonallhad_Pythia8"],
["410502","Background","249.81","1.5216","1.0","PowhegPythia8EvtGen_A14_ttbar_hdamp258p75_allhad","tops","ttbar_allhad_Pythia8"],
["410503","Background","76.93","1.1392","1.0","PowhegPythia8EvtGen_A14_ttbar_hdamp258p75_dil","tops","ttbar_dil_Pythia8"],
]

execpath  = os.path.abspath(os.path.curdir)
inputpath = "/coepp/cephfs/mel/mmilesi/ttH/GFW2MiniNTup/25ns_v28/25ns_v28/01/gfw2"
destpath  = inputpath + "/CoEPP_PlotFormat_reduced_v28"

copy_friends_only = True

for s in samplelist:
    pattern = "*" if not copy_friends_only else "*friend*"
    thisdir = inputpath
    if s[7] == "physics_Main":
        thisdir += "/Data/{0}".format(pattern)
    elif s[7] == "fakes_mm":
        thisdir += "/Fakes/{0}".format(pattern)
    else:
        thisdir += "/Nominal/{0}{1}".format(s[0],pattern)
    cmd = "rsync -azP {0} {1}/".format(thisdir,destpath)
    subprocess.call(cmd,shell=True)

os.chdir(destpath)
filelist = [ f for f in glob.glob("*.root*") ]
if copy_friends_only:
    filelist = [ f for f in glob.glob("*.root*") if "friend" in f ] # Copy only friend trees

print filelist
os.chdir(execpath)

for f in filelist:
    this_id = f[:f.index('.')]
    for s in samplelist:
        if this_id == s[0] or this_id == s[5]:
            sampledir = destpath+"/"+s[6]
            if not os.path.exists(sampledir):
                os.makedirs(sampledir)
            i = destpath+"/"+f
            if s[0]:
                if "friend" in f:
                    o = sampledir+"/"+s[0]+"."+s[5]+".root.reduced.friend"
                else:
                    o = sampledir+"/"+s[0]+"."+s[5]+".root"
            else:
                if "friend" in f:
                    o = sampledir+"/"+s[5]+".root.reduced.friend"
                else:
                    o = sampledir+"/"+s[5]+".root"
            shutil.move(i,o)

