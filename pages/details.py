import ast
import os
import pathlib

import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash_table import DataTable

from utils import Header, create_feature_imp_plot, make_dash_table

dfrunmaster = pd.read_csv('../Artefacts/Overview/runmaster.csv')
projectname = dfrunmaster['ProjectName'].unique()[0]


def create_layout(app, ExpID, projectname=projectname):
    ### Read experiment specific learnings

    try:
        aim = dfrunmaster[dfrunmaster.ExpID==ExpID]['Description'].values[0]
        param = dfrunmaster[dfrunmaster.ExpID==ExpID]['Params'].values[0]
        param = ast.literal_eval(param)

        exppath = param['Artefacts']
        if os.path.exists(f"{exppath}/observations.csv"):
            dffeatobs = pd.read_csv(f"{exppath}/observations.csv")
        else:
            dffeatobs = pd.DataFrame({'Observations' : []})
            dffeatobs.to_csv(f"{exppath}/observations.csv", index=False)

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
                                    create_feature_imp_plot(
                                        topfeatures,
                                        "graph-4",
                                        topfeatures['importance'],
                                        "<b>Importance : %{x:.02f}"
                                    )
                                ],
                                className="seven columns",
                            ),
                            html.Div(
                                [
                                    html.H6(
                                        "Observations from Features",
                                        className="subtitle padded",
                                    ),
                                    DataTable(
                                        id=f'feature_observations_exp{ExpID}',
                                        columns=[{"name":'Observations', "id":'Observations'}],
                                        data=dffeatobs.to_dict('records'),
                                        style_data={'font-size' : '11px'},
                                        style_header={'font-size' : '11px', 'font-weight' : 'bold'},
                                        style_as_list_view=True,
                                        editable=True,
                                        row_deletable=True
                                    ),
                                    html.Button('Add Row', id='editing-rows-button', n_clicks=0),
                                    html.Button(id="save-button",n_clicks=0,children="Save"),
                                    html.Div(id="output-1",children="Press button to save changes")
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
