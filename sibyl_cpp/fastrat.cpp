#include "stdio.h"
#include "stdlib.h"

#include <string>
#include <vector>

#include <TFile.h>
#include <TTree.h>
#include <TVector3.h>

#include <RAT/DS/PMT.hh>
#include <RAT/DS/PMTInfo.hh>
#include <RAT/DS/Root.hh>
#include <RAT/DS/Run.hh>

extern "C" {
double* retArr;
double num = 42.0;
double* square(double* arr, int size) {
  retArr = (double*)malloc(size * sizeof(double));
  for (int i = 0; i < size; i++) {
    retArr[i] = arr[i] * arr[i];
  }
  num += 1;
  return retArr;
}
void freeSquare() { free(retArr); }

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
void openFile(char* p) {
  tfile = new TFile(p);
  // PMT Info
  runT = (TTree*)tfile->Get("runT");
  runT->SetBranchAddress("run", &run);
  runT->GetEntry(0);
  pmtinfo = run->GetPMTInfo();
  pmtcount = pmtinfo->GetPMTCount();
  printf("PMTs: %i\n", pmtcount);
  pmt_posx = (double*)malloc(pmtcount * sizeof(double));
  pmt_posy = (double*)malloc(pmtcount * sizeof(double));
  pmt_posz = (double*)malloc(pmtcount * sizeof(double));
  pmt_charge = (double*)malloc(pmtcount * sizeof(double));
  pmt_time = (double*)malloc(pmtcount * sizeof(double));
  for (int i = 0; i < pmtcount; i++) {
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

int getEntries() { return entries; }

RAT::DS::EV* ev;
int nhit = 0;
void getEvent(int event) {
  // clear last event;
  T->GetEvent(event);

  // reset pmt hits
  for (int i = 0; i < pmtcount; i++) {
    pmt_charge[i] = -100;
    pmt_time[i] = -100;
  }
  // check first
  if (ds->GetEVCount() < 1) return;
  ev = ds->GetEV(0);
  nhit = ev->GetPMTCount();
  for (int i = 0; i < nhit; i++) {
    RAT::DS::PMT* apmt = ev->GetPMT(i);
    int pid = apmt->GetID();
    double charge = apmt->GetCharge();
    double time = apmt->GetTime();
    pmt_charge[pid] = charge;
    pmt_time[pid] = time;
  }
}

std::vector<double> xtrack, ytrack, ztrack;
std::vector<int> pnames;
std::map<std::string, int> pnmap = {
    {"Cerenkov", 1}, {"Scintillation", 2}, {"Reemission", 2},  // from scint.
    {"e-", 3},       {"gamma", 4},         {"mu-", 5},        {"mu+", 5}};

void getTracking() {
  RAT::DS::MC* mc = ds->GetMC();
  int nTracks = mc->GetMCTrackCount();
  // Loop over each track
  xtrack.clear();
  ytrack.clear();
  ztrack.clear();
  pnames.clear();

  for (int trk = 0; trk < nTracks; trk++) {
    RAT::DS::MCTrack* track = mc->GetMCTrack(trk);
    std::string name = track->GetParticleName();
    if (name == "opticalphoton") name = track->GetMCTrackStep(0)->GetProcess();
    int nSteps = track->GetMCTrackStepCount();
    for (int stp = 0; stp < nSteps; stp++) {
      RAT::DS::MCTrackStep* step = track->GetMCTrackStep(stp);
      TVector3 tv = step->GetEndpoint();
      if ((stp != 0) && (stp != nSteps - 1)) {
        xtrack.push_back(tv.X());
        ytrack.push_back(tv.Y());
        ztrack.push_back(tv.Z());
        pnames.push_back(pnmap[name]);
      }
      xtrack.push_back(tv.X());
      ytrack.push_back(tv.Y());
      ztrack.push_back(tv.Z());
      pnames.push_back(pnmap[name]);
    }
  }
}

int getTrackCount() { return xtrack.size(); }
double* getTrackX() { return &xtrack[0]; }
double* getTrackY() { return &ytrack[0]; }
double* getTrackZ() { return &ztrack[0]; }
int* getTrackNames() { return &pnames[0]; }

int getNHit() { return nhit; }
int getPMTCount() { return pmtcount; }
double* getPMTX() { return pmt_posx; }
double* getPMTY() { return pmt_posy; }
double* getPMTZ() { return pmt_posz; }
double* getCharge() { return pmt_charge; }
double* getTime() { return pmt_time; }
}
