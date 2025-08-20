import os
import numpy as np
import json
import cvxpy as cp

with open("parameters.json", "r") as f:
   parameters = json.load(f)

constraints = []

### Define the parameters

TotalLand = parameters["TotalLand"] # shape: [], definition: Total land available for cultivation
WateringTimeTurnips = parameters["WateringTimeTurnips"] # shape: [], definition: Watering time required per acre of turnips
PesticideCostTurnips = parameters["PesticideCostTurnips"] # shape: [], definition: Pesticide cost per acre of turnips
WateringTimePumpkins = parameters["WateringTimePumpkins"] # shape: [], definition: Watering time required per acre of pumpkins
PesticideCostPumpkins = parameters["PesticideCostPumpkins"] # shape: [], definition: Pesticide cost per acre of pumpkins
TotalWateringTime = parameters["TotalWateringTime"] # shape: [], definition: Total available watering time
TotalPesticideBudget = parameters["TotalPesticideBudget"] # shape: [], definition: Total pesticide budget
RevenueTurnips = parameters["RevenueTurnips"] # shape: [], definition: Revenue per acre of turnips
RevenuePumpkins = parameters["RevenuePumpkins"] # shape: [], definition: Revenue per acre of pumpkins


### Define the variables

AcresTurnips = cp.Variable(name='AcresTurnips')
AcresPumpkins = cp.Variable(name='AcresPumpkins')


### Define the constraints

constraints.append(AcresTurnips + AcresPumpkins <= TotalLand)
constraints.append(AcresTurnips >= 0)
constraints.append(AcresPumpkins >= 0)
constraints.append(WateringTimeTurnips * AcresTurnips + WateringTimePumpkins * AcresPumpkins <= TotalWateringTime)
constraints.append(PesticideCostTurnips * AcresTurnips + PesticideCostPumpkins * AcresPumpkins <= TotalPesticideBudget)
constraints.append(AcresTurnips >= 0)
constraints.append(AcresPumpkins >= 0)


### Define the objective

objective = cp.Maximize(RevenueTurnips * AcresTurnips + RevenuePumpkins * AcresPumpkins)


### Optimize the model

problem = cp.Problem(objective, constraints)
problem.solve(verbose=True, solver=cp.GUROBI)

if problem.status in ["OPTIMAL", "OPTIMAL_INACCURATE"]:
    with open("output_solution.txt", "w") as f:
       f.write(str(problem.value))
else:
    with open("output_solution.txt", "w") as f:
       f.write(problem.status)
