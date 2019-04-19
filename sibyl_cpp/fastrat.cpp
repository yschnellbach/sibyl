#include "stdlib.h"
#include "stdio.h"

#include <vector>

#include <TFile.h>
#include <TTree.h>
#include <TVector3.h>

#include <RAT/DS/Root.hh>
#include <RAT/DS/Run.hh>
#include <RAT/DS/PMT.hh>
#include <RAT/DS/PMTInfo.hh>

extern "C"
{
  double* retArr;
  double num = 42.0;
  double* square(double* arr, int size)
  {
    retArr = (double*)malloc(size*sizeof(double));
    for(int i=0; i<size; i++)
    {
      retArr[i] = arr[i]*arr[i];
    }
    num += 1;
    return retArr;
  }
  void freeSquare()
  {
    free(retArr);
  }

  int entries = 0;
  int pmtcount = 0;
  TFile* tfile;
  TTree* runT;
  TTree* T;
  double* pmt_posx;
  double* pmt_posy;
  double* pmt_posz;

  double* pmt_charge;
  double* pmt_time;

  RAT::DS::Run* run;
  RAT::DS::PMTInfo* pmtinfo;
  RAT::DS::Root* ds;
  void openFile(char* p)
  {
    tfile = new TFile(p);
    // PMT Info
    runT = (TTree*)tfile->Get("runT");
    runT->SetBranchAddress("run", &run);
    runT->GetEntry(0);
    pmtinfo = run->GetPMTInfo();
    pmtcount = pmtinfo->GetPMTCount();
    printf("PMTs: %i\n", pmtcount);
    pmt_posx   = (double*)malloc(pmtcount*sizeof(double));
    pmt_posy   = (double*)malloc(pmtcount*sizeof(double));
    pmt_posz   = (double*)malloc(pmtcount*sizeof(double));
    pmt_charge = (double*)malloc(pmtcount*sizeof(double));
    pmt_time   = (double*)malloc(pmtcount*sizeof(double));
    for(int i=0; i<pmtcount; i++)
    {
      TVector3 v = pmtinfo->GetPosition(i);
      pmt_posx[i] = v.X();
      pmt_posy[i] = v.Y();
      pmt_posz[i] = v.Z();
    }

    T = (TTree*)tfile->Get("T");
    entries = T->GetEntries();
    printf("Entries: %i\n", entries);
    T->SetBranchAddress("ds", &ds);
  }

  int getEntries()
  {
    return entries;
  }

  RAT::DS::EV* ev;
  int nhit = 0;
  void getEvent(int event)
  {
    // clear last event;
    T->GetEvent(event);

    // reset pmt hits
    for(int i=0; i<pmtcount; i++)
    {
      pmt_charge[i] = -100;
      pmt_time[i] = -100;
    }
    // check first
    if( ds->GetEVCount() < 1 )
      return;
    ev = ds->GetEV(0);
    nhit = ev->GetPMTCount();
    for(int i=0; i<nhit; i++)
    {
      RAT::DS::PMT* apmt = ev->GetPMT(i);
      int pid = apmt->GetID(); 
      double charge = apmt->GetCharge();
      double time = apmt->GetTime();
      pmt_charge[pid] = charge;
      pmt_time[pid] = time;
    }
  }

  int getNHit(){ return nhit; }
  int getPMTCount(){ return pmtcount; }
  double* getPMTX(){ return pmt_posx; }
  double* getPMTY(){ return pmt_posy; }
  double* getPMTZ(){ return pmt_posz; }
  double* getCharge(){ return pmt_charge; }
  double* getTime(){ return pmt_time; }
}
