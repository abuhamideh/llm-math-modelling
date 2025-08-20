import os
import numpy as np
import json
import cvxpy as cp

with open("parameters.json", "r") as f:
   parameters = json.load(f)

constraints = []

### Define the parameters

TotalPopsicleSticks = parameters["TotalPopsicleSticks"] # shape: [], definition: Total number of Popsicle sticks available
PopsicleSticksPerBeamBridge = parameters["PopsicleSticksPerBeamBridge"] # shape: [], definition: Number of Popsicle sticks required to build one beam bridge
PopsicleSticksPerTrussBridge = parameters["PopsicleSticksPerTrussBridge"] # shape: [], definition: Number of Popsicle sticks required to build one truss bridge
TotalGlue = parameters["TotalGlue"] # shape: [], definition: Total units of glue available
GluePerBeamBridge = parameters["GluePerBeamBridge"] # shape: [], definition: Units of glue required to build one beam bridge
GluePerTrussBridge = parameters["GluePerTrussBridge"] # shape: [], definition: Units of glue required to build one truss bridge
MaxTrussBridges = parameters["MaxTrussBridges"] # shape: [], definition: Maximum number of truss bridges that can be built
MassPerBeamBridge = parameters["MassPerBeamBridge"] # shape: [], definition: Mass that one beam bridge can hold
MassPerTrussBridge = parameters["MassPerTrussBridge"] # shape: [], definition: Mass that one truss bridge can hold


### Define the variables

BeamBridges = cp.Variable(name='BeamBridges', integer=True)
TrussBridges = cp.Variable(name='TrussBridges', integer=True)


### Define the constraints

constraints.append(PopsicleSticksPerBeamBridge * BeamBridges + PopsicleSticksPerTrussBridge * TrussBridges <= TotalPopsicleSticks)
constraints.append(GluePerBeamBridge * BeamBridges + GluePerTrussBridge * TrussBridges <= TotalGlue)
constraints.append(TrussBridges <= MaxTrussBridges)
constraints.append(BeamBridges - TrussBridges >= 1)
constraints.append(BeamBridges >= 0)
constraints.append(TrussBridges >= 0)


### Define the objective

objective = cp.Maximize(MassPerBeamBridge * BeamBridges + MassPerTrussBridge * TrussBridges)


### Optimize the model

problem = cp.Problem(objective, constraints)
problem.solve(verbose=True, solver=cp.GUROBI)

if problem.status in ["OPTIMAL", "OPTIMAL_INACCURATE"]:
    with open("output_solution.txt", "w") as f:
       f.write(str(problem.value))
else:
    with open("output_solution.txt", "w") as f:
       f.write(problem.status)