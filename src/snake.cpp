#include "Snake.h"
#include <iostream>

#include <TString.h>
#include <TVector3.h>

#include <pybind11/numpy.h>

namespace py = pybind11;
using namespace py::literals;  // For _a arguments

double num = 42.0;

Snake::Snake(std::string filename) {
  std::cout << "Opening " << filename << std::endl;
  tfile = new TFile((TString)filename);
  // PMT Info
  runT = (TTree*)tfile->Get("runT");
  runT->SetBranchAddress("run", &run);
  runT->GetEntry(0);
  pmtinfo = run->GetPMTInfo();
  pmtcount = pmtinfo->GetPMTCount();
  std::cout << "PMTs: " << pmtcount << std::endl;
  // Initialize vecs
  pmt_charge.resize(pmtcount);
  pmt_time.resize(pmtcount);
  for (int i = 0; i < pmtcount; i++) {
    TVector3 v = pmtinfo->GetPosition(i);
    pmt_posx.push_back(v.X());
    pmt_posy.push_back(v.Y());
    pmt_posz.push_back(v.Z());
  }

  T = (TTree*)tfile->Get("T");
  entries = T->GetEntries();
  std::cout << "Entries: " << entries << std::endl;
  T->SetBranchAddress("ds", &ds);
}

/* Get one event from opened TTree */
void Snake::getEvent(int event) {
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

void Snake::getTracking() {
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

py::tuple Snake::getXYZ() {
  py::array_t<double> x = py::array(pmt_posx.size(), pmt_posx.data());
  py::array_t<double> y = py::array(pmt_posy.size(), pmt_posy.data());
  py::array_t<double> z = py::array(pmt_posz.size(), pmt_posz.data());
  return py::make_tuple(x, y, z);
}

py::tuple Snake::getHitInfo() {
  py::array_t<double> charge = py::array(pmt_charge.size(), pmt_charge.data());
  py::array_t<double> time = py::array(pmt_time.size(), pmt_time.data());
  return py::make_tuple(charge, time);
}

py::tuple Snake::getTrackSteps() {
  py::array_t<double> x_track = py::array(xtrack.size(), xtrack.data());
  py::array_t<double> y_track = py::array(ytrack.size(), ytrack.data());
  py::array_t<double> z_track = py::array(ztrack.size(), ztrack.data());
  py::array_t<int> names = py::array(pnames.size(), pnames.data());
  return py::make_tuple(x_track, y_track, z_track, names);
}

/* Create python bindings */

PYBIND11_MODULE(snake, m) {
  py::class_<Snake>(m, "Snake")
      .def(py::init<std::string>())
      .def("getEvent", &Snake::getEvent, "event"_a)
      .def("getEntries", &Snake::getEntries)
      .def("getXYZ", &Snake::getXYZ)
      .def("getHitInfo", &Snake::getHitInfo)
      .def("getTracking", &Snake::getTracking)
      .def("getTrackSteps", &Snake::getTrackSteps);
}
