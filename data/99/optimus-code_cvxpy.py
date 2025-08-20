import os
import numpy as np
import json
import cvxpy as cp

with open("parameters.json", "r") as f:
   parameters = json.load(f)

constraints = []

### Define the parameters

AutomaticMachineTimePerPatient = parameters["AutomaticMachineTimePerPatient"] # shape: [], definition: Time taken by the automatic machine to process one patient.
ManualMachineTimePerPatient = parameters["ManualMachineTimePerPatient"] # shape: [], definition: Time taken by the manual machine to process one patient.
ManualPatientMinRatio = parameters["ManualPatientMinRatio"] # shape: [], definition: Minimum ratio of manual machine patients to automatic machine patients.
AutomaticMachineMinimumPatients = parameters["AutomaticMachineMinimumPatients"] # shape: [], definition: Minimum number of patients that must be processed by the automatic machine.
TotalAvailableTime = parameters["TotalAvailableTime"] # shape: [], definition: Total available time for the clinic in minutes.


### Define the variables

AutomaticMachinePatients = cp.Variable(name='AutomaticMachinePatients')
ManualMachinePatients = cp.Variable(name='ManualMachinePatients')


### Define the constraints

constraints.append(AutomaticMachineTimePerPatient * AutomaticMachinePatients + ManualMachineTimePerPatient * ManualMachinePatients <= TotalAvailableTime)
constraints.append(ManualMachinePatients >= ManualPatientMinRatio * AutomaticMachinePatients)
constraints.append(AutomaticMachinePatients >= AutomaticMachineMinimumPatients)
constraints.append(AutomaticMachinePatients >= 0)
constraints.append(ManualMachinePatients >= 0)


### Define the objective

objective = cp.Maximize(AutomaticMachinePatients + ManualMachinePatients)
model = cp.Problem(objective, constraints)  # Corrected initialization


### Optimize the model

problem = cp.Problem(objective, constraints)
problem.solve(verbose=True, solver=cp.GUROBI)  # Fixed the syntax issue

if problem.status in ["OPTIMAL", "OPTIMAL_INACCURATE"]:
    with open("output_solution.txt", "w") as f:
       f.write(str(problem.value))
else:
    with open("output_solution.txt", "w") as f:
       f.write(problem.status)