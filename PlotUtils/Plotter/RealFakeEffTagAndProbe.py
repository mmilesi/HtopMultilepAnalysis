#!/usr/bin/env python

""" RealFakeEffTagAndProbe.py: measure r/f efficiencies/rates for Matrix Method and Fake Factor Method with T&P method"""

__author__     = "Marco Milesi"
__email__      = "marco.milesi@cern.ch"
__maintainer__ = "Marco Milesi"

import os, sys, array, math

sys.path.append(os.path.abspath(os.path.curdir))

# -------------------------------
# Parser for command line options
# -------------------------------
import argparse

parser = argparse.ArgumentParser(description="Module for deriving real/fake lepton efficiencies/rates for MM/FF")

#***********************************
# positional arguments (compulsory!)
#***********************************

parser.add_argument("inputpath", metavar="inputpath",type=str,
                  help="path to the directory containing subdirs w/ input files")

#*******************
# optional arguments
#*******************

parser.add_argument('--variables', dest='variables', action='store', type=str, nargs='*',
                  help='List of variables to be considered. Use a space-separated list. If unspecified, will consider pT only.')
parser.add_argument("--channel", metavar="channel", default="", type=str,
                  help="Flavour composition of the two leptons in CR to be considered (\"ElEl\", \"MuMu\", \"OF\"). If unspecified, will consider all combinations.")
parser.add_argument("--closure", dest="closure", action="store_true",default=False,
                  help="Estimate efficiencies using MonteCarlo (for closure test)")
parser.add_argument("--debug", dest="debug", action="store_true",default=False,
                  help="Run in debug mode")
parser.add_argument("--nosub", dest="nosub", action="store_true",default=False,
                  help="Do not subtract backgrounds to data (NB: subtraction is disabled by default when running w/ option --closure)")
parser.add_argument('--sysstematics', dest='systematics', action='store', default="", type=str, nargs='*',
                  help='Option to pass a list of systematic variations to be considered. Use a space-separated list.')
parser.add_argument("--log", dest="log", action="store_true",default=False,
                  help="Read plots with logarithmic Y scale.")
parser.add_argument('--rebin', dest='rebin', action='store', type=str, nargs='+',
                  help='Option to pass a bin range for rebinning. Use space-separated lists of numbers to define new bins, specifying whether it should apply to real/fake muons/electrons for a given variable in the following way (eg.):\n --rebin Real,El,Pt,10,20,200 Fake,Mu,Eta,0.0,1.3,2.5')

args = parser.parse_args()

from ROOT import ROOT, gROOT, TH1, TH1D, TFile, TGraphAsymmErrors, TEfficiency, Double

gROOT.SetBatch(True)
TH1.SetDefaultSumw2()

class RealFakeEffTagAndProbe:

    def __init__( self, closure=False, variables=[], systematics=[], efficiency=None, nosub=False ):

	self.closure = closure

        self.tp_lep = "Probe"

    	self.__channels     = {"" : ["El","Mu"], "ElEl": ["El"], "MuMu": ["Mu"], "OF" : ["El","Mu"]}
        self.__leptons      = []
    	self.__efficiencies = ["Real","Fake"]
    	self.__variables    = ["Pt"]
    	self.__selections   = ["L","T","AntiT"]
    	self.__inputs       = []
    	self.__subtraction  = []
    	self.__systematics  = []

	if not self.closure:
	    self.__inputs.append("observed")
            if not nosub:
                self.__subtraction.extend(["qmisidbkg","allsimbkg"])
	else:
	    self.__inputs.append("expectedbkg")

        if efficiency:
            self.__efficinecies.append(efficiency)

        if variables:
            for var in variables:
                if var not in self.__variables:
                    self.__variables.append(var)

        if systematics:
            for sys in systematics:
                self.__systematics.append(sys)


    	# -----------------------------------------
    	# these dictionaries will store the inputs
    	# -----------------------------------------

        self.histkeys = []
	
        self.loose_hists     = {}
        self.tight_hists     = {}
        self.antitight_hists = {}

    	# -----------------------------------------
    	# these dictionaries will store the outputs
    	# -----------------------------------------

    	self.histefficiencies	= {}
    	self.grapheffieciencies = {}
    	self.tefficiencies      = {}
    	self.yields             = {}

	# ---------------
    	# General options
    	# ---------------

	self.debug = False
	self.log   = False

    def subtract( self, inputfile, inputhist ):

        if self.debug:
            print("\nSubtracting events to data...")
            print("********************************************")
            print("Events BEFORE subtraction in histogram {0}: {1}".format( inputhist.GetName(), inputhist.Integral(0,inputhist.GetNbinsX()+1) ) )
            print("********************************************")

        for proc in self.__subtraction:

            thishist = inputfile.Get(proc)

            if self.debug:
                print("Now subtracting {0}".format(proc))
                print("Events in histogram {0}: {1}".format( thishist.GetName(), thishist.Integral(0,inputhist.GetNbinsX()+1) ) )

            inputhist.Add( thishist, -1 )

        if self.debug:
            print("********************************************")
            print("Events AFTER subtraction in histogram {0}: {1}".format( inputhist.GetName(), inputhist.Integral(0,inputhist.GetNbinsX()+1) ) )
            print("********************************************")

        return inputhist

    def readInputs(self, inputpath=None, channel=None, log=False):

        if inputpath and inputpath.endswith("/"):
            inputpath = inputpath[:-1]

        log_suffix = ("","_LOGY")[bool(self.log)]

        self.__leptons = self.__channels[channel]

        print("Leptons to be considered:")
        print("\n".join("{0}".format(lep) for lep in self.__leptons))
        print("********************************************")
        print("Efficiencies to be considered:")
        print("\n".join("{0}".format(eff) for eff in self.__efficiencies))
        print("********************************************")
        print("Variables to be considered:")
        print("\n".join("{0}".format(var) for var in self.__variables))
        print("********************************************")

        filename = None

        for lep in self.__leptons:

            for eff in self.__efficiencies:

                actual_eff = eff

                for var in self.__variables:

                    for sel in self.__selections:

                        filename = ( inputpath + "/" + channel + actual_eff + "CR" + lep + sel + log_suffix + "/" + channel + actual_eff + "CR" + lep + sel + "_" + lep + self.tp_lep + var + ".root" )

                        thisfile = TFile(filename)
                        if not thisfile:
                            sys.exit("ERROR: file:\n{0}\ndoes not exist!".format(filename))

                        for proc in self.__inputs:
                            thishist = thisfile.Get(proc)
                            if ( proc == "observed" ) and self.__subtraction:
                                thishist = self.subtract(thisfile, thishist)

                            key = "_".join( (actual_eff,lep,var,proc) )
			    
			    if not key in self.histkeys:
			        self.histkeys.append(key)
			    
                            thishist.SetName(key)

                            thishist.SetDirectory(0)

                            if sel == "T":
                                self.tight_hists[key] = thishist
                            elif sel == "L":
                                self.loose_hists[key] = thishist
                            elif sel == "AntiT":
                                self.antitight_hists[key] = thishist


    def rebinHistograms (self, rebinlist=None):

        if not rebinlist:
            print("Will not do any rebinning...")
            return

        for key in self.histkeys: 
	
	    # By construction, the following will be a list w/ 4 items, where:
	    #
	    # tokens[0] = efficiency ("Real","Fake"...)
	    # tokens[1] = lepton ("El","Mu"...)
	    # tokens[2] = variable ("Pt","Eta"...)
	    # tokens[3] = process ("observed","expectedbkg"...)
	    
	    tokens = key.split("_")
	    
	    print("Current tokens:")
	    print tokens
		    	    
            for rebinitem in rebinlist:
	    
	        rebinitem = rebinitem.split(",")
		
	        if ( tokens[0] in rebinitem ) and ( tokens[1] in rebinitem ) and ( tokens[2] in rebinitem ):

                    nbins = len(rebinitem[3:])-1
		    
                    print("\t===> Rebinning matching histograms with the following values:")
		    print "\tbin edges: ", rebinitem[3:], ", number of bins = ", nbins
	                  
		    bins = [ float(binedge) for binedge in rebinitem[3:] ]	                   
	            arr_bins = array.array("d", bins)
		    
		    self.tight_hists[key].Rebin( nbins, key, arr_bins )                                
		    self.loose_hists[key].Rebin( nbins, key, arr_bins )                                
		    self.antitight_hists[key].Rebin( nbins, key, arr_bins )                                



    def rateToEfficiency(self, r):
        if r < 0:
            r = 0.0
	e = r/(r+1)
        return e

    def efficiencyToRate(self, e):
	r = e/(1-e)
        return r

# -------------------------------------------

if __name__ == "__main__":

    eff = RealFakeEffTagAndProbe( closure=args.closure, variables=args.variables, systematics=args.systematics, nosub=args.nosub )

    eff.debug = args.debug
    eff.log   = args.log

    eff.readInputs( inputpath=args.inputpath, channel=args.channel )

    if eff.debug:
        print("\n\nTIGHT histograms dictionary:\n")
        print("\tkey\t\thistname\n")
        for key, value in eff.tight_hists.iteritems():
            print("\t{0}\t{1}".format(key, value.GetName()))

        print("\n\nLOOSE histograms dictionary:\n")
        print("\tkey\t\thistname\n")
        for key, value in eff.loose_hists.iteritems():
            print("\t{0}\t{1}".format(key, value.GetName()))

        print("\n\nANTI-TIGHT histograms dictionary:\n")
        print("\tkey\t\thistname\n")
        for key, value in eff.antitight_hists.iteritems():
            print("\t{0}\t{1}".format(key, value.GetName()))

    eff.rebinHistograms( rebinlist=args.rebin )
    
    
    
# -------------------------------------------
"""

if __name__ == "__main__":


    # ---------------------------------------------------------------------------------
    # NB: the following string definitions are to be chosen according to the
    #     output name of the files (produced by the MakePlots_HTopMultilep.py scripts)
    #     used for comuting the T/!T(=L) ratio to derive rates.
    #
    #     An example name could be:
    #
    #      MuElFakeCRMuL_ElProbePt
    #
    #      channels[h] + lep_types[i] + CR + leptons[j] + selections[k] + leptons[l] + variables[m]
    # ---------------------------------------------------------------------------------

    if args.rebinEta or args.rebinPt or args.doAvg:
        print("\n******************************************************************************************************\n\nWill perform histogram rebinning...")
        print("\nWARNING!\n(From TH1 docs) If ngroup is not an exact divider of the number of bins, the top limit of the rebinned histogram is reduced to the upper edge of the last bin that can make a complete group.")
        print("The remaining bins are added to the overflow bin. Statistics will be recomputed from the new bin contents.\n")
        print("If rebinning to one single bin, this might lead to an \"empty\" histogram (as everything will end up in the overflow bin)")
        print("\n******************************************************************************************************\n")

    # -------------------------------------------------------
    # for each channel, store which leptons can be associated
    # -------------------------------------------------------
    dict_channels_lep = {
                       "ElEl": ["El"],
                       "OF"  : ["El","Mu"],
                       ""    : ["El","Mu"],
                       "MuMu": ["Mu"]
                      }

    list_lep         = dict_channels_lep[args.flavourComp]
    list_types       = ["Real","RealQMisIDBinning","Fake"]
    list_variables   = ["ProbePt","ProbeEta"] #"ProbeNJets"]
    list_selections  = ["L","T","AntiT"]
    list_prediction  = ["expected", "observed"]   # expected --> use MC distribution for probe lepton to derive the rate (to be used only as a cross check, and in closure test)
                                                  # observed --> use DATA distribution for probe lepton to derive the rate - need to subtract the prompt/ch-flips here!
    list_out_samples = ["factor","factorbkgsub","rate","ratebkgsub"]

    hists  = {}
    graphs = {}
    tefficiencies = {}
    yields = {}
    fin    = []

    channel_str = ""
    if ( args.flavourComp is not "" ):
        #channel_str = "_" + args.flavourComp
        channel_str = args.flavourComp
        print " channel string: ", channel_str

    log_plot = ("","_LOGY")[bool(args.useLogPlots)]

    # For later use
    #
    hist_eff_electron_real = None
    htmp_QMisID = None
    htmp_Prompt = None
    htmp_Data   = None

    for iLep in list_lep:

        print "looking at lepton of flavour: " , iLep

        for iVar in list_variables:

            print "\t looking at variable: " , iVar

            for iType in list_types:

                print "\t\t looking at rate of type: ", iType

                for iSel in list_selections:

                    print "\t\t\t object  is: ", iSel

                    iActualType = iType
                    if iType == "RealQMisIDBinning": iActualType = "Real"

                    fname = args.inputDir + channel_str + iActualType + "CR" + iLep + iSel + log_plot + "/" + channel_str + iActualType + "CR" + iLep + iSel + "_" + iLep + iVar + ".root"

                    print "\t\t\t input filename: ", fname

                    fin.append( TFile(fname) )

                    # Get the QMisID, Prompt, and Data histograms for weight calculation in
		    # the LOOSE region
		    #
		    prompt_list = []
                    if  ( args.usePrediction == "DATA" ) and ( iType == "Fake" ) and ( iLep == "El" ) and ( iVar == "ProbePt" ) and ( iSel == "L" ):
                        htmp_QMisID = fin[-1].Get("qmisidbkg")
                        if not htmp_QMisID:
                            sys.exit("ERROR: histogram w/ name \"qmisidbkg\" does not exist in input file")

			htmp_Prompt = fin[-1].Get("ttbarzbkg")
			prompt_list.append( fin[-1].Get("dibosonbkg") )
			prompt_list.append( fin[-1].Get("raretopbkg") )
			prompt_list.append( fin[-1].Get("ttbarwbkg") )
			prompt_list.append( fin[-1].Get("wjetsbkg") )
			prompt_list.append( fin[-1].Get("ttbarbkg") )
			prompt_list.append( fin[-1].Get("zjetsbkg") )
                        for hist in prompt_list:
			    htmp_Prompt.Add(hist)
			htmp_Data = fin[-1].Get("observed")

                    for iPred in list_prediction:

                        standard_rebin = False

                        print "\t\t\t\t checking prediction from: ", iPred

                        # L[-1] can be used to access the last item in a list
                        htmp = fin[-1].Get( iPred ) # will be either "expected", or "observed"

                        # let the macro know the name of the histogram in the input ROOT file
                        #
                        # do not even bother for "observed" hist if usePrediction = MC
                        #
                        if ( args.usePrediction == "MC" ) and ( iPred == "observed" ) :
                            continue

                        if not htmp:
                            sys.exit("ERROR: histogram w/ name %s does not exist in input file", iPred)

                        histname = iLep + "_" + iVar + "_" + iType + "_" + iSel + "_" + iPred

                        print "\t\t\t\t\t output histname (Num,Denom): ", histname

                        # make a clone of this histogram (expected/observed) by default
                        #
                        hists[histname]  = htmp.Clone( histname )

                        # make a clone also of the QMisID,Data,Prompt histogram (do it only once, for the LOOSE selection)
                        #
                        if  ( args.usePrediction == "DATA" ) and ( iType == "Fake" ) and ( iLep == "El" ) and ( iVar == "ProbePt" ) and ( iSel == "L" ):
			    histname_QMisID = histname + "_QMisID"
			    histname_Prompt = histname + "_Prompt"
			    histname_Data   = histname + "_Data"
			    hists[histname_QMisID]  = htmp_QMisID.Clone( histname_QMisID )
			    hists[histname_Prompt]  = htmp_Prompt.Clone( histname_Prompt )
			    hists[histname_Data]    = htmp_Data.Clone( histname_Data )

                        if iVar == "ProbeEta":

                            if args.rebinEta:

                                if iLep == "Mu":
                                    nBIN  = 5
                                    xbins = [ 0.0 , 0.1 , 0.7, 1.3 , 1.9, 2.5 ]
                                    # the rebinning method automatically creates a new histogram
                                    #
                                    vxbins = array.array("d", xbins)
                                    print "\t\t\t\t\t vxbins: ",vxbins
                                    hists[histname]  = htmp.Rebin( nBIN, histname, vxbins )
                                    if htmp_QMisID : hists[histname_QMisID]  = htmp_QMisID.Rebin( nBIN, histname_QMisID, vxbins )
                                    if htmp_Prompt : hists[histname_Prompt]  = htmp_Prompt.Rebin( nBIN, histname_Prompt, vxbins )
                                    if htmp_Data   : hists[histname_Data]    = htmp_Data.Rebin( nBIN, histname_Data, vxbins )

                                elif iLep == "El":

                                    nBIN  = 6
                                    xbins = [ 0.0 , 0.5 , 0.8 , 1.37 , 1.52 , 2.0 , 2.6]
                                    # the rebinning method automatically creates a new histogram
                                    #
                                    vxbins = array.array("d", xbins)
                                    print "\t\t\t\t\t vxbins: ",vxbins
                                    hists[histname]  = htmp.Rebin( nBIN, histname, vxbins )
                                    if htmp_QMisID : hists[histname_QMisID]  = htmp_QMisID.Rebin( nBIN, histname_QMisID, vxbins )
                                    if htmp_Prompt : hists[histname_Prompt]  = htmp_Prompt.Rebin( nBIN, histname_Prompt, vxbins )
                                    if htmp_Data   : hists[histname_Data]    = htmp_Data.Rebin( nBIN, histname_Data, vxbins )

                        elif iVar == "ProbePt":

                            if args.rebinPt:

                                if iType == "Fake":

                                    if iLep == "Mu":

                                        if args.doAvgMuFake:

                                            # Make one single bin from 25 to 200
                                            #
                                            #nBIN = htmp.GetNbinsX()
                                            #xbins  = [htmp.GetBinLowEdge(1),htmp.GetBinLowEdge(htmp.GetNbinsX()+1)]
                                            #standard_rebin = True

                                            nBIN  = 4
                                            xbins = [10,15,20,25,200]

                                        else:
                                            # nominal binning
                                            #
                                            nBIN  = 5
                                            xbins = [10,15,20,25,35,200] # merged bin [50,200] - this binning works a bit better for ttbar MC at medium-high pT range

                                    elif iLep == "El":

                                        if args.doAvgElFake:

                                            # Make one single bin from 25 to 200

                                            nBIN  = 4
                                            xbins = [10,15,20,25,200]

				        else:
                                            # nominal binning
                                            #
                                            nBIN  = 5
                                            xbins = [10,15,20,25,40,200] # merged bin [60,200]

					    # TEMP! ---> test with probe trigger matching
                                            #nBIN  = 5
                                            #xbins = [10,15,20,25,60,200] # --> follows trigger thresholds

                                elif iType == "Real":

                                    # standard binning
                                    #
                                    nBIN  = 7
                                    xbins = [10,15,20,25,30,40,60,200]

				    # TEMP! ---> test with probe trigger matching
                                    #
				    #if iLep == "Mu":
				    #    nBIN  = 5
                                    #    xbins = [10,15,20,25,50,200] # --> follows trigger thresholds
				    #elif iLep == "El":
				    #    nBIN  = 6
                                    #    xbins = [10,15,20,25,60,140,200] # --> follows trigger thresholds

                                elif iType == "RealQMisIDBinning":

                                    # Need this binning to get the weighted fake eff from QMisID eff.
                                    #
                                    if args.doAvgElFake:

                                    	# Make one single bin from 25 to 200
                                    	#
                                    	#nBIN = htmp.GetNbinsX()
                                    	#xbins  = [htmp.GetBinLowEdge(1),htmp.GetBinLowEdge(htmp.GetNbinsX()+1)]
                                    	#standard_rebin = True

                                    	nBIN  = 4
                                    	xbins = [10,15,20,25,200]

				    else:
                                        nBIN  = 5
                                        xbins = [10,15,20,25,40,200]

                                vxbins = array.array("d", xbins)
                                print "\t\t\t\t\t vxbins: ",vxbins
                                # the rebinning method automatically creates a new histogram
                                #
                                if not standard_rebin:
                                    hists[histname] = htmp.Rebin( nBIN, histname, vxbins )
                                    if htmp_QMisID : hists[histname_QMisID]  = htmp_QMisID.Rebin( nBIN, histname_QMisID, vxbins )
                                    if htmp_Prompt : hists[histname_Prompt]  = htmp_Prompt.Rebin( nBIN, histname_Prompt, vxbins )
                                    if htmp_Data   : hists[histname_Data]    = htmp_Data.Rebin( nBIN, histname_Data, vxbins )

                                else :
                                    hists[histname] = htmp.Rebin( nBIN, histname )
                                    if htmp_QMisID : hists[histname_QMisID]  = htmp_QMisID.Rebin( nBIN, histname_QMisID )
                                    if htmp_Prompt : hists[histname_Prompt]  = htmp_Prompt.Rebin( nBIN, histname_Prompt )
                                    if htmp_Data   : hists[histname_Data]    = htmp_Data.Rebin( nBIN, histname_Data )

                        if args.doAvg:

                            nBIN = htmp.GetNbinsX()
                            xbins  = [htmp.GetBinLowEdge(1),htmp.GetBinLowEdge(htmp.GetNbinsX()+1)]
                            vxbins = array.array("d", xbins)
                            print "\t\t\t\t\t vxbins: ",vxbins
                            hists[histname]  = htmp.Rebin( nBIN, histname )
                            if htmp_QMisID : hists[histname_QMisID]  = htmp_QMisID.Rebin( nBIN, histname_QMisID )
                            if htmp_Prompt : hists[histname_Prompt]  = htmp_Prompt.Rebin( nBIN, histname_Prompt )
                            if htmp_Data   : hists[histname_Data]    = htmp_Data.Rebin( nBIN, histname_Data )

                        if ( args.rebinEta or args.rebinPt or args.doAvg) and args.debug:
                            print("\t\t\t\t\t Integral BEFORE rebinning: {0}".format(htmp.Integral(0,htmp.GetNbinsX()+1)))
                            print("\t\t\t\t\t Integral AFTER rebinning: {0}".format(hists[histname].Integral(0,hists[histname].GetNbinsX()+1)))

                        # -------------------------------------------------------------------
                        # compute the yield for this histogram, considering also the overflow
                        # -------------------------------------------------------------------

                        yields[histname] = hists[histname].Integral(0,hists[histname].GetNbinsX()+1)

                    # -------------------------------------------------
                    # subtract prompt bkg from data in fakes histograms
                    # -------------------------------------------------

                    if args.doBkgSub :

                        if ( args.usePrediction == "MC" ):
                            sys.exit("trying to subtract MC when using --usePrediction=", args.usePrediction ," option. Please use DATA instead, or switch off prompt background subtraction")

                        name = None

                        if ( iType == "Fake" ):

                            name = iLep + "_"+ iVar +"_"+ iType + "_" +  iSel + "_" + list_prediction[1] # --> "observed"

                            print "\t\t\t\t subtracting events w/ prompt/ch-flip probe lepton to data in Fake CR..."

                            hist_sub = hists[ iLep + "_" + iVar + "_" + iType + "_" + iSel + "_" + list_prediction[0] ] # --> "expected"

                            if args.debug:
                                print "\t\t\t\t Integral before sub: ", hists[name].Integral(0,hists[histname].GetNbinsX()+1), " - hist name: ", hists[name].GetName()

                            hists[name].Add( hist_sub, -1 )

                            if args.debug:
                                print "\t\t\t\t Integral after sub: ", hists[name].Integral(0,hists[histname].GetNbinsX()+1)

                        elif ( iType == "Real" ) or ( iType == "RealQMisIDBinning" ):

                            iActualType = iType

                            name = iLep + "_"+ iVar +"_"+ iActualType + "_" +  iSel + "_" + list_prediction[1] # --> "observed"

                            print "\t\t\t\t subtracting events w/ !prompt/ch-flip probe lepton to data in Real CR..."

                            hist_sub = hists[ iLep + "_" + iVar + "_" + iActualType + "_" + iSel + "_" + list_prediction[0] ] # --> "expected"

                            if args.debug:
                                print "\t\t\t\t Integral before sub: ", hists[name].Integral(0,hists[histname].GetNbinsX()+1), " - hist name: ", hists[name].GetName()

                            hists[name].Add( hist_sub, -1 )

                            if args.debug:
                                print "\t\t\t\t Integral after sub: ", hists[name].Integral(0,hists[histname].GetNbinsX()+1)


                        # ----------------------------------------------------------------------
                        # set bin content to zero if subtraction gives negative yields
                        #
                        # re-compute the yield for this histogram, considering also the overflow
                        # ----------------------------------------------------------------------

                        for iBin in range( 0, hists[name].GetNbinsX()+2):

                            if hists[name].GetBinContent( iBin ) < 0:
                                hists[name].SetBinContent( iBin, 0 )

                        yields[name] = hists[name].Integral(0,hists[histname].GetNbinsX()+1)

                # ------------------
                # compute the rate:
                # T / !T
                #
                # and the efficiency:
                # T / ( !T + T ) = T / L
                # ------------------

                histname =  iLep + "_" + iVar +"_"+ iType

                print "\t\t histogram to be used in the ratio: ", histname

                # ---------------------------------------------------
                # use MC based estimate, but only if selected by user
                # ---------------------------------------------------

                append_str = "observed"
                if ( args.usePrediction == "MC" ):
                    append_str = "expected"

                print "Numerator T: tot. yield = ",  yields[histname + "_T_" + append_str]
                for bin in range(1,hists[histname + "_T_" + append_str].GetNbinsX()+1):
                    print("\t Bin nr: {0}, [{1},{2}] - yield = {3}".format(bin,hists[histname + "_T_" + append_str].GetBinLowEdge(bin),hists[histname + "_T_" + append_str].GetBinLowEdge(bin+1),hists[histname + "_T_" + append_str].GetBinContent(bin)))
                print "Denominator AntiT: tot. yield = ",  yields[histname + "_AntiT_" + append_str]
                for bin in range(1,hists[histname + "_AntiT_" + append_str].GetNbinsX()+1):
                    print("\t Bin nr: {0}, [{1},{2}] - yield = {3}".format(bin,hists[histname + "_AntiT_" + append_str].GetBinLowEdge(bin),hists[histname + "_AntiT_" + append_str].GetBinLowEdge(bin+1),hists[histname + "_AntiT_" + append_str].GetBinContent(bin)))

                # -----------------------
                # RATE (T/!T) MEASUREMENT
                # -----------------------

                hists[histname + "_Rate_" + append_str]  = hists[histname + "_T_" + append_str].Clone(histname + "_Rate_" + append_str)
                hists[histname + "_Rate_" + append_str].Divide(hists[histname + "_AntiT_" + append_str])

                yields[histname + "_Rate_" + append_str] = yields[histname + "_T_" + append_str] / yields[histname + "_AntiT_" + append_str]

                # ---------------------------------
                # EFFICIENCY (T/(T+!T)) MEASUREMENT
                # ---------------------------------

                # Define numerator and denominator events

                hist_pass = hists[histname + "_T_" + append_str]
                hist_tot  = hists[histname + "_T_" + append_str] + hists[histname + "_AntiT_" + append_str]

                print "Denominator L (AntiT+T): tot. yield = ", hist_tot.Integral(0,hist_tot.GetNbinsX()+1)
                for bin in range(1,hist_tot.GetNbinsX()+1):
                    print("\t Bin nr: {0}, [{1},{2}] - yield = {3}".format(bin,hist_tot.GetBinLowEdge(bin),hist_tot.GetBinLowEdge(bin+1),hist_tot.GetBinContent(bin)))

                # NB: For efficiency, need to make sure the errors are computed correctly!
                # In this case, numerator and denominator are not independent sets of events! The efficiency is described by a binomial PDF.

                # 1.
                #
		# The TH1::Divide method with the option "B" calculates binomial errors using the "normal" approximation
                # (NB: the approximation fails when eff = 0 or 1. In such cases, TEfficiency or TGraphAsymmErrors should be used, since they know how to handle such cases)
		#
                hist_eff  = hist_pass.Clone(histname + "_Efficiency_" + append_str)
                hist_eff.Divide(hist_pass,hist_tot,1.0,1.0,"B")

                # *********************************************************************************************************************************

                # Cache the electron REAL efficiency w/ same binning as fake eff (only in DATA, and for pT dependence)
                #
                if ( args.usePrediction == "DATA" ) and ( iType == "RealQMisIDBinning" ) and ( iLep == "El" ) and ( iVar == "ProbePt" ):
                    hist_eff_electron_real = hist_eff

                # Get the actual electron FAKE efficiency by scaling the REAL efficiency appropriately by the QMisID rate ratio
                #
                hist_eff_QMisID = hist_eff_fake_scaled = None

                if ( args.usePrediction == "DATA" ) and ( iType == "Fake" ) and ( iLep == "El" ) and ( iVar == "ProbePt" ):

                    if not hist_eff_electron_real:
                        sys.exit("ERROR: histogram hist_eff_electron_real does not exist")

                    hist_eff_QMisID, hist_eff_fake_scaled = scaleEff( hist_eff_electron_real, hist_eff, hists[histname_Data], hists[histname_Prompt], hists[histname_QMisID] )

                    eff_QMisID_name         = (histname + "_Efficiency_" + append_str).replace("Fake","QMisID")
                    eff_fake_scaled_name    = (histname + "_Efficiency_" + append_str).replace("Fake","ScaledFake")

                    hist_eff_QMisID.SetName(eff_QMisID_name)
                    hist_eff_fake_scaled.SetName(eff_fake_scaled_name)

                    hists[eff_QMisID_name]      = hist_eff_QMisID
                    hists[eff_fake_scaled_name] = hist_eff_fake_scaled

                # *********************************************************************************************************************************

                # 2.
                # The TEfficiency class handles the special cases not covered by TH1::Divide
                #
		t_efficiency = None
		if TEfficiency.CheckConsistency(hist_pass, hist_tot,"w"):
		    t_efficiency = TEfficiency(hist_pass, hist_tot)
		    t_efficiency.SetName(histname + "_TEfficiency_" + append_str)

		    t_efficiency.SetConfidenceLevel(0.683)

                    # Use TEfficiency, with the frequentist Clopper-Pearson confidence interval at XX% CL (set before)
                    # (this handles the eff = 0, 1 case)
                    #
                    # DOES NOT SEEM TO WORK FOR WEIGHTED HISTOGRAMS --> IT REDUCES TO THE NORMAL APPROX
                    #
		    #t_efficiency.SetStatisticOption(TEfficiency.kFCP)
                    #
                    # Use TEfficiency, with the Bayesian uniform prior at XX% CL (set before)
                    # (This is the same as the TGraphAsymmErrors below)
                    #
                    # In order to get the same value for efficiency as in a frequentist approach (as from TH1::Divide("B")),
                    # the MODE should be used as an estimator. This works as long as a uniform prior is chosen.
                    #
                    # Please refer to the TEfficiency class docs for details:
                    # https://root.cern.ch/doc/master/classTEfficiency.html
                    #
		    t_efficiency.SetStatisticOption(TEfficiency.kBUniform)
                    t_efficiency.SetPosteriorMode()

                # 3.
                #
                # Calculate efficiency using TGraphAsymmErrors
                # (uses a Bayesian uniform prior beta(1,1) for the efficiency with 68% CL. It handles the errors in case eff is 0 or 1)
                #
                g_efficiency = TGraphAsymmErrors(hist_eff)
                g_efficiency.Divide(hist_pass,hist_tot,"cl=0.683 b(1,1) mode")

                # Save the efficiencies in the proper dictionaries
                #
                hists[histname + "_Efficiency_" + append_str] = hist_eff
                tefficiencies[histname + "_Efficiency_" + append_str] = t_efficiency
                graphs[histname + "_Efficiency_" + append_str + "_graph"] = g_efficiency

                print "\t\t --> RATE hist name: ", histname + "_Rate_" + append_str
                print "\t\t --> EFFICIENCY hist name: ", histname + "_Efficiency_" + append_str

    if args.doAvg:
        channel_str += "Avg"

    outfile = open( args.inputDir + channel_str + "LeptonEfficiencies.txt", "w")
    outfile.write( "Efficiencies/Rates for FF amd Matrix Method \n")

    foutname = args.inputDir + channel_str + "LeptonEfficiencies.root"
    fout = TFile( foutname,"RECREATE" )
    fout.cd()

    for h in sorted( hists.keys() ):
        if not hists[h]: continue
        print("saving histogram: {0}".format(hists[h].GetName()))
        hists[h].Write()
        if ("_Efficiency_" in h) and not ("QMisID" in h) and not ("ScaledFake" in h):
            Eff=[]
            for ibin in range( 1, hists[h].GetNbinsX()+1 ):
                myset = [ ibin, hists[h].GetBinLowEdge(ibin), hists[h].GetBinLowEdge(ibin+1), hists[h].GetBinContent(ibin), hists[h].GetBinError(ibin)]
                Eff.append( myset )
            outfile.write("%s \n" %(h) )
            for myset in Eff:
                outfile.write("{ %s }; \n" %( "Bin nr: " + str(myset[0]) + " [" + str(round(myset[1],3)) + "," + str(round(myset[2],3)) + "], efficiency (from TH1::Divide(\"B\")) = " + str(round(myset[3],3)) + " +- " + str(round(myset[4],3)) ) )

    for t in sorted ( tefficiencies.keys() ):
        if not tefficiencies[t]: continue
        print("saving TEfficiency: {0}".format(tefficiencies[t].GetName()))
	tefficiencies[t].Write()
        if ("_Efficiency_" in t) and not ("QMisID" in t) and not ("ScaledFake" in t):
            TEff=[]
            for ibin in range( 1, tefficiencies[t].GetTotalHistogram().GetNbinsX()+1 ):
                myset = [ ibin, tefficiencies[t].GetTotalHistogram().GetBinLowEdge(ibin), tefficiencies[t].GetTotalHistogram().GetBinLowEdge(ibin+1), tefficiencies[t].GetEfficiency(ibin), tefficiencies[t].GetEfficiencyErrorUp(ibin), tefficiencies[t].GetEfficiencyErrorLow(ibin)]
                TEff.append( myset )
            outfile.write("%s \n" %(t) )
            for myset in TEff:
                outfile.write("{ %s }; \n" %( "Bin nr: " + str(myset[0]) + " [" + str(round(myset[1],3)) + "," + str(round(myset[2],3)) + "], efficiency (from TEfficiency) = " + str(round(myset[3],3)) + " + " + str(round(myset[4],3)) + " - " + str(round(myset[5],3)) ) )

    for g in sorted( graphs.keys() ):
        if not graphs[g]: continue
        print("saving graph: {0}".format(graphs[g].GetName()))
        graphs[g].Write()
        if ("_Efficiency_" in g) and not ("QMisID" in g) and not ("ScaledFake" in g):
            GEff=[]
            for ipoint in range( 0, graphs[g].GetN() ):
                x = Double(0)
                y = Double(0)
                graphs[g].GetPoint(ipoint,x,y)
                myset = [ ipoint+1, y, graphs[g].GetErrorYhigh(ipoint), graphs[g].GetErrorYlow(ipoint) ]
                GEff.append( myset )
            outfile.write("%s \n" %(g) )
            for myset in GEff:
                outfile.write("{ %s }; \n" %( "Bin nr: " + str(myset[0]) + ", efficiency (from TGraphAsymmErrors) = " + str(round(myset[1],3)) + " + " + str(round(myset[2],3)) + " - " + str(round(myset[3],3)) ) )

    outfile.close()
    fout.Write()
    fout.Close()

    for f in range( 0,len(fin) ):
        fin[f].Close()
"""
