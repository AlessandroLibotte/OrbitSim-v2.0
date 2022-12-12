# OrbitSim-v2.0
Basic 2D orbital mechanics simulator with GUI

This basic software is capable of computing and displaying an approximation of the orbit of one or more objects throug the eqation of motion. This is a rivisitation of an older project (OrbitSim) that was crude and poorly optimized, i also came to understand that the eqations i used were completely wrong thus leading to incorrect path projections. I have now completelly redone the whole software adding:

1. Correct motion equation

2. A user friendly GUI interface 

3. A much better displaying method making use of the tkinter canvas instead of resettign and redrawing the whole screen every cycle thus enabling the presence of much more object and path points without the same lag and computing requirements

4. A bunch of personalizable and scalable parameters to easily model a whide range of scenarios

The accuracity of the orbits displayed is based on the "Path Resolution" value, decreasing this value will increase the accuracity of the approximated orbit but also increase the time needed to compute every point of the orbit and the lag when moving the object.

By left clicking on an object a white circle will appear around it indicating that the object is selected, by clicking anywhere else the object will be deselected. Object can be moved by holding down left click on them and dragging.

There are also some keyboard controls to make the interaction with objects easier and faster:

W, A, S, D: velocity vector controls for the selected object

Q, E: decrease/increase path iterations

Z, C: increase/decrease path resolution
