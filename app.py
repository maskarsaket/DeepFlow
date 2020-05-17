# -*- coding: utf-8 -*-
import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
from dash_table import DataTable

from pages import details, overview
from utils import make_unordered_list

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# Describe the layout/ UI of the app
app.layout = html.Div([
        overview.new_first_page(app),
        overview.journey_page(app),
        overview.top_features_page(app),
        overview.detailed_log_page(app),
        details.create_layout(app, 21)
        # tuple(details.create_layout(app, i) for i in range(50))
    ]
)

# # Update feature observations
@app.callback(Output("feature_observations", "children"),
              [Input("submit_observation", "n_clicks")],
              [State('input_observation', 'value')])
def update_observations(n_clicks, value):
    observations = pd.read_csv('../Artefacts/Overview/observations.csv')
    if n_clicks > 0:
        newobservation = pd.DataFrame({'Observations':[value]})
        observations = pd.concat([observations, newobservation], axis=0)
        observations.to_csv('../Artefacts/Overview/observations.csv', index=False)
    return make_unordered_list(observations['Observations'].values)

@app.callback(
    Output('feature_observations_exp21', 'data'),
    [Input('editing-rows-button', 'n_clicks')],
    [State('feature_observations_exp21', 'data'),
     State('feature_observations_exp21', 'columns')])
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

@app.callback(
        Output("output-1","children"),
        [Input("save-button","n_clicks")],
        [State("feature_observations_exp21","data")]
        )

def selected_data_to_csv(nclicks,table1):
    exppath = '/home/maskarasaket/Documents/kaggle/pred_future_sales/Code/../Artefacts/exp_27'
    if nclicks == 0:
        pass
    else:
        pd.DataFrame(table1).to_csv(f"{exppath}/observations.csv", index=False)
        return f"Data Saved{nclicks}"


if __name__ == "__main__":
    app.run_server(debug=True)
