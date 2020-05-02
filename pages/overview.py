import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from utils import Header, make_dash_table, create_feature_imp_plot, create_journey_plot_line

import pandas as pd
import numpy as np
import pathlib
import ast
import os

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../data").resolve()

f = open(DATA_PATH.joinpath("aim.txt"), "r")
aim = f.read()

dfrunmaster = pd.read_csv('../Artefacts/Overview/runmaster.csv')
dfjourneypoints = pd.read_csv('../Artefacts/Overview/learnings.csv')
dffeatobs = pd.read_csv('../Artefacts/Overview/observations.csv')

# ### find series of changes used in best run
# bestexp = dfrunmaster[(dfrunmaster.Score==min(dfrunmaster[(dfrunmaster.ScoreType=='Average RMSE')].Score))]['ExpID'].values[0]
# parent = dfrunmaster[(dfrunmaster.Score==min(dfrunmaster[(dfrunmaster.ScoreType=='Average RMSE')].Score))]['ParentID'].values[0]
# bestruns = [bestexp]

# while not np.isnan(parent):
#     bestexp = dfrunmaster[dfrunmaster.ExpID==parent]['ExpID'].values[0]
#     parent = dfrunmaster[dfrunmaster.ExpID==parent]['ParentID'].values[0]
#     bestruns.append(bestexp)

# dfrunmaster['Chosen'] = [1 if i in bestruns else 0 for i in dfrunmaster.ExpID]

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


def create_layout(app,projectname=projectname):
    # Page layouts
    return html.Div(
        [
            html.Div([Header(app, projectname)]),
            # page 1
            html.Div(
                [
                    # Row 3
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6("Objective : "),
                                    html.Br([]),
                                    html.P(aim,
                                        style={"color": "#ffffff"},
                                        className="row",
                                    ),
                                ],
                                className="product",
                            )
                        ],
                        className="row",
                    ),
                    # Row 4
                    html.Div(
                        [html.Div(
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
                                        ["Key Points in the Journey"], className="subtitle padded"
                                    ),
                                    html.Table(make_dash_table(dfjourneypoints)),
                                ],
                                className="five columns",
                            ),
                        ],
                        className="row",
                        style={"margin-bottom": "35px"},
                    ),
                    # Row 5
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6(
                                        "Observations from Features",
                                        className="subtitle padded",
                                    ),
                                    html.Table(make_dash_table(dffeatobs)),
                                ],
                                className="five columns",
                            ),                            
                            html.Div(
                                [
                                    html.H6(
                                        f"Top Features - across top {featruns} runs",
                                        className="subtitle padded",
                                    ),
                                    create_feature_imp_plot(topfeatures, "graph-1", topfeatures['count'], "<b>Importance : %{x}<br>" + "Count : %{text}"),
                                ],
                                className="seven columns",
                            ),
                        ],
                        className="row ",
                    ),
                ],
                className="sub_page",
            ),
        ],
        className="page",
    )
