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

        self.status = "Running"

        self.runmasterfile = os.path.join(os.getcwd(), "Artefacts/Overview/runmaster.csv")

        self.runmastercols = [
            'ProjectName', 'ExpID', 'ParentID', 'Description',
            'StartTime', 'EndTime', 'Duration', 'ScoreType', 'Metric',
            'Score', 'ParentScore', 'ImprovementParent', 'Benchmark',
            'ImprovementBenchmark', 'Status', 'Params'
        ]

        self.dfcurrentrun = pd.DataFrame(columns=self.runmastercols)

        self.dfcurrentrun['ProjectName'] = [projectname]
        self.dfcurrentrun['StartTime'] = datetime.now()
        self.dfcurrentrun['Description'] = description
        self.dfcurrentrun['Status'] = self.status

        if os.path.exists(self.runmasterfile):
            self.dfrunmaster = pd.read_csv(self.runmasterfile)

            if description.lower() in self.dfrunmaster['Description'].str.lower().values:
                raise AssertionError("Experiment Description must be unique")

            self.dfcurrentrun['ExpID'] = max(self.dfrunmaster.ExpID) + 1

            if 'parentID' not in kwargs:
                raise AssertionError("Please provide a parent expID")

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

        self.logcols = [
            'ExpID', 'Description', 'Status', 'LogMessage', 'ErrorMessage',
            'StartTime', 'LogTime', 'DurationSinceLog', 'DurationSinceStart'
        ]
        self.dflogs = pd.DataFrame(columns = self.logcols)
        self.logfile = f"{self.artefactpath}/logs.csv"
        self.dflogs = pd.concat([self.dflogs, self.dfcurrentrun], axis=0)
        self.dflogs['Status'] = 'Started'
        self.dflogs = self.dflogs[self.logcols]
        self.dflogs['LogTime'] = datetime.now()
        logsavefile = self.dflogs.copy()
        for col in ['StartTime', 'LogTime']:
            logsavefile[col] = logsavefile[col].apply(lambda x : str(x)[:-7])
        logsavefile.to_csv(self.logfile, index=False)
        self._saverunmaster()

    def log_status(self, status="Running", logmessage="", errormessage=""):
        """
        Updates logs.csv in the artefacts folder, calls end_run() if status="Failed"

        Parameters
        ----------
            status(str)     : Overall status of the run ("Running", "Failed", "Completed").
            logmessage(str) : Custom log message
                eg : 'Starting feature engineering', 'Completed feature engineering'
            errormessage    : call this fuction with status="Failed" while catching exceptions and
                pass the caught exception message in this parameter
        """
        if status not in ('Running', 'Failed', 'Completed'):
            raise AssertionError(f"Status should be 'Running', 'Failed' or 'Completed', {status} was passed")
        self.status = status
        logtime = datetime.now()
        newlog = self.dflogs.tail(1).copy()
        newlog['Status'] = status
        newlog['LogMessage'] = logmessage
        newlog['ErrorMessage'] = errormessage
        newlog['DurationSinceLog'] = logtime - newlog['LogTime']
        newlog['DurationSinceStart'] = logtime - newlog['StartTime']
        newlog['LogTime'] = logtime

        self.dflogs = pd.concat([self.dflogs, newlog], axis=0)
        self.dflogs = self.dflogs[self.logcols]

        logsavefile = self.dflogs.copy()
        for col in ['StartTime', 'LogTime', 'DurationSinceLog', 'DurationSinceStart']:
            logsavefile[col] = logsavefile[col].apply(lambda x : str(x)[:-7])
        logsavefile.to_csv(self.logfile, index=False)

        self.dfcurrentrun['Status'] = status
        self._saverunmaster()

        if status in ("Completed", "Failed"):
            self._end_run()

    def _saverunmaster(self):
        """
        Helper function which saves the runmaster file with the current status of the run
        """
        params = self.params.copy()
        for key in params:
            params[key] = str(params[key])

        self.dfcurrentrun['Params'] = json.dumps(params)
        runmastersavefile = self.dfrunmaster.copy()
        runmastersavefile = pd.concat([runmastersavefile, self.dfcurrentrun], axis=0)
        for col in ['StartTime', 'EndTime', 'Duration']:
            runmastersavefile[col] = ["" if pd.isna(i) else str(i).split('.')[0]
                for i in runmastersavefile[col]]

        runmastersavefile = runmastersavefile[self.runmastercols]

        runmastersavefile.to_csv(self.runmasterfile, index=False)

    def _end_run(self):
        """
        Helper function to end the run incase the run fails or completes successfully.
        This function updates the EndTime, Duration and Params
        and saves runmaster.csv file.
        """

        self.dfcurrentrun['EndTime'] = datetime.now()
        self.dfcurrentrun['Duration'] = self.dfcurrentrun['EndTime'] - self.dfcurrentrun['StartTime']

        self._saverunmaster()

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

        Parameters
        ----------
            param(str)                               : This defines which parameter is being stored
            value(any inbuilt python data structure) : The value of the parameter
        """
        self.params[param] = value
