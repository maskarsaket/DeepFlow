import json
import os
from datetime import datetime

import numpy as np
import pandas as pd


class DeepFlow():
    """ 
    A library which helps store the details of all the experiments performed 
    and take a look at the journey made so far

    Attributes
    ----------
    projectname (str)   : (Required) name of the project (will be shown on the dashboard)
        
    description (str)   : (Required) a short description of changes made

    parentID (int)      : ID of parent experiment from which changes are being made,
        Considered a run from scratch if no parentID provided
    
    benchmark (float)   : (Optional) the benchmark score you are trying to beat
    
    params (dict)       : (Optional) a dictionary of params to be saved and shown on the dashboard
    """
    def __init__(self, projectname, description, **kwargs):

        self.runmasterfile = os.path.join(os.getcwd(), "Artefacts/Overview/runmaster.csv")

        self.runmastercols = [
            'ProjectName', 'ExpID', 'ParentID', 'Description',
            'StartTime', 'EndTime', 'Duration', 'ScoreType', 'Metric',
            'Score', 'ParentScore', 'ImprovementParent', 'Benchmark',
            'ImprovementBenchmark', 'Params'
        ] 

        self.dfcurrentrun = pd.DataFrame({
            'ProjectName' : [projectname],
            'StartTime' : [datetime.now()],
            'Description' : [description]
        })
        
        if os.path.exists(self.runmasterfile):
            self.dfrunmaster = pd.read_csv(self.runmasterfile)
            self.dfcurrentrun['ExpID'] = max(self.dfrunmaster.ExpID) + 1
            if 'parentID' not in kwargs:
                raise AssertionError("Please prove a parent expID")
            if int(kwargs['parentID']) not in self.dfrunmaster['ExpID'].values:
                raise AssertionError("Parent ID not found in existing experiments")
            self.dfcurrentrun['ParentID'] = kwargs['parentID']
            self.dfcurrentrun['ParentScore'] = self.dfrunmaster.Score[self.dfrunmaster.ExpID == kwargs['parentID']].values[0]
        else:
            print(f"Starting your first experiment for {projectname}? , Best of Luck \U0001f600")
            self.dfrunmaster = pd.DataFrame()
            self.dfcurrentrun['ExpID'] = 1
            self.dfcurrentrun['ParentID'] = np.NaN
            self.dfcurrentrun['ParentScore'] = np.NaN
            overviewpath = os.path.join(os.getcwd(), "Artefacts/Overview")
            if not os.path.exists(overviewpath):
                os.makedirs(overviewpath)
            #### Create blank Learnings and Observations files
            learnings = pd.DataFrame({
                'Learnings' : []
            })
            learnings.to_csv(f"{overviewpath}/learnings.csv", index=False)
            
            observations = pd.DataFrame({
                'Observations' : []
            })
            observations.to_csv(f"{overviewpath}/observations.csv", index=False)
        
        self.artefactpath = os.path.join(os.getcwd(), "Artefacts/", f"exp_{self.dfcurrentrun['ExpID'].values[0]} - {description}")
        if not os.path.exists(self.artefactpath):
            os.makedirs(self.artefactpath)
        
        observations = pd.DataFrame({
            'Observations' : []
        })

        observations.to_csv(f"{self.artefactpath}/observations.csv", index=False)

        if 'benchmark' in kwargs:
            self.dfcurrentrun['Benchmark'] = kwargs['benchmark']
        else:
            self.dfcurrentrun['Benchmark'] = np.NaN

        if 'params' in kwargs:
            self.params = kwargs['params'] 
        else:
            self.params = dict()

    def end_run(self):
        self.dfcurrentrun['EndTime'] = datetime.now()
        self.dfcurrentrun['Duration'] = self.dfcurrentrun['EndTime'] - self.dfcurrentrun['StartTime']

        for key in self.params:
            self.params[key] = str(self.params[key])

        self.dfcurrentrun['Params'] = json.dumps(self.params)

        for col in ['StartTime', 'EndTime', 'Duration']:
            self.dfcurrentrun[col] = self.dfcurrentrun[col].apply(lambda x : str(x)[:-7])
        
        self.dfrunmaster = pd.concat([self.dfrunmaster, self.dfcurrentrun], axis=0)
        self.dfrunmaster = self.dfrunmaster[self.runmastercols]

        self.dfrunmaster.to_csv(self.runmasterfile, index=False)

        print("\nAll Done : Please make sure to keep the observations and learnings artefacts updated")

    def log_score(self, scoretype, metric, score, decimals=2):
        """
        logs the Score of the experiment

        Parameters
        ----------
            scoretype (str) : type of score eg. 'Error' or 'Accuracy'
            metric (str)    : metric used to measure score eg. 'RMSE', 'SWMAPE', 'MAE', etc
            score (float)   : score of the model
            decimals (int)  : number of decimal places for score
        """
        if scoretype.lower() not in ('error', 'accuracy'):
            raise AssertionError(f"Expected 'Error' or 'Accuracy' for metric, '{scoretype}' was passed")

        bench = self.dfcurrentrun['Benchmark'].values[0]
        improveparent = round(score - self.dfcurrentrun['ParentScore'].values[0], decimals)
        improvebench = round(score - bench, decimals)

        self.dfcurrentrun['ScoreType'] = scoretype.lower()
        self.dfcurrentrun['Metric'] = metric.upper()
        self.dfcurrentrun['Score'] = round(score, decimals)
        self.dfcurrentrun['ImprovementParent'] = improveparent
        self.dfcurrentrun['ImprovementBenchmark'] = improvebench

    def log_artefact(self, artefact, name):
        """
        Saves any artefact dataframe into Artefacts/exp_num folder as a csv, eg: feature importance,
        helps in maintaining a clean folder structure for the project

        Parameters:
        -----------
            artefact (pandas.Dataframe) : the dataframe to be saved, when saving feature importance, 
            colnames should include 'Feature' and 'Importance'
            name (str) : 'importance' when saving importance, custom name when storing anything else
        """
        self.params['Artefacts'] = self.artefactpath
        
        print(f"Saving artefact in dir : {self.artefactpath}/{name}.csv")

        artefact.to_csv(f"{self.artefactpath}/{name}.csv", index=False)

    def log_param(self, param, value):
        """
        adds a param to the params dictionary saved in the run master 
        """
        self.params[param] = value
