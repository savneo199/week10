from dash import html, dcc, Dash, dash_table, Input, Output
import dash_bootstrap_components as dbc
from paralympic_app.paralympic_dash_app import create_charts as cc


fig_line_sports = cc.line_chart_sports()
fig_sb_gender_winter = cc.stacked_bar_gender("Winter")
fig_sb_gender_summer = cc.stacked_bar_gender("Summer")
fig_scatter_mapbox = cc.scatter_mapbox_para_locations("OSM")
df_medals_data = cc.top_ten_gold_data()
df_medals = cc.get_medals_table_data("London", 2012)
fig_cp_map_medals = cc.choropleth_mapbox_medals(df_medals)


def create_dash_app(flask_app):
    """Creates Dash as a route in Flask

    :param flask_app: A confired Flask app
    :return dash_app: A configured Dash app registered to the Flask app
    """
    # Register the Dash app to a route '/dashboard/' on a Flask app
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname="/dashboard/",
        meta_tags=[
            {
                "name": "viewport",
                "content": "width=device-width, initial-scale=1",
            }
        ],
        external_stylesheets=[dbc.themes.BOOTSTRAP],
    )

    dash_app.layout = dbc.Container(
        [
            html.H1("Paralympic History"),
            html.H2(
                "Has the number of athletes, nations, events and sports changed over time?"
            ),
            html.Div(
                children=dcc.Dropdown(
                    id="type-dropdown",
                    options=[
                        {"label": "Events", "value": "EVENTS"},
                        {"label": "Sports", "value": "SPORTS"},
                        {"label": "Countries", "value": "COUNTRIES"},
                        {"label": "Athletes", "value": "PARTICIPANTS"},
                    ],
                    value="EVENTS",
                ),
                style={"width": "150px"},
            ),
            dcc.Graph(id="line-sports", figure=fig_line_sports),
            html.H2(
                "Has the ratio of male and female athletes changed over time?"
            ),
            dcc.Checklist(
                id="mf-ratio-checklist",
                options=[
                    {"label": " Winter", "value": "Winter"},
                    {"label": " Summer", "value": "Summer"},
                ],
                value=["Winter", "Summer"],
                labelStyle={"display": "block"},
            ),
            dcc.Graph(
                id="stacked-bar-gender-win", figure=fig_sb_gender_winter
            ),
            dcc.Graph(
                id="stacked-bar-gender-sum", figure=fig_sb_gender_summer
            ),
            html.H2("Where in the world have the Paralympics have been held?"),
            dcc.Graph(id="scatter-mapbox-osm", figure=fig_scatter_mapbox),
            html.H2(
                "Which countries have won the most gold medals since 1960?"
            ),
            dash_table.DataTable(
                id="table-top-ten-gold-dash",
                columns=[{"name": i, "id": i} for i in df_medals_data.columns],
                data=df_medals_data.to_dict("records"),
                style_cell=dict(textAlign="left"),
            ),
            html.H2("What is the medal performance of each country?"),
            html.P("Medal performance in London 2012"),
            dcc.Graph(id="cp-map-medals", figure=fig_cp_map_medals),
        ],
        fluid=True,
    )

    @dash_app.callback(
        Output(component_id="line-sports", component_property="figure"),
        Input(component_id="type-dropdown", component_property="value"),
    )
    def update_output_div(event_variable):
        """
        Call back for updating the line chart when the type of data to display is changed.

        :param event_variable: one of the following which are columns in the paralympics dataset ['EVENTS', 'SPORTS',
        'COUNTRIES', 'PARTICIPANTS']
        :return: plotly.px.Figure The line chart representing the chosen variable
        """
        fig_line_time = cc.line_chart_over_time(event_variable)
        return fig_line_time

    @dash_app.callback(
        [
            Output("stacked-bar-gender-win", "style"),
            Output("stacked-bar-gender-sum", "style"),
        ],
        Input("mf-ratio-checklist", "value"),
    )
    def show_hide_ratio_charts(selected_types):
        """
        Callback to display or hide the winter and summer male:female ratio bar charts depending on the checkbox values.

        :param selected_types: List of checkbox values for the event type(s) (Winter and/or Summer)
        :return: a list of values, the first sets visibility for the Winter chart, the second for the Summer
        """
        # Default to hiding both
        win_show = {"display": "none"}
        sum_show = {"display": "none"}
        if "Winter" in selected_types:
            win_show = {"display": "block"}
        if "Summer" in selected_types:
            sum_show = {"display": "block"}
        return [win_show, sum_show]

    return dash_app
