import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import plotly.express as px


def Header(app, projectname):
    return html.Div([get_header(app, projectname), html.Br([]), get_menu()])


def get_header(app, projectname):
    header = html.Div(
        [
            html.Div(
                [
                    html.Br(),
                    html.Br(),
                    html.Br(),                    
                    # html.A(
                    #     html.Button("Learn More", id="learn-more-button"),
                    #     href="https://plot.ly/dash/pricing/",
                    # ),
                ],
                className="row",
            ),
            html.Div(
                [
                    html.Div(
                        [html.H5(projectname)], 
                        className="seven columns main-title",
                    ),
                    html.Div(
                        [
                            dcc.Link(
                                "Full View",
                                href="/dash-financial-report/full-view",
                                className="full-view-link",
                            )
                        ],
                        className="five columns",
                    ),
                ],
                className="twelve columns",
                style={"padding-left": "0"},
            ),
        ],
        className="row",
    )
    return header


def get_menu():
    menu = html.Div(
        [
            dcc.Link(
                "Overview",
                href="/deepflow/overview",
                className="tab first",
            ),
            dcc.Link(
                "Details",
                href="/deepflow/details",
                className="tab",
            )
        ],
        className="row all-tabs",
    )
    return menu


def make_dash_table(df):
    """ Return a dash definition of an HTML table for a Pandas dataframe """
    table = []
    for index, row in df.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append(html.Td([row[i]]))
        table.append(html.Tr(html_row))
    return table

def create_feature_imp_plot(df, graphid, text, hovertemplate="Count : %{text}"):
    return  dcc.Graph(
                id=graphid,
                figure={
                    "data": [
                        go.Bar(
                            y=df['feature'],
                            x=df['importance'],
                            marker={
                                "line": {
                                    "color": "rgb(255, 255, 255)",
                                    "width": 2,
                                },
                            },
                            orientation='h',
                            name="",
                            text=text,#df['count'],
                            hovertemplate=hovertemplate
                        ),
                    ],
                    "layout": go.Layout(
                        autosize=True,
                        bargap=0.35,
                        font={"family": "Raleway", "size": 10},
                        height=300,
                        hovermode="y",
                        hoverlabel={"font_family": "Raleway", "font_size": 10},
                        margin={
                            "r": 0,
                            "t": 20,
                            "b": 30,
                            "l": 120,
                        },
                        showlegend=False,
                        title="",
                        yaxis={
                            "autorange": True,
                            "showline": True,
                            "title": "",
                            "type": "category",
                        },
                        xaxis={
                            "autorange": True,
                            "showgrid": True,
                            "showline": True,
                            "title": "",
                            "type": "linear",
                            "zeroline": False,
                        },
                    ),
                },
                config={"displayModeBar": False},
            )

def create_journey_plot(dfrunmaster):
    return dcc.Graph(
            id="graph-2",
            figure={
                "data": [
                    go.Scatter(
                        x=dfrunmaster[dfrunmaster.Chosen==1]['ExpID'],
                        y=dfrunmaster[dfrunmaster.Chosen==1]['Score'],
                        text=dfrunmaster[dfrunmaster.Chosen==1]['Description'],
                        mode="lines+markers",
                        name="Chosen",
                        hovertemplate= "Exp%{x}<br>%{text}<br>" + "Score : %{y}"
                    ),
                    go.Scatter(
                        x=dfrunmaster[dfrunmaster.Chosen==0]['ExpID'],
                        y=dfrunmaster[dfrunmaster.Chosen==0]['Score'],
                        text=dfrunmaster[dfrunmaster.Chosen==0]['Description'],
                        mode="markers",
                        name="Not Chosen",
                        hovertemplate= "Exp%{x}<br>%{text}<br>" + "Score : %{y}"
                    ),
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
        )

def create_journey_plot_new(dfrunmaster):
    fig = px.line(
            data_frame=dfrunmaster[dfrunmaster.Chosen==1],
            x="ExpID",
            y="Score", 
            color="ScoreType",
            hover_data = ["Description"]            
        )
    
    fig.add_trace(
        go.Scatter(
            x=dfrunmaster[dfrunmaster.Chosen==0]['ExpID'],
            y=dfrunmaster[dfrunmaster.Chosen==0]['Score'],
            text=dfrunmaster[dfrunmaster.Chosen==0]['Description'],
            mode="markers",
            name="Not Chosen",
            hovertemplate= "Exp%{x}<br>%{text}<br>" + "Score : %{y}"
        )
    )

    fig.update_layout(
        go.Layout(
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
            )
    )

    return dcc.Graph(
            id="graph-2",
            figure=fig,
            config={"displayModeBar": False},
        )

def create_journey_plot_line(dfrunmaster):
    return dcc.Graph(
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
        )
