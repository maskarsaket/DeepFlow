import pandas as pd
from __init__ import DeepFlow 
from time import sleep
import random
import os

projectname = "DeepFlow"
runmaster = "data/runmaster.csv"
bench = 90

print("Description : ")
desc = input()

print("ParentID : ")
parentID = int(input())

params = {
    'model' : 'LGB',
    'Lagslist' : '1,2,3'
}

flow = DeepFlow(
    projectname = projectname,
    runmasterfile = runmaster,
    description = desc,
    parentID = parentID,
    benchmark = bench,
    params = params
)

print("RMSE : ")

flow.log_score('Accuracy', 'rmse', 94)
sleep(2)

imp = pd.DataFrame({
    'Feature':['test1', 'test2'],
    'Importance':[1,2]
})

path = 'Runs/exp1'

flow.log_imp(imp, 'Runs/exp1')

flow.end_run()