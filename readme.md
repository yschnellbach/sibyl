Sibyl - A watchman event viewer
===============================
Why sibyl: They were oracles which gleamed information from Chthonic
dieties---ie they got their information from within the earth (underground).
The most famous of which was the Pythia, high priestess of the temple of Apollo
at Delphi.

Sibyl is a simple pythonic event viewer that will interact with rat-pac to
provide a 2d and 3d event display. The display itself is meant to look modern
and be cross-platform, with the only strong dependency being on rat-pac.

Installation
------------
To install, first make sure you source ROOT and RAT-PAC

    $ source <root_install>/bin/thisroot.sh
    $ source <ratpac_install>/bin/ratpac.sh

then continue using `pip` or `setuptools`

    $ pip install --user git+https://github.com/ait-watchman/sibyl#egg=sibyl

or to keep a local version

    $ git clone https://github.com/ait-watchman/sibyl
    $ cd sibyl
    $ pip install --user .

Usage
-----

After installing, you will have a script called `sibyl` that you call from the command line

    $ sibyl -h
    usage: sibyl [-h] [--debug] [--tracking]
                [--cherenkov_brightness CHERENKOV_BRIGHTNESS] [--invisible]
                [--onlyHits] [--stream]
                ratfile

    positional arguments:
    ratfile               rat root file

    optional arguments:
    -h, --help            show this help message and exit
    --debug               Turn on debug print statements
    --tracking            ROOT files only. If storeTracking was used during
                            simulation, then the particle tracks will be drawn.
    --cherenkov_brightness CHERENKOV_BRIGHTNESS
                            Scale cherenkov when showing tracks
    --invisible           This is a hack, remove eventually
    --onlyHits            Show only hit pmts
    --stream              Hack to test streaming capabilities

or in cases of complicated python environments

    $ python -m sibyl ...
    


Dependencies
------------
### Required
- Python3
- Qt5 with OpenGL support
- rat-pac (compiled with ROOT-6)
### Optional
- markdown -- properly display the readme page in the about tab
- Plotly -- Useful for a web conversion, not currently implemented.
- SnakeViz is nice for visualizing cProfile

TODO
----
- [ ] Icon/logo update
- [ ] MC View
  - [ ] Display macro TObjString as text file
  - [ ] Primary particles and energy
  - [ ] Primary Vertex and direction
- [ ] Main screen info panel
  - [ ] NHits
  - [ ] Run ID
  - [ ] GTID
  - [ ] Fit Vertex and Direction
  - [ ] Fit energy (n9 and conversion?)
  - [ ] Selection criteria
- [ ] Project 3D to unit sphere (fit vertex or 0,0,0 if none)
- [ ] Tab selector
  - [ ] Slow controls
  - [ ] DAQ
  - [ ] Crate View
    - [ ] Crate Rainbow
- [ ] Setup bonsai library for just-in-time fitting.
  - [ ] libBonsai.so
  - [ ] Bonsai in python
  - [ ] Fit button (print to screen)
  - [ ] Fit, print to QT textdocument
  - [ ] Draw cherenkov ring (3D)
  - [ ] Draw cherenkov ring (2D)
- [ ] Factorize the code
  - [ ] Make geometry independent
  - [ ] Include geometry files
  - [ ] Module base class
- [ ] Draw geant4 solids from .geo file
- [ ] Split module view
- [ ] File menu
  - [x] Quit button
  - [ ] Load data file
- [ ] Save state as json
- [ ] Geometry helper
  - [ ] Helps the flatmap view know where to make PMT cuts
  - [ ] Could be used to draw in Geant4 objects.
- [ ] Histrogram
  - [ ] Axis labels
  - [x] Swap colors
  - [x] Control global colors
  - [x] Axis ticks
  - [ ] Axis tick numbers
  - [ ] Fix grid
- [ ] Option to run as single window widgets.
- [ ] Improve 3D controls (fly/fps mode)
- [ ] Improve 2D projection
  - [ ] Hover over PMTs to get pmtid
  - [ ] Info in corners of panel
  - [ ] Zoom / Pan at mouse location
- [ ] Options / settings tab (or context menu)

- [ ] Determine if I can drop the pyqtgraph dependency in favor of
just python-opengl


Profile
-------
- python -m cProfile -o profile.out sibyl.py data.root
- snakeviz profile.out
