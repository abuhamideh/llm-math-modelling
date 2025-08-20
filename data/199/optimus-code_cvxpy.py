import os
import numpy as np
import json
import cvxpy as cp

with open("parameters.json", "r") as f:
   parameters = json.load(f)

constraints = []

### Define the parameters

MinCalcium = parameters["MinCalcium"] # shape: [], definition: Minimum required units of calcium
MinVitaminMix = parameters["MinVitaminMix"] # shape: [], definition: Minimum required units of vitamin mix
MinProtein = parameters["MinProtein"] # shape: [], definition: Minimum required units of protein
PriceRegular = parameters["PriceRegular"] # shape: [], definition: Price per bag of regular brand
PricePremium = parameters["PricePremium"] # shape: [], definition: Price per bag of premium brand
CalciumRegular = parameters["CalciumRegular"] # shape: [], definition: Units of calcium per bag of regular brand
CalciumPremium = parameters["CalciumPremium"] # shape: [], definition: Units of calcium per bag of premium brand
VitaminMixRegular = parameters["VitaminMixRegular"] # shape: [], definition: Units of vitamin mix per bag of regular brand
VitaminMixPremium = parameters["VitaminMixPremium"] # shape: [], definition: Units of vitamin mix per bag of premium brand
ProteinRegular = parameters["ProteinRegular"] # shape: [], definition: Units of protein per bag of regular brand
ProteinPremium = parameters["ProteinPremium"] # shape: [], definition: Units of protein per bag of premium brand


### Define the variables

RegularBags = cp.Variable(name='RegularBags', integer=True)
PremiumBags = cp.Variable(name='PremiumBags', integer=True)


### Define the constraints

constraints.append(CalciumRegular * RegularBags + CalciumPremium * PremiumBags >= MinCalcium)
constraints.append(VitaminMixRegular * RegularBags + VitaminMixPremium * PremiumBags >= MinVitaminMix)
constraints.append(ProteinRegular * RegularBags + ProteinPremium * PremiumBags >= MinProtein)
constraints.append(RegularBags >= 0)
constraints.append(PremiumBags >= 0)


### Define the objective

objective = cp.Minimize(PriceRegular * RegularBags + PricePremium * PremiumBags)
model = cp.Problem(objective, constraints)


### Optimize the model

problem = cp.Problem(objective, constraints)
problem.solve(verbose=True, solver=cp.GUROBI)

if problem.status in ["OPTIMAL", "OPTIMAL_INACCURATE"]:
    with open("output_solution.txt", "w") as f:
       f.write(str(problem.value))
else:
    with open("output_solution.txt", "w") as f:
       f.write(problem.status)
