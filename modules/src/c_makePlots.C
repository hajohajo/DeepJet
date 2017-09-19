
#define BOOST_PYTHON_MAX_ARITY 20
#include <boost/python.hpp>
#include "boost/python/extract.hpp"
#include "boost/python/numeric.hpp"
#include "boost/python/list.hpp"
#include "boost/python/str.hpp"
//#include "boost/filesystem.hpp"
#include <iostream>
#include <stdint.h>
#include "TString.h"
#include <string>
#include <boost/python/exception_translator.hpp>
#include <exception>
#include "../interface/pythonToSTL.h"
#include "friendTreeInjector.h"
#include "TROOT.h"
#include "colorToTColor.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TF1.h"
#include "TProfile.h"
#include "TCanvas.h"
#include "TLegend.h"
#include "TFile.h"
#include "TStyle.h"
#include <algorithm>
#include <typeinfo>

using namespace boost::python; //for some reason....

TH1F* getProfile(TH2F* scatterHist, TString profileType, Double_t xmin_, Double_t xmax_);

void makePlots(
        const boost::python::list intextfiles,
        const boost::python::list names,
        const boost::python::list variables,
        const boost::python::list cuts,
        const boost::python::list colors,
        std::string outfile,
        std::string xaxis,
        std::string yaxis,
        bool normalized,
        bool makeProfile=false,
        std::string profileType="None",
        bool makeWidthProfile=false,
        float OverrideMin=1e100,
        float OverrideMax=-1e100,
	int xbins_=10,
	Double_t xmin_=0.0,
	Double_t xmax_=1.0,
        std::string sourcetreename="deepntuplizer/tree") {


    std::vector<TString>  s_intextfiles=toSTLVector<TString>(intextfiles);
    std::vector<TString>  s_vars = toSTLVector<TString>(variables);
    std::vector<TString>  s_names = toSTLVector<TString>(names);
    std::vector<TString>  s_colors = toSTLVector<TString>(colors);
    std::vector<TString>  s_cuts = toSTLVector<TString>(cuts);

    //reverse to make the first be on top
    std::reverse(s_intextfiles.begin(),s_intextfiles.end());
    std::reverse(s_vars.begin(),s_vars.end());
    std::reverse(s_names.begin(),s_names.end());
    std::reverse(s_colors.begin(),s_colors.end());
    std::reverse(s_cuts.begin(),s_cuts.end());

    TString tProfileType = profileType;
    if(!(
	(tProfileType=="None") ||
	(tProfileType=="GaussFitMean") ||
	(tProfileType=="GaussFitWidth") ||
	(tProfileType=="GaussFitWidthNormByMean") || 
	(tProfileType=="GaussFitChi2") || 
	(tProfileType=="GaussFitProb") || 
	(tProfileType=="Mean") ||
	(tProfileType=="StandardDeviationNormByMean") ||
	(tProfileType=="StandardDeviation") ||
	(tProfileType=="Median") ||
	(tProfileType=="IQMean") ))
    throw std::runtime_error("makePlots: profileType not known; None|| GaussFitMean|| GaussFitWidth|| GaussFitWidthNormByMean) || GaussFitChi2 || GaussFitProb || Mean|| StandardDeviationNormByMean|| StandardDeviation|| Median|| IQMean");
//    bool makeProfile = false;
//    if(tProfileType!="None") makeProfile = true;

    TString toutfile=outfile;
    if(!toutfile.EndsWith(".pdf"))
        throw std::runtime_error("makePlots: output files need to be pdf format");


    if(!s_names.size())
        throw std::runtime_error("makePlots: needs at least one legend entry");
    /*
     * Size checks!!!
     */
    if(s_intextfiles.size() !=s_names.size()||
            s_names.size() != s_vars.size() ||
            s_names.size() != s_colors.size()||
            s_names.size() != s_cuts.size())
        throw std::runtime_error("makePlots: input lists must have same size");

    //make unique list of infiles
    std::vector<TString> u_infiles;
    std::vector<TString> aliases;
    TString oneinfile="";
    bool onlyonefile=true;
    for(const auto& f:s_intextfiles){
        if(oneinfile.Length()<1)
            oneinfile=f;
        else
            if(f!=oneinfile)
                onlyonefile=false;
    }
    for(const auto& f:s_intextfiles){
        //if(std::find(u_infiles.begin(),u_infiles.end(),f) == u_infiles.end()){
        u_infiles.push_back(f);
        TString s="";
        s+=aliases.size();
        aliases.push_back(s);
        //	std::cout << s <<std::endl;
        //}
    }



    friendTreeInjector injector(sourcetreename);
    for(size_t i=0;i<u_infiles.size();i++){
        if(!aliases.size())
            injector.addFromFile((TString)u_infiles.at(i));
        else
            injector.addFromFile((TString)u_infiles.at(i),aliases.at(i));
    }
    injector.createChain();

    TChain* c=injector.getChain();

    std::vector<TH1F*> allhistos;
    TLegend * leg=new TLegend(0.2,0.75,0.8,0.88);
    leg->SetBorderSize(0);

    leg->SetNColumns(3);
    leg->SetFillStyle(0);

    TString addstr="";
    if(normalized)
        addstr="normalized";
//    if(makeProfile)
//        addstr+="prof";
    else if(makeWidthProfile)
        addstr+="profs";
    if(makeProfile && makeWidthProfile)
        throw std::logic_error("makePlots: Not allowed to use makeProfile and makeWidthProfile at the same time");
    float max=-1e100;
    float min=1e100;

    TString tfileout=toutfile;
    tfileout=tfileout(0,tfileout.Length()-4);
    tfileout+=".root";

    TFile * f = new TFile(tfileout,"RECREATE");
//    gStyle->SetOptStat(0);

    for(size_t i=0;i<s_names.size();i++){
        TString tmpname="hist_";
        tmpname+=i;
//	TString tmphist_= Form("%s(%d,%f,%f)",tmpname.Data(),xbins_,xmin_,xmax_);
//        c->Draw(s_vars.at(i)+">>"+tmphist_,s_cuts.at(i),addstr);
//        std::cout<<"xbins: "<<xbins_<<" xmin_: "<<xmin_<<" xmax_: "<<xmax_<<std::endl;
//	std::cout<<"xbins: "<<xbins_<<" xmin_: "<<xmin_<<" xmax_: "<<xmax_<<std::endl;
//	xbins_=10;
//	xmin_=0.0;
//	xmax_=1.0;
//	TH1F *tmp_=new TH1F(tmpname,tmpname,xbins_,xmin_,xmax_);
//	if(makeProfile){
////	TH2F *tmp_=new TH2F(tmpname,tmpname,xbins_,xmin_,xmax_,10,0.0,2.0);
//	}
//	std::cout<<"blabla 1: "<<tmp_->GetXaxis()->GetBinLowEdge(1)<<", "<<tmp_->GetXaxis()->GetBinUpEdge(tmp_->GetNbinsX())<<", "<<tmp_->GetNbinsX()<<std::endl;
//        std::cout<<"blabla 2: "<<tmp_->GetXaxis()->GetBinLowEdge(0)<<", "<<tmp_->GetXaxis()->GetBinUpEdge(tmp_->GetNbinsX())<<", "<<tmp_->GetNbinsX()<<std::endl;
//	c->Draw(s_vars.at(i)+">>+"+tmpname,s_cuts.at(i),addstr);
	if(makeProfile){
		TString tmphist_= Form("%s(%d,%f,%f,%d,%f,%f)",tmpname.Data(),xbins_,xmin_,xmax_,100,0.0,2.0);
		c->Draw(s_vars.at(i)+">>"+tmphist_,s_cuts.at(i),addstr);
	}else{
		TString tmphist_= Form("%s(%d,%f,%f)",tmpname.Data(),xbins_,xmin_,xmax_);
		c->Draw(s_vars.at(i)+">>"+tmphist_,s_cuts.at(i),addstr);
	}
//	std::cout<<"TMP entries: "<<tmp_->GetEntries()<<std::endl;
	TH1F *histo;
	if(makeProfile){
		std::cout << "pulling in profile of type" << tProfileType << std::endl;
		TH2F *scatterHist = (TH2F*) gROOT->FindObject(tmpname);
		std::cout<<"SCATTER entries: "<<scatterHist->GetEntries()<<std::endl;
/*		for(Int_t j=1;j<scatterHist->GetNbinsX();j++){
			if (j==9 || j==10){
				for(Int_t k=1;k<scatterHist->GetNbinsY();k++){
//					std::cout<<"Bin: "<<j<<" Bin lower edge: "<<scatterHist->GetXaxis()->GetBinLowEdge(j)<<" Content: "<<scatterHist->GetBinContent(j,k)<<std::endl;
				}
			}
		}
*/
//                std::cout<<"blabla 2: "<<scatterHist->GetXaxis()->GetBinLowEdge(1)<<", "<<scatterHist->GetXaxis()->GetBinUpEdge(scatterHist->GetNbinsX())<<", "<<scatterHist->GetNbinsX()<<std::endl;
		histo = getProfile(scatterHist,tProfileType,xmin_,xmax_);
//		histo = getProfile(tmp_,tProfileType,xmin_,xmax_);
//		std::cout<<"blabla 3: "<<histo->GetXaxis()->GetBinLowEdge(1)<<", "<<histo->GetXaxis()->GetBinUpEdge(histo->GetNbinsX())<<", "<<histo->GetNbinsX()<<std::endl;
	}
        else histo = (TH1F*) gROOT->FindObject(tmpname);
        histo->SetLineColor(colorToTColor(s_colors.at(i)));
        histo->SetLineStyle(lineToTLineStyle(s_colors.at(i)));
        histo->SetTitle(s_names.at(i));
        histo->SetName(s_names.at(i));

        histo->SetFillStyle(0);
        histo->SetLineWidth(2);

        float integral=histo->Integral("width");
        //the normalised option doesn't really do well
        if(integral && normalized)
            histo->Scale(1/integral);

        float tmax=histo->GetMaximum();
        float tmin=histo->GetMinimum();
        if(tmax>max)max=tmax;
        if(tmin<min)min=tmin;
        if((makeProfile||makeWidthProfile)  &&OverrideMin < OverrideMax){
            //std::cout << "overriding min/max"<< std::endl;
            max = OverrideMax;
            min = OverrideMin;
        }


        allhistos.push_back(histo);

        histo->Write();


    }
    for(size_t i=allhistos.size();i;i--){
        leg->AddEntry(allhistos.at(i-1),s_names.at(i-1),"l");
    }

    TCanvas cv("plots");

    allhistos.at(0)->Draw("AXIS");
    allhistos.at(0)->GetYaxis()->SetRangeUser(min,1.3*max); //space for legend on top

    allhistos.at(0)->GetXaxis()->SetTitle(xaxis.data());
    allhistos.at(0)->GetYaxis()->SetTitle(yaxis.data());

    allhistos.at(0)->Draw("AXIS");
    for(size_t i=0;i<s_names.size();i++){
        allhistos.at(i)->Draw("same,hist");
    }
    leg->Draw("same");

    cv.Write();
    cv.Print(toutfile);

    f->Close();


}


void makeEffPlots(
        const boost::python::list intextfiles,
        const boost::python::list names,
        const boost::python::list variables,
        const boost::python::list cutsnum,
        const boost::python::list cutsden,
        const boost::python::list colors,
        std::string outfile,
        std::string xaxis,
        std::string yaxis,
        int rebinfactor,
        bool setLogY,
	float Xmin,
	float Xmax,
        float OverrideMin=1e100,
        float OverrideMax=-1e100,
        std::string sourcetreename="deepntuplizer/tree"
		  )
  {


    std::vector<TString>  s_intextfiles=toSTLVector<TString>(intextfiles);
    std::vector<TString>  s_vars = toSTLVector<TString>(variables);
    std::vector<TString>  s_names = toSTLVector<TString>(names);
    std::vector<TString>  s_colors = toSTLVector<TString>(colors);
    std::vector<TString>  s_cutsnum = toSTLVector<TString>(cutsnum);
    std::vector<TString>  s_cutsden = toSTLVector<TString>(cutsden);

    //reverse to make the first be on top
    std::reverse(s_intextfiles.begin(),s_intextfiles.end());
    std::reverse(s_vars.begin(),s_vars.end());
    std::reverse(s_names.begin(),s_names.end());
    std::reverse(s_colors.begin(),s_colors.end());
    std::reverse(s_cutsnum.begin(),s_cutsnum.end());
    std::reverse(s_cutsden.begin(),s_cutsden.end());

    TString toutfile=outfile;
    if(!toutfile.EndsWith(".pdf"))
        throw std::runtime_error("makePlots: output files need to be pdf format");


    if(!s_names.size())
        throw std::runtime_error("makePlots: needs at least one legend entry");
    /*
     * Size checks!!!
     */
    if(s_intextfiles.size() !=s_names.size()||
            s_names.size() != s_vars.size() ||
            s_names.size() != s_colors.size()||
            s_names.size() != s_cutsden.size()||
            s_names.size() != s_cutsnum.size())
        throw std::runtime_error("makePlots: input lists must have same size");

    //make unique list of infiles
    std::vector<TString> u_infiles;
    std::vector<TString> aliases;
    TString oneinfile="";
    bool onlyonefile=true;
    for(const auto& f:s_intextfiles){
        if(oneinfile.Length()<1)
            oneinfile=f;
        else
            if(f!=oneinfile)
                onlyonefile=false;
    }
    for(const auto& f:s_intextfiles){
        //if(std::find(u_infiles.begin(),u_infiles.end(),f) == u_infiles.end()){
        u_infiles.push_back(f);
        TString s="";
        s+=aliases.size();
        aliases.push_back(s);
        //  std::cout << s <<std::endl;
        //}
    }

    friendTreeInjector injector(sourcetreename);
    for(size_t i=0;i<u_infiles.size();i++){
        if(!aliases.size())
            injector.addFromFile((TString)u_infiles.at(i));
        else
            injector.addFromFile((TString)u_infiles.at(i),aliases.at(i));
    }
    injector.createChain();

    TChain* c=injector.getChain();
    std::vector<TH1F*> allhistos;
    TLegend * leg=new TLegend(0.2,0.75,0.8,0.88);
    leg->SetBorderSize(0);

    leg->SetNColumns(3);
    leg->SetFillStyle(0);

    TString addstr="";
    float max=-1e100;
    float min=1e100;

    TString tfileout=toutfile;
    tfileout=tfileout(0,tfileout.Length()-4);
    tfileout+=".root";

    TFile * f = new TFile(tfileout,"RECREATE");
    gStyle->SetOptStat(0);

    for(size_t i=0;i<s_names.size();i++){
        TString tmpname="hist_";
        TString numcuts=s_cutsnum.at(i);
        if(s_cutsden.at(i).Length())
            numcuts+="&&("+s_cutsden.at(i)+")";
        tmpname+=i;
        c->Draw(s_vars.at(i)+">>"+tmpname,numcuts,addstr);
        TH1F *numhisto = (TH1F*) gROOT->FindObject(tmpname);
        if(rebinfactor>1)
            numhisto->Rebin(rebinfactor);
        TH1F *denhisto=(TH1F *)numhisto->Clone(tmpname+"den");


        c->Draw(s_vars.at(i)+">>"+tmpname+"den",s_cutsden.at(i),addstr);
        for(int bin=0;bin<=numhisto->GetNbinsX();bin++){
            float denbin=denhisto->GetBinContent(bin);
            if(denbin){
                numhisto->SetBinContent(bin, numhisto->GetBinContent(bin)/denbin);
            }
            else{
                numhisto->SetBinContent(bin,0);
            }
        }
        TH1F *histo = numhisto; //(TH1F *)()->Clone(tmpname) ;


        histo->SetLineColor(colorToTColor(s_colors.at(i)));
        histo->SetLineStyle(lineToTLineStyle(s_colors.at(i)));
        histo->SetTitle(s_names.at(i));
        histo->SetName(s_names.at(i));

        histo->SetFillStyle(0);
        histo->SetLineWidth(2);

        float tmax=histo->GetMaximum();
        float tmin=histo->GetMinimum();
        if(tmax>max)max=tmax;
        if(tmin<min)min=tmin;
        if(OverrideMin<OverrideMax){
            //std::cout << "overriding min/max"<< std::endl;
            max = OverrideMax;
            min = OverrideMin;
        }
        //std::cout << "min" << min << " max" << max << std::endl;

        allhistos.push_back(histo);

        histo->Write();


    }
    for(size_t i=allhistos.size();i;i--){
        leg->AddEntry(allhistos.at(i-1),s_names.at(i-1),"l");
    }

    TCanvas cv("plots");

    if(setLogY) cv.SetLogy();
    allhistos.at(0)->Draw("AXIS");
    allhistos.at(0)->GetYaxis()->SetRangeUser(min,1.3*max); //space for legend on top

    allhistos.at(0)->GetXaxis()->SetTitle(xaxis.data());
    if(Xmin<Xmax)  allhistos.at(0)->GetXaxis()->SetRangeUser(Xmin,Xmax);
    allhistos.at(0)->GetYaxis()->SetTitle(yaxis.data());

    allhistos.at(0)->Draw("AXIS");
    for(size_t i=0;i<s_names.size();i++){
        allhistos.at(i)->Draw("same,hist");
    }
    leg->Draw("same");

    cv.Write();
    cv.Print(toutfile);

    f->Close();


}

void makeProfiles(
        const boost::python::list intextfiles,
        const boost::python::list names,
        const boost::python::list variables,
        const boost::python::list cuts,
        const boost::python::list colors,
        std::string outfile,
        std::string xaxis,
        std::string yaxis,
        bool normalized, bool profiles,
	std::string profileType, bool makeWidthProfile,
	float minimum,
        float maximum,
	int xbins_,
	Double_t xmin_,
	Double_t xmax_,
        std::string treename) {

    makePlots(
            intextfiles,
            names,
            variables,
            cuts,
            colors,
            outfile,
            xaxis,
            yaxis,
            normalized,
            profiles,profileType,makeWidthProfile,
            minimum,
            maximum,
	    xbins_,
	    xmin_,
	    xmax_,
	    treename);
}  

TH1F* getProfile(TH2F* scatterHist, TString profileType, Double_t xmin_, Double_t xmax_)
{
	TH1F *hProfile = new TH1F("hProfile","",
		scatterHist->GetNbinsX(),
		xmin_, //scatterHist->GetXaxis()->GetBinLowEdge(1), //GetXmin(),
		xmax_); //scatterHist->GetXaxis()->GetBinUpEdge(scatterHist->GetNbinsX())); //GetXmax());
	hProfile->Sumw2();

	TH1F *htemp = new TH1F("htemp","",
		scatterHist->GetNbinsY(),
		scatterHist->GetYaxis()->GetXmin(),
		scatterHist->GetYaxis()->GetXmax());
	htemp->Sumw2();


	const int nq = 2;
	double yq[2],xq[2];
	xq[0] = 0.5;
	xq[1] = 0.90;
	double yq_IQM[2],xq_IQM[2];
	xq_IQM[0] = 0.25;
	xq_IQM[1] = 0.75;

	// Loop over x bins
	for(int xBin = 1; xBin <= scatterHist->GetNbinsX(); xBin++) { //1
		htemp->Reset();
		// Copy y bin content in this x bins to htemp
		for(int yBin = 1; yBin <= scatterHist->GetNbinsY(); yBin++) { //1
			htemp->SetBinContent(yBin,scatterHist->GetBinContent(xBin,yBin));
			htemp->SetBinError(yBin,scatterHist->GetBinError(xBin,yBin));
		}


		htemp->SetEntries(htemp->GetEffectiveEntries());
		htemp->GetXaxis()->SetRange(0,-1);

		if(htemp->GetEntries()>100){
			double mean = htemp->GetMean(); 
			double meanerror = htemp->GetMeanError();
			double width = htemp->GetRMS();
			if(width < 0.1) width = 0.1;
			if(htemp->GetSumOfWeights() <= 0) {
				continue; 
			} else {
				htemp->Fit("gaus","QNI","", mean - 3 * width,mean + 3 * width);
				TF1 *f = (TF1*)gROOT->GetFunction("gaus")->Clone();
				mean = f->GetParameter(1);
				meanerror = f->GetParError(1);
				width = f->GetParameter(2);
				if(width < 0.05) width = 0.05;
				if( (htemp->Fit(f,"QI","goff",mean - 1.5 * width, mean + 1.5 * width) == 0) ) { //removed N option to store GaussFit with histogram
					mean = f->GetParameter(1);
					meanerror = f->GetParError(1);
					width = f->GetParameter(2);
	              
					if(profileType=="GaussFitMean"){
						hProfile->SetBinContent(xBin,mean);
						hProfile->SetBinError(xBin,meanerror);
					}
					else if (profileType=="GaussFitWidth"){
						hProfile->SetBinContent(xBin,width);
						hProfile->SetBinError(xBin,f->GetParError(2));
					}
					else if  (profileType=="GaussFitWidthNormByMean"){ 
						hProfile->SetBinContent(xBin,width/mean);
						hProfile->SetBinError(xBin,f->GetParError(2)/mean);
					}
					else if  (profileType=="GaussFitChi2"){ 
						hProfile->SetBinContent(xBin,f->GetChisquare() / f->GetNumberFreeParameters());
						hProfile->SetBinError(xBin,0.01);
					}
					else if  (profileType=="GaussFitProb"){ 
						hProfile->SetBinContent(xBin,f->GetProb());
						hProfile->SetBinError(xBin,0.01);
					}
					mean = htemp->GetMean();
					meanerror = htemp->GetMeanError();
					width = htemp->GetRMS();
					htemp->ComputeIntegral(); //needed for TH1::GetQuantiles() according to documentation
					htemp->GetQuantiles(nq,yq,xq);
	
					if(profileType=="Mean"){
						hProfile->SetBinContent(xBin,mean);
						hProfile->SetBinError(xBin,meanerror);
					}
					else if (profileType=="StandardDeviationNormByMean"){
						hProfile->SetBinContent(xBin,width/mean);
						hProfile->SetBinError(xBin,htemp->GetRMSError()/mean);
					}
					else if (profileType=="StandardDeviation"){
						hProfile->SetBinContent(xBin,width);
						hProfile->SetBinError(xBin,htemp->GetRMSError());
					}
					else if (profileType=="Median"){
						hProfile->SetBinContent(xBin,yq[0]);
						hProfile->SetBinError(xBin,0.0001);//not meaningful
					}
					htemp->GetQuantiles(nq,yq_IQM,xq_IQM);
					Int_t IQ_low_bin_i = htemp->FindBin(yq_IQM[0]);
					Int_t IQ_hig_bin_i = htemp->FindBin(yq_IQM[1]);
					htemp->GetXaxis()->SetRange(IQ_low_bin_i,IQ_hig_bin_i);
					mean = htemp->GetMean();
					meanerror = htemp->GetMeanError();
					if(profileType=="IQMean"){
						hProfile->SetBinContent(xBin,mean);
						hProfile->SetBinError(xBin,meanerror);
					}
				}
			}//endweightelse
		}
//		std::cout<<"Xbin low edge: "<<hProfile->GetBinLowEdge(xBin)<<" Xbin up edge: "<<" content: "<<hProfile->GetBinContent(xBin)<<std::endl;
	}

	delete htemp;
	return hProfile;
}

// Expose classes and methods to Python
BOOST_PYTHON_MODULE(c_makePlots) {
    //__hidden::indata();//for some reason exposing the class prevents segfaults. garbage collector?
    //anyway, it doesn't hurt, just leave this here
    def("makePlots", &makePlots);
    def("makeEffPlots", &makeEffPlots);
    def("makeProfiles", &makeProfiles);
}

