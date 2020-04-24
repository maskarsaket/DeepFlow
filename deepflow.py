import pandas as pd
import numpy as np
import os
from datetime import datetime

class DeepFlow():
    """ 
    A library which helps store the details of all the experiments performed 
    and take a look at the journey made so far

    Attributes:
        projectname (str)   : name of the project (will be shown on the dashboard)
        runmasterfile (str) : path/filename.csv of the master run file, new file will 
                                will be created if specified file does not exist
        parentID (int)      : ID of parent experiment from which changes are being made
        description (str)   : a short description of changes made
        benchmark (float)   : the benchmark score you are trying to beat
        params (dict)       : a dictionary of params to be saved and shown on the dashboard
    """
    def __init__(self, projectname, runmasterfile, **kwargs):
        self.projectname = projectname
        self.runmasterfile = runmasterfile
        
        if os.path.exists(runmasterfile):
            self.dfrunmaster = pd.read_csv(runmasterfile)
            expID = max(self.dfrunmaster.ExpID) + 1
            if 'parentID' not in kwargs:
                raise AssertionError("Please prove a parent expID")
            parentID = kwargs['parentID']
        else:
            print(f"Starting your first experiment for {projectname}? , Best of Luck \U0001f600")
            self.dfrunmaster = pd.DataFrame()
            expID = 1
            parentID = np.NaN

        self.runmastercols = [
            'StartTime', 'EndTime', 'Duration', 'ParentID', 
            'ExpID', 'Description', 'Score', 'ScoreType',
            'ParentScore', 'ImprovementParent', 'Benchmark',
            'ImprovementBenchmark', 'FeatureImp', 'params'
        ]

    def start_run(self):
        self.starttime = datetime.now()

    def end_run(self):
        endtime = datetime.now()
        duration = endtime - self.starttime
        ### save runmaster file

    def log_score(self, scoretype, score):
        """
        logs the Score of the experiment

        Parameters:
            scoretype (str) : type of score eg. 'RMSE','SWMAPE', 'MAPE' 
        """
        raise NotImplementedError

    def log_imp(self, importance, path):
        """
        saves the feature importance daframe into the given path

        Parameters:
            importance (pandas.Dataframe) : feature importance dataframe with 
                                            columns 'Feature' and 'Importance' 
            path (str) : path/filename.csv where importance dataframe will be saved
                         this path will be used to read the file and show importance
                         plot in the dashboard
        """
        raise NotImplementedError