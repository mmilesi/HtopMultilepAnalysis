#######################################
# full xAOD - mc15 13TeV  
# ----------------------
#test-HTopMultilep --inDSType DxAOD-2015-13TeV --inDir /data/mmilesi/HTopMultileptonsTestSamples/MC15/ --inDSName mc15_13TeV.410000.PowhegPythiaEvtGen_P2012_ttbar_hdamp172p5_nonallhad.merge.AOD.e3698_s2608_s2183_r6630_r6264_tid05382618_00 --outDir out_xAOD_HTopMultilep_mc --maxEvents 10
#######################################
# data15 13TeV DAOD - Week 1 
# --------------------------
#test-HTopMultilep --inDSType DxAOD-2015-13TeV --inDir /data/mmilesi/HTopMultileptonsTestSamples/HIGG8D1_20.1.5.1/ --inDSName data15_13TeV.00267073.physics_Main.merge.DAOD_HIGG8D1.f594_m1435_p2361 --outDir out_xAOD_HTopMultilep_data --maxEvents -1
#######################################
# mc15 13TeV DAOD HIGG8D1 
# ----------------------
#test-HTopMultilep --inDSType DxAOD-2015-13TeV --inDir /data/mmilesi/HTopMultileptonsTestSamples/HIGG8D1_20.1.5.1/ --inDSName mc15_13TeV.410000.PowhegPythiaEvtGen_P2012_ttbar_hdamp172p5_nonallhad.merge.DAOD_HIGG8D1.e3698_s2608_s2183_r6630_r6264_p2363_tid05629971_00 --outDir out_DxAOD_HTopMultilep_mc --maxEvents 10000
#test-HTopMultilep --inDSType DxAOD-2015-13TeV --inDir /data/mmilesi/HTopMultileptonsTestSamples/HIGG8D1_20.1.5.1/ --inDSName mc15_13TeV.361106.PowhegPythia8EvtGen_AZNLOCTEQ6L1_Zee.merge.DAOD_HIGG8D1.e3601_s2576_s2132_r6630_r6264_p2363 --outDir out_DxAOD_HTopMultilep_mc --maxEvents 10000
#test-HTopMultilep --inDSType DxAOD-2015-13TeV --inDir /data/mmilesi/HTopMultileptonsTestSamples/HIGG8D1_20.1.5.1_FullTruth/ --inDSName mc15_13TeV.410000.PowhegPythiaEvtGen_P2012_ttbar_hdamp172p5_nonallhad.merge.DAOD_HIGG8D1.e3698_s2608_s2183_r6630_r6264_p2363 --outDir out_DxAOD_HTopMultilep_mc --maxEvents -1
test-HTopMultilep --inDSType DxAOD-2015-13TeV --inDir /data/mmilesi/HTopMultileptonsTestSamples/crash_Zee/ --inDSName mc15_13TeV --outDir out_DxAOD_HTopMultilep_mc --maxEvents 1000 
#######################################
