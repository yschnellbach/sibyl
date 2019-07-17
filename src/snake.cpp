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

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>  // Use numpy arrays

namespace py = pybind11;

double num = 42.0;

int entries = 0;
int pmtcount = 0;
TFile* tfile;
TTree* runT;
TTree* T;
// TODO can I rewrite this using vectors or py::array?
double* pmt_posx;
double* pmt_posy;
double* pmt_posz;

double* pmt_charge;
double* pmt_time;

RAT::DS::Run* run;
RAT::DS::PMTInfo* pmtinfo;
RAT::DS::Root* ds;

/*
 * Opens RATPAC root file
 */
void openFile(string filename) {
  std::cout << "Opening " << filename << std::endl;
  tfile = new TFile(filename);
  // PMT Info
  runT = (TTree*)tfile->Get("runT");
  runT->SetBranchAddress("run", &run);
  runT->GetEntry(0);
  pmtinfo = run->GetPMTInfo();
  pmtcount = pmtinfo->GetPMTCount();
  std::cout << "PMTs: " << pmtcount << std::endl;
  pmt_posx = (double*) malloc(pmtcount * sizeof(double));
  pmt_posy = (double*) malloc(pmtcount * sizeof(double));
  pmt_posz = (double*) malloc(pmtcount * sizeof(double));
  pmt_charge = (double*) malloc(pmtcount * sizeof(double));
  pmt_time = (double*) malloc(pmtcount * sizeof(double));
  for (int i = 0; i < pmtcount; i++) {
    TVector3 v = pmtinfo->GetPosition(i);
    pmt_posx[i] = v.X();
    pmt_posy[i] = v.Y();
    pmt_posz[i] = v.Z();
  }

  T = (TTree*)tfile->Get("T");
  entries = T->GetEntries();
  std::cout << "Entries: " << entries << std::endl;
  T->SetBranchAddress("ds", &ds);
}

/* Return entries from opened TTree */
int getEntries() { return entries; }

RAT::DS::EV* ev;
int nhit = 0;

/* Get one event from opened TTree */
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

// TODO how to cast from double* to pyarray
py::Array<double> getPMTX() { 
  py::Array<double> ret(xtrack.size());
  return pmt_posx; 
  }
py::Array<double> getPMTY() { 
  py::Array<double> ret(xtrack.size());
  return pmt_posy; 
  }
py::Array<double> getPMTZ() { 
  py::Array<double> ret(xtrack.size());
  return pmt_posz; 
  }
py::Array<double> getCharge() { 
  py::Array<double> ret(xtrack.size());
  return pmt_charge; 
  }
py::Array<double> getTime() { 
  py::Array<double> ret(xtrack.size());
  return pmt_time; 
  }

void getXYZ() {
  py::Array<double> x = getPMTX();
  py::Array<double> y = getPMTY();
  py::Array<double> z = getPMTZ();
  return x, y, z;
}

// TODO how to return the two objects as tuple?
void getHitInfo() {
  int num_pmt = getPMTCount();
  py::Array<double> charge = getCharge();
  py::Array<double> time = getTime();
  return charge, time;
}

void getTrackSteps() {
  int track_steps = getTrackCount();
  py::Array<double> x_track = getTrackX();
  py::Array<double> y_track = getTrackY();
  py::Array<double> z_track = getTrackZ();
  py::Array<int> names = getTrackNames();
  return x_track, y_track, z_track, names;
}

/* Create python bindings */

PYBIND11_DEF_MODULE(snake, m) {
  m.def("openFile", &openFile, "filename"_a);
  m.def("getEvent", &getEvent, "event"_a);
  m.def("getEntries", &getEntries);
  m.def("getXYZ", &getXYZ);
  m.def("getHitInfo", &getHitInfo);
  m.def("getTracking", &getTracking);
  m.def("getTrackSteps", &getTrackSteps);
}
