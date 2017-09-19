import ROOT
import array
from argparse import ArgumentParser as argps
import numpy as np


def Comparison(namelist,colorlist,file1,file2,title,xaxistitle,yaxistitle,xmin_=0.0,xmax_=300.0,ymin_=0.0,ymax_=1.3,outfile="Default_comparison_name.pdf",ratio="Normal",showStats=True):
#	ROOT.gStyle.SetOptStat(0)

#	ROOT.gStyle.SetTitleAlign(31)
#	ROOT.gStyle.SetTitleX(.01)

	histlist1={}
	histlist2={}
	histlist3={}
	colors={'green': ROOT.kGreen+2, 'blue': ROOT.kBlue+2, 'purple': ROOT.kViolet+2, 'red': ROOT.kRed+2}

	f1=ROOT.TFile.Open(file1,"read")
	f2=ROOT.TFile.Open(file2,"read")
	if ratio=="Density":
		print "DENSITY_"+file1
		f3=ROOT.TFile.Open("DENSITY_"+file1,"read")

	for i in range(0,len(namelist)):
		histlist1["hist{0}".format(i)]=f1.Get(namelist[i])
		histlist2["hist{0}".format(i)]=f2.Get(namelist[i])
		histlist1["hist"+str(i)].SetName(namelist[i]+"_L1L2L3")
		histlist2["hist"+str(i)].SetName(namelist[i]+"_Reg")
		if ratio=="Density":
			histlist3["hist{0}".format(i)]=f3.Get(namelist[i])

        c = ROOT.TCanvas("c","",800,800)
	if ratio=="Normal" or ratio=="Density":
	        pad1= ROOT.TPad("pad1","pad1",0.,0.3,1.,1.)
	        pad1.SetBottomMargin(0.02)
	else:
		pad1=ROOT.TPad("pad1","pad1",0.,0.,1.,1.)
		pad1.SetBottomMargin(0.08)
        pad1.Draw()
        pad1.cd()
        pad1.SetGridx()

	#statbox locations
	ys_=np.linspace(0.5,0.90,len(histlist1)+1)

	for i in range(0,len(histlist1)):
		#histlist1["hist"+str(i)].GetXaxis().SetRangeUser(xmin_+0.001,xmax_)
                histlist1["hist"+str(i)].Draw("hist sames")
		ROOT.gPad.Update()
                histlist1["hist"+str(i)].SetLineColor(colors[colorlist[i]])

		#Set styling options on the first histogram drawn. For some reason pyroot prefers that.
		if i==0:
			#histlist1["hist"+str(i)].SetStats(1)
			histlist1["hist"+str(i)].SetTitle(title)
			title_=ROOT.gPad.FindObject("title")
			title_.SetX1NDC(0.1)
			ROOT.gPad.Update()
		histlist1["hist"+str(i)].SetMinimum(ymin_)
		histlist1["hist"+str(i)].SetMaximum(ymax_)
		histlist1["hist"+str(i)].GetXaxis().SetTitle(xaxistitle)
		histlist1["hist"+str(i)].GetYaxis().SetTitle(yaxistitle)
		histlist1["hist"+str(i)].GetYaxis().SetTitleOffset(1.4)
		if ratio=="Normal" or ratio=="Density":
			histlist1["hist"+str(i)].GetXaxis().SetLabelSize(0.)

		if showStats:
			histlist1["hist"+str(i)].SetStats(1)
			stats=histlist1["hist"+str(i)].GetListOfFunctions().FindObject( "stats" )
			stats.SetY1NDC(ys_[i])
			stats.SetY2NDC(ys_[i+1])
			stats.SetX1NDC(0.65)
			stats.SetX2NDC(0.8)
		else:
			histlist1["hist"+str(i)].SetStats(0)
	for i in range(0,len(histlist2)):
		histlist2["hist"+str(i)].GetXaxis().SetRangeUser(xmin_+0.001,xmax_)
                histlist2["hist"+str(i)].Draw("hist sames")
		histlist2["hist"+str(i)].SetLineColor(colors[colorlist[i]])
		histlist2["hist"+str(i)].SetLineStyle(2)
		ROOT.gPad.Update()
		if showStats:
			histlist2["hist"+str(i)].SetStats(1)
			stats=histlist2["hist"+str(i)].GetListOfFunctions().FindObject( "stats" )
	                stats.SetY1NDC(ys_[i])
	                stats.SetY2NDC(ys_[i+1])
	                stats.SetX1NDC(0.8)
	                stats.SetX2NDC(0.95)
		else:
			histlist2["hist"+str(i)].SetStats(0)

        legend = ROOT.TLegend(.20,.65,.4,.85)
        legend.SetNColumns(2)
	for i in range(0,len(namelist)):
		legend.AddEntry(histlist1["hist"+str(i)],namelist[i]+"_L1L2L3","l")
                legend.AddEntry(histlist2["hist"+str(i)],namelist[i]+"_Reg","l")
        legend.SetBorderSize(0)
        legend.Draw()


	if ratio=="Normal":
	        c.cd()
	        pad2 = ROOT.TPad("pad2","pad2",0,0,1,0.3)
	        pad2.SetTopMargin(0.02)
	        pad2.SetBottomMargin(0.2)
	        pad2.Draw()
	        pad2.cd()
	        pad2.SetGridx()
	        textsize = 18/(pad2.GetWh()*pad2.GetAbsHNDC())

		ratios={}
		for i in range(0,len(namelist)):
	                ratios["hist{0}".format(i)]=histlist2["hist"+str(i)].Clone("h_"+str(i))
			ratios["hist"+str(i)].SetStats(0)
			ratios["hist"+str(i)].Divide(histlist1["hist"+str(i)])
	                ratios["hist"+str(i)].GetXaxis().SetRangeUser(xmin_+0.001,xmax_)
			ratios["hist"+str(i)].Draw("p sames")
			ratios["hist"+str(i)].SetLineColor(colors[colorlist[i]])
			ratios["hist"+str(i)].SetLineStyle(1)
			if i==0:
				ratios["hist"+str(i)].SetTitle("")
				ratios["hist"+str(i)].SetStats(0)
			        ratios["hist"+str(i)].SetMinimum(0.0)
			        ratios["hist"+str(i)].SetMaximum(3.0)
			        ratios["hist"+str(i)].SetMarkerStyle(1)
			        ratios["hist"+str(i)].GetYaxis().SetTitle("Ratio")
			        ratios["hist"+str(i)].GetXaxis().SetTitle(xaxistitle)
			        ratios["hist"+str(i)].GetYaxis().SetTitleSize(textsize)
				ratios["hist"+str(i)].GetYaxis().SetLabelSize(0.9*textsize)
			        ratios["hist"+str(i)].GetYaxis().SetTitleOffset(0.6)
			        ratios["hist"+str(i)].GetXaxis().SetTitleSize(textsize)
				ratios["hist"+str(i)].GetXaxis().SetLabelSize(0.9*textsize)
			        ratios["hist"+str(i)].GetXaxis().SetTitleOffset(1.0)
				min=ratios["hist"+str(i)].GetXaxis().GetXmin()
			        max=ratios["hist"+str(i)].GetXaxis().GetXmax()
				line = ROOT.TLine(min,1.0,max,1.0)
				line.SetLineColor(ROOT.kBlack)
				line.SetLineStyle(2)
				line.Draw()
				pad2.Update()


        if ratio=="Density":
                c.cd()
                pad2 = ROOT.TPad("pad2","pad2",0,0,1,0.3)
                pad2.SetTopMargin(0.02)
                pad2.SetBottomMargin(0.2)
                pad2.Draw()
                pad2.cd()
                pad2.SetGridx()
                textsize = 18/(pad2.GetWh()*pad2.GetAbsHNDC())

		hs = ROOT.THStack("hs","")

                for i in range(0,len(namelist)):

			histlist3["hist"+str(i)].SetStats(0)
			histlist3["hist"+str(i)].SetLineColor(colors[colorlist[i]])
			histlist3["hist"+str(i)].SetFillColor(colors[colorlist[i]])
			histlist3["hist"+str(i)].SetFillStyle(1001)
			histlist3["hist"+str(i)].Scale(histlist3["hist"+str(i)].GetBinWidth(1)/3.0)

			hs.Add(histlist3["hist"+str(i)])

#                        if i==0:
#                                histlist3["hist"+str(i)].SetTitle("")
#                                histlist3["hist"+str(i)].SetStats(0)
#                                histlist3["hist"+str(i)].SetMinimum(0.0)
#                                histlist3["hist"+str(i)].SetMaximum(1.0)
#                                histlist3["hist"+str(i)].SetMarkerStyle(1)
#                                histlist3["hist"+str(i)].GetYaxis().SetTitle("Fraction of jets")
#                                histlist3["hist"+str(i)].GetXaxis().SetTitle(xaxistitle)
#                                histlist3["hist"+str(i)].GetYaxis().SetTitleSize(textsize)
#                                histlist3["hist"+str(i)].GetYaxis().SetLabelSize(0.9*textsize)
#                                histlist3["hist"+str(i)].GetYaxis().SetTitleOffset(0.6)
#                                histlist3["hist"+str(i)].GetXaxis().SetTitleSize(textsize)
#                                histlist3["hist"+str(i)].GetXaxis().SetLabelSize(0.9*textsize)
#                                histlist3["hist"+str(i)].GetXaxis().SetTitleOffset(1.0)
#                                min=histlist3["hist"+str(i)].GetXaxis().GetXmin()
#                                max=histlist3["hist"+str(i)].GetXaxis().GetXmax()
#                                line = ROOT.TLine(min,1.0,max,1.0)
#                                line.SetLineColor(ROOT.kBlack)
#                                line.SetLineStyle(2)
#                                line.Draw()
#                                pad2.Update()


		hs.Draw()
		hs.GetXaxis().SetRangeUser(xmin_+0.001,xmax_)
		hs.Draw("same hist")
		ROOT.gPad.RedrawAxis()
		ROOT.gPad.RedrawAxis("g")
		ROOT.gPad.Update()

                hs.GetYaxis().SetTitle("Fraction of jets")
                hs.GetXaxis().SetTitle(xaxistitle)
                hs.GetXaxis().SetTitle(xaxistitle)
                hs.GetYaxis().SetTitleSize(textsize)
                hs.GetYaxis().SetLabelSize(0.9*textsize)
                hs.GetYaxis().SetTitleOffset(0.6)
                hs.GetXaxis().SetTitleSize(textsize)
                hs.GetXaxis().SetLabelSize(0.9*textsize)
                hs.GetXaxis().SetTitleOffset(1.0)

		c.Update();

        c.Print(outfile)

	c.Close()

	del c

def Comparison_Stack(namelist,colorlist,file1,file2,title,xaxistitle,yaxistitle,xmin_=0.0,xmax_=300.0,ymin_=0.0,ymax_=1.3,outfile="Default_comparison_name.pdf",ratio="Normal",showStats=True):
        histlist1={}
        histlist2={}
        histlist3={}
        colors={'green': ROOT.kGreen+2, 'blue': ROOT.kBlue+2, 'purple': ROOT.kViolet+2, 'red': ROOT.kRed+2}

        f1=ROOT.TFile.Open(file1,"read")
        f2=ROOT.TFile.Open(file2,"read")
        if ratio=="Density":
                print "DENSITY_"+file1
                f3=ROOT.TFile.Open("DENSITY_"+file1,"read")

        for i in range(0,len(namelist)):
                histlist1["hist{0}".format(i)]=f1.Get(namelist[i])
                histlist2["hist{0}".format(i)]=f2.Get(namelist[i])
                histlist1["hist"+str(i)].SetName(namelist[i]+"_L1L2L3")
                histlist2["hist"+str(i)].SetName(namelist[i]+"_Reg")
                if ratio=="Density":
                        histlist3["hist{0}".format(i)]=f3.Get(namelist[i])

        c = ROOT.TCanvas("c","",800,800)
        if ratio=="Normal" or ratio=="Density":
                pad1= ROOT.TPad("pad1","pad1",0.,0.3,1.,1.)
                pad1.SetBottomMargin(0.02)
        else:
                pad1=ROOT.TPad("pad1","pad1",0.,0.,1.,1.)
                pad1.SetBottomMargin(0.08)
        pad1.Draw()
        pad1.cd()
        pad1.SetGridx()

        #statbox locations
        ys_=np.linspace(0.5,0.90,len(histlist1)+1)

	stack=ROOT.THStack("stack1","")
        for i in range(0,len(histlist1)):
                histlist1["hist"+str(i)].SetLineColor(colors[colorlist[i]])
		histlist1["hist"+str(i)].GetXaxis().SetRangeUser(xmin_,xmax_)
		histlist1["hist"+str(i)].Draw("goff") #to generate stats
		ROOT.gPad.Update()
                if showStats:
			histlist1["hist"+str(i)].SetStats(1)
                        stats=histlist1["hist"+str(i)].GetListOfFunctions().FindObject( "stats" )
			ROOT.gPad.Update()
                        stats.SetY1NDC(ys_[i])
                        stats.SetY2NDC(ys_[i+1])
                        stats.SetX1NDC(0.65)
                        stats.SetX2NDC(0.8)
                else:
                        histlist1["hist"+str(i)].SetStats(0)
		stack.Add(histlist1["hist"+str(i)])

	for i in range(0,len(histlist2)):
		histlist2["hist"+str(i)].SetLineColor(colors[colorlist[i]])
		histlist2["hist"+str(i)].SetLineStyle(2)
                histlist2["hist"+str(i)].GetXaxis().SetRangeUser(xmin_,xmax_)
		histlist2["hist"+str(i)].Draw("goff")
		ROOT.gPad.Update()
                if showStats:
			histlist2["hist"+str(i)].SetStats(1)
                        stats=histlist2["hist"+str(i)].GetListOfFunctions().FindObject( "stats" )
			ROOT.gPad.Update()
                        stats.SetY1NDC(ys_[i])
                        stats.SetY2NDC(ys_[i+1])
                        stats.SetX1NDC(0.8)
                        stats.SetX2NDC(0.95)
                else:
                        histlist2["hist"+str(i)].SetStats(0)
		stack.Add(histlist2["hist"+str(i)])

	stack.SetTitle(title)
	stack.Draw("nostack")
	stack.GetXaxis().SetRangeUser(xmin_,xmax_)
	stack.SetMinimum(ymin_)
	stack.SetMaximum(ymax_)
	stack.GetHistogram().GetXaxis().SetTitle(xaxistitle)
	stack.GetHistogram().GetYaxis().SetTitle(yaxistitle)
	stack.GetHistogram().GetYaxis().SetTitleOffset(1.4)
	stack.GetHistogram().GetYaxis().CenterTitle()
	title_=ROOT.gPad.FindObject("title")
	title_.SetX1NDC(0.1)
	if ratio=="Normal" or ratio=="Density":
		stack.GetHistogram().GetXaxis().SetLabelSize(0.)
	ROOT.gPad.Update()
	stack.Draw("nostack")

        legend = ROOT.TLegend(.20,.65,.4,.85)
        legend.SetNColumns(2)
        for i in range(0,len(namelist)):
                legend.AddEntry(histlist1["hist"+str(i)],namelist[i]+"_{L1L2L3}","l")
                legend.AddEntry(histlist2["hist"+str(i)],namelist[i]+"_{Reg}","l")
        legend.SetBorderSize(0)
        legend.Draw()

	c.cd()
        #CMS Preliminary text
        text = ROOT.TPaveText(0.02,0.95,0.15,.99,"nbNDC")
        text.AddText("CMS")
	text.AddText("Preliminary")
#	text.SetTextAlign(1)
	text.SetFillColor(0)
	text.SetTextSize(0.025)
        text.Draw()
        c.Update()


        if ratio=="Normal":
                c.cd()
                pad2 = ROOT.TPad("pad2","pad2",0,0,1,0.3)
                pad2.SetTopMargin(0.02)
                pad2.SetBottomMargin(0.2)
                pad2.Draw()
                pad2.cd()
                pad2.SetGridx()
                textsize = 18/(pad2.GetWh()*pad2.GetAbsHNDC())

                ratios={}
                for i in range(0,len(namelist)):
                        ratios["hist{0}".format(i)]=histlist2["hist"+str(i)].Clone("h_"+str(i))
                        ratios["hist"+str(i)].SetStats(0)
                        ratios["hist"+str(i)].Divide(histlist1["hist"+str(i)])
                        ratios["hist"+str(i)].GetXaxis().SetRangeUser(xmin_,xmax_)
                        ratios["hist"+str(i)].Draw("p sames")
                        ratios["hist"+str(i)].SetLineColor(colors[colorlist[i]])
                        ratios["hist"+str(i)].SetLineStyle(1)
                        ratios["hist"+str(i)].SetMinimum(0.0)
                        ratios["hist"+str(i)].SetMaximum(2.0)

                        if i==0:
                                ratios["hist"+str(i)].SetTitle("")
                                ratios["hist"+str(i)].SetStats(0)
                                ratios["hist"+str(i)].SetMinimum(0.0)
                                ratios["hist"+str(i)].SetMaximum(2.0)
                                ratios["hist"+str(i)].SetMarkerStyle(1)
                                ratios["hist"+str(i)].GetYaxis().SetTitle("Ratio")
				ratios["hist"+str(i)].GetYaxis().CenterTitle()
                                ratios["hist"+str(i)].GetXaxis().SetTitle(xaxistitle)
                                ratios["hist"+str(i)].GetYaxis().SetTitleSize(textsize)
                                ratios["hist"+str(i)].GetYaxis().SetLabelSize(0.9*textsize)
                                ratios["hist"+str(i)].GetYaxis().SetTitleOffset(0.6)
                                ratios["hist"+str(i)].GetXaxis().SetTitleSize(textsize)
                                ratios["hist"+str(i)].GetXaxis().SetLabelSize(0.9*textsize)
                                ratios["hist"+str(i)].GetXaxis().SetTitleOffset(1.0)
                                min=ratios["hist"+str(i)].GetXaxis().GetXmin()
                                max=ratios["hist"+str(i)].GetXaxis().GetXmax()
                                line = ROOT.TLine(min,1.0,max,1.0)
                                line.SetLineColor(ROOT.kBlack)
                                line.SetLineStyle(2)
                                line.Draw()
                                pad2.Update()


        if ratio=="Density":
                c.cd()
                pad2 = ROOT.TPad("pad2","pad2",0,0,1,0.3)
                pad2.SetTopMargin(0.02)
                pad2.SetBottomMargin(0.2)
                pad2.Draw()
                pad2.cd()
                pad2.SetGridx()
                textsize = 18/(pad2.GetWh()*pad2.GetAbsHNDC())
		hs_= ROOT.THStack("hs_","")
                hs = ROOT.THStack("hs","")

		#THStack being what it is, one has to know beforehand the total number of entries
		#and normalize the individual distributions before adding them...
		tot_entries=0 #0
		for i in range(0,len(namelist)):
			tot_entries=+histlist3["hist"+str(i)].Integral()
#		print "TOTAL: "+str(tot_entries)

                for i in range(0,len(namelist)):

#                        histlist3["hist"+str(i)].SetStats(0)
#                        histlist3["hist"+str(i)].SetLineColor(colors[colorlist[i]])
#                        histlist3["hist"+str(i)].SetFillColor(colors[colorlist[i]])
#                        histlist3["hist"+str(i)].SetFillStyle(1001)
#                        histlist3["hist"+str(i)].Scale(1./tot_entries)

                        hs_.Add(histlist3["hist"+str(i)])

		tot_entries=hs_.GetStack().Last().Integral()
		print "TOTAL: "+str(tot_entries)

                for i in range(0,len(namelist)):

                        histlist3["hist"+str(i)].SetStats(0)
                        histlist3["hist"+str(i)].SetLineColor(colors[colorlist[i]])
                        histlist3["hist"+str(i)].SetFillColor(colors[colorlist[i]])
                        histlist3["hist"+str(i)].SetFillStyle(1001)
                        histlist3["hist"+str(i)].Scale(1./tot_entries)

                        hs.Add(histlist3["hist"+str(i)])


                hs.Draw()
                hs.GetXaxis().SetRangeUser(xmin_,xmax_)
                hs.Draw("same hist")
                ROOT.gPad.RedrawAxis()
                ROOT.gPad.RedrawAxis("g")
                ROOT.gPad.Update()

		print "ENTRIES: "+str(hs.GetStack().Last().Integral())

                hs.GetYaxis().SetTitle("Fraction of jets")
		hs.GetYaxis().CenterTitle()
                hs.GetXaxis().SetTitle(xaxistitle)
                hs.GetXaxis().SetTitle(xaxistitle)
                hs.GetYaxis().SetTitleSize(textsize)
                hs.GetYaxis().SetLabelSize(0.9*textsize)
                hs.GetYaxis().SetTitleOffset(0.6)
                hs.GetXaxis().SetTitleSize(textsize)
                hs.GetXaxis().SetLabelSize(0.9*textsize)
                hs.GetXaxis().SetTitleOffset(1.0)

                c.Update();

        c.Print(outfile)

        c.Close()

        del c


