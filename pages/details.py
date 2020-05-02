import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from utils import Header, make_dash_table, create_feature_imp_plot

import pandas as pd
import pathlib
import ast
import os

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../data").resolve()

dfrunmaster = pd.read_csv('../Artefacts/Overview/runmaster.csv')
projectname = dfrunmaster['ProjectName'].unique()[0]


def create_layout(app, ExpID, projectname=projectname):
    ### Read experiment specific learnings

    try:
        aim = dfrunmaster[dfrunmaster.ExpID==ExpID]['Description'].values[0]
        param = dfrunmaster[dfrunmaster.ExpID==ExpID]['Params'].values[0]
        param = ast.literal_eval(param)

        exppath = param['Artefacts']
        dffeatobs = pd.read_csv(f"{exppath}/observations.csv")
        
        if os.path.exists(f"{exppath}/importance.csv"):
            imp = pd.read_csv(f"{exppath}/importance.csv")
            imp.columns = [i.lower() for i in imp.columns]
            imp = imp.groupby('feature', as_index=False).agg({'importance':'sum'})
            imp['importance'] = imp['importance']/sum(imp['importance'])

            topfeatures = imp.sort_values(by='importance', ascending=False).head(10)
            topfeatures.sort_values(by='importance', ascending=True, inplace=True)
    except:
        return html.Div()

    return html.Div(
        [
            html.Div([Header(app, projectname)]),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6(f"Experiment{ExpID} : {aim}"),
                                ],
                                className="product",
                            )
                        ],
                        className="row",
                    ),
                    html.Div(
                        [                            
                            html.Div(
                                [
                                    html.H6(
                                        f"Top 10 Features",
                                        className="subtitle padded",
                                    ),
                                    create_feature_imp_plot(topfeatures, "graph-4", topfeatures['importance'], "<b>Importance : %{x:.02f}")
                                ],
                                className="seven columns",
                            ),
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
                        ],
                        className="row ",
                    ),
                ],
                className="sub_page",
            ),
        ],
        className="page",
    )
