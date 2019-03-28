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
  Python3
  PyQt5
  PyQtGraph
  python-opengl
  rat-pac
### Optional
- Plotly -- Useful for a web conversion, not currently implemented.
- SnakeViz is nice for visualizing cProfile

TODO
----
- Setup bonsai library for just-in-time fitting.
- Factorize the code
- Split module view
- File menu: Quit button.
  - Quit button
  - Load data file
- Save state as json
- Datastream simulator & datastream reading
  - Define a speed requirement. Maybe 4-10Hz at full occupancy.
- Geometry helper
  - Helps the flatmap view know where to make PMT cuts
  - Could be used to draw in Geant4 objects.
- Option to run as single window widgets.

- Determine if I can drop the pyqtgraph dependency in favor of
just python-opengl


Profile:
- python -m cProfile -o profile.out sibyl.py data.root
- snakeviz profile.out
