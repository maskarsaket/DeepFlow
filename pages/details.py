import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from utils import Header, make_dash_table

import pandas as pd
import pathlib
import ast

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../data").resolve()

dfrunmaster = pd.read_csv(DATA_PATH.joinpath("runmaster.csv"))
projectname = dfrunmaster['ProjectName'].unique()[0]


def create_layout(app, projectname=projectname, ExpID=23):
    ### Read experiment specific learnings
    dfjourneypoints = pd.read_csv(DATA_PATH.joinpath("journeypoints.csv"))
    dffeatobs = pd.read_csv(DATA_PATH.joinpath("featureobservations.csv"))

    param = dfrunmaster[dfrunmaster.ExpID==ExpID]['Params'].values[0]
    param = ast.literal_eval(param)

    aim = dfrunmaster[dfrunmaster.ExpID==ExpID]['Description'].values[0]

    ### TODO : Sort values based on Acc/Error col in runmaster 
    if 'FeatureImp' in param:
        imp = pd.read_csv(param['FeatureImp'])
        imp.columns = [i.lower() for i in imp.columns]
        imp = imp.groupby('feature', as_index=False).agg({'importance':'sum'})
        imp['importance'] = imp['importance']/sum(imp['importance'])

        topfeatures = imp.sort_values(by='importance', ascending=False).head(10)
        topfeatures.sort_values(by='importance', ascending=True, inplace=True)

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
                                    html.H6(f"Experiment{ExpID} : "),
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
                                    dcc.Graph(
                                        id="graph-3",
                                        figure={
                                            "data": [
                                                go.Scatter(
                                                    x=dfrunmaster[dfrunmaster.ScoreType=='RMSE'].ExpID,
                                                    y=dfrunmaster[dfrunmaster.ScoreType=='RMSE'].Score,
                                                    # line={"color": "#97151c"},
                                                    mode="lines",
                                                    name="RMSE",
                                                ),
                                                go.Scatter(
                                                    x=dfrunmaster[dfrunmaster.ScoreType=='Average RMSE'].ExpID,
                                                    y=dfrunmaster[dfrunmaster.ScoreType=='Average RMSE'].Score,
                                                    # line={"color": "#97151c"},
                                                    mode="lines",
                                                    name="Average RMSE",
                                                ),                                                
                                            ],
                                            "layout": go.Layout(
                                                autosize=True,
                                                title="",
                                                font={"family": "Raleway", "size": 10},
                                                height=200,
                                                width=340,
                                                hovermode="closest",
                                                legend={
                                                    "x": -0.0277108433735,
                                                    "y": -0.142606516291,
                                                    "orientation": "h",
                                                },
                                                margin={
                                                    "r": 20,
                                                    "t": 20,
                                                    "b": 20,
                                                    "l": 50,
                                                },
                                                showlegend=True,
                                                xaxis={
                                                    "autorange": True,
                                                    "linecolor": "rgb(0, 0, 0)",
                                                    "linewidth": 1,
                                                    "showgrid": False,
                                                    "showline": True,
                                                    "title": "",
                                                    "type": "linear",
                                                },
                                                yaxis={
                                                    "autorange": True,
                                                    "gridcolor": "rgba(127, 127, 127, 0.2)",
                                                    "mirror": False,
                                                    "nticks": 4,
                                                    "showgrid": True,
                                                    "showline": True,
                                                    "ticklen": 10,
                                                    "ticks": "outside",
                                                    "title": "Score",
                                                    "type": "linear",
                                                    "zeroline": False,
                                                    "zerolinewidth": 4,
                                                },
                                            ),
                                        },
                                        config={"displayModeBar": False},
                                    ),                                    
                                ],
                                className="six columns",
                            ),
                            html.Div(
                                [
                                    html.H6(
                                        ["Key Points in the Journey"], className="subtitle padded"
                                    ),
                                    html.Table(make_dash_table(dfjourneypoints)),
                                ],
                                className="six columns",
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
                                className="six columns",
                            ),                            
                            html.Div(
                                [
                                    html.H6(
                                        f"Top 10 Features",
                                        className="subtitle padded",
                                    ),
                                    dcc.Graph(
                                        id="graph-4",
                                        figure={
                                            "data": [
                                                go.Bar(
                                                    y=topfeatures['feature'],
                                                    x=topfeatures['importance'],
                                                    marker={
                                                        # "color": "#97151c",
                                                        "line": {
                                                            "color": "rgb(255, 255, 255)",
                                                            "width": 2,
                                                        },
                                                    },
                                                    orientation='h',
                                                    name="Importance",
                                                ),
                                            ],
                                            "layout": go.Layout(
                                                autosize=True,
                                                bargap=0.35,
                                                font={"family": "Raleway", "size": 10},
                                                height=300,
                                                hovermode="closest",
                                                # legend={
                                                #     "y": -0.0228945952895,
                                                #     "x": -0.189563896463,
                                                #     "orientation": "h",
                                                #     "yanchor": "top",
                                                # },
                                                margin={
                                                    "r": 0,
                                                    "t": 20,
                                                    "b": 30,
                                                    "l": 120,
                                                },
                                                showlegend=False,
                                                title="",
                                                # width=330,
                                                yaxis={
                                                    "autorange": True,
                                                    # "range": [-0.5, 4.5],
                                                    "showline": True,
                                                    "title": "",
                                                    "type": "category",
                                                },
                                                xaxis={
                                                    "autorange": True,
                                                    # "range": [0, 0.5],
                                                    "showgrid": True,
                                                    "showline": True,
                                                    "title": "",
                                                    "type": "linear",
                                                    "zeroline": False,
                                                },
                                            ),
                                        },
                                        config={"displayModeBar": False},
                                    ),
                                ],
                                className="six columns",
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
