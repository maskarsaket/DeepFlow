import ast
import os
import pathlib

import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from dash_table import DataTable

from utils import (Header, create_feature_imp_plot, create_journey_plot_line,
                   discrete_background_color_bins, make_unordered_list)

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../data").resolve()

f = open(DATA_PATH.joinpath("aim.txt"), "r")
aim = f.read()

dfrunmaster = pd.read_csv('../Artefacts/Overview/runmaster.csv')

metriccols = ['Score', 'ParentScore', 'ImprovementParent',
              'Benchmark', 'ImprovementBenchmark']
for col in metriccols:
    dfrunmaster[col] = dfrunmaster[col].apply(lambda x : round(x, 4))

# ### find series of changes used in best run
bestScore = min(dfrunmaster[(dfrunmaster.Metric=='Average RMSE')].Score)
bestexp = dfrunmaster[dfrunmaster.Score==bestScore]['ExpID'].values[0]
parent = dfrunmaster[dfrunmaster.Score==bestScore]['ParentID'].values[0]
bestruns = [bestexp]

while not np.isnan(parent):
    bestexp = dfrunmaster[dfrunmaster.ExpID==parent]['ExpID'].values[0]
    parent = dfrunmaster[dfrunmaster.ExpID==parent]['ParentID'].values[0]
    bestruns.append(bestexp)

dfrunmaster['Chosen'] = [1 if i in bestruns else 0 for i in dfrunmaster.ExpID]

projectname = dfrunmaster['ProjectName'].unique()[0]

### TODO : Sort values based on Acc/Error col in runmaster
topruns = dfrunmaster.sort_values(by='Score').head(5)
toprunparams = topruns['Params'].dropna()
topfeatures = pd.DataFrame()
featruns = 0

for _, param in toprunparams.iteritems():
    param = ast.literal_eval(param)
    if os.path.exists(f"{param['Artefacts']}/importance.csv"):
        featruns += 1
        imp = pd.read_csv(f"{param['Artefacts']}/importance.csv")
        imp.columns = [i.lower() for i in imp.columns]
        imp = imp.groupby('feature', as_index=False).agg({'importance':'sum'})
        imp['importance'] = imp['importance']/sum(imp['importance'])
        topfeatures = pd.concat([topfeatures, imp], axis=0)

if topfeatures.shape[0] != 0:
    topfeatures['count'] = 1
    topfeatures = topfeatures.groupby('feature', as_index=False).agg({'importance':sum, 'count':'sum'})
    topfeatures['importance'] = topfeatures['importance']/sum(topfeatures['importance'])
    topfeatures['importance'] = topfeatures['importance'].apply(lambda x : round(x, 2))
    topfeatures = topfeatures.sort_values(by='importance', ascending=False).head(10)
    topfeatures.sort_values(by='importance', ascending=True, inplace=True)


def new_first_page(app, title=projectname):
    return  html.Div(
                [
                    html.Div([Header(app, title)]),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6(f"Objective : {aim}",
                                        className="row",
                                    ),
                                ],
                                className="product",
                            ),
                            html.Div(
                                [
                                    html.H6("Success Criteria",
                                        className="row",
                                    ),
                                ],
                                className="product",
                            )
                        ],
                        className="sub_page",
                    )
                ],
                className="page"
            )

def journey_page(app, title=projectname):
    chosenChanges = dfrunmaster[dfrunmaster.Chosen==1]['Description'].values
    return  html.Div(
                [
                    html.Div([Header(app, title)]),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6(
                                        "Journey Plot",
                                        className="subtitle padded",
                                    ),
                                    create_journey_plot_line(dfrunmaster),
                                ],
                                className="seven columns",
                            ),
                            html.Div(
                                [
                                    html.H6(
                                        "Road to best model",
                                        className="subtitle padded",
                                    ),
                                    make_unordered_list(chosenChanges),
                                ],
                                className="five columns",
                            ),
                        ],
                        className="sub_page",
                    )
                ],
                className="page"
            )

def top_features_page(app, title=projectname):
        return  html.Div(
                [
                    html.Div([Header(app, title)]),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6(
                                        f"Top Features - across top {featruns} runs",
                                        className="subtitle padded",
                                    ),
                                    create_feature_imp_plot(
                                        topfeatures,
                                        "graph-1",
                                        topfeatures['count'],
                                        "<b>Importance : %{x}<br>" + "Count : %{text}"
                                    ),
                                ],
                                className="seven columns",
                            ),
                            html.Div(
                                [
                                    html.H6(
                                        "Observations",
                                        className="subtitle padded",
                                    ),
                                    html.Div(id='feature_observations'),
                                    html.Div(
                                        [
                                            dcc.Input(
                                                id='input_observation',
                                                type='text',
                                                placeholder='Enter new observations'
                                            ),
                                            html.Button(
                                                'Add',
                                                id='submit_observation',
                                                n_clicks=0
                                            )
                                        ],
                                        className="row"
                                    )
                                ],
                                className="five columns",
                            ),
                        ],
                        className="sub_page",
                    )
                ],
                className="page"
            )

def detailed_log_page(app, title=projectname):
    cols = [
        'ExpID', 'ParentID', 'Description', 'Status', 'Duration',
        'Metric', 'Score', 'ParentScore', 'ImprovementParent',
        'Benchmark', 'ImprovementBenchmark', 'Chosen'
    ]
    scorestyles, _ = discrete_background_color_bins(dfrunmaster, columns=['Score'])
    impParentstyles, _ = discrete_background_color_bins(dfrunmaster, columns=['ImprovementParent'])
    impBenchstyles, _ = discrete_background_color_bins(dfrunmaster, columns=['ImprovementBenchmark'])

    return  html.Div(
                [
                    html.Div([Header(app, title)]),
                    html.Div(
                        [
                            html.H6("Detailed Log of Experiments",
                                    className="subtitle padded",
                            ),
                            html.Br(),
                            html.Br(),
                            html.Br(),
                            DataTable(
                                id='detailed-log',
                                columns=[{"name":i, "id":i} for i in cols],
                                data=dfrunmaster[cols].to_dict('records'),
                                page_size=15,
                                style_cell_conditional=[
                                    {
                                        'if': {'column_id': c},
                                        'textAlign': ('left' if c in ['ExpID', 'ParentID', 'Description'] else 'center')
                                    } for c in cols
                                ],
                                style_data={'font-size' : '11px'},
                                style_header={'font-size' : '11px', 'font-weight' : 'bold'},
                                style_as_list_view=True,
                                sort_action="native",
                                sort_mode="multi",
                                filter_action="native",
                                style_data_conditional=[
                                    {
                                        'if': {
                                            'filter_query': '{Status} = "Completed"',
                                            'column_id' : 'Status'
                                        },
                                        'backgroundColor': '#228B22',
                                        'color': 'white'
                                    },
                                    {
                                        'if': {
                                            'filter_query': '{Status} = "Failed"',
                                            'column_id' : 'Status'
                                        },
                                        'backgroundColor': '#FF6347',
                                        'color': 'white'
                                    },
                                    {
                                        'if': {
                                            'filter_query': '{Status} = "Running"',
                                            'column_id' : 'Status'
                                        },
                                        'backgroundColor': '#FFFF66',
                                        'color': 'black'
                                    },
                                    {
                                        'if': {
                                            'filter_query': '{Chosen} = "1"',
                                            'column_id' : 'Chosen'
                                        },
                                        'backgroundColor': '#228B22',
                                        'color': 'white'
                                    },
                                    {
                                        'if': {
                                            'filter_query': '{Chosen} = "0"',
                                            'column_id' : 'Chosen'
                                        },
                                        'backgroundColor': '#FF6347',
                                        'color': 'white'
                                    }
                                ] + impParentstyles + scorestyles + impBenchstyles
                            )
                        ],
                        className="sub_page",
                    )
                ],
                className="page"
            )