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

    runmasterfile (str) : (Required) path/filename.csv of the master run file, new file
        will be created if specified file does not exist

    parentID (int)      : ID of parent experiment from which changes are being made,
        Considered a run from scratch if no parentID provided
    
    description (str)   : (Required) a short description of changes made
    
    benchmark (float)   : (Optional) the benchmark score you are trying to beat
    
    params (dict)       : (Optional) a dictionary of params to be saved and shown on the dashboard
    """
    def __init__(self, **kwargs):
        if 'projectname' not in kwargs:
            raise AssertionError("Missing required parameter projectname")

        if 'runmasterfile' not in kwargs:
            raise AssertionError("Missing required parameter runmasterfile")    
        self.runmasterfile = kwargs['runmasterfile']

        if 'description' not in kwargs:
            raise AssertionError("Missing required parameter description")

        self.runmastercols = [
            'ProjectName', 'ExpID', 'ParentID', 'Description',
            'StartTime', 'EndTime', 'Duration', 'ScoreType', 'Metric',
            'Score', 'ParentScore', 'ImprovementParent', 'Benchmark',
            'ImprovementBenchmark', 'Params'
        ] 

        self.dfcurrentrun = pd.DataFrame({
            'ProjectName' : [kwargs['projectname']],
            'StartTime' : [datetime.now()],
            'Description' : [kwargs['description']]
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
            print(f"Starting your first experiment for {kwargs['projectname']}? , Best of Luck \U0001f600")
            self.dfrunmaster = pd.DataFrame()
            self.dfcurrentrun['ExpID'] = 1
            self.dfcurrentrun['ParentID'] = np.NaN
            self.dfcurrentrun['ParentScore'] = np.NaN

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

    def log_imp(self, importance, path):
        """
        saves the feature importance daframe into the given path

        Parameters:
            importance (pandas.Dataframe) : feature importance dataframe with 
                                            columns 'Feature' and 'Importance' 
            path (str) : path where importance dataframe will be saved
                         this path will be used to read the file and show importance
                         plot in the dashboard
            the importances will be stored as a csv in path/impartance.csv
            the code creates the path if it does not exist
        """
        if not os.path.exists(path):
            os.makedirs(path)

        path = os.path.join(os.getcwd(), path, 'importance.csv')
        self.params['FeatureImp'] = path

        print(f"Importance file saved in dir : {path}")

        importance.to_csv(path, index=False)

    def log_param(self, param, value):
        """
        adds a param to the params dictionary saved in the run master 
        """
        self.params[param] = value
