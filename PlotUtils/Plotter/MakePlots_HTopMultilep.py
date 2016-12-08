#!/usr/bin/env python

""" MakePlots_HTopMultilep.py: plotting script for the HTopMultilep Run 2 analysis """

__author__     = "Marco Milesi, Francesco Nuti"
__email__      = "marco.milesi@cern.ch, francesco.nuti@cern.ch"
__maintainer__ = "Marco Milesi"

import os, sys, math, array

sys.path.append(os.path.abspath(os.path.curdir))

# -------------------------------
# Parser for command line options
# -------------------------------
import argparse

parser = argparse.ArgumentParser(description='Plotting script for the HTopMultilep Run 2 analysis')

#***********************************
# positional arguments (compulsory!)
#***********************************

parser.add_argument('inputDir', metavar='inputDir',type=str,
                   help='Path to the directory containing input files')

#*******************
# optional arguments
#*******************

list_available_channel    = ["TwoLepSR","ThreeLepSR","FourLepSR","MMRates(,DATA,CLOSURE,NO_CORR,LH,TRUTH_TP,SUSY_TP,DATAMC,PROBE_TM,PROBE_NOT_TM)",
                             "TwoLepLowNJetCR", "ThreeLepLowNJetCR",
                             "WZonCR", "WZoffCR", "WZHFonCR", "WZHFoffCR",
                             "ttWCR", "ttZCR","ZSSpeakCR", "DataMC", "MMClosureTest(,NO_CORR,HIGHNJ,LOWNJ,ALLNJ)",
                             "CutFlowChallenge(,MM,2LepSS,2LepSS1Tau,3Lep)","MMSidebands(,NO_CORR,CLOSURE,HIGHNJ,LOWNJ,ALLNJ)","TriggerEff"]
list_available_fakemethod = ["MC","MM","FF","THETA"]
list_available_flavcomp   = ["OF","SF","INCLUSIVE","ICHEP_2016","TEST"]

jet_multiplicity_opt = ["HIGHNJ","LOWNJ","ALLNJ"]

luminosities = { "Moriond 2016 GRL":3.209,            # March 2016
                 "ICHEP 2015+2016 DS":13.20768,       # August 2016
                 "POST-ICHEP 2015+2016 DS":22.07036,  # October 2016
                 "FULL 2015+2016 DS":36.4702          # December 2016
               }

triggers = ["SLT","DLT"]

parser.add_argument('--samplesCSV', dest='samplesCSV',action='store',const='Files/samples_HTopMultilep_Priority1.csv',default='Files/samples_HTopMultilep_Priority1.csv',type=str,nargs='?',
                    help='Path to the .csv file containing the processes of interest with their cross sections and other metadata. If this option is unspecified, or it is not followed by any command-line argument, default will be \"Files/samples_HTopMultilep_Priority1.csv\"')
parser.add_argument('--debug', dest='debug', action='store_true', default=False,
                    help='Run in debug mode')
parser.add_argument('--lumi', dest='lumi', action='store', type=float, default=luminosities["FULL 2015+2016 DS"],
                    help="The luminosity of the dataset. Pick one of these values: ==> " + ",".join( "{0} ({1})".format( lumi, tag ) for tag, lumi in luminosities.iteritems() ) + ". Default is {0}".format(luminosities["FULL 2015+2016 DS"] ) )
parser.add_argument('--trigger', dest='trigger', action='store', default=triggers[0], type=str, nargs='+',
                    help='The trigger strategy to be used. Choose one of:\n{0}.\nIf this option is not specified, default is {1}'.format(triggers,triggers[0]))
parser.add_argument('--channel', dest='channel', action='store', default='TwoLepSR', type=str, nargs='+',
                    help='The channel chosen. Full list of available options:\n{1}'.format(jet_multiplicity_opt,list_available_channel))
parser.add_argument('--ratesMC', dest='ratesMC', action='store_true', default=False,
                    help='Distributions to get rates/efficiencies from pure simulation. Use w/ option --channel=MMRates')
parser.add_argument('--useMCQMisID', dest='useMCQMisID', action='store_true', default=False,
                    help='Use Monte-Carlo based estimate of QMisID')
parser.add_argument('--MCCompRF', dest='MCCompRF', action='store_true', default=False,
                    help='Plot simulation estimate in real/fake efficiency CRs. Use w/ option --channel=MMRates')
parser.add_argument('--outdirname', dest='outdirname', action='store', default='', type=str,
                    help='Specify a name to append to the output directory')
parser.add_argument('--fakeMethod', dest='fakeMethod', action='store', default=None, type=str,
                    help='The fake estimation method chosen ({0}). Default is None'.format(list_available_fakemethod))
parser.add_argument('--lepFlavComp', dest='lepFlavComp', action='store', default="ICHEP_2016", type=str,
                    help='Flavour composition in the CRs used for r/f efficiency measurement. Use w/ option --channel=MMRates. Default is \"ICHEP_2016\". ({0})'.format(list_available_flavcomp))
parser.add_argument('--doShowRatio', action='store_true', dest='doShowRatio', default=False,
                    help='Show ratio plot with data/expected')
parser.add_argument('--mergeOverflow', dest='mergeOverflow', action='store_true', default=False,
                    help='Merge the overflow bin to the last visible bin. Default is False.')
parser.add_argument('--doLogScaleX', dest='doLogScaleX', action='store_true',
                    help='Use log scale on the X axis')
parser.add_argument('--doLogScaleY', dest='doLogScaleY', action='store_true',
                    help='Use log scale on the Y axis')
parser.add_argument('--doSyst', dest='doSyst', action='store_true',
                    help='Run systematics')
parser.add_argument('--noSignal', action='store_true', dest='noSignal',
                    help='Exclude signal')
parser.add_argument('--noWeights', action='store_true', dest='noWeights', default=False,
                    help='Do not apply any weight, correction. Also the Xsec weight and mcEvtWeight are reset to 1. This is used e.g. to get raw cutflow.')
parser.add_argument('--noStandardPlots', action='store_true', dest='noStandardPlots',
                    help='Exclude all standard plots')
parser.add_argument('--doQMisIDRate', dest='doQMisIDRate', action='store_true',
                    help='Measure charge flip rate in MC (to be used with --channel=MMRates CLOSURE)')
parser.add_argument('--doUnblinding', dest='doUnblinding', action='store_true', default=False,
                    help='Unblind data in SRs')
parser.add_argument('--printEventYields', dest='printEventYields', action='store_true', default=False,
                    help='Prints out event yields in tabular form (NB: can be slow)')
parser.add_argument('--useMoriondTruth', dest='useMoriondTruth', action='store_true', default=False,
                    help='Use 2016 Moriond-style truth matching (aka, just rely on type/origin info)')
parser.add_argument('--optimisation', dest='optimisation', action='store', default=None, type=str, nargs='+',
                    help='Optimise cuts. At the moment, performs 1D optimisation on pT(lep1) only if \"SLT\" option is passed, 2D optimisation on pT(lep0),pT(lep1) if \"DLT\" option is passed')
parser.add_argument('--trigAcceptance', action='store', dest='trigAcceptance', const='TIGHT', default=None, nargs='?',
                    help='Use 2LepSS SR selection to make study on trigger acceptance. Can specify whether to use a \"TIGHT\" or \"LOOSE\" selection. If option string is present, but command-line argument is not specified, default is \"TIGHT\".')

args = parser.parse_args()

# -----------------
# Some ROOT imports
# -----------------

from ROOT import gROOT, gStyle, gPad
from ROOT import TH1I, TH1D, TH2D, TH2F, TH2I, TMath, TFile, TAttFill, TColor, kBlack, kWhite, kGray, kBlue, kRed, kYellow, kAzure, kTeal, kSpring, kOrange, kGreen, kCyan, kViolet, kMagenta, kPink, Double
from ROOT import TCanvas, TPaveText, TGraph, TGraph2D, TGraphErrors, TColor

def calculate_Z( s, b, err_s, err_b ):

    Z = math.sqrt( 2.0 * ( ( s + b ) * math.log( 1.0 + s/b ) - s ) )

    dZ_ds = ( -1.0 + ( b + s )/( b * ( 1.0 + s/b ) ) + math.log( 1 + s/b ) ) / ( math.sqrt(2.0) * math.sqrt( -s + ( b + s ) * math.log( 1.0 + s/b ) ) )
    dZ_db = ( -( s * ( b + s ) )/( b*b * ( 1.0 + s/b ) ) + math.log( 1.0 + s/b ) ) / ( math.sqrt(2.0) * math.sqrt( -s + ( b + s ) * math.log( 1.0 + s/b ) ) )

    err_Z = math.sqrt( ( dZ_ds * dZ_ds ) * ( err_s * err_s ) + ( dZ_db * dZ_db ) *( err_b * err_b ) )

    return (Z, err_Z)


def plot_significance( Z_dict, dim ):

    gROOT.SetBatch(True)

    for key, value in Z_dict.iteritems():

        print("pT-SORTED:\nkey: {0}".format(key) + ",\n(lep_Pt_0,lep_Pt_1) cut: [" + ",".join( "({0},{1})".format(val[0],val[1]) for val in sorted(value) )  + "],\nZ: [" + ",".join( "{0:.3f} +- {1:.3f}".format(val[2],val[3]) for val in sorted(value) ) + "]\n")

        if dim == "1D":

            bins  = [ val[1] for val in sorted(value) ]
            Z     = [ val[2] for val in sorted(value) ]
            Z_err = [ val[3] for val in sorted(value) ]

            import ROOT

            graph_significance = TGraphErrors( len(value), array.array("f", bins ), array.array("f", Z ), ROOT.nullptr,  array.array("f", Z_err ) )
            graph_significance.SetName(key)
            graph_significance.GetXaxis().SetTitle("p_{T}^{2nd lead lep} [GeV]")
            graph_significance.GetYaxis().SetTitle("Z significance")
            graph_significance.SetLineWidth(2)
            graph_significance.SetMarkerStyle(20)
            graph_significance.SetMarkerSize(1.3)
            graph_significance.SetMarkerColor(2)

            c = TCanvas("c_Z_Significance_lep_Pt_1_"+ key,"Z")

            graph_significance.Draw("ACP")

            max_Z = max( value, key=(lambda val : val[2]) )
            print("Z max: {0:.3f} +- {1:.3f} ({2}{3})\n".format(max_Z[2], max_Z[3], max_Z[0], max_Z[1]))

            text = TPaveText(0.22,0.80,0.50,0.87,"blNDC")
            text.AddText("Z_{{max}}: {0:.2f} #pm {1:.2f} ({2},{3})".format(max_Z[2], max_Z[3], max_Z[0], max_Z[1]))
            text.Paint("NDC")
            text.Draw()

            c.SaveAs(os.path.abspath(os.path.curdir) + "/" + basedirname + "Z_Significance_lep_Pt_1_"+key+".png")

        elif dim == "2D":

            graph_significance = TGraph2D()

            for idx, val in enumerate(sorted(value)):
                graph_significance.SetPoint(idx, val[0], val[1], val[2])

            graph_significance.SetName(key)

            set_fancy_2D_style()

            c = TCanvas("c_Z_Significance_lep_Pt_0_lep_Pt_1_"+ key,"Z")

            gPad.SetRightMargin(0.2)

	    graph_significance.Draw("COLZ")

            max_Z = max( value, key=(lambda val : val[2]) )

            print("Z max: {0:.3f} +- {1:.3f} ({2},{3})".format(max_Z[2], max_Z[3], max_Z[0], max_Z[1]))

            text = TPaveText(0.22,0.80,0.50,0.87,"blNDC")
            text.AddText("Z_{{max}}: {0:.2f} #pm {1:.2f} ({2},{3})".format(max_Z[2], max_Z[3], max_Z[0], max_Z[1]))
            text.SetFillColor(0)
	    text.Paint("NDC")
            text.Draw()

	    gPad.Update()
            graph_significance.GetXaxis().SetTitle("p_{T}^{lead lep} [GeV]")
            graph_significance.GetYaxis().SetTitle("p_{T}^{2nd lead lep} [GeV]")

            c.SaveAs(os.path.abspath(os.path.curdir) + "/" + basedirname + "Z_Significance_lep_Pt_0_lep_Pt_1_"+key+".png")


# ---------------------------------------------------------------------
# Importing all the tools and the definitions used to produce the plots
# ---------------------------------------------------------------------

from Plotter.BackgroundTools import loadSamples, Category, Background, Process, VariableDB, Variable, Cut, Systematics, Category, set_fancy_2D_style

# ---------------------------------------------------------------------------
# Importing the classes for the different processes.
# They contains many info on the normalization and treatment of the processes
# ---------------------------------------------------------------------------

from Plotter.Backgrounds_HTopMultilep import MyCategory, TTHBackgrounds

if __name__ == "__main__":

    try:
        args.channel in list_available_channel
    except ValueError:
        sys.exit("the channel specified (", args.channel ,") is incorrect. Must be one of: ", list_available_channel)

    doTwoLepSR              = bool( "TwoLepSR" in args.channel )
    doThreeLepSR            = bool( "ThreeLepSR" in args.channel )
    doFourLepSR             = bool( "FourLepSR" in args.channel )
    doMMRates               = bool( "MMRates" in args.channel )
    doTwoLepLowNJetCR       = bool( "TwoLepLowNJetCR" in args.channel )
    doThreeLepLowNJetCR     = bool( "ThreeLepLowNJetCR" in args.channel )
    doWZonCR                = bool( "WZonCR" in args.channel )
    doWZoffCR               = bool( "WZoffCR" in args.channel )
    doWZHFonCR              = bool( "WZHFonCR" in args.channel )
    doWZHFoffCR             = bool( "WZHFoffCR" in args.channel )
    dottWCR                 = bool( "ttWCR" in args.channel )
    dottZCR                 = bool( "ttZCR" in args.channel )
    doZSSpeakCR             = bool( "ZSSpeakCR" in args.channel )
    doDataMCCR              = bool( "DataMC" in args.channel )
    doMMClosureTest         = bool( "MMClosureTest" in args.channel )
    doCFChallenge           = bool( "CutFlowChallenge" in args.channel )
    doMMSidebands           = bool( "MMSidebands" in args.channel )
    doTriggerEff            = bool( "TriggerEff" in args.channel )

    print( "input directory: {0}\n".format(args.inputDir) )
    print( "channel = {0}\n".format(args.channel) )

    # -----------------------------------------
    # a comprehensive flag for all possible SRs
    # -----------------------------------------
    doSR = (doTwoLepSR or doThreeLepSR or doFourLepSR)

    # -----------------------------------------
    # a comprehensive flag for the low-Njet CR
    # -----------------------------------------
    doLowNJetCR = (doTwoLepLowNJetCR or doThreeLepLowNJetCR)

    # ------------------------------------------
    # a comprehensive flag for all the other CRs
    # ------------------------------------------
    doOtherCR = (doWZonCR or doWZoffCR or doWZHFonCR or doWZHFoffCR or dottWCR or dottZCR or doZSSpeakCR or doMMRates or doDataMCCR or doMMClosureTest or doCFChallenge or doMMSidebands or doTriggerEff )

    # ------------------------------------------------
    # make standard plots unless differently specified
    # ------------------------------------------------
    doStandardPlots = False if (args.noStandardPlots) else (doSR or doLowNJetCR or doOtherCR)

    # ----------------------------
    # Check fake estimation method
    # ----------------------------

    try:
        args.fakeMethod in list_available_fakemethod
    except ValueError:
        sys.exit("the Fake Method specified (", args.fakeMethod ,") is incorrect. Must be one of ", list_available_fakemethod)

    doMM    = bool( args.fakeMethod == "MM" )
    doFF    = bool( args.fakeMethod == "FF" )
    doTHETA = bool( args.fakeMethod == "THETA" )
    doMC    = bool( args.fakeMethod == "MC" )

    # -----------------------------------------------------
    # Check lepton flavour composition of the dilepton pair
    # for efficiency measurement
    # -----------------------------------------------------

    try:
        args.lepFlavComp in list_available_flavcomp
    except ValueError:
        sys.exit("ERROR: the lepton flavour composition of the 2Lep pair is incorrect. Must be one of ", list_available_flavcomp)

    # ----------------------------------------------------
    # When in debug mode, print out all the input commands
    # ----------------------------------------------------
    if ( args.debug ):
        print args

    # --------------------------
    # Retrieve the input samples
    # --------------------------
    inputs = loadSamples(
        # path of the data to be processed
        inputdir    = args.inputDir,
        samplescsv  = args.samplesCSV,
        nomtree     = "physics",
        # name of the trees that contains values for shifted systematics
        systrees =  [
            ##'METSys',
            #'ElEnResSys',
            #'ElES_LowPt',
            #'ElES_Zee',
            #'ElES_R12',
            #'ElES_PS',
            ##'EESSys',
            #'MuSys',
            ##'METResSys',
            ##'METScaleSys',
            #'JES_Total',
            #'JER',
            ],
        )

    # ------------------------------------------------------
    # Here you include all names of variables to be plotted,
    # with min, max, number of bins and ntuple name.
    # ------------------------------------------------------

    vardb = VariableDB()

    # -----------------------------------------------------
    # The list of event-level TCuts
    #
    # WARNING:
    # To avoid unexpected behaviour,
    # ALWAYS enclose the cut string in '()'!!!
    #
    # -----------------------------------------------------

    # ---------------------
    # General cuts
    # ---------------------

    vardb.registerCut( Cut('DummyCut',    '( 1 )') )

    #vardb.registerCut( Cut('BlindingCut', '( isBlinded == 0 )') ) # <--- use this cut to get blinded results!
    vardb.registerCut( Cut('BlindingCut', '( 1 )') )
    if args.doUnblinding:
        vardb.getCut('BlindingCut').cutstr = '( 1 )'

    vardb.registerCut( Cut('IsMC', '( mc_channel_number != 0 )') )

    # -------
    # Trigger
    # -------

    # Lowest unprescaled SLT in ICHEP DS have 24 GeV threshold

    e_SLT = "( ( RunYear == 2015 && ( HLT_e24_lhmedium_L1EM20VH || HLT_e60_lhmedium || HLT_e120_lhloose ) ) || ( RunYear == 2016 && ( HLT_e24_lhtight_nod0_ivarloose || HLT_e60_lhmedium_nod0 || HLT_e140_lhloose_nod0 ) ) )"
    m_SLT = "( ( RunYear == 2015 && ( HLT_mu20_iloose_L1MU15 || HLT_mu50 ) ) || ( RunYear == 2016 && ( HLT_mu24_ivarmedium || HLT_mu50 ) ) )"

    if any( vers in args.inputDir for vers in ["v21","v23","v24"]):

	# Lowest unprescaled SLT in POST-ICHEP DS have 26 GeV threshold

	e_SLT = "( ( RunYear == 2015 && ( HLT_e24_lhmedium_L1EM20VH || HLT_e60_lhmedium || HLT_e120_lhloose ) ) || ( RunYear == 2016 && ( HLT_e26_lhtight_nod0_ivarloose || HLT_e60_lhmedium_nod0 || HLT_e140_lhloose_nod0 ) ) )"
	m_SLT = "( ( RunYear == 2015 && ( HLT_mu20_iloose_L1MU15 || HLT_mu50 ) ) || ( RunYear == 2016 && ( HLT_mu26_ivarmedium || HLT_mu50 ) ) )"

    ee_DLT = "( ( RunYear == 2015 && HLT_2e12_lhloose_L12EM10VH ) || ( RunYear == 2016 && HLT_2e17_lhvloose_nod0 ) )"
    mm_DLT = "( ( RunYear == 2015 && HLT_mu18_mu8noL1 ) || ( RunYear == 2016 && HLT_mu22_mu8noL1 ) )"
    of_DLT = "( ( RunYear == 2015 && ( HLT_e24_medium_L1EM20VHI_mu8noL1 || HLT_e7_medium_mu24 ) ) || ( RunYear == 2016 && HLT_e17_lhloose_nod0_mu14 ) )"

    if "SLT" in args.trigger:

        vardb.registerCut( Cut("TrigDec", "( " + e_SLT + " || " + m_SLT + " )" ) )

    elif "DLT" in args.trigger:

        # use DLT for all categories
	#
        vardb.registerCut( Cut("TrigDec", "( " + "( dilep_type == 1 && " + mm_DLT + " )" + " || " + "( dilep_type == 2 && " + of_DLT + " )" + " || " + "( dilep_type == 3 && " + ee_DLT + " )" + " )" ) )
        #
	# use DLT for ee, mm, OR of SLT for OF
	#
        #vardb.registerCut( Cut("TrigDec", "( " + "( dilep_type == 1 && " + mm_DLT + " )" + " || " + "( dilep_type == 2 && ( " + e_SLT + " || " + m_SLT + " ) )" + " || " + "( dilep_type == 3 && " + ee_DLT + " )" + " )" ) )

    vardb.registerCut( Cut('LargeNBJet',      '( nJets_OR_T_MV2c10_70 > 1 )') )
    vardb.registerCut( Cut('VetoLargeNBJet',  '( nJets_OR_T_MV2c10_70 < 4 )') )
    vardb.registerCut( Cut('BJetVeto',        '( nJets_OR_T_MV2c10_70 == 0 )') )
    vardb.registerCut( Cut('OneBJet',         '( nJets_OR_T_MV2c10_70 == 1 )') )
    vardb.registerCut( Cut('TauVeto',         '( nTaus_OR_Pt25 == 0 )') )
    vardb.registerCut( Cut('OneTau',          '( nTaus_OR_Pt25 == 1 )') )

    # ---------------------
    # 2Lep SS + 0 tau cuts
    # ---------------------

    # ----------------
    # Trigger matching
    # ----------------

    if "SLT" in args.trigger:

        vardb.registerCut( Cut('2Lep_TrigMatch','( lep_isTrigMatch_0 || lep_isTrigMatch_1 )') )

    elif "DLT" in args.trigger:

        # In NTuples < v21, no trigger matching for DLT available: just require pT in efficiency plateau
        #
        vardb.registerCut( Cut('2Lep_TrigMatch', '( ( dilep_type == 1 && ( ( RunYear == 2015 && HLT_2mu10 == 1 && lep_Pt_0 > 11e3 && lep_Pt_1 > 11e3 ) || ( RunYear == 2016 && HLT_2mu14 == 1 && lep_Pt_0 > 15e3 && lep_Pt_1 > 15e3 ) ) ) || ( dilep_type == 2 && ( ( RunYear == 2015 && HLT_e17_loose_mu14 == 1 ) || ( RunYear == 2016 && HLT_e17_lhloose_mu14 == 1 ) ) && ( ( TMath::Abs( lep_ID_0 ) == 11 && lep_Pt_0 > 18e3 && lep_Pt_1 > 15e3 ) || (  TMath::Abs( lep_ID_0 ) == 13 && lep_Pt_0 > 15e3 && lep_Pt_1 > 18e3 ) ) ) || ( dilep_type == 3 && ( ( RunYear == 2015 && HLT_2e12_lhloose_L12EM10VH == 1 && lep_Pt_0 > 13e3 && lep_Pt_1 > 13e3 ) || ( RunYear == 2016 && HLT_2e15_lhvloose_nod0_L12EM13VH == 1 && lep_Pt_0 > 16e3 && lep_Pt_1 > 16e3 ) ) ) )') )

	if any( vers in args.inputDir for vers in ["v21","v23","v24"]):

            # use DLT for all categories
            #
            vardb.getCut('2Lep_TrigMatch').cutstr = '( lep_isTrigMatchDLT_0 == 1 && lep_isTrigMatchDLT_1 == 1 )' # Require BOTH leptons to be matched
            #
            # use DLT for ee, mm, OR of SLT for OF
            #
            #vardb.getCut('2Lep_TrigMatch').cutstr = '( ( ( dilep_type == 1 || dilep_type == 3 ) && ( lep_isTrigMatchDLT_0 == 1 && lep_isTrigMatchDLT_1 == 1 ) ) || ( dilep_type == 2 && ( lep_isTrigMatchDLT_0 == 1 && lep_isTrigMatchDLT_1 == 1 ) ) )'

    vardb.registerCut( Cut('2Lep_NBJet',                  '( nJets_OR_T_MV2c10_70 > 0 )') )
    vardb.registerCut( Cut('2Lep_NBJet_SR',		  '( nJets_OR_T_MV2c10_70 > 0 )') )
    vardb.registerCut( Cut('2Lep_MinNJet',		  '( nJets_OR_T > 1 )') )
    vardb.registerCut( Cut('2Lep_NJet_SR',		  '( nJets_OR_T > 4 )') )
    vardb.registerCut( Cut('2Lep_NJet_CR',		  '( nJets_OR_T > 1 && nJets_OR_T <= 4 )') )
    vardb.registerCut( Cut('2Lep_NJet_CR_SStt', 	  '( nJets_OR_T < 4 )') )
    vardb.registerCut( Cut('2Lep_SS',			  '( lep_ID_0 * lep_ID_1 > 0 )') )
    vardb.registerCut( Cut('2Lep_OS',			  '( !( lep_ID_0 * lep_ID_1 > 0 ) )') )
    vardb.registerCut( Cut('2Lep_NLep', 		  '( dilep_type > 0 )') )
    vardb.registerCut( Cut('2Lep_pT',			  '( lep_Pt_0 > 25e3 && lep_Pt_1 > 25e3 )') )
    vardb.registerCut( Cut('2Lep_pT_MMRates',		  '( lep_Pt_0 > 10e3 && lep_Pt_1 > 10e3 )') )
    vardb.registerCut( Cut('2Lep_pT_Relaxed',		  '( lep_Pt_0 > 25e3 && lep_Pt_1 > 10e3 )') )
    vardb.registerCut( Cut('2Lep_SF_Event',		  '( dilep_type == 1 || dilep_type == 3 )') )
    vardb.registerCut( Cut('2Lep_MuMu_Event',		  '( dilep_type == 1 )') )
    vardb.registerCut( Cut('2Lep_ElEl_Event',		  '( dilep_type == 3 )') )
    vardb.registerCut( Cut('2Lep_OF_Event',		  '( dilep_type == 2 )') )
    vardb.registerCut( Cut('2Lep_MuEl_Event',		  '( dilep_type == 2 && TMath::Abs( lep_ID_0 ) == 13  )') )
    vardb.registerCut( Cut('2Lep_ElMu_Event',		  '( dilep_type == 2 && TMath::Abs( lep_ID_0 ) == 11  )') )
    vardb.registerCut( Cut('2Lep_Zsidescut',              '( ( dilep_type != 3 ) || ( dilep_type == 3 && TMath::Abs( Mll01 - 91.2e3 ) > 7.5e3 ) )' ) )   # Use this to require the 2 SF electrons to be outside Z peak
    vardb.registerCut( Cut('2Lep_Zpeakcut',               '( ( dilep_type == 2 ) || ( TMath::Abs( Mll01 - 91.2e3 ) < 30e3  ) )' ) )       # Use this to require the 2 SF leptons to be around Z peak
    vardb.registerCut( Cut('2Lep_Zmincut',                '( ( dilep_type == 2 ) || ( Mll01  > 20e3 ) )' ) )   # Remove J/Psi, Upsilon peak

    gROOT.LoadMacro("$ROOTCOREBIN/user_scripts/HTopMultilepAnalysis/ROOT_TTreeFormulas/largeEtaEvent.cxx+")
    from ROOT import largeEtaEvent

    vardb.registerCut( Cut('2Lep_ElEtaCut',               '( largeEtaEvent( dilep_type,lep_ID_0,lep_ID_1,lep_EtaBE2_0,lep_EtaBE2_1 ) == 0 )') )

    # -------------------
    # Tag and probe stuff
    # -------------------

    vardb.registerCut( Cut('2Lep_LepTagTightTrigMatched', '( lep_Tag_isTightSelected == 1 && lep_Tag_isTrigMatch == 1 )') )
    vardb.registerCut( Cut('2Lep_LepTagTrigMatched',      '( lep_Tag_isTrigMatch == 1 )') )
    vardb.registerCut( Cut('2Lep_LepProbeTrigMatched',    '( lep_Probe_isTrigMatch == 1 )') )
    vardb.registerCut( Cut('2Lep_ElProbe',  	          '( TMath::Abs( lep_Probe_ID ) == 11 )') )
    vardb.registerCut( Cut('2Lep_MuProbe',  	          '( TMath::Abs( lep_Probe_ID ) == 13 )') )
    vardb.registerCut( Cut('2Lep_ProbeTight',	          '( lep_Probe_isTightSelected == 1 )') )
    vardb.registerCut( Cut('2Lep_ProbeAntiTight',	  '( lep_Probe_isTightSelected == 0 )') )
    vardb.registerCut( Cut('2Lep_TagAndProbe_GoodEvent',  '( 1 )') )
    vardb.registerCut( Cut('2Lep_ElTagEtaCut',            '( ( TMath::Abs( lep_Tag_ID ) == 13 ) || ( TMath::Abs( lep_Tag_ID ) == 11 && TMath::Abs( lep_Tag_EtaBE2 ) < 1.37 ) )') )

    if any( vers in args.inputDir for vers in ["v21","v23","v24"]):

        if "SLT" in args.trigger:

	    vardb.getCut('2Lep_LepTagTightTrigMatched').cutstr = '( lep_Tag_SLT_isTightSelected == 1 && lep_Tag_SLT_isTrigMatch == 1 )'
	    vardb.getCut('2Lep_LepTagTrigMatched').cutstr      = '( lep_Tag_SLT_isTrigMatch == 1 )'
            vardb.getCut('2Lep_LepProbeTrigMatched').cutstr    = '( lep_Probe_SLT_isTrigMatch == 1 )'
            vardb.getCut('2Lep_ElProbe').cutstr                = '( TMath::Abs( lep_Probe_SLT_ID ) == 11 )'
            vardb.getCut('2Lep_MuProbe').cutstr                = '( TMath::Abs( lep_Probe_SLT_ID ) == 13 )'
            vardb.getCut('2Lep_ProbeTight').cutstr             = '( lep_Probe_SLT_isTightSelected == 1 )'
            vardb.getCut('2Lep_ProbeAntiTight').cutstr         = '( lep_Probe_SLT_isTightSelected == 0 )'
	    vardb.getCut('2Lep_TagAndProbe_GoodEvent').cutstr  = '( event_isBadTP_SLT == 0 )'
            vardb.getCut('2Lep_ElTagEtaCut').cutsr             = '( ( TMath::Abs( lep_Tag_SLT_ID ) == 13 ) || ( TMath::Abs( lep_Tag_SLT_ID ) == 11 && TMath::Abs( lep_Tag_SLT_EtaBE2 ) < 1.37 ) )'

        elif "DLT" in args.trigger:

	    vardb.getCut('2Lep_LepTagTightTrigMatched').cutstr = '( lep_Tag_DLT_isTightSelected == 1 && lep_Tag_DLT_isTrigMatch == 1 )'
            vardb.getCut('2Lep_LepTagTrigMatched').cutstr      = '( lep_Tag_DLT_isTrigMatch == 1 )'
            vardb.getCut('2Lep_LepProbeTrigMatched').cutstr    = '( lep_Probe_DLT_isTrigMatch == 1 )'
            vardb.getCut('2Lep_ElProbe').cutstr                = '( TMath::Abs( lep_Probe_DLT_ID ) == 11 )'
            vardb.getCut('2Lep_MuProbe').cutstr                = '( TMath::Abs( lep_Probe_DLT_ID ) == 13 )'
            vardb.getCut('2Lep_ProbeTight').cutstr             = '( lep_Probe_DLT_isTightSelected == 1 )'
            vardb.getCut('2Lep_ProbeAntiTight').cutstr         = '( lep_Probe_DLT_isTightSelected == 0 )'
	    vardb.getCut('2Lep_TagAndProbe_GoodEvent').cutstr  = '( event_isBadTP_DLT == 0 )'
            vardb.getCut('2Lep_ElTagEtaCut').cutsr             = '( ( TMath::Abs( lep_Tag_DLT_ID ) == 13 ) || ( TMath::Abs( lep_Tag_DLT_ID ) == 11 && TMath::Abs( lep_Tag_DLT_EtaBE2 ) < 1.37 ) )'

        if "SUSY_TP" in args.channel:

            if "SLT" in args.trigger:
                vardb.getCut('2Lep_LepTagTightTrigMatched').cutstr = '( event_isBadTP_SLT == 0 )'
            elif "DLT" in args.trigger:
	        vardb.getCut('2Lep_LepTagTightTrigMatched').cutstr = '( event_isBadTP_DLT == 0 )'

            # SUSY T&P uses vector branches for el and mu: do not specify the flavour of the probe
            # (this is particularly crucial for the Real CR, where in the ambiguous "both T&TM leptons" case there is no distinction between T&P)

            vardb.getCut('2Lep_ElProbe').cutstr = '( 1 )'
            vardb.getCut('2Lep_MuProbe').cutstr = '( 1 )'

    # -----------------
    # Event "tightness"
    # -----------------

    vardb.registerCut( Cut('TT',      '( is_T_T == 1 )') )
    vardb.registerCut( Cut('TL',      '( is_T_AntiT == 1 )') )
    vardb.registerCut( Cut('LT',      '( is_AntiT_T == 1 )') )
    vardb.registerCut( Cut('TL_LT',   '( is_T_AntiT == 1 || is_AntiT_T == 1 )') )
    vardb.registerCut( Cut('LL',      '( is_AntiT_AntiT == 1 )') )
    vardb.registerCut( Cut('TelLmu',  '( is_Tel_AntiTmu == 1 )') )
    vardb.registerCut( Cut('LelTmu',  '( is_AntiTel_Tmu == 1 )') )
    vardb.registerCut( Cut('TmuLel',  '( is_Tmu_AntiTel == 1 )') )
    vardb.registerCut( Cut('LmuTel',  '( is_AntiTmu_Tel == 1 )') )

    if args.trigAcceptance == "LOOSE":
        vardb.getCut('TT').cutstr = '( 1 )'

    # ---------------------------
    # Cuts for ttW Control Region
    # ---------------------------

    # >= 2 btag
    # <= 3 jets
    # HT(jets) > 220 GeV in ee and emu
    # Z peak [+- 15 GeV] veto in ee
    # MET > 50 GeV in ee

    vardb.registerCut( Cut('2Lep_HTJ_ttW',        '( dilep_type == 1 || HT_jets > 220e3 )') )
    vardb.registerCut( Cut('2Lep_MET_ttW',        '( dilep_type != 3 || ( MET_RefFinal_et > 50e3 ) )') )
    vardb.registerCut( Cut('2Lep_Zsidescut_ttW',  '( dilep_type != 3 || ( TMath::Abs( Mll01 - 91.2e3 ) > 15e3 ) )') )
    vardb.registerCut( Cut('2Lep_NJet_ttW',       '( nJets_OR_T <= 4 )') )
    vardb.registerCut( Cut('2Lep_NBJet_ttW',      '( nJets_OR_T_MV2c10_70 >= 2 )') )
    vardb.registerCut( Cut('2Lep_Zmincut_ttW',    '( Mll01 > 40e3 )'))

    # -------------------
    # TRUTH MATCHING CUTS
    # -------------------
    #
    # The following cuts must be used only on MC :
    #
    #   -) plot only prompt-matched MC to avoid double counting of non prompt
    #      (as they are estimated via MM or FF)
    #   -) in case there are electrons in the regions, also brem electrons must be taken into account
    #   -) what is left must be charge flip
    #
    # Use these cuts to plot specific MC contaminations in:
    #
    #   -) SR and low njet CR
    #     (here you want the pure prompt MC contribution
    #      to be plotted in SR/low-jet CR if
    #      fakes and charge flips are already taken into account
    #      by rescaling the data)
    #
    #   -) CR for FAKE rate measurement
    #      (here you want to plot whatever is NON-non-prompt,
    #       which then you will subtract to data for the fake rate estimate)
    #
    # Values of MC truth matching flags ( i.e., 'truthType', 'truthOrigin' ) are defined in MCTruthClassifier:
    #
    # https://svnweb.cern.ch/trac/atlasoff/browser/PhysicsAnalysis/MCTruthClassifier/trunk/MCTruthClassifier/MCTruthClassifierDefs.h
    #
    # -------------------------------------------------------------------------------

    if args.useMoriondTruth:

        vardb.registerCut( Cut('2Lep_TRUTH_PurePromptEvent',             '( ( mc_channel_number == 0 ) || ( ( ( lep_truthType_0 == 2 || lep_truthType_0 == 6 ) && ( lep_truthType_1 == 2 || lep_truthType_1 == 6 ) ) ) )') )
        vardb.registerCut( Cut('2Lep_TRUTH_NonPromptEvent',              '( ( mc_channel_number == 0 ) || ( ( ( !( lep_truthType_0 == 2 || lep_truthType_0 == 6 ) || !( lep_truthType_1 == 2 || lep_truthType_1 == 6 ) ) && !( lep_truthType_0 == 4 && lep_truthOrigin_0 == 5 ) && !( lep_truthType_1 == 4 && lep_truthOrigin_1 == 5 ) ) ) )') )
        vardb.registerCut( Cut('2Lep_TRUTH_QMisIDVeto',                  '( ( mc_channel_number == 0 ) || ( ( !( lep_truthType_0 == 4 && lep_truthOrigin_0 == 5 ) && !( lep_truthType_1 == 4 && lep_truthOrigin_1 == 5 ) ) ) )') )

        vardb.registerCut( Cut('2Lep_TRUTH_ProbePromptEvent',	         '( ( mc_channel_number == 0 ) || ( ( lep_Probe_truthType == 2 || lep_Probe_truthType == 6 ) ) )') )
        vardb.registerCut( Cut('2Lep_TRUTH_ProbeNonPromptOrQMisIDEvent', '( ( mc_channel_number == 0 ) || ( !( lep_Probe_truthType == 2 || lep_Probe_truthType == 6 ) ) )') )
        vardb.registerCut( Cut('2Lep_TRUTH_ProbeNonPromptEvent',	 '( ( mc_channel_number == 0 ) || ( ( !( lep_Probe_truthType == 2 || lep_Probe_truthType == 6 ) && !( lep_Probe_truthType == 4 && lep_Probe_truthOrigin == 5 ) ) ) )') )

    else:

        # 1.
        #
        # Event passes this cut if ALL leptons are prompt (MCTruthClassifier --> Iso), and none is charge flip
        # We classify as 'prompt' also a 'brems' lepton whose charge has been reconstructed with the correct sign
        #
        vardb.registerCut( Cut('2Lep_TRUTH_PurePromptEvent', '( ( mc_channel_number == 0 ) || ( ( ( lep_isPrompt_0 == 1 || ( lep_isBrems_0 == 1 && lep_isQMisID_0 == 0 ) ) && ( lep_isPrompt_1 == 1 || ( lep_isBrems_1 == 1 && lep_isQMisID_1 == 0 ) ) ) && ( isQMisIDEvent == 0 ) ) )') )
        #
        # 2.
        #
        # Event passes this cut if AT LEAST ONE lepton is !prompt (MCTruthClassifier --> !Iso), and none is charge flip
        # (i.e., the !prompt lepton will be ( HF lepton || photon conv || lepton from Dalitz decay || mis-reco jet...)
        # We classify as 'prompt' also a 'brems' lepton whose charge has been reconstructed with the correct sign
        #
	vardb.registerCut( Cut('2Lep_TRUTH_NonPromptEvent', '( ( mc_channel_number == 0 ) || ( ( ( lep_isPrompt_0 == 0 && !( lep_isBrems_0 == 1 && lep_isQMisID_0 == 0 ) ) || ( lep_isPrompt_1 == 0 && !( lep_isBrems_1 == 1 && lep_isQMisID_1 == 0 ) ) ) && ( isQMisIDEvent == 0 ) ) )') )
        #
        # 3.
        #
        # Event passes this cut if AT LEAST ONE lepton is charge flip (does not distinguish trident VS charge-misreconstructed)
        #
        vardb.registerCut( Cut('2Lep_TRUTH_QMisIDEvent',    '( ( mc_channel_number == 0 ) || ( ( isQMisIDEvent == 1 ) ) )') )
        #
        # 3a.
        #
        # Event passes this cut if AT LEAST ONE lepton is (prompt and charge flip) (it will be a charge-misId charge flip)
        #
        vardb.registerCut( Cut('2Lep_TRUTH_QMisIDPromptEvent',  '( ( mc_channel_number == 0 ) || ( ( ( lep_isQMisID_0 == 1 && lep_isPrompt_0 == 1 ) || ( lep_isQMisID_1 == 1 && lep_isPrompt_1 == 1 ) ) ) )') )
        #
        # 3b.
        #
        # Event passes this cut if AT LEAST ONE object is charge flip from bremsstrahlung (this will be a trident charge flip)
        #
        vardb.registerCut( Cut('2Lep_TRUTH_QMisIDBremEvent', '( ( mc_channel_number == 0 ) || ( ( ( lep_isBrems_0 == 1 && lep_isQMisID_0 == 1 ) || ( lep_isBrems_1 == 1 && lep_isQMisID_1 == 1 ) ) ) )') )
        #
        # 3c.
        #
        # Event passes this cut if AT LEAST ONE lepton is (!prompt and charge flip)
        #
        vardb.registerCut( Cut('2Lep_TRUTH_QMisIDNonPromptEvent', '( ( mc_channel_number == 0 ) || ( ( ( lep_isQMisID_0 == 1 && lep_isPrompt_0 == 0 ) || ( lep_isQMisID_1 == 1 && lep_isPrompt_1 == 0 ) ) ) )') )
        #
        # 4.
        #
        # Event passes this cut if NONE of the leptons is charge flip
        #
        vardb.registerCut( Cut('2Lep_TRUTH_QMisIDVeto', '( ( mc_channel_number == 0 ) || ( isQMisIDEvent == 0 ) )') )
        #
        # 4.a
        #
        # Event passes this cut if NONE of the leptons is charge flip / from photon conversion
        #
        vardb.registerCut( Cut('2Lep_TRUTH_QMisIDANDConvPhVeto',   '( ( mc_channel_number == 0 ) || ( isQMisIDEvent == 0 && isLepFromPhEvent == 0 ) )') )
        #
        # 5.
        #
        # Event passes this cut if AT LEAST ONE lepton is from a primary photon conversion
        #
        vardb.registerCut( Cut('2Lep_TRUTH_LepFromPhEvent', '( ( mc_channel_number == 0 ) || ( isLepFromPhEvent == 1 ) )') )
        #
        # 6.
        #
        # Event passes this cut if AT LEAST ONE lepton is charge flip OR from a primary photon conversion
        #
        vardb.registerCut( Cut('2Lep_TRUTH_QMisIDORLepFromPhEvent', '( ( mc_channel_number == 0 ) || ( ( isQMisIDEvent == 1 || isLepFromPhEvent == 1 ) ) )') )
        #
        # 6a.
        # Event passes this cut if AT LEAST ONE lepton is coming from ISR/FSR photon
        #
        vardb.registerCut( Cut('2Lep_TRUTH_ISRPhEvent',  '( ( mc_channel_number == 0 ) || ( ( lep_isISRFSRPh_0 == 1 || lep_isISRFSRPh_1 == 1 ) ) )') )

        # ------------------------------------------------------------------------------
        # The following cuts enforce truth requirements only on the probe lepton for T&P
        # ------------------------------------------------------------------------------

        vardb.registerCut( Cut('2Lep_TRUTH_ProbePromptEvent',            '( ( mc_channel_number == 0 ) || ( ( ( lep_Probe_isPrompt == 1 || ( lep_Probe_isBrems == 1 && lep_Probe_isQMisID == 0 ) ) && lep_Probe_isQMisID == 0 ) ) )') )
        vardb.registerCut( Cut('2Lep_TRUTH_ProbeNonPromptEvent',         '( ( mc_channel_number == 0 ) || ( ( ( lep_Probe_isPrompt == 0 && !( lep_Probe_isBrems == 1 && lep_Probe_isQMisID == 0 ) ) && lep_Probe_isQMisID == 0 ) ) )') )
        vardb.registerCut( Cut('2Lep_TRUTH_ProbeNonPromptOrQMisIDEvent', '( ( mc_channel_number == 0 ) || ( ( ( lep_Probe_isPrompt == 0 && !( lep_Probe_isBrems == 1 && lep_Probe_isQMisID == 0 ) ) || lep_Probe_isQMisID == 1 ) ) )') )
        vardb.registerCut( Cut('2Lep_TRUTH_ProbeQMisIDEvent',            '( ( mc_channel_number == 0 ) || ( ( lep_Probe_isQMisID == 1 ) ) )') )
        vardb.registerCut( Cut('2Lep_TRUTH_ProbeLepFromPhEvent',         '( ( mc_channel_number == 0 ) || ( ( lep_Probe_isConvPh == 1 || lep_Probe_isISRFSRPh_0 == 1 ) ) )') )

	if any( vers in args.inputDir for vers in ["v21","v23","v24"]):

	     if "SLT" in args.trigger:

             	 vardb.getCut('2Lep_TRUTH_ProbePromptEvent').cutstr            = '( ( mc_channel_number == 0 ) || ( ( ( lep_Probe_SLT_isPrompt == 1 || ( lep_Probe_SLT_isBrems == 1 && lep_Probe_SLT_isQMisID == 0 ) ) && lep_Probe_SLT_isQMisID == 0 ) ) )'
             	 vardb.getCut('2Lep_TRUTH_ProbeNonPromptEvent').cutstr         = '( ( mc_channel_number == 0 ) || ( ( ( lep_Probe_SLT_isPrompt == 0 && !( lep_Probe_SLT_isBrems == 1 && lep_Probe_SLT_isQMisID == 0 ) ) && lep_Probe_SLT_isQMisID == 0 ) ) )'
             	 vardb.getCut('2Lep_TRUTH_ProbeNonPromptOrQMisIDEvent').cutstr = '( ( mc_channel_number == 0 ) || ( ( ( lep_Probe_SLT_isPrompt == 0 && !( lep_Probe_SLT_isBrems == 1 && lep_Probe_SLT_isQMisID == 0 ) ) || lep_Probe_SLT_isQMisID == 1 ) ) )'
             	 vardb.getCut('2Lep_TRUTH_ProbeQMisIDEvent').cutstr            = '( ( mc_channel_number == 0 ) || ( ( lep_Probe_SLT_isQMisID == 1 ) ) )'
             	 vardb.getCut('2Lep_TRUTH_ProbeLepFromPhEvent').cutstr         = '( ( mc_channel_number == 0 ) || ( ( lep_Probe_SLT_isConvPh == 1 || lep_Probe_SLT_isISRFSRPh_0 == 1 ) ) )'

	     elif "DLT" in args.trigger:

             	 vardb.getCut('2Lep_TRUTH_ProbePromptEvent').cutstr            = '( ( mc_channel_number == 0 ) || ( ( ( lep_Probe_DLT_isPrompt == 1 || ( lep_Probe_DLT_isBrems == 1 && lep_Probe_DLT_isQMisID == 0 ) ) && lep_Probe_DLT_isQMisID == 0 ) ) )'
             	 vardb.getCut('2Lep_TRUTH_ProbeNonPromptEvent').cutstr         = '( ( mc_channel_number == 0 ) || ( ( ( lep_Probe_DLT_isPrompt == 0 && !( lep_Probe_DLT_isBrems == 1 && lep_Probe_DLT_isQMisID == 0 ) ) && lep_Probe_DLT_isQMisID == 0 ) ) )'
             	 vardb.getCut('2Lep_TRUTH_ProbeNonPromptOrQMisIDEvent').cutstr = '( ( mc_channel_number == 0 ) || ( ( ( lep_Probe_DLT_isPrompt == 0 && !( lep_Probe_DLT_isBrems == 1 && lep_Probe_DLT_isQMisID == 0 ) ) || lep_Probe_DLT_isQMisID == 1 ) ) )'
             	 vardb.getCut('2Lep_TRUTH_ProbeQMisIDEvent').cutstr            = '( ( mc_channel_number == 0 ) || ( ( lep_Probe_DLT_isQMisID == 1 ) ) )'
             	 vardb.getCut('2Lep_TRUTH_ProbeLepFromPhEvent').cutstr         = '( ( mc_channel_number == 0 ) || ( ( lep_Probe_DLT_isConvPh == 1 || lep_Probe_DLT_isISRFSRPh_0 == 1 ) ) )'

    # ---------
    # 3lep cuts
    # ---------

    vardb.registerCut( Cut('3Lep_NLep',         '( trilep_type > 0 )') )
    vardb.registerCut( Cut('3Lep_pT',           '( lep_Pt_0 > 10e3 && lep_Pt_1 > 20e3 && lep_Pt_2 > 20e3 )') )
    vardb.registerCut( Cut('3Lep_Charge',       '( TMath::Abs(total_charge) == 1 )') )
    vardb.registerCut( Cut('3Lep_TightLeptons', '( ( TMath::Abs( lep_Z0SinTheta_0 ) < 0.5 && ( TMath::Abs( lep_ID_0 ) == 13 && TMath::Abs( lep_sigd0PV_0 ) < 3.0 || TMath::Abs( lep_ID_0 ) == 11 && TMath::Abs( lep_sigd0PV_0 ) < 5.0 ) ) && ( ( TMath::Abs( lep_ID_1 ) == 13 && lep_isolationFixedCutTightTrackOnly_1 > 0 && TMath::Abs( lep_sigd0PV_1 ) < 3.0 ) || ( TMath::Abs( lep_ID_1 ) == 11 && lep_isolationFixedCutTight_1 > 0 && lep_isTightLH_1 > 0 && TMath::Abs( lep_sigd0PV_1 ) < 5.0 ) ) && ( ( TMath::Abs( lep_ID_2 ) == 13 && lep_isolationFixedCutTightTrackOnly_2 > 0 && TMath::Abs( lep_sigd0PV_2 ) < 3.0 ) || ( TMath::Abs( lep_ID_2 ) == 11 && lep_isolationFixedCutTight_2 > 0 && lep_isTightLH_2 > 0 && TMath::Abs( lep_sigd0PV_2 ) < 5.0 ) ) ) ') )
    vardb.registerCut( Cut('3Lep_TrigMatch',    '( lep_isTrigMatch_0 || lep_isTrigMatch_1 || lep_isTrigMatch_2 )') )
    vardb.registerCut( Cut('3Lep_ZVeto',        '( ( lep_ID_0 != -lep_ID_1 || TMath::Abs( Mll01 - 91.2e3 ) > 10e3 ) && ( lep_ID_0! = -lep_ID_2 || TMath::Abs( Mll02 - 91.2e3 ) > 10e3 ) )') )
    vardb.registerCut( Cut('3Lep_MinZCut',      '( ( lep_ID_0 != -lep_ID_1 || Mll01 > 12e3 ) && ( lep_ID_0 != -lep_ID_2 || Mll02 > 12e3 ) )') )
    vardb.registerCut( Cut('3Lep_NJets',        '( ( nJets_OR >= 4 && nJets_OR_MV2c10_70 >= 1 ) || ( nJets_OR >=3 && nJets_OR_MV2c10_70 >= 2 ) )') )

    # ---------------------
    # 4lep cuts
    # ---------------------

    # FIXME!
    vardb.registerCut( Cut('4Lep_NJets',  '( nJets_OR_T >= 2 )') )
    vardb.registerCut( Cut('4Lep',        '( nleptons == 4 )') )

    # ---------------------
    # 2Lep SS + 1 tau cuts
    # ---------------------

    vardb.registerCut( Cut('2Lep1Tau_NLep',         '( dilep_type > 0 )') )
    vardb.registerCut( Cut('2Lep1Tau_TightLeptons', '( is_T_T == 1 )') )
    vardb.registerCut( Cut('2Lep1Tau_pT',           '( lep_Pt_0 > 25e3 && lep_Pt_1 > 15e3  )') )
    vardb.registerCut( Cut('2Lep1Tau_TrigMatch',    '( lep_isTrigMatch_0|| lep_isTrigMatch_1 )') )
    vardb.registerCut( Cut('2Lep1Tau_SS',           '( lep_ID_0 * lep_ID_1 > 0 )') )
    vardb.registerCut( Cut('2Lep1Tau_1Tau',         '( nTaus_OR_Pt25 == 1 && ( lep_ID_0 * tau_charge_0 ) < 0 )') )
    vardb.registerCut( Cut('2Lep1Tau_Zsidescut',    '( dilep_type != 3 || TMath::Abs( Mll01 - 91.2e3 ) > 10e3 )' )  )
    vardb.registerCut( Cut('2Lep1Tau_NJet_SR',      '( nJets_OR_T >= 4 )') )
    vardb.registerCut( Cut('2Lep1Tau_NJet_CR',      '( nJets_OR_T > 1 && nJets_OR_T < 4 )') )
    vardb.registerCut( Cut('2Lep1Tau_NBJet',        '( nJets_OR_T_MV2c10_70 > 0 )') )

    # ---------------------------
    # A list of variables to plot
    # ---------------------------

    if args.doSyst:
        print("De-activating standard plots for systematics...")
        doStandardPlots = False

    # Reconstructed pT of the Z
    #
    pT_Z = '( TMath::Sqrt( (lep_Pt_0*lep_Pt_0) + (lep_Pt_1*lep_Pt_1) + 2*lep_Pt_0*lep_Pt_1*(TMath::Cos( lep_Phi_0 - lep_Phi_1 )) ) )/1e3'

    # Calculate DeltaR(lep0,lep1) in 2LepSS + 0 tau category
    #
    gROOT.LoadMacro("$ROOTCOREBIN/user_scripts/HTopMultilepAnalysis/ROOT_TTreeFormulas/deltaR.cxx+")
    from ROOT import deltaR
    delta_R_lep0lep1 = 'deltaR( lep_ID_0, lep_Eta_0, lep_EtaBE2_0, lep_Phi_0, lep_ID_1, lep_Eta_1, lep_EtaBE2_1, lep_Phi_1 )'
    delta_R_lep0lep2 = 'deltaR( lep_ID_0, lep_Eta_0, lep_EtaBE2_0, lep_Phi_0, lep_ID_2, lep_Eta_2, lep_EtaBE2_2, lep_Phi_2 )'
    delta_R_lep1lep2 = 'deltaR( lep_ID_1, lep_Eta_1, lep_EtaBE2_1, lep_Phi_1, lep_ID_2, lep_Eta_2, lep_EtaBE2_2, lep_Phi_2 )'

    if doSR or doLowNJetCR:
        print ''
        #vardb.registerVar( Variable(shortname = 'NJets', latexname = 'Jet multiplicity', ntuplename = 'nJets_OR_T', bins = 10, minval = -0.5, maxval = 9.5, weight = 'JVT_EventWeight') )
        if doSR:
            #vardb.registerVar( Variable(shortname = 'Lep0Pt_VS_Lep1Pt', latexnameX = 'p_{T}^{lead lep} [GeV]', latexnameY = 'p_{T}^{2nd lead lep} [GeV]', ntuplename = 'lep_Pt_1/1e3:lep_Pt_0/1e3', bins = 20, minval = 0.0, maxval = 60.0, typeval = TH2D) )
            #vardb.registerVar( Variable(shortname = 'Mu0Pt_VS_El0Pt', latexnameX = 'p_{T}^{#mu} [GeV]', latexnameY = 'p_{T}^{el} [GeV]', ntuplename = 'electron_Pt_0/1e3:muon_Pt_0/1e3', bins = 20, minval = 0.0, maxval = 60.0, typeval = TH2D) )
	    vardb.registerVar( Variable(shortname = 'NJets5j', latexname = 'Jet multiplicity', ntuplename = 'nJets_OR_T', bins = 6, minval = 3.5, maxval = 9.5, weight = "JVT_EventWeight") )
        elif doLowNJetCR:
            vardb.registerVar( Variable(shortname = 'NJets2j3j4j', latexname = 'Jet multiplicity', ntuplename = 'nJets_OR_T', bins = 4, minval = 1.5, maxval = 5.5) )
        #vardb.registerVar( Variable(shortname = 'NBJets', latexname = 'BJet multiplicity', ntuplename = 'nJets_OR_T_MV2c10_70', bins = 4, minval = -0.5, maxval = 3.5, weight = 'JVT_EventWeight * MV2c10_70_EventWeight') )
        #vardb.registerVar( Variable(shortname = 'Mll01_inc', latexname = 'm(l_{0}l_{1}) [GeV]', ntuplename = 'Mll01/1e3', bins = 13, minval = 0.0, maxval = 260.0,) )
        #vardb.registerVar( Variable(shortname = 'Lep0Eta', latexname = '#eta^{lead lep}', ntuplename = 'lep_Eta_0', bins = 16, minval = -2.6, maxval = 2.6) )
        #vardb.registerVar( Variable(shortname = 'Lep1Eta', latexname = '#eta^{2nd lead lep}', ntuplename = 'lep_Eta_1', bins = 16, minval = -2.6, maxval = 2.6) )
        #vardb.registerVar( Variable(shortname = 'Lep0Pt', latexname = 'p_{T}^{lead lep} [GeV]', ntuplename = 'lep_Pt_0/1e3', bins = 18, minval = 25.0, maxval = 205.0,) )
        #vardb.registerVar( Variable(shortname = 'Lep1Pt', latexname = 'p_{T}^{2nd lead lep} [GeV]', ntuplename = 'lep_Pt_1/1e3', bins = 6, minval = 25.0, maxval = 145.0,) )
        #vardb.registerVar( Variable(shortname = 'MET_FinalTrk', latexname = 'E_{T}^{miss} (FinalTrk) [GeV]', ntuplename = 'MET_RefFinal_et/1e3', bins = 9, minval = 0.0, maxval = 180.0,) )
        #vardb.registerVar( Variable(shortname = 'deltaRLep0Lep1', latexname = '#DeltaR(lep_{0},lep_{1})', ntuplename = delta_R_lep0lep1, bins = 10, minval = 0.0, maxval = 5.0) )

    if doMMSidebands:
        #vardb.registerVar( Variable(shortname = 'MMWeight', latexname = 'MM weight', ntuplename = 'MMWeight', bins = 50, minval = -0.5, maxval = 0.5) )
        #vardb.registerVar( Variable(shortname = 'Lep0Pt', latexname = 'p_{T}^{lead lep} [GeV]', ntuplename = 'lep_Pt_0/1e3', bins = 9, minval = 25.0, maxval = 205.0,) )
        vardb.registerVar( Variable(shortname = 'Lep0TM_VS_Lep1TM', latexnameX = 'lead lep TM', latexnameY = '2nd lead lep TM', ntuplename = 'lep_isTrigMatch_1:lep_isTrigMatch_0', bins = 2, minval = -0.5, maxval = 1.5, typeval = TH2F) )
        if "HIGHNJ" in args.channel:
            vardb.registerVar( Variable(shortname = 'NJets5j', latexname = 'Jet multiplicity', ntuplename = 'nJets_OR_T', bins = 6, minval = 3.5, maxval = 9.5, weight = 'JVT_EventWeight') )
        elif "LOWNJ" in args.channel:
            vardb.registerVar( Variable(shortname = 'NJets2j3j4j', latexname = 'Jet multiplicity', ntuplename = 'nJets_OR_T', bins = 4, minval = 1.5, maxval = 5.5, weight = 'JVT_EventWeight') )
        elif "ALLNJ" in args.channel:
            vardb.registerVar( Variable(shortname = 'NJets', latexname = 'Jet multiplicity', ntuplename = 'nJets_OR_T', bins = 8, minval = 1.5, maxval = 9.5, weight = 'JVT_EventWeight') )

    if doMMClosureTest:
        print ''
        if "ALLNJ" in args.channel:
            vardb.registerVar( Variable(shortname = 'NJets', latexname = 'Jet multiplicity', ntuplename = 'nJets_OR_T', bins = 8, minval = 1.5, maxval = 9.5, weight = 'JVT_EventWeight') )
        elif "HIGHNJ" in args.channel:
            vardb.registerVar( Variable(shortname = 'NJets5j', latexname = 'Jet multiplicity', ntuplename = 'nJets_OR_T', bins = 6, minval = 3.5, maxval = 9.5, weight = 'JVT_EventWeight') )
        elif "LOWNJ" in args.channel:
            vardb.registerVar( Variable(shortname = 'NJets2j3j4j', latexname = 'Jet multiplicity', ntuplename = 'nJets_OR_T', bins = 4, minval = 1.5, maxval = 5.5, weight = 'JVT_EventWeight') )
        #vardb.registerVar( Variable(shortname = 'NBJets', latexname = 'BJet multiplicity', ntuplename ='nJets_OR_T_MV2c10_70', bins = 4, minval = -0.5, maxval = 3.5, weight = 'JVT_EventWeight * MV2c10_70_EventWeight') )
        #vardb.registerVar( Variable(shortname = 'Mll01_inc', latexname = 'm(l_{0}l_{1}) [GeV]', ntuplename = 'Mll01/1e3', bins = 13, minval = 0.0, maxval = 260.0,) )
	vardb.registerVar( Variable(shortname = 'Lep0Pt', latexname = 'p_{T}^{lead lep} [GeV]', ntuplename = 'lep_Pt_0/1e3', bins = 10, minval = 25.0, maxval = 205.0) )
        #vardb.registerVar( Variable(shortname = 'Lep1Pt', latexname = 'p_{T}^{2nd lead lep} [GeV]', ntuplename = 'lep_Pt_1/1e3', bins = 6, minval = 25.0, maxval = 145.0) )
	#vardb.registerVar( Variable(shortname = 'Lep0Pt_ElBinning', latexname = 'p_{T}^{lead lep} [GeV]', ntuplename = 'lep_Pt_0/1e3', bins = 18, minval = 25.0, maxval = 205.0, manualbins = [25,40,60,100,200]) )
        #vardb.registerVar( Variable(shortname = 'Lep1Pt_ElBinning', latexname = 'p_{T}^{2nd lead lep} [GeV]', ntuplename = 'lep_Pt_1/1e3', bins = 18, minval = 25.0, maxval = 205.0, manualbins = [25,40,60,100,200]) )
        #vardb.registerVar( Variable(shortname = 'Lep0Pt_MuBinning', latexname = 'p_{T}^{lead lep} [GeV]', ntuplename = 'lep_Pt_0/1e3', bins = 18, minval = 25.0, maxval = 205.0, manualbins = [25,35,200]) )
        #vardb.registerVar( Variable(shortname = 'Lep1Pt_MuBinning', latexname = 'p_{T}^{2nd lead lep} [GeV]', ntuplename = 'lep_Pt_1/1e3', bins = 18, minval = 25.0, maxval = 205.0, manualbins = [25,35,200]) )
        #vardb.registerVar( Variable(shortname = 'MET_FinalTrk', latexname = 'E_{T}^{miss} (FinalTrk) [GeV]', ntuplename = 'MET_RefFinal_et/1e3', bins = 9, minval = 0.0, maxval = 180.0,) )
        #vardb.registerVar( Variable(shortname = 'deltaRLep0Lep1', latexname = '#DeltaR(lep_{0},lep_{1})', ntuplename = delta_R_lep0lep1, bins = 10, minval = 0.0, maxval = 5.0) )

    if doZSSpeakCR:
        print ''
        vardb.registerVar( Variable(shortname = 'Mll01_NarrowPeak', latexname = 'm(l_{0}l_{1}) [GeV]', ntuplename = 'Mll01/1e3', bins = 26, minval = 60.0, maxval = 125.0) )

    if doCFChallenge:
        print ''
        vardb.registerVar( Variable(shortname = 'NJets', latexname = 'Jet multiplicity', ntuplename = 'nJets_OR_T', bins = 10, minval = -0.5, maxval = 9.5, weight = 'JVT_EventWeight') )

    if doStandardPlots:
        print ''
        vardb.registerVar( Variable(shortname = 'NJets', latexname = 'Jet multiplicity', ntuplename = 'nJets_OR_T', bins = 8, minval = 1.5, maxval = 9.5, weight = 'JVT_EventWeight') )
        vardb.registerVar( Variable(shortname = 'NJets2j3j4j', latexname = 'Jet multiplicity', ntuplename = 'nJets_OR_T', bins = 4, minval = 1.5, maxval = 5.5, weight = 'JVT_EventWeight') )
        vardb.registerVar( Variable(shortname = 'NBJets', latexname = 'BJet multiplicity', ntuplename = 'nJets_OR_T_MV2c10_70', bins = 4, minval = -0.5, maxval = 3.5, weight = 'JVT_EventWeight * MV2c10_70_EventWeight') )
        vardb.registerVar( Variable(shortname = 'NJetsPlus10NBJets', latexname = 'N_{Jets}+10*N_{BJets}', ntuplename = 'nJets_OR_T+10.0*nJets_OR_T_MV2c10_70', bins = 40, minval = 0, maxval = 40, basecut = vardb.getCut('VetoLargeNBJet'), weight = 'JVT_EventWeight * MV2c10_70_EventWeight') )
        vardb.registerVar( Variable(shortname = 'NElectrons', latexname = 'Electron multiplicity', ntuplename = 'nelectrons', bins = 5, minval = -0.5, maxval = 4.5) )
        vardb.registerVar( Variable(shortname = 'NMuons', latexname = 'Muon multiplicity', ntuplename = 'nmuons', bins = 5, minval = -0.5, maxval = 4.5) )
        #
        # Inclusive m(ll) plot
        #
        vardb.registerVar( Variable(shortname = 'Mll01_inc', latexname = 'm(l_{0}l_{1}) [GeV]', ntuplename = 'Mll01/1e3', bins = 46, minval = 10.0, maxval = 240.0,) )
        #
        # Z peak plot
        #
        vardb.registerVar( Variable(shortname = 'Mll01_peak', latexname = 'm(l_{0}l_{1}) [GeV]', ntuplename = 'Mll01/1e3', bins = 40, minval = 40.0, maxval = 120.0,) )
        #
        vardb.registerVar( Variable(shortname = 'pT_Z', latexname = 'p_{T} Z (reco) [GeV]', ntuplename = pT_Z, bins = 100, minval = 0.0, maxval = 1000.0, logaxisX = True) )
        vardb.registerVar( Variable(shortname = 'Lep0Pt', latexname = 'p_{T}^{lead lep} [GeV]', ntuplename = 'lep_Pt_0/1e3', bins = 36, minval = 10.0, maxval = 190.0) )
        vardb.registerVar( Variable(shortname = 'Lep1Pt', latexname = 'p_{T}^{2nd lead lep} [GeV]', ntuplename = 'lep_Pt_1/1e3', bins = 20, minval = 10.0, maxval = 110.0) )
        vardb.registerVar( Variable(shortname = 'Lep0Eta', latexname = '#eta^{lead lep}', ntuplename = 'lep_Eta_0', bins = 16, minval = -2.6, maxval = 2.6) )
        vardb.registerVar( Variable(shortname = 'Lep1Eta', latexname = '#eta^{2nd lead lep}', ntuplename = 'lep_Eta_1', bins = 16, minval = -2.6, maxval = 2.6) )
        vardb.registerVar( Variable(shortname = 'deltaRLep0Lep1', latexname = '#DeltaR(lep_{0},lep_{1})', ntuplename = delta_R_lep0lep1, bins = 20, minval = 0.0, maxval = 5.0) )
        vardb.registerVar( Variable(shortname = 'deltaRLep0Lep2', latexname = '#DeltaR(lep_{0},lep_{2})', ntuplename = delta_R_lep0lep2, bins = 20, minval = 0.0, maxval = 5.0) )
        vardb.registerVar( Variable(shortname = 'deltaRLep1Lep2', latexname = '#DeltaR(lep_{1},lep_{2})', ntuplename = delta_R_lep1lep2, bins = 20, minval = 0.0, maxval = 5.0) )
        vardb.registerVar( Variable(shortname = 'Mll12', latexname = 'm(l_{1}l_{2}) [GeV]', ntuplename = 'Mll12/1e3', bins = 15, minval = 0.0, maxval = 300.0,) )
        vardb.registerVar( Variable(shortname = 'Jet0Pt', latexname = 'p_{T}^{lead jet} [GeV]', ntuplename = 'lead_jetPt/1e3', bins = 36, minval = 20.0, maxval = 200.0,) )
        vardb.registerVar( Variable(shortname = 'Jet0Eta', latexname = '#eta^{lead jet}', ntuplename = 'lead_jetEta', bins = 50, minval = -5.0, maxval = 5.0) )
        vardb.registerVar( Variable(shortname = 'avgint', latexname = 'Average Interactions Per Bunch Crossing', ntuplename = 'averageIntPerXing*1.16', bins = 50, minval = 0, maxval = 50, typeval = TH1I) )
        vardb.registerVar( Variable(shortname = 'MET_FinalTrk', latexname = 'E_{T}^{miss} (FinalTrk) [GeV]', ntuplename = 'MET_RefFinal_et/1e3', bins = 45, minval = 0.0, maxval = 180.0,) )
        vardb.registerVar( Variable(shortname = 'Tau0Pt', latexname = 'p_{T}^{lead tau} [GeV]', ntuplename = 'tau_pt_0', bins = 30, minval = 25.0, maxval = 100.0,) )

    # -------------------------------------------------
    # Alterantive ranges and binning for the histograms
    # -------------------------------------------------

    midstatsbin = {
        'MMC': (25, 0., 250.),
        'mvis': (25, 0., 250.),
        'mT': (30, 0., 120.),
        'MET': (25, 0., 100.),
        'leppt': (30, 17., 77.),
        'taupt': (25, 20., 70.),
        'jetpt': (25, 25., 125.),
    }
    lowstatsbin = {
        'MMC': (12, 0., 240.),
        'mvis': (12, 0., 240.),
        'mT': (12, 0., 120.),
        'MET': (12, 0., 120.),
        'leppt': (12, 17., 77.),
        'taupt': (12, 20., 80.),
        'jetpt': (12, 25., 121.),
    }

    # ---------------------
    # A list of systematics
    # ---------------------

    if args.doSyst:

        #vardb.registerSystematics( Systematics(name='PU',             eventweight='evtsel_sys_PU_rescaling_') )
        #vardb.registerSystematics( Systematics(name='el_reco',        eventweight='evtsel_sys_sf_el_reco_') )
        #vardb.registerSystematics( Systematics(name='el_id',          eventweight='evtsel_sys_sf_el_id_') )
        #vardb.registerSystematics( Systematics(name='el_iso',         eventweight='evtsel_sys_sf_el_iso_') )
        #vardb.registerSystematics( Systematics(name='mu_id',          eventweight='evtsel_sys_sf_mu_id_') )
        #vardb.registerSystematics( Systematics(name='mu_iso',         eventweight='evtsel_sys_sf_mu_iso_') )
        #vardb.registerSystematics( Systematics(name='lep_trig',       eventweight='evtsel_sys_sf_lep_trig_') )
        #vardb.registerSystematics( Systematics(name='bjet_b',         eventweight='evtsel_sys_sf_bjet_b_') )
        #vardb.registerSystematics( Systematics(name='bjet_c',         eventweight='evtsel_sys_sf_bjet_c_') )
        #vardb.registerSystematics( Systematics(name='bjet_m',         eventweight='evtsel_sys_sf_bjet_m_') )

        #vardb.registerSystematics( Systematics(name='METSys',         treename='METSys') )
        #vardb.registerSystematics( Systematics(name='ElEnResSys',     treename='ElEnResSys') )
        #vardb.registerSystematics( Systematics(name='ElES_LowPt',     treename='ElES_LowPt') )
        #vardb.registerSystematics( Systematics(name='ElES_Zee',       treename='ElES_Zee') )
        #vardb.registerSystematics( Systematics(name='ElES_R12',       treename='ElES_R12') )
        #vardb.registerSystematics( Systematics(name='ElES_PS',        treename='ElES_PS') )
        #vardb.registerSystematics( Systematics(name='EESSys',         treename='EESSys') )
        #vardb.registerSystematics( Systematics(name='MuSys',          treename='MuSys') )
        #vardb.registerSystematics( Systematics(name='JES_Total',      treename='JES_Total') )
        #vardb.registerSystematics( Systematics(name='JER',            treename='JER') )

        if doMMRates and "DATA" in args.channel:
            vardb.registerSystematics( Systematics(name='QMisIDsys', eventweight='QMisIDWeight_', process='QMisID') )

        # Efficiency binning for ICHEP - v19

	bins_real_el_pt = range(1,9)
        bins_real_mu_pt = range(1,9)
        bins_fake_el_pt = range(1,7)
        bins_fake_mu_pt = range(1,6)

        if doMMClosureTest:

	    if doMM:
		for ibin in bins_real_el_pt:
		   thiscat    = "MMsys_Real_El_Pt_Stat_" + str(ibin)
		   thisweight = "MMWeight_Real_El_Pt_Stat_" + str(ibin) + "_"
		   vardb.registerSystematics(Systematics(name=thiscat, eventweight=thisweight, process="FakesClosureMM"))
		for ibin in bins_real_mu_pt:
		   thiscat    = "MMsys_Real_Mu_Pt_Stat_" + str(ibin)
		   thisweight = "MMWeight_Real_Mu_Pt_Stat_" + str(ibin) + "_"
		   vardb.registerSystematics(Systematics(name=thiscat, eventweight=thisweight, process="FakesClosureMM"))
		for ibin in bins_fake_el_pt:
		   thiscat    = "MMsys_Fake_El_Pt_Stat_" + str(ibin)
		   thisweight = "MMWeight_Fake_El_Pt_Stat_" + str(ibin) + "_"
		   vardb.registerSystematics(Systematics(name=thiscat, eventweight=thisweight, process="FakesClosureMM"))
		for ibin in bins_fake_mu_pt:
		   thiscat    = "MMsys_Fake_Mu_Pt_Stat_" + str(ibin)
		   thisweight = "MMWeight_Fake_Mu_Pt_Stat_" + str(ibin) + "_"
		   vardb.registerSystematics(Systematics(name=thiscat, eventweight=thisweight, process="FakesClosureMM"))

	    if doFF:
                vardb.registerSystematics( Systematics(name="FFsys", eventweight="FFWeight_", process="FakesClosureMM") )

        if doTwoLepSR or doThreeLepSR or doTwoLepLowNJetCR or doThreeLepLowNJetCR:

	    #vardb.registerSystematics( Systematics(name="QMisIDsys", eventweight="QMisIDWeight_") )

	    if doMM:

		#sys_sources = ["Stat","numerator_QMisID","denominator_QMisID"]
		sys_sources = ["Stat"]

		for sys in sys_sources:
		   for ibin in bins_real_el_pt:
		       thiscat    = "MMsys_Real_El_Pt_" + sys + "_" + str(ibin)
		       thisweight = "MMWeight_Real_El_Pt_" + sys + "_" + str(ibin) + "_"
		       vardb.registerSystematics(Systematics(name=thiscat, eventweight=thisweight, process="FakesMM"))
		   for ibin in bins_real_mu_pt:
		       thiscat    = "MMsys_Real_Mu_Pt_" + sys + "_" + str(ibin)
		       thisweight = "MMWeight_Real_Mu_Pt_" + sys + "_" + str(ibin) + "_"
		       vardb.registerSystematics(Systematics(name=thiscat, eventweight=thisweight, process="FakesMM"))
		   for ibin in bins_fake_el_pt:
		       thiscat    = "MMsys_Fake_El_Pt_" + sys + "_" + str(ibin)
		       thisweight = "MMWeight_Fake_El_Pt_" + sys + "_" + str(ibin) + "_"
		       vardb.registerSystematics(Systematics(name=thiscat, eventweight=thisweight, process="FakesMM"))
		   for ibin in bins_fake_mu_pt:
		       thiscat    = "MMsys_Fake_Mu_Pt_" + sys + "_" + str(ibin)
		       thisweight = "MMWeight_Fake_Mu_Pt_" + sys + "_" + str(ibin) + "_"
		       vardb.registerSystematics(Systematics(name=thiscat, eventweight=thisweight, process="FakesMM"))

            if doFF:
                vardb.registerSystematics( Systematics(name="FFsys", eventweight="FFWeight_", process="FakesMM") )

    # -------------------------------------------------------------------
    # Definition of the categories for which one wants produce histograms
    # -------------------------------------------------------------------

    weight_SR_CR = "tauSFTight * weight_event_trig * weight_event_lep * JVT_EventWeight * MV2c10_70_EventWeight"

    # TEMP: remove trigger SF for trig acceptance studies b/c no dilepton SF available yet
    #
    if args.trigAcceptance:
        print("WARNING - Removing trigger SFs! Make sure it's really what you want...")
        weight_SR_CR = "tauSFTight * weight_event_lep * JVT_EventWeight * MV2c10_70_EventWeight"

    # ---
    # SRs
    # ---

    if doSR:

        if doTwoLepSR :

            if not args.optimisation:

                cat_name_mm = 'MuMuSS_SR'
                cat_name_ee = 'ElElSS_SR'
                cat_name_OF = 'OFSS_SR'
                cat_name_em = 'ElMuSS_SR'
                cat_name_me = 'MuElSS_SR'

                if ( doMM or doFF or doTHETA ):
                    cat_name_mm += '_DataDriven'
                    cat_name_ee += '_DataDriven'
                    cat_name_OF += '_DataDriven'
                    cat_name_em += '_DataDriven'
                    cat_name_me += '_DataDriven'

                if args.trigAcceptance:

		    # Trigger matching stuff
		    #
		    #vardb.registerCut( Cut('2Lep_TrigMatch_SLT','( lep_isTrigMatch_0 || lep_isTrigMatch_1 )') )
		    #vardb.registerCut( Cut('2Lep_TrigMatch_DLT','( lep_isTrigMatchDLT_0 || lep_isTrigMatchDLT_1 )') )
		    vardb.registerCut( Cut('2Lep_TrigMatch_SLT','( 1 )') )
		    vardb.registerCut( Cut('2Lep_TrigMatch_DLT','( 1 )') )

		    # NB:
		    #
		    # All the minimal pT threshold are chosen wrt the 2016 triggers only!

		    # -) MuMu

		    # DLT
                    #
		    vardb.registerCut( Cut('TrigDec_DLT_MuMu', '( ( RunYear == 2015 && HLT_mu18_mu8noL1 ) || ( RunYear == 2016 && HLT_mu22_mu8noL1 ) )') )
		    # SLT
                    #
		    vardb.registerCut( Cut('TrigDec_SLT_MuMu', '( ( RunYear == 2015 && ( HLT_mu20_iloose_L1MU15 || HLT_mu50 ) ) || ( RunYear == 2016 && ( HLT_mu26_ivarmedium || HLT_mu50 ) ) )') )
		    # DLT || SLT(m)
                    #
                    vardb.registerCut( Cut('TrigDec_DLT_OR_SLT_MuMu', '( ( RunYear == 2015 && ( HLT_mu20_iloose_L1MU15 || HLT_mu50 || HLT_mu18_mu8noL1 ) ) || ( RunYear == 2016 && ( HLT_mu26_ivarmedium || HLT_mu50 || HLT_mu22_mu8noL1 ) ) )') )

		    # Region A:  23 < pt(0) < 27; pt(1) > 10
		    #
		    vardb.registerCut( Cut('Pt_MuMu_A', '( lep_Pt_0 > 1.05*22e3 && lep_Pt_0 <= 1.05*26e3 && lep_Pt_1 > 10e3 )') )
 		    # Region B: pt(0) > 27; pt(1) > 10
		    #
		    vardb.registerCut( Cut('Pt_MuMu_B', '( lep_Pt_0 > 1.05*26e3 && lep_Pt_1 > 10e3 )') )
		    # Region A+B:  pt(0) > 23;  pt(1) > 10
		    #
		    vardb.registerCut( Cut('Pt_MuMu_AB', '( lep_Pt_0 > 1.05*22e3 && lep_Pt_1 > 10e3 )') )

                    vardb.registerCategory( MyCategory(cat_name_mm+"_DLT_A",	  cut = vardb.getCuts(['2Lep_TrigMatch_DLT','TrigDec_DLT_MuMu','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_MuMu_A','2Lep_SS','2Lep_MuMu_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_NJet_SR']), weight = weight_SR_CR ) )
                    vardb.registerCategory( MyCategory(cat_name_mm+"_DLT_B",	  cut = vardb.getCuts(['2Lep_TrigMatch_DLT','TrigDec_DLT_MuMu','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_MuMu_B','2Lep_SS','2Lep_MuMu_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_NJet_SR']), weight = weight_SR_CR ) )
                    vardb.registerCategory( MyCategory(cat_name_mm+"_SLT_B",	  cut = vardb.getCuts(['2Lep_TrigMatch_SLT','TrigDec_SLT_MuMu','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_MuMu_B','2Lep_SS','2Lep_MuMu_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_NJet_SR']), weight = weight_SR_CR ) )
                    vardb.registerCategory( MyCategory(cat_name_mm+"_DLT_OR_SLT", cut = vardb.getCuts(['2Lep_TrigMatch_SLT','TrigDec_DLT_OR_SLT_MuMu','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_MuMu_AB','2Lep_SS','2Lep_MuMu_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_NJet_SR']), weight = weight_SR_CR ) )

		    # -----------------------------------------

		    # -) ElEl

		    # DLT
                    #
		    vardb.registerCut( Cut('TrigDec_DLT_ElEl', '( ( RunYear == 2015 && HLT_2e12_lhloose_L12EM10VH ) || ( RunYear == 2016 && HLT_2e17_lhvloose_nod0 ) )') )
		    # SLT
                    #
                    vardb.registerCut( Cut('TrigDec_SLT_ElEl', '( ( RunYear == 2015 && ( HLT_e24_lhmedium_L1EM20VH || HLT_e60_lhmedium || HLT_e120_lhloose ) ) || ( RunYear == 2016 && ( HLT_e26_lhtight_nod0_ivarloose || HLT_e60_lhmedium_nod0 || HLT_e140_lhloose_nod0 ) ) )') )
		    # DLT || SLT(e)
                    #
                    vardb.registerCut( Cut('TrigDec_DLT_OR_SLT_ElEl', '( ( RunYear == 2015 && ( HLT_e24_lhmedium_L1EM20VH || HLT_e60_lhmedium || HLT_e120_lhloose || HLT_2e12_lhloose_L12EM10VH ) ) || ( RunYear == 2016 && ( HLT_e26_lhtight_nod0_ivarloose || HLT_e60_lhmedium_nod0 || HLT_e140_lhloose_nod0 || HLT_2e17_lhvloose_nod0 ) ) )') )

		    # Region A:  18 < pt(0) < 27; pt(1) > 18
		    #
		    vardb.registerCut( Cut('Pt_ElEl_A', '( lep_Pt_0 > 18e3 && lep_Pt_0 <= 27e3 && lep_Pt_1 > 18e3 )') )
 		    # Region B: pt(0) > 27; pt(1) > 18
		    #
		    vardb.registerCut( Cut('Pt_ElEl_B', '( lep_Pt_0 > 27e3 && lep_Pt_1 > 18e3 )') )
 		    # Region X: pt(0) > 27;  10 < pt(1) < 18 (low sensitivity)
		    vardb.registerCut( Cut('Pt_ElEl_X', '( lep_Pt_0 > 27e3 && lep_Pt_1 > 10e3 && lep_Pt_1 <= 18e3 )') )
		    # Region A+B:  pt(0) > 18;  pt(0) > 18
		    #
		    vardb.registerCut( Cut('Pt_ElEl_AB', '( lep_Pt_0 > 18e3 && lep_Pt_1 > 18e3 )') )

                    vardb.registerCategory( MyCategory(cat_name_ee+"_DLT_A",	   cut = vardb.getCuts(['2Lep_TrigMatch_DLT','TrigDec_DLT_ElEl','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_ElEl_A','2Lep_SS','2Lep_ElEl_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_NJet_SR','2Lep_ElEtaCut']), weight = weight_SR_CR ) )
                    vardb.registerCategory( MyCategory(cat_name_ee+"_DLT_B",	   cut = vardb.getCuts(['2Lep_TrigMatch_DLT','TrigDec_DLT_ElEl','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_ElEl_B','2Lep_SS','2Lep_ElEl_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_NJet_SR','2Lep_ElEtaCut']), weight = weight_SR_CR ) )
                    vardb.registerCategory( MyCategory(cat_name_ee+"_SLT_B",	   cut = vardb.getCuts(['2Lep_TrigMatch_SLT','TrigDec_SLT_ElEl','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_ElEl_B','2Lep_SS','2Lep_ElEl_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_NJet_SR','2Lep_ElEtaCut']), weight = weight_SR_CR ) )
                    vardb.registerCategory( MyCategory(cat_name_ee+"_DLT_OR_SLT",  cut = vardb.getCuts(['2Lep_TrigMatch_SLT','TrigDec_DLT_OR_SLT_ElEl','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_ElEl_AB','2Lep_SS','2Lep_ElEl_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_NJet_SR','2Lep_ElEtaCut']), weight = weight_SR_CR ) )
		    vardb.registerCategory( MyCategory(cat_name_ee+"_SLT_X",	   cut = vardb.getCuts(['2Lep_TrigMatch_SLT','TrigDec_SLT_ElEl','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_ElEl_X','2Lep_SS','2Lep_ElEl_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_NJet_SR','2Lep_ElEtaCut']), weight = weight_SR_CR ) )

		    # -----------------------------------------

		    # -) OF

		    # DLT
                    #
		    vardb.registerCut( Cut('TrigDec_DLT_OF',	  '( ( RunYear == 2015 && ( HLT_e24_medium_L1EM20VHI_mu8noL1 || HLT_e7_medium_mu24 ) ) || ( RunYear == 2016 && HLT_e17_lhloose_nod0_mu14 ) )') )
		    # SLT(e)
                    #
                    vardb.registerCut( Cut('TrigDec_SLT_e_OF',    '( ( RunYear == 2015 && ( HLT_e24_lhmedium_L1EM20VH || HLT_e60_lhmedium || HLT_e120_lhloose ) ) || ( RunYear == 2016 && ( HLT_e26_lhtight_nod0_ivarloose || HLT_e60_lhmedium_nod0 || HLT_e140_lhloose_nod0 ) ) )') )
		    # SLT(m)
                    #
		    vardb.registerCut( Cut('TrigDec_SLT_m_OF',    '( ( RunYear == 2015 && ( HLT_mu20_iloose_L1MU15 || HLT_mu50 ) ) || ( RunYear == 2016 && ( HLT_mu26_ivarmedium || HLT_mu50 ) ) )') )
		    # SLT(e) || SLT(m)
                    #
                    vardb.registerCut( Cut('TrigDec_SLT_eORm_OF', '( ( RunYear == 2015 && ( HLT_e24_lhmedium_L1EM20VH || HLT_e60_lhmedium || HLT_e120_lhloose || HLT_mu20_iloose_L1MU15 || HLT_mu50  ) ) || ( RunYear == 2016 && ( HLT_e26_lhtight_nod0_ivarloose || HLT_e60_lhmedium_nod0 || HLT_e140_lhloose_nod0 || HLT_mu26_ivarmedium || HLT_mu50 ) ) )') )
		    # DLT || SLT(e) || SLT(m)
                    #
                    vardb.registerCut( Cut('TrigDec_DLT_OR_SLT_OF', '( ( RunYear == 2015 && ( HLT_e24_lhmedium_L1EM20VH || HLT_e60_lhmedium || HLT_e120_lhloose || HLT_mu20_iloose_L1MU15 || HLT_mu50 || HLT_e24_medium_L1EM20VHI_mu8noL1 || HLT_e7_medium_mu24 ) ) || ( RunYear == 2016 && ( HLT_e26_lhtight_nod0_ivarloose || HLT_e60_lhmedium_nod0 || HLT_e140_lhloose_nod0 || HLT_mu26_ivarmedium || HLT_mu50 || HLT_e17_lhloose_nod0_mu14 ) ) )') )

		    # Region A:  15 < pt(m) < 27;  18 < pt(e) < 27
		    #
		    vardb.registerCut( Cut('Pt_OF_A', '( muon_Pt_0 > 1.05*14e3 && muon_Pt_0 <= 27e3 && electron_Pt_0 > 18e3 && electron_Pt_0 <= 27e3 )') )
 		    # Region B:  pt(m) > 27;  18 < pt(e) < 27
		    #
		    vardb.registerCut( Cut('Pt_OF_B', '( muon_Pt_0 > 1.05*26e3 && electron_Pt_0 > 18e3 && electron_Pt_0 <= 27e3 )') )
		    # Region C:  pt(m) > 27;  pt(e) > 27
		    #
		    vardb.registerCut( Cut('Pt_OF_C', '( muon_Pt_0 > 1.05*26e3 && electron_Pt_0 > 27e3 )') )
		    # Region D:  15 < pt(m) < 27;  pt(e) > 27
		    #
		    vardb.registerCut( Cut('Pt_OF_D', '( muon_Pt_0 > 1.05*14e3 && muon_Pt_0 <= 27e3 && electron_Pt_0 > 27e3 )') )
		    # Region X:  10 < pt(m) > 15;  pt(e) > 27 (low sensitivity)
		    #
		    vardb.registerCut( Cut('Pt_OF_X', '( muon_Pt_0 > 10e3 && muon_Pt_0 < 1.05*14e3 && electron_Pt_0 > 27e3 )') )
 		    # Region Y:  pt(m) > 27;  10 < pt(e) < 18 (low sensitivity)
		    #
		    vardb.registerCut( Cut('Pt_OF_Y', '( muon_Pt_0 > 1.05*26e3 && electron_Pt_0 > 10e3 && electron_Pt_0 < 18e3 )') )
		    # Region A+B+C+D:  pt(m) > 15;  pt(e) > 18
		    #
		    vardb.registerCut( Cut('Pt_OF_ABCD', '( muon_Pt_0 > 1.05*14e3 && electron_Pt_0 > 18e3 )') )

                    vardb.registerCategory( MyCategory(cat_name_OF+"_DLT_A",	  cut = vardb.getCuts(['2Lep_TrigMatch_DLT','TrigDec_DLT_OF','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_OF_A','2Lep_SS','2Lep_OF_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_SR']), weight = weight_SR_CR ) )
                    vardb.registerCategory( MyCategory(cat_name_OF+"_DLT_B",	  cut = vardb.getCuts(['2Lep_TrigMatch_DLT','TrigDec_DLT_OF','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_OF_B','2Lep_SS','2Lep_OF_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_SR']), weight = weight_SR_CR ) )
                    vardb.registerCategory( MyCategory(cat_name_OF+"_DLT_C",	  cut = vardb.getCuts(['2Lep_TrigMatch_DLT','TrigDec_DLT_OF','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_OF_C','2Lep_SS','2Lep_OF_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_SR']), weight = weight_SR_CR ) )
                    vardb.registerCategory( MyCategory(cat_name_OF+"_DLT_D",	  cut = vardb.getCuts(['2Lep_TrigMatch_DLT','TrigDec_DLT_OF','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_OF_D','2Lep_SS','2Lep_OF_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_SR']), weight = weight_SR_CR ) )

                    vardb.registerCategory( MyCategory(cat_name_OF+"_SLT_m_C",    cut = vardb.getCuts(['2Lep_TrigMatch_SLT','TrigDec_SLT_m_OF','2Lep_TrigMatch','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_OF_C','2Lep_SS','2Lep_OF_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_SR']), weight = weight_SR_CR ) )
                    vardb.registerCategory( MyCategory(cat_name_OF+"_SLT_m_B",    cut = vardb.getCuts(['2Lep_TrigMatch_SLT','TrigDec_SLT_m_OF','2Lep_TrigMatch','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_OF_B','2Lep_SS','2Lep_OF_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_SR']), weight = weight_SR_CR ) )
                    vardb.registerCategory( MyCategory(cat_name_OF+"_SLT_e_C",    cut = vardb.getCuts(['2Lep_TrigMatch_SLT','TrigDec_SLT_e_OF','2Lep_TrigMatch','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_OF_C','2Lep_SS','2Lep_OF_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_SR']), weight = weight_SR_CR ) )
                    vardb.registerCategory( MyCategory(cat_name_OF+"_SLT_e_D",    cut = vardb.getCuts(['2Lep_TrigMatch_SLT','TrigDec_SLT_e_OF','2Lep_TrigMatch','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_OF_D','2Lep_SS','2Lep_OF_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_SR']), weight = weight_SR_CR ) )

                    vardb.registerCategory( MyCategory(cat_name_OF+"_SLT_eORm_C", cut = vardb.getCuts(['2Lep_TrigMatch_SLT','TrigDec_SLT_eORm_OF','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_OF_C','2Lep_SS','2Lep_OF_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_SR']), weight = weight_SR_CR ) )

                    vardb.registerCategory( MyCategory(cat_name_OF+"_SLT_e_X",    cut = vardb.getCuts(['2Lep_TrigMatch_SLT','TrigDec_SLT_e_OF','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_OF_X','2Lep_SS','2Lep_OF_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_SR']), weight = weight_SR_CR ) )
                    vardb.registerCategory( MyCategory(cat_name_OF+"_SLT_m_Y",    cut = vardb.getCuts(['2Lep_TrigMatch_SLT','TrigDec_SLT_m_OF','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_OF_Y','2Lep_SS','2Lep_OF_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_SR']), weight = weight_SR_CR ) )

                    vardb.registerCategory( MyCategory(cat_name_OF+"_DLT_OR_SLT", cut = vardb.getCuts(['2Lep_TrigMatch_SLT','TrigDec_DLT_OR_SLT_OF','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','Pt_OF_ABCD','2Lep_SS','2Lep_OF_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_SR']), weight = weight_SR_CR ) )

                else:

                    vardb.registerCategory( MyCategory(cat_name_mm,  cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_MuMu_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_NJet_SR']), weight = weight_SR_CR ) )
                    vardb.registerCategory( MyCategory(cat_name_ee,  cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_ElEl_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_SR']), weight = weight_SR_CR ) )
                    vardb.registerCategory( MyCategory(cat_name_OF,  cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_OF_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_SR']), weight = weight_SR_CR ) )
                    #
                    # 2lep+tau region
                    #
                    #vardb.registerCategory( MyCategory('TwoLepSSTau_SR', cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep1Tau_NLep','2Lep1Tau_pT','2Lep1Tau_TrigMatch','2Lep1Tau_SS','2Lep1Tau_1Tau','2Lep1Tau_Zsidescut','2Lep1Tau_NJet_SR','2Lep1Tau_NBJet']) ) )

            else:

                listflav = []

                if "SLT" in args.optimisation:
                    #listflav.extend(["MuMu","ElEl","OF"])
                    listflav.extend(["OF"])
                elif "DLT" in args.optimisation:
                    #listflav.extend(["MuMu","ElEl","ElMu","MuEl"])
                    #listflav.extend(["MuMu","ElEl","OF"])
                    #listflav.extend(["OF"])
                    #listflav.extend(["ElMu","MuEl"])
                    #listflav.extend(["MuMu","ElEl"])
                    listflav.extend(["ElEl"])

                for flav in listflav:

                    # Make as many categories as the number of different pT cuts on (lep0,lep1) you want to test

                    cutvalues_lep0 = cutvalues_lep1 = []

                    if "SLT" in args.optimisation:

                        cutvalues_lep0 = [ float(x) for x in range(27,28) ]
                        cutvalues_lep1 = [ float(x) for x in range(15,28) ] # use this
                        #cutvalues_lep1 = [ float(x) for x in range(20,21,1) ] # temp!

                    elif "DLT" in args.optimisation:

                        if flav == "MuMu":
                            cutvalues_lep0 = [ float(x) for x in range(23,32,2) ]
                            cutvalues_lep1 = [ float(x) for x in range(9,27,2) ]
                            #cutvalues_lep0 = [ float(x) for x in range(24,25) ] # optimal!
                            #cutvalues_lep1 = [ float(x) for x in range(20,21) ] # optimal!
                        elif flav == "ElEl":
                            #cutvalues_lep0 = [ float(x) for x in range(18,31,2) ]
                            #cutvalues_lep1 = [ float(x) for x in range(18,27,2) ]
                            cutvalues_lep0 = [ float(x) for x in range(18,19) ] # optimal!
                            cutvalues_lep1 = [ float(x) for x in range(18,19) ] # optimal!
                        elif flav == "ElMu":
                            #cutvalues_lep0 = [ float(x) for x in range(18,31,2) ]
                            #cutvalues_lep1 = [ float(x) for x in range(15,27,2) ]
			    cutvalues_lep0 = [ float(x) for x in range(20,21) ] # optimal!
                            cutvalues_lep1 = [ float(x) for x in range(20,21) ] # optimal!
                        elif flav == "MuEl":
                            #cutvalues_lep0 = [ float(x) for x in range(25,35,2) ]
                            #cutvalues_lep1 = [ float(x) for x in range(8,29,2) ]
                            cutvalues_lep0 = [ float(x) for x in range(29,30) ] # optimal!
                            cutvalues_lep1 = [ float(x) for x in range(24,25) ] # optimal!
                        elif flav == "OF":
                            cutvalues_lep0 = [ float(x) for x in range(20,21) ] # optimal!
                            cutvalues_lep1 = [ float(x) for x in range(20,21) ] # optimal!

                    for cutval_lep0 in cutvalues_lep0:

                        for cutval_lep1 in cutvalues_lep1:

                            if cutval_lep1 > cutval_lep0: continue

                            this_cutname = "2Lep_pT" + "_Lep0_" + str(cutval_lep0) + "_Lep1_" + str(cutval_lep1)
                            this_cutstr  = "( lep_Pt_0 > {0}e3 && lep_Pt_1 > {1}e3 )".format( str(cutval_lep0), str(cutval_lep1) )
                            this_cut     = Cut( this_cutname, this_cutstr )

                            if flav == "MuMu":
                                basecut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_SS','2Lep_MuMu_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_NJet_SR']) & this_cut
                                this_cat_name = "MuMuSS_SR"
                            elif flav == "ElEl":
                                basecut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_SS','2Lep_ElEl_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_SR']) & this_cut
                                this_cat_name = "ElElSS_SR"
                            elif flav == "ElMu":
                                basecut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_SS','2Lep_ElMu_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_SR']) & this_cut
                                this_cat_name = "ElMuSS_SR"
                            elif flav == "MuEl":
                                basecut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_SS','2Lep_MuEl_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_SR']) & this_cut
                                this_cat_name = "MuElSS_SR"
                            elif flav == "OF":
                                basecut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_SS','2Lep_OF_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_SR']) & this_cut
                                this_cat_name = "OFSS_SR"

                            if ( doMM or doFF or doTHETA ):
                                this_cat_name += "_DataDriven"

                            this_cat_name += "_Lep0_" + str(cutval_lep0) + "_Lep1_" + str(cutval_lep1)

                            vardb.registerCategory( MyCategory(this_cat_name, cut = basecut, weight = weight_SR_CR ) )


        if doThreeLepSR:
            vardb.registerCategory( MyCategory('ThreeLep_SR',    cut = vardb.getCuts(['TrigDec','BlindingCut','3Lep_pT','3Lep_TrigMatch','3Lep_NLep','3Lep_Charge','3Lep_TightLeptons','3Lep_ZVeto','3Lep_MinZCut','3Lep_NJets']), weight = weight_SR_CR ) )

        if doFourLepSR:
            vardb.registerCategory( MyCategory('FourLep_SR',     cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','4Lep','4Lep_NJets']), weight = weight_SR_CR ) )

    # -------------
    # low N-jet CRs
    # -------------

    if doTwoLepLowNJetCR :

        cat_name_mm = 'MuMuSS_LowNJetCR'
        cat_name_ee = 'ElElSS_LowNJetCR'
        cat_name_OF = 'OFSS_LowNJetCR'

        if ( doMM or doFF or doTHETA ):
            cat_name_mm += '_DataDriven'
            cat_name_ee += '_DataDriven'
            cat_name_OF += '_DataDriven'

        if ( doTHETA ):
            vardb.registerCategory( MyCategory(cat_name_OF, cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_OF_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_CR']), weight = weight_SR_CR ) )
        else:
            vardb.registerCategory( MyCategory(cat_name_mm, cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_MuMu_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_NJet_CR']), weight = weight_SR_CR ) )
            vardb.registerCategory( MyCategory(cat_name_ee, cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_ElEl_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_CR']), weight = weight_SR_CR ) )
            vardb.registerCategory( MyCategory(cat_name_OF, cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_OF_Event','TauVeto','2Lep_TRUTH_PurePromptEvent','2Lep_ElEtaCut','2Lep_NJet_CR']), weight = weight_SR_CR ) )
            #
            # 2lep+tau region
            #
            #vardb.registerCategory( MyCategory('TwoLepSSTau_LowNJetCR',  cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep1Tau_NLep','2Lep1Tau_pT','2Lep1Tau_TrigMatch','2Lep1Tau_SS','2Lep1Tau_1Tau','2Lep1Tau_Zsidescut','2Lep1Tau_NJet_CR','2Lep1Tau_NBJet']), weight = weight_SR_CR ) )


    if doThreeLepLowNJetCR:
        # take OS pairs
        #
        vardb.registerCategory( MyCategory('ThreeLep_LowNJetCR',   cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','3Lep_NLep','2Lep_NJet_CR','ZOSsidescut','2Lep_OS']), weight = weight_SR_CR ) )

    # -------------
    # other CRs
    # -------------

    if doWZonCR:
        vardb.registerCategory( MyCategory('WZonCR',      cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','BJetVeto','3Lep_NLep','2Lep_Zpeakcut','2Lep_OS']), weight = weight_SR_CR ) )

    if doWZoffCR:
        vardb.registerCategory( MyCategory('WZoffCR',     cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','BJetVeto','3Lep_NLep','2Lep_Zsidescut','2Lep_OS']), weight = weight_SR_CR ) )

    if doWZHFonCR:
        vardb.registerCategory( MyCategory('WZHFonCR',    cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','3Lep_NLep','2Lep_Zpeakcut','2Lep_OS']), weight = weight_SR_CR ) )

    if doWZHFoffCR:
        vardb.registerCategory( MyCategory('WZHFoffCR',   cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','3Lep_NLep','2Lep_Zsidescut','2Lep_OS']), weight = weight_SR_CR ) )

    if dottZCR:
        vardb.registerCategory( MyCategory('ttZCR',       cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','3Lep_NLep','NJet3L','2Lep_Zpeakcut','2Lep_OS']), weight = weight_SR_CR ) )

    if dottWCR:
        vardb.registerCategory( MyCategory('ttWCR',       cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NJet_ttW','2Lep_NBJet_ttW','2Lep_NLep','2Lep_pT_Relaxed','TauVeto','TT','2Lep_Zmincut_ttW','2Lep_OS']), weight = weight_SR_CR ) )

    if doZSSpeakCR:
        vardb.registerCategory( MyCategory('ZSSpeakCR_ElEl',   cut = vardb.getCuts(['2Lep_NLep','2Lep_pT','TrigDec','BlindingCut','2Lep_TrigMatch','TauVeto','2Lep_ElEl_Event','2Lep_SS','2Lep_Zpeakcut','2Lep_TRUTH_PurePromptEvent']), weight = weight_SR_CR ) )
        vardb.registerCategory( MyCategory('ZSSpeakCR_MuMu',   cut = vardb.getCuts(['2Lep_NLep','2Lep_pT','TrigDec','BlindingCut','2Lep_TrigMatch','TauVeto','2Lep_MuMu_Event','2Lep_SS','2Lep_Zpeakcut','2Lep_TRUTH_PurePromptEvent']), weight = weight_SR_CR ) )

    # ------------------------------------
    # Special CR for Data/MC control plots
    # ------------------------------------

    if doDataMCCR:

        # ----------------------------------------------------
        # Inclusive OS dilepton (ee,mumu, emu)
        #
        vardb.registerCategory( MyCategory('DataMC_InclusiveOS_MuMu', cut = vardb.getCuts(['2Lep_NLep','2Lep_pT_Relaxed','TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_MuMu_Event','TT','2Lep_Zmincut','2Lep_OS']), weight = weight_SR_CR ) )
        vardb.registerCategory( MyCategory('DataMC_InclusiveOS_ElEl', cut = vardb.getCuts(['2Lep_NLep','2Lep_pT_Relaxed','TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_ElEl_Event','TT','2Lep_ElEtaCut','2Lep_Zmincut','2Lep_OS']), weight = weight_SR_CR ) )
        vardb.registerCategory( MyCategory('DataMC_InclusiveOS_OF',   cut = vardb.getCuts(['2Lep_NLep','2Lep_pT_Relaxed','TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_OF_Event','TT','2Lep_ElEtaCut','2Lep_Zmincut','2Lep_OS']), weight = weight_SR_CR ) )

        # ----------------------------------------------------
        # OS ttbar ( top dilepton) (ee,mumu,emu)
        #
        vardb.registerCategory( MyCategory('DataMC_OS_ttbar_MuMu',    cut = vardb.getCuts(['2Lep_NLep','2Lep_pT_Relaxed','TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_MuMu_Event','TT','4Lep_NJets','2Lep_NBJet','2Lep_Zsidescut','2Lep_Zmincut','2Lep_OS']), weight = weight_SR_CR ) )
        vardb.registerCategory( MyCategory('DataMC_OS_ttbar_ElEl',    cut = vardb.getCuts(['2Lep_NLep','2Lep_pT_Relaxed','TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_ElEl_Event','TT','2Lep_ElEtaCut','4Lep_NJets','2Lep_NBJet','2Lep_Zsidescut','2Lep_Zmincut','2Lep_OS']), weight = weight_SR_CR ) )
        vardb.registerCategory( MyCategory('DataMC_OS_ttbar_OF',      cut = vardb.getCuts(['2Lep_NLep','2Lep_pT_Relaxed','TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_OF_Event','TT','2Lep_ElEtaCut','4Lep_NJets','2Lep_NBJet','2Lep_Zsidescut','2Lep_Zmincut','2Lep_OS']), weight = weight_SR_CR ) )

        # ----------------------------------------------------
        # SS ttbar (ee,mumu,emu)
        #
        vardb.registerCategory( MyCategory('DataMC_SS_ttbar',        cut = vardb.getCuts(['2Lep_NLep','2Lep_pT_Relaxed','TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NJet_CR_SStt','TT','2Lep_ElEtaCut','OneBJet','2Lep_SS','2Lep_Zmincut']), weight = weight_SR_CR ) )

    # --------------------------------------------
    # Full breakdown of cuts for cutflow challenge
    # --------------------------------------------

    if doCFChallenge:

        weight_CFC    = "lepSFObjTight * lepSFTrigTight * tauSFTight * JVT_EventWeight * MV2c10_70_EventWeight"
        weight_CFC_MM = "tauSFTight * JVT_EventWeight * MV2c10_70_EventWeight"

        if "MM" in args.channel:
            # CF Challenge for MM efficiency measurement
            #
            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_TrigDec',                cut = vardb.getCuts(['TrigDec','BlindingCut'])  ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_NLep',                   cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep'])  ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_pT',                     cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep','2Lep_pT_MMRates'])  ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_TrigMatch',              cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep','2Lep_pT_MMRates','2Lep_TrigMatch'])  ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_TauVeto',                cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep','2Lep_pT_MMRates','2Lep_TrigMatch','TauVeto'])  ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_NBJets',                 cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep','2Lep_pT_MMRates','2Lep_TrigMatch','TauVeto','2Lep_NBJet'])  ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_EtaEl',                  cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep','2Lep_pT_MMRates','2Lep_TrigMatch','TauVeto','2Lep_NBJet','2Lep_ElEtaCut'])  ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_NJets',                  cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep','2Lep_pT_MMRates','2Lep_TrigMatch','TauVeto','2Lep_NBJet','2Lep_ElEtaCut','2Lep_NJet_CR']), weight = weight_CFC_MM  ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_LepTagTightTrigMatched', cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep','2Lep_pT_MMRates','2Lep_TrigMatch','TauVeto','2Lep_NBJet','2Lep_ElEtaCut','2Lep_NJet_CR','2Lep_LepTagTightTrigMatched']), weight = ( weight_CFC_MM + " * weight_tag" ) ) )

            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_OS',                     cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep','2Lep_pT_MMRates','2Lep_TrigMatch','TauVeto','2Lep_NBJet','2Lep_ElEtaCut','2Lep_NJet_CR','2Lep_LepTagTightTrigMatched','2Lep_OS']), weight = ( weight_CFC_MM + " * weight_tag" ) ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_OS_OF',                  cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep','2Lep_pT_MMRates','2Lep_TrigMatch','TauVeto','2Lep_NBJet','2Lep_ElEtaCut','2Lep_NJet_CR','2Lep_LepTagTightTrigMatched','2Lep_OS','2Lep_OF_Event']), weight = ( weight_CFC_MM + " * weight_tag" ) ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_OS_ProbeElT',            cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep','2Lep_pT_MMRates','2Lep_TrigMatch','TauVeto','2Lep_NBJet','2Lep_ElEtaCut','2Lep_NJet_CR','2Lep_LepTagTightTrigMatched','2Lep_OS','2Lep_OF_Event','2Lep_ElProbe','2Lep_ProbeTight']), weight = ( weight_CFC_MM + " * weight_tag * weight_probe" ) ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_OS_ProbeMuT',            cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep','2Lep_pT_MMRates','2Lep_TrigMatch','TauVeto','2Lep_NBJet','2Lep_ElEtaCut','2Lep_NJet_CR','2Lep_LepTagTightTrigMatched','2Lep_OS','2Lep_OF_Event','2Lep_MuProbe','2Lep_ProbeTight']), weight = ( weight_CFC_MM + " * weight_tag * weight_probe" )  ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_OS_ProbeElAntiT',        cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep','2Lep_pT_MMRates','2Lep_TrigMatch','TauVeto','2Lep_NBJet','2Lep_ElEtaCut','2Lep_NJet_CR','2Lep_LepTagTightTrigMatched','2Lep_OS','2Lep_OF_Event','2Lep_ElProbe','2Lep_ProbeAntiTight']), weight = ( weight_CFC_MM + " * weight_tag * weight_probe" )  ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_OS_ProbeMuAntiT',        cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep','2Lep_pT_MMRates','2Lep_TrigMatch','TauVeto','2Lep_NBJet','2Lep_ElEtaCut','2Lep_NJet_CR','2Lep_LepTagTightTrigMatched','2Lep_OS','2Lep_OF_Event','2Lep_MuProbe','2Lep_ProbeAntiTight']), weight = ( weight_CFC_MM + " * weight_tag * weight_probe" )  ) )

            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_SS',                     cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep','2Lep_pT_MMRates','2Lep_TrigMatch','TauVeto','2Lep_NBJet','2Lep_ElEtaCut','2Lep_NJet_CR','2Lep_LepTagTightTrigMatched','2Lep_SS']), weight = ( weight_CFC_MM + " * weight_tag" ) ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_SS_Zmin',                cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep','2Lep_pT_MMRates','2Lep_TrigMatch','TauVeto','2Lep_NBJet','2Lep_ElEtaCut','2Lep_NJet_CR','2Lep_LepTagTightTrigMatched','2Lep_SS','2Lep_Zmincut']), weight = ( weight_CFC_MM + " * weight_tag" ) ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_SS_Zveto',               cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep','2Lep_pT_MMRates','2Lep_TrigMatch','TauVeto','2Lep_NBJet','2Lep_ElEtaCut','2Lep_NJet_CR','2Lep_LepTagTightTrigMatched','2Lep_SS','2Lep_Zmincut','2Lep_Zsidescut']), weight = ( weight_CFC_MM + " * weight_tag" ) ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_SS_ProbeElT',            cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep','2Lep_pT_MMRates','2Lep_TrigMatch','TauVeto','2Lep_NBJet','2Lep_ElEtaCut','2Lep_NJet_CR','2Lep_LepTagTightTrigMatched','2Lep_SS','2Lep_Zmincut','2Lep_Zsidescut','2Lep_ElProbe','2Lep_ProbeTight']), weight = ( weight_CFC_MM + " * weight_tag * weight_probe" ) ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_SS_ProbeMuT',            cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep','2Lep_pT_MMRates','2Lep_TrigMatch','TauVeto','2Lep_NBJet','2Lep_ElEtaCut','2Lep_NJet_CR','2Lep_LepTagTightTrigMatched','2Lep_SS','2Lep_Zmincut','2Lep_Zsidescut','2Lep_MuMu_Event','2Lep_MuProbe','2Lep_ProbeTight']), weight = ( weight_CFC_MM + " * weight_tag * weight_probe" ) ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_SS_ProbeElAntiT',        cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep','2Lep_pT_MMRates','2Lep_TrigMatch','TauVeto','2Lep_NBJet','2Lep_ElEtaCut','2Lep_NJet_CR','2Lep_LepTagTightTrigMatched','2Lep_SS','2Lep_Zmincut','2Lep_Zsidescut','2Lep_ElProbe','2Lep_ProbeAntiTight']), weight = ( weight_CFC_MM + " * weight_tag * weight_probe" ) ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep_MMRates_SS_ProbeMuAntiT',        cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_NLep','2Lep_pT_MMRates','2Lep_TrigMatch','TauVeto','2Lep_NBJet','2Lep_ElEtaCut','2Lep_NJet_CR','2Lep_LepTagTightTrigMatched','2Lep_SS','2Lep_Zmincut','2Lep_Zsidescut','2Lep_MuMu_Event','2Lep_MuProbe','2Lep_ProbeAntiTight']), weight = ( weight_CFC_MM + " * weight_tag * weight_probe" ) ) )

        if "2LepSS" in args.channel:
            # 2lepSS + 0tau
            #
            vardb.registerCategory( MyCategory('CFChallenge_2LepSS0Tau_SR_DataDriven_TrigDec',    cut = vardb.getCuts(['TrigDec']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_2LepSS0Tau_SR_DataDriven_NLep',       cut = vardb.getCuts(['TrigDec','2Lep_NLep']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_2LepSS0Tau_SR_DataDriven_TT',         cut = vardb.getCuts(['TrigDec','2Lep_NLep','TT']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_2LepSS0Tau_SR_DataDriven_TrigMatch',  cut = vardb.getCuts(['TrigDec','2Lep_NLep','TT','2Lep_TrigMatch']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_2LepSS0Tau_SR_DataDriven_SS',         cut = vardb.getCuts(['TrigDec','2Lep_NLep','TT','2Lep_TrigMatch','2Lep_SS']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_2LepSS0Tau_SR_DataDriven_pT',         cut = vardb.getCuts(['TrigDec','2Lep_NLep','TT','2Lep_TrigMatch','2Lep_SS','2Lep_pT']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_2LepSS0Tau_SR_DataDriven_ElEta',      cut = vardb.getCuts(['TrigDec','2Lep_NLep','TT','2Lep_TrigMatch','2Lep_SS','2Lep_pT','2Lep_ElEtaCut']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_2LepSS0Tau_SR_DataDriven_TauVeto',    cut = vardb.getCuts(['TrigDec','2Lep_NLep','TT','2Lep_TrigMatch','2Lep_SS','2Lep_pT','2Lep_ElEtaCut','TauVeto']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_2LepSS0Tau_SR_DataDriven_NJets',      cut = vardb.getCuts(['TrigDec','2Lep_NLep','TT','2Lep_TrigMatch','2Lep_SS','2Lep_pT','2Lep_ElEtaCut','TauVeto','2Lep_NJet_SR']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_2LepSS0Tau_SR_DataDriven_NBJets',     cut = vardb.getCuts(['TrigDec','2Lep_NLep','TT','2Lep_TrigMatch','2Lep_SS','2Lep_pT','2Lep_ElEtaCut','TauVeto','2Lep_NJet_SR','2Lep_NBJet_SR']), weight = weight_CFC ) )

        if "2LepSS1Tau" in args.channel:
            # 2lepSS + 1tau
            #
            vardb.registerCategory( MyCategory('CFChallenge_2Lep1Tau_NLep',         cut = vardb.getCuts(['2Lep1Tau_NLep']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep1Tau_TightLeptons', cut = vardb.getCuts(['2Lep1Tau_NLep','2Lep1Tau_TightLeptons']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep1Tau_pT',           cut = vardb.getCuts(['2Lep1Tau_NLep','2Lep1Tau_TightLeptons','2Lep1Tau_pT']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep1Tau_TrigMatch',    cut = vardb.getCuts(['2Lep1Tau_NLep','2Lep1Tau_TightLeptons','2Lep1Tau_pT','2Lep1Tau_TrigMatch']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep1Tau_SS',           cut = vardb.getCuts(['2Lep1Tau_NLep','2Lep1Tau_TightLeptons','2Lep1Tau_pT','2Lep1Tau_TrigMatch','2Lep1Tau_SS']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep1Tau_1Tau',         cut = vardb.getCuts(['2Lep1Tau_NLep','2Lep1Tau_TightLeptons','2Lep1Tau_pT','2Lep1Tau_TrigMatch','2Lep1Tau_SS','2Lep1Tau_1Tau']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep1Tau_Zsidescut',    cut = vardb.getCuts(['2Lep1Tau_NLep','2Lep1Tau_TightLeptons','2Lep1Tau_pT','2Lep1Tau_TrigMatch','2Lep1Tau_SS','2Lep1Tau_1Tau','2Lep1Tau_Zsidescut']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep1Tau_NJets',        cut = vardb.getCuts(['2Lep1Tau_NLep','2Lep1Tau_TightLeptons','2Lep1Tau_pT','2Lep1Tau_TrigMatch','2Lep1Tau_SS','2Lep1Tau_1Tau','2Lep1Tau_Zsidescut','2Lep1Tau_NJet_SR']), weight = weight_CFC  ) )
            vardb.registerCategory( MyCategory('CFChallenge_2Lep1Tau_NBJets',       cut = vardb.getCuts(['2Lep1Tau_NLep','2Lep1Tau_TightLeptons','2Lep1Tau_pT','2Lep1Tau_TrigMatch','2Lep1Tau_SS','2Lep1Tau_1Tau','2Lep1Tau_Zsidescut','2Lep1Tau_NJet_SR','2Lep1Tau_NBJet']), weight = weight_CFC  ) )

        if "3Lep" in args.channel:
            # 3 lep
            #
            vardb.registerCategory( MyCategory('CFChallenge_3Lep_NLep',         cut = vardb.getCuts(['3Lep_NLep']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_3Lep_Charge',       cut = vardb.getCuts(['3Lep_NLep','3Lep_Charge']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_3Lep_TightLeptons', cut = vardb.getCuts(['3Lep_NLep','3Lep_Charge','3Lep_TightLeptons']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_3Lep_pT',           cut = vardb.getCuts(['3Lep_NLep','3Lep_Charge','3Lep_TightLeptons','3Lep_pT']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_3Lep_TrigMatch',    cut = vardb.getCuts(['3Lep_NLep','3Lep_Charge','3Lep_TightLeptons','3Lep_pT','3Lep_TrigMatch']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_3Lep_ZVeto',        cut = vardb.getCuts(['3Lep_NLep','3Lep_Charge','3Lep_TightLeptons','3Lep_pT','3Lep_TrigMatch','3Lep_ZVeto']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_3Lep_MinZCut',      cut = vardb.getCuts(['3Lep_NLep','3Lep_Charge','3Lep_TightLeptons','3Lep_pT','3Lep_TrigMatch','3Lep_ZVeto','3Lep_MinZCut']), weight = weight_CFC ) )
            vardb.registerCategory( MyCategory('CFChallenge_3Lep_NJets',        cut = vardb.getCuts(['3Lep_NLep','3Lep_Charge','3Lep_TightLeptons','3Lep_pT','3Lep_TrigMatch','3Lep_ZVeto','3Lep_MinZCut','3Lep_NJets']), weight = weight_CFC ) )

    # -----------------------------------------------------------
    # CRs where trigger efficinecies are measured for r/f leptons
    # -----------------------------------------------------------

    if "TriggerEff" in args.channel:

        # ----------------------
	# Tag & Probe selection
        # ----------------------

        tag   = "lep_Tag_"
        probe = "lep_Probe_"

        if any( vers in args.inputDir for vers in ["v21","v23","v24"]):
            if "SLT" in args.trigger:
                tag   += "SLT_"
                probe += "SLT_"
            elif "DLT" in args.trigger:
                tag   += "DLT_"
                probe += "DLT_"

        vardb.registerVar( Variable(shortname = "ElProbePt", latexname = "p_{T}^{probe e} [GeV]", ntuplename = probe + "Pt/1e3", bins = 40, minval = 10.0, maxval = 210.0,) )
        vardb.registerVar( Variable(shortname = "MuProbePt", latexname = "p_{T}^{probe #mu} [GeV]", ntuplename = probe + "Pt/1e3", bins = 40, minval = 10.0, maxval = 210.0) )

        # Trigger efficiency for REAL leptons
        #
        #"""
        vardb.registerCategory( MyCategory('RealCRMuLAnyTM',      cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent']), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('RealCRMuLAntiTM',     cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent']) & -vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('RealCRMuLTM',         cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent']) & vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        #"""
        #"""
        vardb.registerCategory( MyCategory('RealCRMuTAnyTM',      cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeTight']), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('RealCRMuTAntiTM',     cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeTight']) & -vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('RealCRMuTTM',         cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeTight']) & vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        #"""
        #"""
        vardb.registerCategory( MyCategory('RealCRMuAntiTAnyTM',  cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeAntiTight']), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('RealCRMuAntiTAntiTM', cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeAntiTight']) & -vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('RealCRMuAntiTTM',     cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeAntiTight']) & vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        #"""
        #"""
        vardb.registerCategory( MyCategory('RealCRElLAnyTM',      cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent']), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('RealCRElLAntiTM',     cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent']) & -vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('RealCRElLTM',         cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent']) & vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        #"""
        #"""
        vardb.registerCategory( MyCategory('RealCRElTAnyTM',      cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeTight']), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('RealCRElTAntiTM',     cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeTight']) & -vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('RealCRElTTM',         cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeTight']) & vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        #"""
        #"""
        vardb.registerCategory( MyCategory('RealCRElAntiTAnyTM',  cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeAntiTight']), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('RealCRElAntiTAntiTM', cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeAntiTight']) & -vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('RealCRElAntiTTM',     cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeAntiTight']) & vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        #"""
        # Trigger efficiency for FAKE leptons
        #
        #"""
        vardb.registerCategory( MyCategory('FakeCRMuLAnyTM',      cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent']), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('FakeCRMuLAntiTM',     cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent']) & -vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('FakeCRMuLTM',         cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent']) & vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        #"""
        #"""
        vardb.registerCategory( MyCategory('FakeCRMuTAnyTM',      cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeTight']), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('FakeCRMuTAntiTM',     cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeTight']) & -vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('FakeCRMuTTM',         cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeTight']) & vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        #"""
        #"""
        vardb.registerCategory( MyCategory('FakeCRMuAntiTAnyTM',  cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeAntiTight']), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('FakeCRMuAntiTAntiTM', cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeAntiTight']) & -vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('FakeCRMuAntiTTM',     cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeAntiTight']) & vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        #"""
        #"""
        vardb.registerCategory( MyCategory('FakeCRElLAnyTM',      cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent']), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('FakeCRElLAntiTM',     cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent']) & -vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('FakeCRElLTM',         cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent']) & vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        #"""
        #"""
        vardb.registerCategory( MyCategory('FakeCRElTAnyTM',      cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeTight']), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('FakeCRElTAntiTM',     cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeTight']) & -vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('FakeCRElTTM',         cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeTight']) & vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        #"""
        #"""
        vardb.registerCategory( MyCategory('FakeCRElAntiTAnyTM',  cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeAntiTight']), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('FakeCRElAntiTAntiTM', cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeAntiTight']) & -vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        vardb.registerCategory( MyCategory('FakeCRElAntiTTM',     cut = vardb.getCuts(['TrigDec','BlindingCut','2Lep_LepTagTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_Zsidescut','2Lep_Zmincut','2Lep_TagAndProbe_GoodEvent','2Lep_ProbeAntiTight']) & vardb.getCut('2Lep_LepProbeTrigMatched'), weight = "1.0" ) )
        #"""

    # ----------------------------------------------
    # CRs where r/f rates for MM method are measured
    # ----------------------------------------------

    if "MMRates" in args.channel:

        # ----------------------
	# Tag & Probe selection
        # ----------------------

        if not "LH" in args.channel:

            el_tag   = mu_tag   = "lep_Tag_"
            el_probe = mu_probe = "lep_Probe_"

            if "SUSY_TP" in args.channel: # Use vector branches!
                el_tag   = "electron_TagVec_"
                el_probe = "electron_ProbeVec_"
                mu_tag   = "muon_TagVec_"
                mu_probe = "muon_ProbeVec_"

            if any( vers in args.inputDir for vers in ["v21","v23","v24"]):
	    	if "SLT" in args.trigger:
    	    	    el_tag   += "SLT_"
    	    	    mu_tag   += "SLT_"
	    	    el_probe += "SLT_"
	    	    mu_probe += "SLT_"
	    	elif "DLT" in args.trigger:
    	    	    el_tag   += "DLT_"
    	    	    mu_tag   += "DLT_"
	    	    el_probe += "DLT_"
	    	    mu_probe += "DLT_"

            # ---------------------------------------
            # Special plots for MM real/fake eff CRs
            # ---------------------------------------

            vardb.registerVar( Variable(shortname = "ElProbePt", latexname = "p_{T}^{probe e} [GeV]", ntuplename = el_probe + "Pt/1e3", bins = 40, minval = 10.0, maxval = 210.0,) )
            #vardb.registerVar( Variable(shortname = "ElProbeEta",latexname = "#eta^{probe e}", ntuplename = "TMath::Abs( " + el_probe + "EtaBE2 )", bins = 26, minval = 0.0,  maxval = 2.6) )
            #vardb.registerVar( Variable(shortname = "ElProbeDistanceClosestBJet", latexname = '#DeltaR(probe e, closest b-jet)', ntuplename = el_probe + "deltaRClosestBJet", bins = 20, minval = 0.0, maxval = 5.0) )
            #vardb.registerVar( Variable(shortname = "ElProbed0sig", latexname = "|d_{0}^{sig}| probe e", ntuplename = "TMath::Abs(" + el_probe + "sigd0PV)", bins = 40, minval = 0.0, maxval = 10.0,) )
            #vardb.registerVar( Variable(shortname = "ElProbez0sintheta", latexname = "|z_{0}*sin(#theta)| probe e [mm]", ntuplename = "TMath::Abs(" + el_probe + "Z0SinTheta)", bins = 15, minval = 0.0, maxval = 1.5,) )
            #vardb.registerVar( Variable(shortname = "ElProbePtFakeRebinned", latexname = "p_{T}^{probe e} [GeV]", ntuplename = el_probe + "Pt/1e3", bins = 40, minval = 10.0, maxval = 210.0, manualbins = [10,15,20,25,40,200,210]) )
            #vardb.registerVar( Variable(shortname = "ElProbePtRealRebinned", latexname = "p_{T}^{probe e} [GeV]", ntuplename = el_probe + "Pt/1e3", bins = 40, minval = 10.0, maxval = 210.0, manualbins = [10,15,20,25,30,40,60,200,210]) )
            #vardb.registerVar( Variable(shortname = "ElProbeNJets", latexname = "Jet multiplicity", ntuplename = "nJets_OR_T", bins = 8, minval = 2, maxval = 10, weight = "JVT_EventWeight") )
            #vardb.registerVar( Variable(shortname = 'ElProbeType_VS_ElProbeOrigin', latexnameX = 'truthType^{probe e}', latexnameY = 'truthOrigin^{probe e}', ntuplename = el_probe + "truthOrigin" + ":" + el_probe + "truthType", binsX = 41, minvalX = -0.5, maxvalX = 40.5, binsY = 46, minvalY = -0.5, maxvalY = 45.5, typeval = TH2D) )
            #
            #vardb.registerVar( Variable(shortname = "ElTagPt", latexname = "p_{T}^{tag e} [GeV]", ntuplename = el_tag + "Pt/1e3", bins = 40, minval = 10.0, maxval = 210.0,) )
            #vardb.registerVar( Variable(shortname = "ElTagEta", latexname = "#eta^{tag e}", ntuplename = "TMath::Abs( " + el_tag + "EtaBE2 )",bins = 8, minval = 0.0,  maxval = 2.6) )
            #vardb.registerVar( Variable(shortname = "ElTagDistanceClosestBJet", latexname = '#DeltaR(tag e, closest b-jet)', ntuplename = el_tag + "deltaRClosestBJet", bins = 20, minval = 0.0, maxval = 5.0) )
            #vardb.registerVar( Variable(shortname = 'ElTagType_VS_ElTagOrigin', latexnameX = 'truthType^{tag e}', latexnameY = 'truthOrigin^{tag e}', ntuplename = el_tag + "truthOrigin" + ":" + el_tag + "truthType", binsX = 41, minvalX = -0.5, maxvalX = 40.5, binsY = 46, minvalY = -0.5, maxvalY = 45.5, typeval = TH2D) )
            #
            #vardb.registerVar( Variable(shortname = 'ElTagPt_VS_ElProbePt', latexnameX = 'p_{T}^{tag e} [GeV]', latexnameY = 'p_{T}^{probe e} [GeV]', ntuplename = el_probe + "Pt/1e3" + ":" + el_tag + "Pt/1e3", binsX = 40, minvalX = 10.0, maxvalX = 210.0, binsY = 40, minvalY = 10.0, maxvalY = 210.0, typeval = TH2D) )
            #vardb.registerVar( Variable(shortname = "ElTagDistanceClosestBJet_VS_ElProbeDistanceClosestBJet", latexnameX = '#DeltaR(tag e, closest b-jet)', latexnameY = '#DeltaR(probe e, closest b-jet)', ntuplename = el_probe + "deltaRClosestBJet" + ":" + el_tag + "deltaRClosestBJet", binsX = 20, minvalX = 0.0, maxvalX = 5.0, binsY = 20, minvalY = 0.0, maxvalY = 5.0, typeval = TH2D) )
            #vardb.registerVar( Variable(shortname = "ElTagMassClosestBJet_VS_ElProbeMassClosestBJet", latexnameX = 'm(tag e, closest b-jet) [GeV]', latexnameY = 'm(probe e, closest b-jet) [GeV]', ntuplename = el_probe + "massClosestBJet/1e3" + ":" + el_tag + "massClosestBJet/1e3", binsX = 20, minvalX = 0.0, maxvalX = 200.0, binsY = 20, minvalY = 0.0, maxvalY = 200.0, typeval = TH2D) )

            vardb.registerVar( Variable(shortname = "MuProbePt", latexname = "p_{T}^{probe #mu} [GeV]", ntuplename = mu_probe + "Pt/1e3", bins = 40, minval = 10.0, maxval = 210.0) )
            #vardb.registerVar( Variable(shortname = "MuProbeEta", latexname = "#eta^{probe #mu}", ntuplename = "TMath::Abs( " + mu_probe + "Eta )", bins = 25, minval = 0.0, maxval = 2.5) )
            #vardb.registerVar( Variable(shortname = "MuProbeDistanceClosestBJet", latexname = '#DeltaR(probe #mu, closest b-jet)', ntuplename = mu_probe + "deltaRClosestBJet", bins = 20, minval = 0.0, maxval = 5.0) )
            #vardb.registerVar( Variable(shortname = "MuProbed0sig", latexname = "|d_{0}^{sig}| mu_probe #mu", ntuplename = "TMath::Abs(" + mu_probe + "sigd0PV)", bins = 40, minval = 0.0, maxval = 10.0,) )
            #vardb.registerVar( Variable(shortname = "MuProbez0sintheta", latexname = "|z_{0}*sin(#theta)| mu_probe #mu [mm]", ntuplename = "TMath::Abs(" + mu_probe + "Z0SinTheta)", bins = 15, minval = 0.0, maxval = 1.5,) )
            #vardb.registerVar( Variable(shortname = "MuProbePtFakeRebinned", latexname = "p_{T}^{probe #mu} [GeV]", ntuplename = mu_probe + "Pt/1e3", bins = 40, minval = 10.0, maxval = 210.0, manualbins = [10,15,20,25,200,210]) )
            #vardb.registerVar( Variable(shortname = "MuProbePtRealRebinned", latexname = "p_{T}^{probe #mu} [GeV]", ntuplename = mu_probe + "Pt/1e3", bins = 40, minval = 10.0, maxval = 210.0, manualbins = [10,15,20,25,200,210]) )
            #vardb.registerVar( Variable(shortname = "MuProbeNJets", latexname = "Jet multiplicity", ntuplename = "nJets_OR_T", bins = 8, minval = 2, maxval = 10, weight = "JVT_EventWeight") )
            #vardb.registerVar( Variable(shortname = 'MuProbeType_VS_MuProbeOrigin', latexnameX = 'truthType^{probe #mu}', latexnameY = 'truthOrigin^{probe #mu}', ntuplename = mu_probe + "truthOrigin" + ":" + mu_probe + "truthType", binsX = 41, minvalX = -0.5, maxvalX = 40.5, binsY = 46, minvalY = -0.5, maxvalY = 45.5, typeval = TH2D) )
            #
            #vardb.registerVar( Variable(shortname = "MuTagPt", latexname = "p_{T}^{tag #mu} [GeV]", ntuplename = mu_tag + "Pt/1e3", bins = 40, minval = 10.0, maxval = 210.0,) )
            #vardb.registerVar( Variable(shortname = "MuTagEta", latexname = "#eta^{tag #mu}", ntuplename = "TMath::Abs( " + mu_tag + "Eta )", bins = 8,  minval = 0.0, maxval = 2.5) )
            #vardb.registerVar( Variable(shortname = "MuTagDistanceClosestBJet", latexname = '#DeltaR(tag #mu, closest b-jet)', ntuplename = mu_tag + "deltaRClosestBJet", bins = 20, minval = 0.0, maxval = 5.0) )
            #vardb.registerVar( Variable(shortname = 'MuTagType_VS_MuTagOrigin', latexnameX = 'truthType^{tag #mu}', latexnameY = 'truthOrigin^{tag #mu}', ntuplename = mu_tag + "truthOrigin" + ":" + mu_tag + "truthType", binsX = 41, minvalX = -0.5, maxvalX = 40.5, binsY = 46, minvalY = -0.5, maxvalY = 45.5, typeval = TH2D) )
            #
            #vardb.registerVar( Variable(shortname = 'MuTagPt_VS_MuProbePt', latexnameX = 'p_{T}^{tag #mu} [GeV]', latexnameY = 'p_{T}^{probe #mu} [GeV]', ntuplename = mu_probe + "Pt/1e3" + ":" + mu_tag + "Pt/1e3", binsX = 40, minvalX = 10.0, maxvalX = 210.0, binsY = 40, minvalY = 10.0, maxvalY = 210.0, typeval = TH2D) )
            #vardb.registerVar( Variable(shortname = "MuTagDistanceClosestBJet_VS_MuProbeDistanceClosestBJet", latexnameX = '#DeltaR(tag #mu, closest b-jet)', latexnameY = '#DeltaR(probe #mu, closest b-jet)', ntuplename = mu_probe + "deltaRClosestBJet" + ":" + mu_tag + "deltaRClosestBJet", binsX = 20, minvalX = 0.0, maxvalX = 5.0, binsY = 20, minvalY = 0.0, maxvalY = 5.0, typeval = TH2D) )
            #vardb.registerVar( Variable(shortname = "MuTagMassClosestBJet_VS_MuProbeMassClosestBJet", latexnameX = 'm(tag #mu, closest b-jet) [GeV]', latexnameY = 'm(probe #mu, closest b-jet) [GeV]', ntuplename = mu_probe + "massClosestBJet/1e3" + ":" + mu_tag + "massClosestBJet/1e3", binsX = 20, minvalX = 0.0, maxvalX = 200.0, binsY = 20, minvalY = 0.0, maxvalY = 200.0, typeval = TH2D) )

            # -----------------------------------------------------------------------------------------------------------------
            # MC subtraction in Real OS CR: what gets plotted will be subtracted to data:
            #
            # ---> events where PROBE is !prompt (aka, a fake or QMisID or photon conv)
            # This removes events where the probe is a fake lepton.
            # This procedure is quite questionable, as we'd be trusting MC for the fakes (whcih is the exact opposite of what we want to do!)
            # However, for a ttbar-dominated OS CR, the fakes are contaminating mostly @ low pT ( < 25 GeV ), so we could forget about the bias...

            truth_sub_OS = vardb.getCut('2Lep_TRUTH_ProbeNonPromptOrQMisIDEvent')

            if "DATAMC" in args.channel:
            	# Plot all MC, no matter what
            	#
            	truth_sub_OS = vardb.getCut('DummyCut')

            # -----------------------------------------------------------------------------------------------------------------
            # MC subtraction in Fake SS CR: what gets plotted will be subtracted to data:
            #
            # ---> events where PROBE is prompt
            # This removes ttV,VV, rare top, and events where the probe was mis-assigned (i.e, we picked the real lepton in the pair rather than the fake)
            # The MC subtraction here is justified, as we can trust MC at modeling prompts.
            #
            # ---> all events w/ at least one QMisID
            # By default we use the data-driven charge flip estimate. To use MC charge flips, switch on specific flag.
            # When using DD QMisID, we need to veto in MC all events w/ at least one (truth) QMisID, to avoid double subtraction (since ttV, VV might have QMisID leptons)
            #
            truth_sub_SS = ( vardb.getCut('2Lep_TRUTH_ProbePromptEvent') & vardb.getCut('2Lep_TRUTH_QMisIDVeto') )

            # TEMP: SS --> OS
            #truth_sub_SS = vardb.getCut('2Lep_TRUTH_ProbeNonPromptEvent') & vardb.getCut('2Lep_TRUTH_QMisIDVeto')

            if "DATAMC" in args.channel:
            	# Plot all MC, except for QMisID (as we plot them using DD)
            	#
            	truth_sub_SS = ( vardb.getCut('2Lep_TRUTH_QMisIDVeto') )

            # Require at least one non-prompt or charge flip lepton if you want to see the MC bkg composition in the fake region
            #
            if args.MCCompRF:
            	truth_sub_SS = ( vardb.getCut('2Lep_TRUTH_NonPromptEvent') | vardb.getCut('2Lep_TRUTH_QMisIDEvent') )

            # ------------------------------------------------------------
            # Closure test: truth selection in MC for Real/Fake OS/SS CRs:
            # ------------------------------------------------------------
            #
            # 1.
            # REAL CR: select events w/ only prompt leptons, and veto on charge flips.
            #
            # 2.
            # FAKE CR: select events w/ at least one non-prompt lepton, and veto on charge flips.
            #
            if ( "CLOSURE" in args.channel or args.ratesMC ) :

            	truth_sub_OS = vardb.getCut('2Lep_TRUTH_PurePromptEvent')  # Both leptons be real ( and none is QMisID )
                truth_sub_SS = vardb.getCut('2Lep_TRUTH_NonPromptEvent')   # At least one lepton is fake ( and none is QMisID )
                # This is what we did for ICHEP:
            	#truth_sub_SS = vardb.getCut('2Lep_TRUTH_ProbeNonPromptEvent') # probe lepton is fake, and not QMisID

                # Use this truth cut if T&P was defined at truth level in skimming code.
		# Simply ensure event is not "bad" and nothing else ( !bad = RR (OS), RF||FR (SS, QMisID vetoed) ).
		#
		if "TRUTH_TP" in args.channel:
		    truth_sub_OS = truth_sub_SS = vardb.getCut("2Lep_TagAndProbe_GoodEvent")

            	if ( args.doQMisIDRate ):
            	    print ("\n\Measuring efficiency/rate for QMisID leptons in MC!\n")
            	    truth_sub_SS = vardb.getCut('2Lep_TRUTH_ProbeQMisIDEvent')

                # --------------------------------------------
                # Fake probe assignment efficiency
                # (Make sure all events w/ QMisID are removed)
                # --------------------------------------------

                fake_match_cut = vardb.getCut('2Lep_TRUTH_ProbeNonPromptEvent')  # Require probe to be fake
                real_match_cut = -vardb.getCut('2Lep_TRUTH_ProbeNonPromptEvent') # Require probe to be !fake

                probe_sel_cut = vardb.getCuts(['2Lep_ProbeTight','2Lep_LepProbeTrigMatched']) # This selects only ambiguous events w/ both leptons T & TM
                #probe_sel_cut = vardb.getCut('DummyCut')                                     # This selects any event (remembering that the tag lepton is always required to be T & TM)


            # DEFAULT: do not apply any trigger matching on the probe
            # (require to pass/not pass TM only optionally)
            #
            probe_TM_cut = vardb.getCut('DummyCut')
            if "PROBE_TM" in args.channel:
            	probe_TM_cut = vardb.getCut('2Lep_LepProbeTrigMatched')
            elif "PROBE_NOT_TM" in args.channel:
            	probe_TM_cut = -vardb.getCut('2Lep_LepProbeTrigMatched')

            # ------------------------------------------
            # Define common event weight and common cuts
            # ------------------------------------------

            weight_TP_MM = "tauSFTight * JVT_EventWeight * MV2c10_70_EventWeight * weight_tag"

            cc_list = ['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_LepTagTightTrigMatched','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_NJet_CR','2Lep_ElEtaCut','2Lep_Zsidescut','2Lep_Zmincut']
            common_cuts = vardb.getCuts(cc_list)

            # This is what is done in SUSY SS analysis:
            # for electron fake efficiency, use only OF events collected by the single *muon* trigger. In this way, the tag muon is more likely to be a real, and the probe el a fake
            #
            vardb.registerCut( Cut("TrigDecFakeCREl", "( " + m_SLT + " )" ) )
            common_cuts_fake_el = vardb.getCuts([ "TrigDecFakeCREl" if cut == "TrigDec" else cut for cut in cc_list ])

            # --------------------------
            # Define the control regions
            # --------------------------

            if ( args.lepFlavComp == "TEST" ):

                # Test something similar to SUSY SS analysis:

            	# Real CR: OF only
            	#
            	#"""
            	vardb.registerCategory( MyCategory('RealCRMuL',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_MuProbe','2Lep_OF_Event']) & truth_sub_OS, weight = weight_TP_MM ) )
            	vardb.registerCategory( MyCategory('RealCRMuAntiT', cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_MuProbe','2Lep_OF_Event','2Lep_ProbeAntiTight']) & truth_sub_OS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('RealCRMuT',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_MuProbe','2Lep_OF_Event','2Lep_ProbeTight']) & truth_sub_OS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('RealCRElL',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_ElProbe','2Lep_OF_Event']) & truth_sub_OS, weight = weight_TP_MM ) )
            	vardb.registerCategory( MyCategory('RealCRElAntiT', cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_ElProbe','2Lep_OF_Event','2Lep_ProbeAntiTight']) & truth_sub_OS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('RealCRElT',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_ElProbe','2Lep_OF_Event','2Lep_ProbeTight']) & truth_sub_OS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	#"""
            	# Fake CR: OF for electrons (triggering events w/ SL muon trigger only, so that the tag is always a muon), SF for muons
            	#
            	#"""
            	vardb.registerCategory( MyCategory('FakeCRMuL',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_MuMu_Event']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRMuAntiT', cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_ProbeAntiTight']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRMuT',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_ProbeTight']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRElL',     cut = probe_TM_cut & common_cuts_fake_el & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_OF_Event']) & truth_sub_SS, weight = weight_TP_MM ) )
            	vardb.registerCategory( MyCategory('FakeCRElAntiT', cut = probe_TM_cut & common_cuts_fake_el & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_OF_Event','2Lep_ProbeAntiTight']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRElT',     cut = probe_TM_cut & common_cuts_fake_el & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_OF_Event','2Lep_ProbeTight']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
                #"""

                #"""
                vardb.registerCategory( MyCategory('FakeCRMuProbeTMatchedToFake',  cut = probe_sel_cut & fake_match_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                vardb.registerCategory( MyCategory('FakeCRMuProbeTMatchedToReal',  cut = probe_sel_cut & real_match_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                vardb.registerCategory( MyCategory('FakeCRMuProbeTMatchedToAny',   cut = probe_sel_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                vardb.registerCategory( MyCategory('FakeCRElProbeTMatchedToFake',  cut = probe_sel_cut & fake_match_cut & common_cuts_fake_el & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_OF_Event','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                vardb.registerCategory( MyCategory('FakeCRElProbeTMatchedToReal',  cut = probe_sel_cut & real_match_cut & common_cuts_fake_el & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_OF_Event','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                vardb.registerCategory( MyCategory('FakeCRElProbeTMatchedToAny',   cut = probe_sel_cut & common_cuts_fake_el & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_OF_Event','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                #"""

            if ( args.lepFlavComp == "ICHEP_2016" ): # Real CR: OF, Fake CR: INCLUSIVE(el), SF(mu)
                print""
            	#"""
            	vardb.registerCategory( MyCategory('RealCRMuL',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_MuProbe','2Lep_OF_Event']) & truth_sub_OS, weight = weight_TP_MM ) )
            	vardb.registerCategory( MyCategory('RealCRMuAntiT', cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_MuProbe','2Lep_OF_Event','2Lep_ProbeAntiTight']) & truth_sub_OS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('RealCRMuT',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_MuProbe','2Lep_OF_Event','2Lep_ProbeTight']) & truth_sub_OS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('RealCRElL',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_ElProbe','2Lep_OF_Event']) & truth_sub_OS, weight = weight_TP_MM ) )
            	vardb.registerCategory( MyCategory('RealCRElAntiT', cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_ElProbe','2Lep_OF_Event','2Lep_ProbeAntiTight']) & truth_sub_OS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('RealCRElT',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_ElProbe','2Lep_OF_Event','2Lep_ProbeTight']) & truth_sub_OS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRMuL',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_MuMu_Event']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRMuAntiT', cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_ProbeAntiTight']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRMuT',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_ProbeTight']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRElL',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe']) & truth_sub_SS, weight = weight_TP_MM ) )
            	vardb.registerCategory( MyCategory('FakeCRElAntiT', cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_ProbeAntiTight']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRElT',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_ProbeTight']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
                #"""

            if ( args.lepFlavComp == "INCLUSIVE" ): # combine OF + SF
            	print""
                #"""
            	vardb.registerCategory( MyCategory('RealCRMuL',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_MuProbe']) & truth_sub_OS, weight = weight_TP_MM ) )
            	vardb.registerCategory( MyCategory('RealCRMuAntiT', cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_MuProbe','2Lep_ProbeAntiTight']) & truth_sub_OS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('RealCRMuT',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_MuProbe','2Lep_ProbeTight']) & truth_sub_OS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('RealCRElL',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_ElProbe']) & truth_sub_OS, weight = weight_TP_MM ) )
            	vardb.registerCategory( MyCategory('RealCRElAntiT', cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_ElProbe','2Lep_ProbeAntiTight']) & truth_sub_OS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('RealCRElT',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_ElProbe','2Lep_ProbeTight']) & truth_sub_OS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRMuL',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRMuAntiT', cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_ProbeAntiTight']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRMuT',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_ProbeTight']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRElL',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe']) & truth_sub_SS, weight = weight_TP_MM ) )
            	vardb.registerCategory( MyCategory('FakeCRElAntiT', cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_ProbeAntiTight']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRElT',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_ProbeTight']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
                #"""

                #"""
                vardb.registerCategory( MyCategory('FakeCRMuProbeTMatchedToFake',  cut = probe_sel_cut & fake_match_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                vardb.registerCategory( MyCategory('FakeCRMuProbeTMatchedToReal',  cut = probe_sel_cut & real_match_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                vardb.registerCategory( MyCategory('FakeCRMuProbeTMatchedToAny',   cut = probe_sel_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                vardb.registerCategory( MyCategory('FakeCRElProbeTMatchedToFake',  cut = probe_sel_cut & fake_match_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                vardb.registerCategory( MyCategory('FakeCRElProbeTMatchedToReal',  cut = probe_sel_cut & real_match_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                vardb.registerCategory( MyCategory('FakeCRElProbeTMatchedToAny',   cut = probe_sel_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                #"""

            if ( args.lepFlavComp == "SF" ): # SF only
            	print ""
                #"""
            	vardb.registerCategory( MyCategory('RealCRMuL',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_MuProbe','2Lep_MuMu_Event']) & truth_sub_OS, weight = weight_TP_MM ) )
            	vardb.registerCategory( MyCategory('RealCRMuAntiT', cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_ProbeAntiTight']) & truth_sub_OS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('RealCRMuT',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_ProbeTight']) & truth_sub_OS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('RealCRElL',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_ElProbe','2Lep_ElEl_Event']) & truth_sub_OS, weight = weight_TP_MM ) )
            	vardb.registerCategory( MyCategory('RealCRElAntiT', cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_ProbeAntiTight']) & truth_sub_OS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('RealCRElT',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_ProbeTight']) & truth_sub_OS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRMuL',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_MuMu_Event']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRMuAntiT', cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_ProbeAntiTight']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRMuT',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_ProbeTight']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRElL',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_ElEl_Event']) & truth_sub_SS, weight = weight_TP_MM ) )
            	vardb.registerCategory( MyCategory('FakeCRElAntiT', cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_ProbeAntiTight']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRElT',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_ProbeTight']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
                #"""

                #"""
                vardb.registerCategory( MyCategory('FakeCRMuProbeTMatchedToFake',  cut = probe_sel_cut & fake_match_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                vardb.registerCategory( MyCategory('FakeCRMuProbeTMatchedToReal',  cut = probe_sel_cut & real_match_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                vardb.registerCategory( MyCategory('FakeCRMuProbeTMatchedToAny',   cut = probe_sel_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_MuMu_Event','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                vardb.registerCategory( MyCategory('FakeCRElProbeTMatchedToFake',  cut = probe_sel_cut & fake_match_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                vardb.registerCategory( MyCategory('FakeCRElProbeTMatchedToReal',  cut = probe_sel_cut & real_match_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                vardb.registerCategory( MyCategory('FakeCRElProbeTMatchedToAny',   cut = probe_sel_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_ElEl_Event','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                #"""

            if ( args.lepFlavComp == "OF" ): # OF only
            	print ""
                #"""
            	vardb.registerCategory( MyCategory('RealCRMuL',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_MuProbe','2Lep_OF_Event']) & truth_sub_OS, weight = weight_TP_MM ) )
            	vardb.registerCategory( MyCategory('RealCRMuAntiT', cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_MuProbe','2Lep_OF_Event','2Lep_ProbeAntiTight']) & truth_sub_OS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('RealCRMuT',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_MuProbe','2Lep_OF_Event','2Lep_ProbeTight']) & truth_sub_OS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('RealCRElL',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_ElProbe','2Lep_OF_Event']) & truth_sub_OS, weight = weight_TP_MM ) )
            	vardb.registerCategory( MyCategory('RealCRElAntiT', cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_ElProbe','2Lep_OF_Event','2Lep_ProbeAntiTight']) & truth_sub_OS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('RealCRElT',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_OS','2Lep_ElProbe','2Lep_OF_Event','2Lep_ProbeTight']) & truth_sub_OS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRMuL',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_OF_Event']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRMuAntiT', cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_OF_Event','2Lep_ProbeAntiTight']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRMuT',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_OF_Event','2Lep_ProbeTight']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRElL',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_OF_Event']) & truth_sub_SS, weight = weight_TP_MM ) )
            	vardb.registerCategory( MyCategory('FakeCRElAntiT', cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_OF_Event','2Lep_ProbeAntiTight']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
            	vardb.registerCategory( MyCategory('FakeCRElT',     cut = probe_TM_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_OF_Event','2Lep_ProbeTight']) & truth_sub_SS, weight = ( weight_TP_MM + " * weight_probe" ) ) )
                #"""

                #"""
                vardb.registerCategory( MyCategory('FakeCRMuProbeTMatchedToFake',  cut = probe_sel_cut & fake_match_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_OF_Event','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                vardb.registerCategory( MyCategory('FakeCRMuProbeTMatchedToReal',  cut = probe_sel_cut & real_match_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_OF_Event','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                vardb.registerCategory( MyCategory('FakeCRMuProbeTMatchedToAny',   cut = probe_sel_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_MuProbe','2Lep_OF_Event','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                vardb.registerCategory( MyCategory('FakeCRElProbeTMatchedToFake',  cut = probe_sel_cut & fake_match_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_OF_Event','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                vardb.registerCategory( MyCategory('FakeCRElProbeTMatchedToReal',  cut = probe_sel_cut & real_match_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_OF_Event','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                vardb.registerCategory( MyCategory('FakeCRElProbeTMatchedToAny',   cut = probe_sel_cut & common_cuts & vardb.getCuts(['2Lep_SS','2Lep_ElProbe','2Lep_OF_Event','2Lep_TRUTH_QMisIDVeto','2Lep_TagAndProbe_GoodEvent']), weight = ( weight_TP_MM + " * weight_probe" ) ) )
                #"""

        # ------------------------
	# Likelihood fit selection
        # ------------------------

	elif "LH" in args.channel:

            vardb.registerVar( Variable(shortname = 'Lep0Pt_VS_Lep1Pt', latexnameX = 'p_{T}^{lead lep} [GeV]', latexnameY = 'p_{T}^{2nd lead lep} [GeV]', ntuplename = 'lep_Pt_1/1e3:lep_Pt_0/1e3', bins = 40, minval = 10.0, maxval = 210.0, typeval = TH2D) )

            # For measurement in data: do subtraction
            #
            truth_sub_OS = ( vardb.getCut('2Lep_TRUTH_NonPromptEvent') )  # Subtract events w/ at least one non-prompt, and no QMisID
            truth_sub_SS = ( vardb.getCut('2Lep_TRUTH_PurePromptEvent') ) # Subtract events w/ both prompt leptons, and no QMisID. This assumes QMisID will be estimated independently from data

            # For closure rates
            #
            # This is not really a subtraction --> it's really a truth selection
	    #
            if "CLOSURE" in args.channel:

		truth_sub_OS = ( vardb.getCut('2Lep_TRUTH_PurePromptEvent') ) # both leptons be real ( and no QMisID )
            	truth_sub_SS = ( vardb.getCut('2Lep_TRUTH_NonPromptEvent') )  # at least one lepton is fake, and none is charge flip

                # Use this truth cut if T&P was defined at truth level in skimming code.
		# Simply ensure event is not "bad" and nothing else ( !bad = RR (OS), RF||FR (SS, QMisID vetoed) ).
		#
		if "TRUTH_TP" in args.channel:
		    truth_sub_OS = truth_sub_SS = vardb.getCut("2Lep_TagAndProbe_GoodEvent")

            # Real CR - SF
            #
            if ( args.lepFlavComp == "SF" or args.lepFlavComp == "INCLUSIVE" ):
            	print ""
            	#"""
            	vardb.registerCategory( MyCategory('OS_ElEl_TT', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEl_Event','TT','2Lep_ElEtaCut','2Lep_Zsidescut','2Lep_Zmincut']) & truth_sub_OS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('OS_ElEl_TL', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEl_Event','TL','2Lep_ElEtaCut','2Lep_Zsidescut','2Lep_Zmincut']) & truth_sub_OS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('OS_ElEl_LT', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEl_Event','LT','2Lep_ElEtaCut','2Lep_Zsidescut','2Lep_Zmincut']) & truth_sub_OS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('OS_ElEl_LL', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElEl_Event','LL','2Lep_ElEtaCut','2Lep_Zsidescut','2Lep_Zmincut']) & truth_sub_OS ), weight = weight_SR_CR ) )
            	#"""
            	#"""
            	vardb.registerCategory( MyCategory('OS_MuMu_TT', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_MuMu_Event','TT','2Lep_Zsidescut','2Lep_Zmincut']) & truth_sub_OS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('OS_MuMu_TL', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_MuMu_Event','TL','2Lep_Zsidescut','2Lep_Zmincut']) & truth_sub_OS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('OS_MuMu_LT', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_MuMu_Event','LT','2Lep_Zsidescut','2Lep_Zmincut']) & truth_sub_OS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('OS_MuMu_LL', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_MuMu_Event','LL','2Lep_Zsidescut','2Lep_Zmincut']) & truth_sub_OS ), weight = weight_SR_CR ) )
            	#"""

            # Real CR - OF
            #
            if ( args.lepFlavComp == "OF" or args.lepFlavComp == "INCLUSIVE" ):
            	print ""
            	#"""
            	vardb.registerCategory( MyCategory('OS_MuEl_TT', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_MuEl_Event','TT','2Lep_ElEtaCut']) & truth_sub_OS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('OS_ElMu_TT', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElMu_Event','TT','2Lep_ElEtaCut']) & truth_sub_OS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('OS_MuEl_TL', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_MuEl_Event','TL','2Lep_ElEtaCut']) & truth_sub_OS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('OS_ElMu_TL', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElMu_Event','TL','2Lep_ElEtaCut']) & truth_sub_OS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('OS_MuEl_LT', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_MuEl_Event','LT','2Lep_ElEtaCut']) & truth_sub_OS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('OS_ElMu_LT', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElMu_Event','LT','2Lep_ElEtaCut']) & truth_sub_OS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('OS_MuEl_LL', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_MuEl_Event','LL','2Lep_ElEtaCut']) & truth_sub_OS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('OS_ElMu_LL', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_OS','2Lep_NJet_CR','2Lep_ElMu_Event','LL','2Lep_ElEtaCut']) & truth_sub_OS ), weight = weight_SR_CR ) )
            	#"""

            # Fake CR - SF
            #
            # """
            if ( args.lepFlavComp == "SF" or args.lepFlavComp == "INCLUSIVE" ):
            	print ""
            	#"""
            	vardb.registerCategory( MyCategory('SS_ElEl_TT',    cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEl_Event','TT','2Lep_Zsidescut','2Lep_ElEtaCut','2Lep_Zmincut']) & truth_sub_SS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('SS_ElEl_TL',    cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEl_Event','TL','2Lep_Zsidescut','2Lep_ElEtaCut','2Lep_Zmincut']) & truth_sub_SS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('SS_ElEl_LT',    cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEl_Event','LT','2Lep_Zsidescut','2Lep_ElEtaCut','2Lep_Zmincut']) & truth_sub_SS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('SS_ElEl_LL',    cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElEl_Event','LL','2Lep_Zsidescut','2Lep_ElEtaCut','2Lep_Zmincut']) & truth_sub_SS ), weight = weight_SR_CR ) )
            	#"""
            	#"""
            	vardb.registerCategory( MyCategory('SS_MuMu_TT',    cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_MuMu_Event','TT','2Lep_Zsidescut','2Lep_Zmincut']) & truth_sub_SS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('SS_MuMu_TL',    cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_MuMu_Event','TL','2Lep_Zsidescut','2Lep_Zmincut']) & truth_sub_SS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('SS_MuMu_LT',    cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_MuMu_Event','LT','2Lep_Zsidescut','2Lep_Zmincut']) & truth_sub_SS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('SS_MuMu_LL',    cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_MuMu_Event','LL','2Lep_Zsidescut','2Lep_Zmincut']) & truth_sub_SS ), weight = weight_SR_CR ) )
            	#"""

            # Fake CR - OF
            #
            if ( args.lepFlavComp == "OF" or args.lepFlavComp == "INCLUSIVE" ):
            	print ""
            	#"""
            	vardb.registerCategory( MyCategory('SS_MuEl_TT', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_MuEl_Event','TT','2Lep_ElEtaCut']) & truth_sub_SS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('SS_ElMu_TT', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElMu_Event','TT','2Lep_ElEtaCut']) & truth_sub_SS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('SS_MuEl_TL', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_MuEl_Event','TL','2Lep_ElEtaCut']) & truth_sub_SS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('SS_ElMu_TL', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElMu_Event','TL','2Lep_ElEtaCut']) & truth_sub_SS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('SS_MuEl_LT', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_MuEl_Event','LT','2Lep_ElEtaCut']) & truth_sub_SS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('SS_ElMu_LT', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElMu_Event','LT','2Lep_ElEtaCut']) & truth_sub_SS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('SS_MuEl_LL', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_MuEl_Event','LL','2Lep_ElEtaCut']) & truth_sub_SS ), weight = weight_SR_CR ) )
            	vardb.registerCategory( MyCategory('SS_ElMu_LL', cut = ( vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet','2Lep_NLep','2Lep_pT_MMRates','TauVeto','2Lep_SS','2Lep_NJet_CR','2Lep_ElMu_Event','LL','2Lep_ElEtaCut']) & truth_sub_SS ), weight = weight_SR_CR ) )
            	#"""


    if doMMClosureTest:
        print ''

        # Plot only events where at least one lepton is !prompt, and none is charge flip
        #
        truth_cut = ( vardb.getCut('2Lep_TRUTH_NonPromptEvent') )

        if ( doMM or doFF ):

            if "ALLNJ" in args.channel:
                vardb.registerCategory( MyCategory('MuMuSS_SR_AllJet_DataDriven_Closure',    cut = truth_cut & vardb.getCuts(['2Lep_TrigMatch','TrigDec','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','TauVeto','2Lep_SS','2Lep_MuMu_Event','2Lep_MinNJet']), weight = weight_SR_CR ) )
                vardb.registerCategory( MyCategory('OFSS_SR_AllJet_DataDriven_Closure',      cut = truth_cut & vardb.getCuts(['2Lep_TrigMatch','TrigDec','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','TauVeto','2Lep_SS','2Lep_OF_Event','2Lep_ElEtaCut','2Lep_MinNJet']), weight = weight_SR_CR ) )
                vardb.registerCategory( MyCategory('ElElSS_SR_AllJet_DataDriven_Closure',    cut = truth_cut & vardb.getCuts(['2Lep_TrigMatch','TrigDec','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','TauVeto','2Lep_SS','2Lep_ElEl_Event','2Lep_ElEtaCut','2Lep_MinNJet']), weight = weight_SR_CR ) )
            elif "HIGHNJ" in args.channel:
                vardb.registerCategory( MyCategory('MuMuSS_SR_HighJet_DataDriven_Closure',   cut = truth_cut & vardb.getCuts(['2Lep_TrigMatch','TrigDec','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','TauVeto','2Lep_SS','2Lep_MuMu_Event','2Lep_NJet_SR']), weight = weight_SR_CR ) )
                vardb.registerCategory( MyCategory('OFSS_SR_HighJet_DataDriven_Closure',     cut = truth_cut & vardb.getCuts(['2Lep_TrigMatch','TrigDec','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','TauVeto','2Lep_SS','2Lep_OF_Event','2Lep_ElEtaCut','2Lep_NJet_SR']), weight = weight_SR_CR ) )
                vardb.registerCategory( MyCategory('ElElSS_SR_HighJet_DataDriven_Closure',   cut = truth_cut & vardb.getCuts(['2Lep_TrigMatch','TrigDec','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','TauVeto','2Lep_SS','2Lep_ElEl_Event','2Lep_ElEtaCut','2Lep_NJet_SR']), weight = weight_SR_CR ) )
            elif "LOWNJ" in args.channel:
                vardb.registerCategory( MyCategory('MuMuSS_SR_LowJet_DataDriven_Closure',    cut = truth_cut & vardb.getCuts(['2Lep_TrigMatch','TrigDec','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','TauVeto','2Lep_SS','2Lep_MuMu_Event','2Lep_NJet_CR']), weight = weight_SR_CR ) )
                vardb.registerCategory( MyCategory('OFSS_SR_LowJet_DataDriven_Closure',      cut = truth_cut & vardb.getCuts(['2Lep_TrigMatch','TrigDec','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','TauVeto','2Lep_SS','2Lep_OF_Event','2Lep_ElEtaCut','2Lep_NJet_CR']), weight = weight_SR_CR ) )
                vardb.registerCategory( MyCategory('ElElSS_SR_LowJet_DataDriven_Closure',    cut = truth_cut & vardb.getCuts(['2Lep_TrigMatch','TrigDec','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','TauVeto','2Lep_SS','2Lep_ElEl_Event','2Lep_ElEtaCut','2Lep_NJet_CR']), weight = weight_SR_CR ) )

        elif ( doTHETA ):
            # NB: for SF events, the closure test for THETA is meaningful only in SR, b/c the [TT,low nr. jet] CR is already used to derive the theta factor
            #     In the OF case, also the low njet region can be used
            #
            vardb.registerCategory( MyCategory('MuMuSS_SR_HighJet_DataDriven_Closure',   cut = truth_cut & vardb.getCuts(['2Lep_TrigMatch','TrigDec','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','TauVeto','2Lep_SS','2Lep_MuMu_Event','2Lep_NJet_SR']), weight = weight_SR_CR ) )
            vardb.registerCategory( MyCategory('ElElSS_SR_HighJet_DataDriven_Closure',   cut = truth_cut & vardb.getCuts(['2Lep_TrigMatch','TrigDec','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','TauVeto','2Lep_SS','2Lep_ElEl_Event','2Lep_ElEtaCut','2Lep_NJet_SR']), weight = weight_SR_CR ) )
            vardb.registerCategory( MyCategory('OFSS_SR_HighJet_DataDriven_Closure',     cut = truth_cut & vardb.getCuts(['2Lep_TrigMatch','TrigDec','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','TauVeto','2Lep_SS','2Lep_OF_Event','2Lep_ElEtaCut','2Lep_NJet_SR']), weight = weight_SR_CR ) )
            if "LOWNJ" in args.channel:
                vardb.registerCategory( MyCategory('OFSS_SR_LowJet_DataDriven_Closure',  cut = truth_cut & vardb.getCuts(['2Lep_TrigMatch','TrigDec','BlindingCut','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','TauVeto','2Lep_SS','2Lep_OF_Event','2Lep_ElEtaCut','2Lep_NJet_CR']), weight = weight_SR_CR ) )


    # ---------------------------------------------
    # Sidebands (and SR) used for MM fakes estimate
    # ---------------------------------------------

    if doMMSidebands:

        # If doing TTBar closure, use a trth cut to require at least 1 fake, and QMisID veto
        #
        truth_cut = ( vardb.getCut('2Lep_TRUTH_PurePromptEvent'), vardb.getCut('2Lep_TRUTH_NonPromptEvent') )[bool("CLOSURE" in args.channel)]

        if "HIGHNJ" in args.channel:

            # MuMu region
            #
            vardb.registerCategory( MyCategory('MuMuSS_MMSideband_LL',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_MuMu_Event','TauVeto','2Lep_NJet_SR','LL']), weight = weight_SR_CR ) )
            vardb.registerCategory( MyCategory('MuMuSS_MMSideband_TL',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_MuMu_Event','TauVeto','2Lep_NJet_SR','TL']), weight = weight_SR_CR ) )
            vardb.registerCategory( MyCategory('MuMuSS_MMSideband_LT',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_MuMu_Event','TauVeto','2Lep_NJet_SR','LT']), weight = weight_SR_CR ) )
            vardb.registerCategory( MyCategory('MuMuSS_MMSideband_TT',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_SS','2Lep_SS','2Lep_MuMu_Event','TauVeto','2Lep_NJet_SR','TT']), weight = weight_SR_CR ) )
            # ElEl region
            #
            vardb.registerCategory( MyCategory('ElElSS_MMSideband_LL',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_ElEl_Event','2Lep_ElEtaCut','TauVeto','2Lep_NJet_SR','LL']), weight = weight_SR_CR ) )
            vardb.registerCategory( MyCategory('ElElSS_MMSideband_TL',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_ElEl_Event','2Lep_ElEtaCut','TauVeto','2Lep_NJet_SR','TL']), weight = weight_SR_CR ) )
            vardb.registerCategory( MyCategory('ElElSS_MMSideband_LT',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_ElEl_Event','2Lep_ElEtaCut','TauVeto','2Lep_NJet_SR','LT']), weight = weight_SR_CR ) )
            vardb.registerCategory( MyCategory('ElElSS_MMSideband_TT',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_ElEl_Event','2Lep_ElEtaCut','TauVeto','2Lep_NJet_SR','TT']), weight = weight_SR_CR ) )
            # OF region
            #
            vardb.registerCategory( MyCategory('OFSS_MMSideband_LL',    cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_OF_Event','2Lep_ElEtaCut','TauVeto','2Lep_NJet_SR','LL']), weight = weight_SR_CR ) )
            vardb.registerCategory( MyCategory('OFSS_MMSideband_TL',    cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_OF_Event','2Lep_ElEtaCut','TauVeto','2Lep_NJet_SR','TL']), weight = weight_SR_CR ) )
            vardb.registerCategory( MyCategory('OFSS_MMSideband_LT',    cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_OF_Event','2Lep_ElEtaCut','TauVeto','2Lep_NJet_SR','LT']), weight = weight_SR_CR ) )
            vardb.registerCategory( MyCategory('OFSS_MMSideband_TT',    cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_OF_Event','2Lep_ElEtaCut','TauVeto','2Lep_NJet_SR','TT']), weight = weight_SR_CR ) )

        elif "LOWNJ" in args.channel:

            # MuMu region
            #
            vardb.registerCategory( MyCategory('MuMuSS_MMSideband_LL',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_MuMu_Event','TauVeto','2Lep_NJet_CR','LL']), weight = weight_SR_CR ) )
            vardb.registerCategory( MyCategory('MuMuSS_MMSideband_TL',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_MuMu_Event','TauVeto','2Lep_NJet_CR','TL']), weight = weight_SR_CR ) )
            vardb.registerCategory( MyCategory('MuMuSS_MMSideband_LT',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_MuMu_Event','TauVeto','2Lep_NJet_CR','LT']), weight = weight_SR_CR ) )
            vardb.registerCategory( MyCategory('MuMuSS_MMSideband_TT',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_MuMu_Event','TauVeto','2Lep_NJet_CR','TT']), weight = weight_SR_CR ) )
            # ElEl region
            #
            vardb.registerCategory( MyCategory('ElElSS_MMSideband_LL',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_ElEl_Event','2Lep_ElEtaCut','TauVeto','2Lep_NJet_CR','LL']), weight = weight_SR_CR  ) )
            vardb.registerCategory( MyCategory('ElElSS_MMSideband_TL',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_ElEl_Event','2Lep_ElEtaCut','TauVeto','2Lep_NJet_CR','TL']), weight = weight_SR_CR  ) )
            vardb.registerCategory( MyCategory('ElElSS_MMSideband_LT',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_ElEl_Event','2Lep_ElEtaCut','TauVeto','2Lep_NJet_CR','LT']), weight = weight_SR_CR  ) )
            vardb.registerCategory( MyCategory('ElElSS_MMSideband_TT',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_ElEl_Event','2Lep_ElEtaCut','TauVeto','2Lep_NJet_CR','TT']), weight = weight_SR_CR  ) )
            # OF region
            #
            vardb.registerCategory( MyCategory('OFSS_MMSideband_LL',    cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_OF_Event','2Lep_ElEtaCut','TauVeto','2Lep_NJet_CR','LL']), weight = weight_SR_CR  ) )
            vardb.registerCategory( MyCategory('OFSS_MMSideband_TL',    cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_OF_Event','2Lep_ElEtaCut','TauVeto','2Lep_NJet_CR','TL']), weight = weight_SR_CR  ) )
            vardb.registerCategory( MyCategory('OFSS_MMSideband_LT',    cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_OF_Event','2Lep_ElEtaCut','TauVeto','2Lep_NJet_CR','LT']), weight = weight_SR_CR  ) )
            vardb.registerCategory( MyCategory('OFSS_MMSideband_TT',    cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_OF_Event','2Lep_ElEtaCut','TauVeto','2Lep_NJet_CR','TT']), weight = weight_SR_CR  ) )

        elif "ALLNJ" in args.channel:

            # MuMu region
            #
            vardb.registerCategory( MyCategory('MuMuSS_MMSideband_LL',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_MuMu_Event','TauVeto','2Lep_MinNJet','LL']), weight = weight_SR_CR  ) )
            vardb.registerCategory( MyCategory('MuMuSS_MMSideband_TL',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_MuMu_Event','TauVeto','2Lep_MinNJet','TL']), weight = weight_SR_CR  ) )
            vardb.registerCategory( MyCategory('MuMuSS_MMSideband_LT',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_MuMu_Event','TauVeto','2Lep_MinNJet','LT']), weight = weight_SR_CR  ) )
            vardb.registerCategory( MyCategory('MuMuSS_MMSideband_TT',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_MuMu_Event','TauVeto','2Lep_MinNJet','TT']), weight = weight_SR_CR  ) )
            # ElEl region
            #
            vardb.registerCategory( MyCategory('ElElSS_MMSideband_LL',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_ElEl_Event','2Lep_ElEtaCut','TauVeto','2Lep_MinNJet','LL']), weight = weight_SR_CR  ) )
            vardb.registerCategory( MyCategory('ElElSS_MMSideband_TL',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_ElEl_Event','2Lep_ElEtaCut','TauVeto','2Lep_MinNJet','TL']), weight = weight_SR_CR  ) )
            vardb.registerCategory( MyCategory('ElElSS_MMSideband_LT',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_ElEl_Event','2Lep_ElEtaCut','TauVeto','2Lep_MinNJet','LT']), weight = weight_SR_CR  ) )
            vardb.registerCategory( MyCategory('ElElSS_MMSideband_TT',  cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_ElEl_Event','2Lep_ElEtaCut','TauVeto','2Lep_MinNJet','TT']), weight = weight_SR_CR  ) )
            # OF region
            #
            vardb.registerCategory( MyCategory('OFSS_MMSideband_LL',    cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_OF_Event','2Lep_ElEtaCut','TauVeto','2Lep_MinNJet','LL']), weight = weight_SR_CR  ) )
            vardb.registerCategory( MyCategory('OFSS_MMSideband_TL',    cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_OF_Event','2Lep_ElEtaCut','TauVeto','2Lep_MinNJet','TL']), weight = weight_SR_CR  ) )
            vardb.registerCategory( MyCategory('OFSS_MMSideband_LT',    cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_OF_Event','2Lep_ElEtaCut','TauVeto','2Lep_MinNJet','LT']), weight = weight_SR_CR  ) )
            vardb.registerCategory( MyCategory('OFSS_MMSideband_TT',    cut = truth_cut & vardb.getCuts(['TrigDec','BlindingCut','2Lep_TrigMatch','2Lep_NBJet_SR','2Lep_NLep','2Lep_pT','2Lep_SS','2Lep_OF_Event','2Lep_ElEtaCut','TauVeto','2Lep_MinNJet','TT']), weight = weight_SR_CR  ) )

    # ------------------------------------------------------------
    # TTHBackgrounds is the class used to manage each process:
    #
    #   Pass the input informations and the definitions and it
    #   will perform the background estimation
    # ------------------------------------------------------------

    ttH = TTHBackgrounds(inputs, vardb)

    # ------------------------------------
    # Set the integrated luminosity (fb-1)
    # ------------------------------------

    ttH.luminosity = args.lumi

    ttH.lumi_units = 'fb-1'

    print ("Normalising to lumi ==> {0} [{1}]\n".format( args.lumi, ttH.lumi_units ) )

    # ----------------------------------
    # Set the global event weight for MC
    # ----------------------------------

    ttH.eventweight = "mcWeightOrg * pileupEventWeight_090"

    if args.noWeights:
        ttH.eventweight = "1.0"
        ttH.luminosity  = 1.0
        ttH.rescaleXsecAndLumi = True

    if doMMClosureTest or "CLOSURE" in args.channel:
        # Closure w/o any correction (but keep MC evt weight!)
        #
        if "NO_CORR" in args.channel:
            ttH.eventweight = "mcWeightOrg"

    # ------------------------------------

    ttH.noWeights = args.noWeights

    # ------------------------------------

    ttH.useZCorrections = False

    # ------------------------------------

    ttH.useSherpaNNPDF30NNLO = False

    # ------------------------------------

    if doTwoLepSR or doTwoLepLowNJetCR or dottWCR or doMMClosureTest:
        ttH.channel = 'TwoLepSS'
    elif doThreeLepSR or doThreeLepLowNJetCR or dottZCR or doWZonCR or doWZoffCR or doWZHFonCR or doWZHFoffCR:
        ttH.channel = 'ThreeLep'
    elif doFourLepSR:
        ttH.channel = 'FourLep'
    elif doDataMCCR or doZSSpeakCR or doMMRates or doCFChallenge or doMMSidebands or doTriggerEff:
        ttH.channel = 'TwoLepCR'

    events = {}
    hists  = {}

    # --------------------------------------
    # Dictionary with systematics histograms
    # --------------------------------------

    systs = {}

    # ----------------------------------
    # List of the backgrounds considered
    # ----------------------------------

    samplenames = {
        'Observed':'observed',
        'TTBarH':'signal',
        'TTBarHDilep':'signal',
        'tHbj':'tHbbkg',
        'WtH':'WtHbkg',
        'TTBarW':'ttbarwbkg',
        'TTBarZ':'ttbarzbkg',
        'SingleTop':'singletopbkg',
        'RareTop':'raretopbkg',
        'Triboson':'tribosonbkg',
        'Rare':'raretopbkg',
        'TTBar':'ttbarbkg',
        'TopCF':'topcfbkg',
        'Diboson':'dibosonbkg',
        'DibosonCF':'dibosoncfbkg',
        'Zjets':'zjetsbkg',
        'Zeejets':'zeejetsbkg',
        'Zmumujets':'zmumujetsbkg',
        'Ztautaujets':'ztautaujetsbkg',
        'ZjetsHF':'zjetsbkg',
        'ZjetsLF':'zjetsbkg',
        'ZjetsCF':'zjetscfbkg',
        'Wjets':'wjetsbkg',
        'Wenujets':'wenujets',
        'Wmunujets':'wmunujets',
        'Wtaunujets':'wtaunujets',
        'Prompt':'promptbkg',
        'QMisID':'qmisidbkg',
        'QMisIDMC':'qmisidbkg',
        'FakesMC':'fakesbkg',
        'FakesFF':'fakesbkg',
        'FakesMM':'fakesbkg',
        'FakesTHETA':'fakesbkg',
        'FakesClosureMM':'fakesbkg',
        'FakesClosureTHETA':'fakesbkg',
        'FakesClosureDataTHETA':'fakesbkg',
    }

    # Override colours!
    #
    colours = {
        'Observed':kBlack,
        'TTBarH':kRed,
        'TTBarHDilep':kRed,
        'tHbj':kPink+7,
        'WtH':kPink-4,
        'TTBarW':kYellow-9,
        'TTBarZ':kAzure+1,
        'SingleTop':kOrange+6,
        'RareTop':kOrange+7,
        'Triboson':kTeal+10,
        'Rare':kGray,
        'TTBar': kRed - 4,
        'TopCF':kAzure-4,
        'Diboson':kGreen-9,
        'DibosonCF':kOrange-3,
        'Zjets': kCyan -9,
        'Zeejets':kAzure+10,
        'Zmumujets':kAzure-3,
        'Ztautaujets':kCyan-7,
        'ZjetsHF':kGreen+2,
        'ZjetsLF':kGreen,
        'ZjetsCF':kGreen+4,
        'Wjets':kWhite,
        'Wenujets':kGray,
        'Wmunujets':kGray+1,
        'Wtaunujets':kGray+2,
        'Prompt':kOrange-3,
        'QMisID':kMagenta+1,
        'QMisIDMC':kMagenta+1,
        'FakesMC':kMagenta-9,
        'FakesMM':kMagenta-9,
        'FakesFF':kMagenta-9,
        'FakesMM':kMagenta-9,
        'FakesTHETA':kMagenta-9,
        'FakesClosureMM':kTeal+1,
        'FakesClosureTHETA':kCyan-9,
        'FakesClosureDataTHETA': kMagenta-9,
    }

    if ( doSR or doLowNJetCR ):

        ttH.signals     = ['TTBarH']
        ttH.observed    = ['Observed']

        if not doFourLepSR:

            if doMM:
                # ---> all the MC backgrounds use a truth req. of only prompt leptons in the event (and ch-flip veto) to avoid double counting with
                #      data-driven charge flip and fakes estimate

                ttH.backgrounds = ['TTBarW','TTBarZ','Diboson','Rare','FakesMM']
                #ttH.backgrounds = ['Prompt','FakesMM']
                ttH.sub_backgrounds = []

                if args.useMCQMisID:
                    ttH.backgrounds.append('QMisIDMC')
                    ttH.sub_backgrounds.append('QMisIDMC')
                else:
                    ttH.backgrounds.append('QMisID')
                    ttH.sub_backgrounds.append('QMisID')

            elif doFF:

                ttH.backgrounds     = ['TTBarW','TTBarZ','Diboson','Rare','FakesFF']
                ttH.sub_backgrounds = ['TTBarW','TTBarZ','Diboson','Rare']

                if args.useMCQMisID:
                    ttH.backgrounds.append('QMisIDMC')
                    ttH.sub_backgrounds.append('QMisIDMC')
                else:
                    ttH.backgrounds.append('QMisID')
                    ttH.sub_backgrounds.append('QMisID')

            elif doTHETA:

                ttH.backgrounds = ['TTBarW','TTBarZ','Diboson','Rare','FakesTHETA']
                ttH.sub_backgrounds = ['TTBarW','TTBarZ','Diboson','Rare']

                if args.useMCQMisID:
                    ttH.backgrounds.append('QMisIDMC')
                    ttH.sub_backgrounds.append('QMisIDMC')
                else:
                    ttH.backgrounds.append('QMisID')
                    ttH.sub_backgrounds.append('QMisID')

            else:

                # MC based estimate of fakes

                ttH.backgrounds = ['TTBarW','TTBarZ','Diboson','Rare','FakesMC']

                if args.useMCQMisID:
                    ttH.backgrounds.append('QMisIDMC')
                    ttH.sub_backgrounds.append('QMisIDMC')
                else:
                    ttH.backgrounds.append('QMisID')
                    ttH.sub_backgrounds.append('QMisID')

                if args.trigAcceptance:
                    ttH.backgrounds = ['TTBarH']

        else:
            # no fakes in 4lep
            ttH.backgrounds = ['TTBarW','TTBarZ','Diboson','TTBar','Rare','Zjets']

    if doMMRates:

        ttH.signals     = []
        ttH.observed    = ['Observed']
        if args.ratesMC:
            ttH.observed = []

        ttH.backgrounds = ['TTBar','SingleTop','Rare','Zjets','Wjets','TTBarW','TTBarZ','Diboson']

        if args.useMCQMisID:
            ttH.backgrounds.append('QMisIDMC')
        else:
            ttH.backgrounds.append('QMisID')

        if "CLOSURE" in args.channel:
            ttH.signals     = []
            ttH.observed    = []
            ttH.backgrounds = ['TTBar']
            #ttH.backgrounds = ['Zjets']

    if doTriggerEff:
        ttH.signals     = []
        ttH.observed    = []
        ttH.backgrounds = ['TTBar']


    if doMMSidebands:

        ttH.signals     = ['TTBarH']
        ttH.observed    = ['Observed']
        #ttH.backgrounds = ['TTBarW','TTBarZ','Diboson','Rare']
        ttH.backgrounds = ['Prompt']

        if args.useMCQMisID:
            ttH.backgrounds.append('QMisIDMC')
        else:
            ttH.backgrounds.append('QMisID')

        if "CLOSURE" in args.channel:
            ttH.signals     = []
            ttH.observed    = ['Observed']
            ttH.backgrounds = ['TTBar']

    if doDataMCCR:

        ttH.signals     = []
        ttH.observed    = ['Observed']

        ttH.backgrounds = ['TTBar','SingleTop','Rare','Zeejets','Zmumujets','Ztautaujets','Wjets','TTBarW','TTBarZ','Diboson']

        if not args.useMCQMisID:
            ttH.backgrounds.append('QMisID')

    if doZSSpeakCR:

        ttH.signals     = ['TTBarH']
        ttH.observed    = ['Observed']
        ttH.backgrounds = ['QMisIDMC','FakesMC','Prompt']

    if doCFChallenge:

        ttH.signals     = ['TTBarHDilep']
        ttH.observed    = ['Observed']
        ttH.backgrounds = ['TTBar']

    if doMMClosureTest:

        if doMM:
            ttH.signals     = [] # ['FakesClosureTHETA']
            ttH.observed    = ['TTBar']
            ttH.backgrounds = ['FakesClosureMM']
        elif doFF:
            ttH.signals     = []
            ttH.observed    = ['TTBar']
            ttH.backgrounds = ['FakesClosureFF']
        elif doTHETA:
            ttH.signals     = []
            ttH.observed    = ['TTBar']
            ttH.backgrounds = ['FakesClosureTHETA']
        else:
            ttH.signals     = []
            ttH.observed    = []
            ttH.backgrounds = ['TTBar']

    if args.noSignal:
        ttH.signals = []

    showRatio = args.doShowRatio
    if doMMClosureTest:
        showRatio = True

    # Make blinded plots in SR unless configured from input
    #
    if ( doSR or ( doMMSidebands and ( "HIGHNJ" in args.channel or "ALLJ" in args.channel ) ) ) and not args.doUnblinding:
        ttH.observed = []
        showRatio  = False

    # -------------------------------------------------------
    # Filling histname with the name of the variables we want
    #
    # Override colours as well
    # -------------------------------------------------------

    histname   = {'Expected':'expectedbkg','AllSimulation':'allsimbkg'}
    histcolour = {'Expected': kGray+1,'AllSimulation':kOrange+2}

    for sample in ttH.backgrounds:
        histname[sample]   = samplenames[sample]
        histcolour[sample] = colours[sample]
        #
        # Will override default colour based on the dictionary provided above
        #
        ttH.str_to_class(sample).colour = colours[sample]
    for sample in ttH.observed:
        histname[sample]   = samplenames[sample]
        histcolour[sample] = colours[sample]
        #
        # Will override default colour based on the dictionary provided above
        #
        ttH.str_to_class(sample).colour = colours[sample]
    for sample in ttH.signals:
        histname[sample]   = samplenames[sample]
        histcolour[sample] = colours[sample]
        #
        # Will override default colour based on the dictionary provided above
        #
        ttH.str_to_class(sample).colour = colours[sample]

    print "Processes:\n", histname
    print "Processes' colours:\n", histcolour

    # ---------------------------------
    # Processing categories in sequence
    # ---------------------------------

    fakeestimate = ""
    if doMM:
        fakeestimate="_MM"
    if doFF:
        fakeestimate="_FF"
    if doTHETA:
        fakeestimate="_THETA"
    if doMC:
        fakeestimate="_MC"

    basedirname = "OutputPlots" + fakeestimate + "_" + args.outdirname + "/"

    significance_dict = {}

    for category in sorted(vardb.categorylist, key=(lambda category: category.name) ):

        print ("\n*********************************************\n\nMaking plots in category:\t{0}\n".format( category.name ))

        # ----------------------------------------------------
        # Reset the weight for *this* category to 1 if neeeded
        # ----------------------------------------------------

        if args.noWeights or "NO_CORR" in args.channel:
	    print("Resetting category weight to 1...\n")
            category.weight = "1.0"

        # TEMP!
        # For DLT, trigger SF not available in v21 (and before).
        # Set trigger weight to 1
        #
        if "DLT" in args.trigger and "weight_event_trig" in category.weight:
	    print("Using DLT. Trigger SFs not available yet. Do not apply trigger SF...\n")
            category.weight = category.weight.replace("weight_event_trig","1.0")

        # ------------------------------
        # Processing different variables
        # ------------------------------

        for idx,var in enumerate(vardb.varlist, start=0):

            # ----------------------------------------------------
            # Reset the weight for *this* variable to 1 if neeeded
            # ----------------------------------------------------

            if args.noWeights or "NO_CORR" in args.channel and var.weight:
                var.weight = "1.0"

            # --------------------------
            # Avoid making useless plots
            # --------------------------

            if not ("OF") in category.name and ("Mu0Pt_VS_El0Pt") in var.shortname:
                print ("\tSkipping variable:\t{0}\n".format( var.shortname ))
                continue

            if ( ("MuMu") in category.name and ("El") in var.shortname ) or ( ("ElEl") in category.name and ("Mu") in var.shortname ):
                print ("\tSkipping variable:\t{0}\n".format( var.shortname ))
                continue

            if ( ( ("MuEl") in category.name ) and ( ("Mu1") in var.shortname ) ) :
                print ("\tSkipping variable:\t{0}\n".format( var.shortname ))
                continue

            if ( ( ("ElMu") in category.name ) and ( ("El1") in var.shortname ) ) :
                print ("\tSkipping variable:\t{0}\n".format( var.shortname ))
                continue

            if doMMRates or doTriggerEff:
                # if probe is a muon, do not plot ElProbe* stuff!
                if ( ( ("MuProbe") in category.cut.cutname ) and ( ("ElProbe") in var.shortname ) ):
                    print ("\tSkipping variable:\t{0}\n".format( var.shortname ))
                    continue
                # if probe is an electron, do not plot MuProbe* stuff!
                if ( ( ("ElProbe") in category.cut.cutname ) and ( ("MuProbe") in var.shortname ) ):
                    print ("\tSkipping variable:\t{0}\n".format( var.shortname ))
                    continue

            print ("\tPlotting variable:\t{0}\n\tNTup name:\t{1}\n".format(var.shortname, var.ntuplename))

            total_weight = ttH.eventweight
            if category.weight:
                total_weight += ( " * " + category.weight )
            if var.weight and not var.weight in category.weight:
                total_weight += ( " * " + var.weight )

            print ("\t-----------------------------------------------------------------------------------------------------------------------------\n")
            print ("\tMC event weight for this (category, variable):\n\n\t\t{0}\n".format( total_weight ) )
            print ("\t-----------------------------------------------------------------------------------------------------------------------------\n")

            # Get table w/ event yields for *this* category. Do it only for the first variable in the list
            #
            if ( args.printEventYields and idx is 0 ):
                events[category.name] = ttH.events(eventweight=category.weight, category=category, hmass=['125'])

            #"""

            # ---------------------------------------------------------
            # Creating a directory for the category if it doesn't exist
            # ---------------------------------------------------------

            dirname = basedirname + category.name

            if args.doLogScaleX:
                dirname += "_LOGX"
            if args.doLogScaleY:
                dirname += "_LOGY"

            if not os.path.exists(dirname):
                os.makedirs(dirname)

            # -----------------------------------------------
            # Making a plot with ( category + variable ) name
            # -----------------------------------------------

            plotname = dirname + "/" + category.name + "_" + var.shortname

            if ( args.debug ):
                print ("\tPlotname: {0}\n".format( plotname ))


            # If this option is set True, the last visible bin of the histogram will contain ALSO the overflow

            merge_overflow = args.mergeOverflow

            list_formats = [ plotname + ".png", plotname + ".eps" ]

            # Here is where the plotting is actually performed!
            #
            hists[category.name + ' ' + var.shortname] = ttH.plot( var,
                                                                   eventweight=category.weight,
                                                                   category=category,
                                                                   signal='',#'125',
                                                                   signalfactor=1.0,
                                                                   overridebackground=ttH.backgrounds,
                                                                   overflowbins=merge_overflow,
                                                                   showratio=showRatio,
                                                                   wait=False,
                                                                   save=list_formats,
                                                                   log=args.doLogScaleY,
                                                                   logx=args.doLogScaleX
                                                                 )

            # Creating a file with the observed and expected distributions and systematics.
            #
            foutput = TFile(plotname + ".root","RECREATE")
            if ( "Mll01" in var.shortname ) or ( "NJets" in var.shortname ) or ( "ProbePt" in var.shortname ):
                outfile = open(plotname + "_yields.txt", "w")

            if args.doSyst:

                # systematics go into a different folder
                #
                dirname += "_Syst"

                # loop on the defined systematics
                #
                total_syst      = 0.0
                total_syst_up   = 0.0
                total_syst_down = 0.0
                histograms_syst = {}

                for syst in vardb.systlist:

                    if not os.path.exists(dirname):
                        os.makedirs(dirname)

                    plotname = dirname + "/" + category.name + "_" + var.shortname + "_" + syst.name

                    print("")
		    print ("\t\t-----------------------------------------------------------------------------------------------------------------------------\n")
                    print ("\t\tSystematic:\t{0}\n".format( syst.name ))
                    if args.debug:
		        print ("\t\tDirectory for systematic plot:\t{0}/".format( plotname ))
                    print ("\t\t-----------------------------------------------------------------------------------------------------------------------------\n")

                    list_formats_sys = [ plotname + ".png", plotname + ".eps" ]

                    # plotSystematics is the function which takes care of the systematics
                    #
                    systs[category.name + " " + var.shortname] = ttH.plotSystematics( syst,
                                                                                      var=var,
                                                                                      eventweight=category.weight,
                                                                                      category=category,
                                                                                      overflowbins=merge_overflow,
                                                                                      showratio=True,
                                                                                      wait=False,
                                                                                      save=list_formats_sys,
                                                                                      log=args.doLogScaleY,
                                                                                      logx=args.doLogScaleX
                                                                                      )

                    # Obtaining histograms for processes and total expected histogram with a particular systematics shifted,
                    # and saving them in the ROOT file
                    #
                    systobs, systnom, systup, systdown, systlistup, systlistdown = systs[category.name + " " + var.shortname]

                    histograms_syst["Expected_"+syst.name+"_up"]=systup
                    histograms_syst["Expected_"+syst.name+"_up"].SetNameTitle(histname["Expected"]+"_"+syst.name+"_up","")
                    histograms_syst["Expected_"+syst.name+"_up"].SetLineColor(histcolour["Expected"])
                    histograms_syst["Expected_"+syst.name+"_up"].Write()
                    histograms_syst["Expected_"+syst.name+"_dn"]=systdown
                    histograms_syst["Expected_"+syst.name+"_dn"].SetNameTitle(histname["Expected"]+"_"+syst.name+"_dn","")
                    histograms_syst["Expected_"+syst.name+"_dn"].SetLineColor(histcolour["Expected"])
                    histograms_syst["Expected_"+syst.name+"_dn"].Write()

                    # The code does not consider systematics on the signal.
                    # Put the signal in the backgrounds list if you want systematics on it.

                    for samp in ttH.backgrounds:
                        if syst.process and not ( syst.process == samp ) :
                            continue
                        histograms_syst[samp+"_"+syst.name+"_up"] = systlistup[samp]
                        histograms_syst[samp+"_"+syst.name+"_up"].SetNameTitle(histname[samp]+"_"+syst.name+"_up","")
                        histograms_syst[samp+"_"+syst.name+"_up"].SetLineColor(histcolour[samp])
                        histograms_syst[samp+"_"+syst.name+"_up"].Write()
                        histograms_syst[samp+"_"+syst.name+"_dn"] = systlistdown[samp]
                        histograms_syst[samp+"_"+syst.name+"_dn"].SetNameTitle(histname[samp]+"_"+syst.name+"_dn","")
                        histograms_syst[samp+"_"+syst.name+"_dn"].SetLineColor(histcolour[samp])
                        histograms_syst[samp+"_"+syst.name+"_dn"].Write()

                    if ( "Mll01" in var.shortname ) or ( "NJets" in var.shortname ) or ( "ProbePt" in var.shortname ):
                        outfile.write("Integral syst: \n")
                        outfile.write("syst %s up:   delta_yields = %.2f \n" %(syst.name,(systup.Integral()-systnom.Integral())))
                        outfile.write("syst %s down: delta_yields = %.2f \n" %(syst.name,(systdown.Integral()-systnom.Integral())))
                        if ( args.debug ):
                            outfile.write("GetEntries syst: \n")
                            outfile.write("syst %s up:   delta_entries %.2f \n" %(syst.name,(systup.GetEntries()-systnom.GetEntries())))
                            outfile.write("syst %s down: delta_entries %.2f \n" %(syst.name,(systdown.GetEntries()-systnom.GetEntries())))
                    total_syst      += (systup.Integral()-systdown.Integral())/2.0*(systup.Integral()-systdown.Integral())/2.0
                    total_syst_up   += (systup.Integral()-systnom.Integral())*(systup.Integral()-systnom.Integral())
                    total_syst_down += (systdown.Integral()-systnom.Integral())*(systdown.Integral()-systnom.Integral())

                total_syst      = math.sqrt(total_syst)
                total_syst_up   = math.sqrt(total_syst_up)
                total_syst_down = math.sqrt(total_syst_down)

                if ( "Mll01" in var.shortname ) or ( "NJets" in var.shortname ) or ( "ProbePt" in var.shortname ):
                    outfile.write("yields total syst UP: %.2f \n" %(total_syst_up))
                    outfile.write("yields total syst DN: %.2f \n" %(total_syst_down))
                    outfile.write("yields total syst: %.2f \n" %(total_syst))

            # ------------------------------------------------------------------

            # Obtain the histograms correctly normalized
            #
            bkghists, expected, observed, signal, _ = hists[category.name + " " + var.shortname]
            histograms = {}

            for sample in ttH.observed:

                histograms[sample] = observed

            if ttH.backgrounds:

                histograms["Expected"] = expected

                # Store an additional histogram as the sum of all the MC-based backgrounds (useful e.g. to get all "prompt" backgrounds in one go)
                # Take the first *non-data-driven* sample in the background histograms list and clone it, then add all the others
                #

                allsim = TH1D()
                (firstsim_idx, firstsim_name) = ttH.getFirstSimulatedProc(category)
                if firstsim_name:
                    allsim = bkghists[firstsim_name].Clone(histname["AllSimulation"])

                for idx, sample in enumerate(ttH.backgrounds):
                    histograms[sample] = bkghists[sample]
                    if idx != firstsim_idx  and ( not "QMisID" in sample ) and ( not "Fakes" in sample):
                        allsim.Add(bkghists[sample].Clone(histname[sample]))

                histograms["AllSimulation"] = allsim

                if ttH.signals:
                    for sample in ttH.signals:
                        histograms[sample] = signal

                # ------------------------------------------------------------------

                # Set basic properties for histograms
                #
                for sample in histograms.keys():
                    histograms[sample].SetNameTitle(histname[sample],"")
                    histograms[sample].SetLineColor(histcolour[sample])
                    histograms[sample].SetMarkerColor(histcolour[sample])

                # ------------------------------------------------------------------

                # Print yields
                #
                if any( v in var.shortname for v in ["Mll01","NJets","ProbePt"] ) and not ( var.typeval in [TH2I,TH2D,TH2F] ):

                    s = 0
                    err_s = Double(0)
                    err_b = Double(0)
                    if ttH.signals:
                        s = histograms["TTBarH"].IntegralAndError(0,histograms["TTBarH"].GetNbinsX(),err_s)
                    b = histograms["Expected"].IntegralAndError(0,histograms["Expected"].GetNbinsX(),err_b)

                    print (" ")
                    print ("\t\tCategory: {0} - Variable: {1}\n".format( category.name, var.shortname ))
                    print ("\t\tIntegral:\n")
                    outfile.write("Category: %s \n" %(category.name))
                    outfile.write("Variable: %s \n" %(var.shortname))
                    outfile.write("Integral: \n")
                    err=Double(0)  # integral error
                    value=0        # integral value

		    for sample in histograms.keys():

			# Include underflow, but if option merge_overflow = True, do not take overflow explicitly! In fact, in that case
                        # the last bin will be merged with the OFlow bin
                        #
                        if merge_overflow:
                            last_bin_idx = histograms[sample].GetNbinsX()
                        else:
                            last_bin_idx = histograms[sample].GetNbinsX()+1

                        value = histograms[sample].IntegralAndError(0,last_bin_idx,err)

			yields_outstream     = "\t\t{0}: {1:.2f} +- {2:.2f}".format(histname[sample], value, err)
			yields_outfilestream = "yields {0}: {1:.2f} +- {2:.2f}".format(histname[sample], value, err)

                        if b and not sample in ["Observed","TTBarH","Expected"]:

			    yields_outstream     += " ({0:.1f} % tot. bkg.)".format((value/b)*1e2)
			    yields_outfilestream += " ({0:.1f} % tot. bkg.)".format((value/b)*1e2)

			print (yields_outstream)
                        outfile.write(yields_outfilestream)

                        # Print each bin content
                        #
			if ( "NJets" in var.shortname ):
                            # Neglect underflow, but not overflow!
                            #
                            for bin in range(1,histograms[sample].GetNbinsX()+2):
                                err_bin   = Double(0)
                                value_bin = 0
                                this_bin  = histograms[sample].GetBinCenter(bin)
                                value_bin = histograms[sample].GetBinContent(bin)
                                err_bin   = histograms[sample].GetBinError(bin)

                                if (histograms[sample].IsBinOverflow(bin)):
                                    print ("\t\t  OVERFLOW BIN:")
                                    outfile.write("  OVERFLOW BIN:\n")

                                # If it"s the last bin before OFlow, and merge_overflow = True, subtract OFlow from this bin
                                #
                                if ( merge_overflow and histograms[sample].IsBinOverflow(bin+1) ):
                                    value_bin -= histograms[sample].GetBinContent(bin+1)
                                    err_bin   = 0
                                print ("\t\t  {0}-jets bin: {1:.2f} +- {2:.2f}".format(this_bin, value_bin, err_bin))
                                outfile.write("  %i-jets bin: %.2f +- %.2f \n" %(this_bin, value_bin, err_bin))

                            # Get integral and error from njets>=5 bins (including OFlow) in one go!
                            #
                            if ( var.shortname == "NJets" ):
                                err_HJ   = Double(0)
                                value_HJ = histograms[sample].IntegralAndError (6,last_bin_idx,err_HJ)
                                print ("\n\t\t  >=5-jets bin: {0:.2f} +- {1:.2f}".format(value_HJ, err_HJ))
                                outfile.write("\n  >=5-jets bin: %.2f +- %.2f \n" %(value_HJ, err_HJ))

                    if not args.noSignal and ttH.signals:

			Z = calculate_Z( s, b, err_s, err_b )

                        print("\n\t\tSignificance:\n\t\ts = {0:.2f} +- {1:.2f}\n\t\tb = {2:.2f} +- {3:.2f}\n\t\tZ = {4:.3f} +- {5:.3f}".format(s, err_s, b, err_b, Z[0], Z[1]) )
                        outfile.write("\nSignificance:\ns = %.2f +- %.2f\nb = %.2f +- %.2f\nZ = %.3f +- %.3f\n" %(s, err_s, b, err_b, Z[0], Z[1]))

                    	if args.optimisation:

		      	    tokens = category.name.split("_")
                    	    key   = tokens[0]
                    	    bin_lep0   = float(tokens[tokens.index("Lep0")+1])
                    	    bin_lep1   = float(tokens[tokens.index("Lep1")+1])

                    	    if not significance_dict.get(key):
                    		significance_dict[key] = [ (bin_lep0, bin_lep1, Z[0], Z[1]) ]
                    	    else:
                    		significance_dict[key].append( (bin_lep0, bin_lep1, Z[0], Z[1]) )

                    print ("\n\t\tGetEntries:\n")
                    print ("\t\tNB 1): this is actually N = GetEntries()-2 \n\t\t       Still not understood why there's such an offset...\n")
                    print ("\t\tNB 2): this number does not take into account overflow bin. Better to look at the integral obtained with --noWeights option...\n")
                    outfile.write("\nGetEntries: \n")
                    for sample in histograms.keys():
                        print ("\t\t{0}: {1}".format(histname[sample], histograms[sample].GetEntries()-2))
                        outfile.write("entries %s: %f \n" %(histname[sample], histograms[sample].GetEntries()-2))

                for sample in histograms.keys():
                    histograms[sample].Write()
                foutput.Close()

                if ( "Mll01" in var.shortname ) or ( "NJets" in  var.shortname ) or ( "ProbePt" in var.shortname ):
                    outfile.close()

            #"""

    if not args.noSignal and args.optimisation:
        if "SLT" in args.optimisation:
            dim = "1D"
        elif "DLT" in args.optimisation:
            dim = "2D"
        plot_significance( significance_dict, dim )
