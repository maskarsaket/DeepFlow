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

f = open(DATA_PATH.joinpath("aim.txt"), "r")
aim = f.read()

dfrunmaster = pd.read_csv(DATA_PATH.joinpath("runmaster.csv"))
dfjourneypoints = pd.read_csv(DATA_PATH.joinpath("journeypoints.csv"))
dffeatobs = pd.read_csv(DATA_PATH.joinpath("featureobservations.csv"))

projectname = dfrunmaster['ProjectName'].unique()[0]

### TODO : Sort values based on Acc/Error col in runmaster 
topruns = dfrunmaster[dfrunmaster.ScoreType=='Average RMSE'].sort_values(by='Score').head(5)
toprunparams = topruns['Params'].dropna()
topfeatures = pd.DataFrame()
featruns = 0

for _, param in toprunparams.iteritems():
    param = ast.literal_eval(param)
    if 'FeatureImp' in param:
        featruns += 1
        imp = pd.read_csv(param['FeatureImp'])
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
                                    dcc.Graph(
                                        id="graph-2",
                                        figure={
                                            "data": [
                                                dict(
                                                    x=dfrunmaster[dfrunmaster.ScoreType==i]['ExpID'],
                                                    y=dfrunmaster[dfrunmaster.ScoreType==i]['Score'],
                                                    text=dfrunmaster[dfrunmaster.ScoreType==i]['Description'],
                                                    mode="line",
                                                    name=i,
                                                    hovertemplate= "%{text}<br>" + "<b>Score : <b>%{y}<br>"
                                                ) for i in dfrunmaster.ScoreType.unique()
                                            ],
                                            "layout": go.Layout(
                                                autosize=True,
                                                title="",
                                                font={"family": "Raleway", "size": 10},
                                                height=250,
                                                # width=340,
                                                hovermode="closest",
                                                hoverlabel={"font_family": "Raleway", "font_size": 10},
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
                                                    # "type": "linear",
                                                    "zeroline" : False
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
                                    dcc.Graph(
                                        id="graph-1",
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
                                                    name="",
                                                    text=topfeatures['count'],
                                                    hovertemplate="<b>Importance : %{x}<br>" + "Count : %{text}"
                                                ),
                                            ],
                                            "layout": go.Layout(
                                                autosize=True,
                                                bargap=0.35,
                                                font={"family": "Raleway", "size": 10},
                                                height=300,
                                                hovermode="y",
                                                hoverlabel={"font_family": "Raleway", "font_size": 10},
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
