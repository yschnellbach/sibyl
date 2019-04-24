Sibyl - A watchman event viewer
===============================
Why sibyl: They were oracles which gleamed information from Chthonic
dieties---ie they got their information from within the earth (underground).
The most famous of which was the Pythia, high priestess of the temple of Apollo
at Delphi.

Sibyl is a simple pythonic event viewer that will interact with rat-pac to
provide a 2d and 3d event display. The display itself is meant to look modern
and be cross-platform, with the only strong dependency being on rat-pac.

Dependencies
------------
### Required
- Python3
- PyQt5
- PyQtGraph
- python-opengl
- rat-pac (compiled with ROOT-6)
### Optional
- python-markdown -- properly display the readme page in the about tab
- Plotly -- Useful for a web conversion, not currently implemented.
- SnakeViz is nice for visualizing cProfile

TODO
----
- [ ] Setup bonsai library for just-in-time fitting.
  - [ ] libBonsai.so
  - [ ] Bonsai in python
  - [ ] Fit button (print to screen)
  - [ ] Fit, print to QT textdocument
  - [ ] Draw cherenkov ring
- [ ] Factorize the code
  - [ ] Make geometry independent
  - [ ] Include geometry files
  - [ ] Module base class
- [x] Colors
  - [x] Make color choice global.
  - [x] Choose from MPL code in context menu
- [ ] Split module view
- [ ] File menu
  - [x] Quit button
  - [ ] Load data file
- [ ] Save state as json
- [x] Datastream simulator & datastream reading
  - [x] Define a speed requirement. Maybe 4-10Hz at full occupancy.
- [ ] Geometry helper
  - [ ] Helps the flatmap view know where to make PMT cuts
  - [ ] Could be used to draw in Geant4 objects.
- [ ] Histrogram
  - [ ] Axis labels
  - [x] Swap colors
  - [x] Control global colors
  - [x] Axis ticks
  - [ ] Axis tick numbers
- [ ] Option to run as single window widgets.

- [ ] Determine if I can drop the pyqtgraph dependency in favor of
just python-opengl


Profile
-------
- python -m cProfile -o profile.out sibyl.py data.root
- snakeviz profile.out
