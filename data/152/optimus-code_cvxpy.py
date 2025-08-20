import os
import numpy as np
import json
import cvxpy as cp

with open("parameters.json", "r") as f:
   parameters = json.load(f)

constraints = []

### Define the parameters

TotalMonkeys = parameters["TotalMonkeys"] # shape: [], definition: Number of monkeys to transport
BusCapacity = parameters["BusCapacity"] # shape: [], definition: Number of monkeys a bus can transport per trip
BusTripTime = parameters["BusTripTime"] # shape: [], definition: Time in minutes a bus takes per trip
CarCapacity = parameters["CarCapacity"] # shape: [], definition: Number of monkeys a car can transport per trip
CarTripTime = parameters["CarTripTime"] # shape: [], definition: Time in minutes a car takes per trip
MaxBusTrips = parameters["MaxBusTrips"] # shape: [], definition: Maximum number of bus trips allowed
MinCarTripFraction = parameters["MinCarTripFraction"] # shape: [], definition: Minimum fraction of trips that must be by car


### Define the variables

BusTrips = cp.Variable(name='BusTrips', integer=True)
CarTrips = cp.Variable(name='CarTrips', integer=True)


### Define the constraints

constraints.append(BusTrips <= MaxBusTrips)
constraints.append((1 - MinCarTripFraction) * CarTrips >= MinCarTripFraction * BusTrips)
constraints.append(BusCapacity * BusTrips + CarCapacity * CarTrips == TotalMonkeys)
constraints.append(BusTrips >= 0)
constraints.append(CarTrips >= 0)


### Define the objective

objective = cp.Minimize(BusTrips * BusTripTime + CarTrips * CarTripTime)

### Optimize the model

problem = cp.Problem(objective, constraints)
problem.solve(verbose=True, solver=cp.GUROBI)

if problem.status in ["OPTIMAL", "OPTIMAL_INACCURATE"]:
    with open("output_solution.txt", "w") as f:
       f.write(str(problem.value))
else:
    with open("output_solution.txt", "w") as f:
       f.write(problem.status)
