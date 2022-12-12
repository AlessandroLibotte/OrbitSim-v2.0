# OrbitSim-v2.0
Basic 2D orbital mechanics simulator with GUI

This basic software is capable of computing and displaying an approximation of the orbit of one or more objects throug the eqation of motion.
The accuracity of the orbits displayed is based on the "Path Resolution" value, decreasing this value will increase the accuracity of the approximated orbit but also increase the time needed to compute every point of the orbit and the lag when moving the object.

By left clicking on an object a white circle will appear around it indicating that the object is selected, by clicking anywhere else the object will be deselected. Object can be moved by holding down left click on them and dragging.

There are also some keyboard controls to make the interaction with objects easier and faster:

W, A, S, D: velocity control for the selected object
Q, E: decrease/increase path iterations
Z, C: increase/decrease path resolution
