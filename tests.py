import pandas as pd
from __init__ import DeepFlow 
from time import sleep
import random
import os

projectname = "DeepFlow"
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
    description = desc,
    parentID = parentID,
    benchmark = bench,
    params = params
)

flow.log_score('Accuracy', 'rmse', 94)

imp = pd.DataFrame({
    'Feature':['test1', 'test2'],
    'Importance':[1,2]
})

flow.log_artefact(artefact=imp, name='importance')

learnings = pd.DataFrame({
    'Learnings':['test1', 'test2'],
})

flow.log_artefact(artefact=learnings, name='learnings')

flow.end_run()