#include <string>

#include <TFile.h>
#include <TTree.h>

#include <RAT/DS/PMT.hh>
#include <RAT/DS/PMTInfo.hh>
#include <RAT/DS/Root.hh>
#include <RAT/DS/Run.hh>

#include <pybind11/pybind11.h>

namespace py = pybind11;

std::map<std::string, int> pnmap = {
    {"Cerenkov", 1}, {"Scintillation", 2}, {"Reemission", 2},  // from scint.
    {"e-", 3},       {"gamma", 4},         {"mu-", 5},        {"mu+", 5}};

class Snake {
 public:
  Snake(std::string);
  ~Snake() = default;
  int getEntries() { return entries; };
  void getEvent(int);
  void getTracks();
  void getTracking();
  int getTrackCount() { return xtrack.size(); };
  int getNHit() { return nhit; };
  int getPMTCount() { return pmtcount; }
  py::tuple getXYZ();
  py::tuple getHitInfo();
  py::tuple getTrackSteps();

 protected:
  int entries;
  int pmtcount;
  int nhit;

  TFile* tfile;
  TTree* runT;
  TTree* T;

  std::vector<double> pmt_posx;
  std::vector<double> pmt_posy;
  std::vector<double> pmt_posz;

  std::vector<double> pmt_charge;
  std::vector<double> pmt_time;

  RAT::DS::Run* run;
  RAT::DS::Root* ds;
  RAT::DS::PMTInfo* pmtinfo;
  RAT::DS::EV* ev;

  std::vector<double> xtrack;
  std::vector<double> ytrack;
  std::vector<double> ztrack;
  std::vector<int> pnames;
};