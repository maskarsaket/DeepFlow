import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import plotly.express as px


def Header(app, projectname):
    return html.Div([get_header(app, projectname)])


def get_header(app, projectname):
    header = html.Div(
        [
            html.Div(
                [
                    html.Br(),
                    html.Br(),
                    html.Br()
                ],
                className="row",
            ),
            html.Div(
                [
                    html.Div(
                        [html.H5(projectname)],
                        className="seven columns main-title",
                    ),
                    # html.Div(
                    #     [html.H6("Add best score here")],
                    #     className="five columns",
                    # ),
                ],
                className="twelve columns",
                style={"padding-left": "0"},
            ),
        ],
        className="row",
    )
    return header


def make_dash_table(df):
    """ Return a dash definition of an HTML table for a Pandas dataframe """
    table = []
    for index, row in df.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append(html.Td([row[i]]))
        table.append(html.Tr(html_row))
    return table

def make_unordered_list(arr):
    """ Return a dash definition of a bulleted list of an array """
    return html.Div(
        html.Ul([html.Li(x) for x in arr]),
        className="padded"
    )

def create_feature_imp_plot(df, graphid, text, hovertemplate="Count : %{text}"):
    return  dcc.Graph(
                # id=graphid,
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
                        font={"family": "Raleway", "size": 14},
                        height=400,
                        hovermode="y",
                        hoverlabel={"font_family": "Raleway", "font_size": 14},
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

def create_journey_plot_line(dfrunmaster):
    figure = go.Figure()

    ### Add traces for scores
    for metric in dfrunmaster.Metric.unique():
        figure.add_traces([
            go.Scatter(
                x=dfrunmaster[dfrunmaster.Metric==metric]['ExpID'],
                y=dfrunmaster[dfrunmaster.Metric==metric]['Score'],
                text=dfrunmaster[dfrunmaster.Metric==metric]['Description'],
                mode="lines+markers",
                name=metric,
                hovertemplate= "%{text}<br>" + "<b>Score : <b>%{y}<br>"
            )
        ])

    ### Add trace for benchmark
    figure.add_traces([
        go.Scatter(
            x=dfrunmaster['ExpID'],
            y=dfrunmaster['Benchmark'],
            line={'dash':'dash'},
            name="Benchmark",
            hovertemplate="Benchmark %{y}"
        )
    ])

    figure.update_layout(
        go.Layout(
            autosize=True,
            title="",
            font={"family": "Raleway", "size": 14},
            height=320,
            # width=340,
            hovermode="x",
            hoverlabel={"font_family": "Raleway", "font_size": 14},
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
            }
        ),
        overwrite=True
    )

    return dcc.Graph(
            id="graph-2",
            figure=figure,
            config={"displayModeBar": False},
        )

def discrete_background_color_bins(df, n_bins=5, columns='all'):
    import colorlover
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    if columns == 'all':
        if 'id' in df:
            df_numeric_columns = df.select_dtypes('number').drop(['id'], axis=1)
        else:
            df_numeric_columns = df.select_dtypes('number')
    else:
        df_numeric_columns = df[columns]
    df_max = df_numeric_columns.max().max()
    df_min = df_numeric_columns.min().min()
    ranges = [
        ((df_max - df_min) * i) + df_min
        for i in bounds
    ]
    styles = []
    legend = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        backgroundColor = colorlover.scales[str(n_bins)]['seq']['Blues'][i - 1]
        color = 'white' if i > len(bounds) / 2. else 'inherit'

        for column in df_numeric_columns:
            styles.append({
                'if': {
                    'filter_query': (
                        '{{{column}}} >= {min_bound}' +
                        (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                    ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                    'column_id': column
                },
                'backgroundColor': backgroundColor,
                'color': color
            })
        legend.append(
            html.Div(style={'display': 'inline-block', 'width': '60px'}, children=[
                html.Div(
                    style={
                        'backgroundColor': backgroundColor,
                        'borderLeft': '1px rgb(50, 50, 50) solid',
                        'height': '10px'
                    }
                ),
                html.Small(round(min_bound, 2), style={'paddingLeft': '2px'})
            ])
        )

    return (styles, html.Div(legend, style={'padding': '5px 0 5px 0'}))