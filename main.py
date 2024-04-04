# created by: @madsenav1
from dash import Dash, html, dcc, callback, Output, Input, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import random
import pandas as pd
import numpy as np
import cocktailData


app = Dash(__name__, external_stylesheets=[dbc.themes.VAPOR, dbc.icons.FONT_AWESOME])
# initializing an object of the cocktailData class
cocktails = cocktailData.cocktailData()
cocktail_list = cocktails.clean_dataset()

app.layout = html.Div([
    # introduction modal that pops up when loading the application
    dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Don't know what to drink tonight?"),
                                close_button=False),
                dbc.ModalBody("Mixed-up Mixies selects from over a hundred cocktails to provide you with a new recipe to try based on your preferences."),
                dbc.ModalBody("Enter your desired spirit and level of difficulty to begin."),
                dbc.Row([
                    dbc.Col([
                        dbc.Button("Let's get started!", id="start-button", color="secondary", style={"width": "200px"})
                        ], style={'padding-left':'162px'})
                    ]),
                html.Br()
            ],
            id="instructional-modal",
            is_open=True,
            centered=True,
            autofocus=True,
            backdrop="static",
            style={"backgroundColor": "#170229"}
        ),
    # below is what is shown when you actually enter the web application
    html.Br(),
    html.Br(),
    html.Div(html.H1(children='Mixed-up Mixies', style={'textAlign':'center'})),
    dbc.Row([
        # these are all of the elements located on the left side of the screen
        dbc.Col(
            html.Div([
                html.Br(),
                html.H3("Welcome cocktail lovers!", className="drink-text", style={"width": "650px"}),
                html.P("Enter a desired spirit and level of difficulty to begin. Lack of selection will result in the inclusion of all available spirits.",
                        className="drink-text", style={"width": "650px"}),
                html.P("Cocktail recipes are sourced from The Joy of Mixology, PDT, The Ultimate Bar Book, IBA and The Fine Art of Mixing Drinks",
                        className="drink-text", style={"width": "650px"}),
                # note: spirits include beer and wine in this case too - even though they are not!
                html.H5("Select a spirit:", style={"color": "primary"}),
                html.Div(dbc.Row(dcc.Dropdown(options=cocktails.liquor, searchable=False, 
                                               id="spirit", className="dropdown-inputs"))),
                html.Br(),
                html.H5("Level of difficulty:"),
                html.Div(dbc.RadioItems(
                    options=[
                        {"label": "Easy", "value": 2},
                        {"label": "Medium", "value": 4},
                        {"label": "Expert", "value": 5},
                        {"label": "Surprise Me!", "value": 0},
                    ],
                    value=0,
                    id="difficulty-level",
                    inline=True,
                    inputStyle={"paddingLeft": "10px"}
                ), style={"paddingLeft": "100px"}),
                html.Br(),
                dbc.Button("Generate Cocktail Recipe", id="submit-button", className="submit-button", color="secondary")
                ],
                  style={"paddingLeft": "50px", "paddingTop": "100px"}),
        ),
        # these are all the elements on the right side of the screen
        dbc.Col([
            html.Br(),
            html.Br(),
            html.Div([
                html.Br(),
                # the three martini glass icons that are shown upon initial load - coming from font awesome
                html.Div([html.Div([html.I(className="fa-solid fa-martini-glass",
                                            style={"color": "#ea39b8", "fontSize": 30, "paddingLeft": "10px"}),
                                            html.I(className="fa-solid fa-martini-glass",
                                            style={"color": "#ea39b8", "fontSize": 30, "paddingLeft": "10px"}),
                                            html.I(className="fa-solid fa-martini-glass",
                                            style={"color": "#ea39b8", "fontSize": 30, "paddingLeft": "10px"})], style={"textAlign": "center", "paddingTop": "215px"})], id="cocktail-name"), 
                html.Br(),
                html.Div(id="ingredient-list", style={"textAlign": "center", "width": "97%"}),
                html.Br(),
                html.Div(id="direction-list", style={"textAlign": "center", "width": "97%"}),
                html.Br()
            ], className="drink-card", style={"marginLeft": "75px", "width": "80%", "min-height": "600px", "backgroundColor": "#170229"}),
            html.Br(),
            html.Br()
    ]),
    ]),

])

@callback(
    Output("instructional-modal", "is_open"),
    Input("start-button", "n_clicks"),
    State("instructional-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_modal(n_clicks, is_open):
    if n_clicks > 0:
        return not is_open
    return is_open

@callback(
    Output("cocktail-name", "children"),
    Output("ingredient-list", "children"),
    Output("direction-list", "children"),
    Input("submit-button", "n_clicks"),
    State("spirit", "value"),
    State("difficulty-level", "value"),
    prevent_initial_call=True
)

def submit_cocktail(n_clicks, spirit, level):
    if n_clicks > 0:

        print(level)

        # getting the full cleaned data set to start with 
        cocktail_list = cocktails.clean_dataset()

        # if a spirit has been selected, we need to filter for it
        if spirit != None:
            spirit = spirit.lower()
            cocktail_list = cocktail_list[cocktail_list["ner"].apply(lambda x: spirit in x )]

        # filtering for the easy and medium levels - we want direction quantity less than or equal to a certain number
        if (level == 2) | (level == 4):
            cocktail_list = cocktail_list[cocktail_list["directions"].apply(lambda x: len(x) <= level)]
            if (level == 2):
                # having too many ingredients leads to complexity, capping the number of ingredients for easy recipes
                cocktail_list = cocktail_list[cocktail_list["ingredients"].apply(lambda x: len(x) <= 3)]
        # filtering for expert and all levels - we want direction quantity greater than or equal to a certain number
        if (level == 0) | (level == 5):
            cocktail_list = cocktail_list[cocktail_list["directions"].apply(lambda x: len(x) >= level)]

        # need to reset index after
        cocktail_list = cocktail_list.reset_index(drop=True)

        # error catching
        if (len(cocktail_list) == 0):
            return html.H4("No available recipes. Try Again.", className="drink-text", style={"textAlign": "center", "paddingTop": "220px"}), html.P(""), html.P("")

        num = random.randint(0, (len(cocktail_list) - 1))

        # formatting the ingredients so that they appear as a bulleted list
        ingredient_data = {"Ingredients": cocktail_list.at[num, "ingredients"]}
        ingredient_df = pd.DataFrame(ingredient_data)
        ingredient_df = ingredient_df[~ingredient_df["Ingredients"].str.endswith(".")]
        ingredient_df = ingredient_df[ingredient_df["Ingredients"] != ""]
        ingredient_df["Ingredients"] = "• " + ingredient_df["Ingredients"]

        # formatting the directions so they appear as a numbered list
        direction_data = {"Directions": cocktail_list.at[num, "directions"]}
        direction_df = pd.DataFrame(direction_data)
        direction_df = direction_df[direction_df["Directions"] != ""]
        direction_df = direction_df.reset_index(drop=True)
        direction_df["Directions"] = (direction_df.index + 1).astype(str) + ". " + direction_df["Directions"]

        return html.H4(cocktail_list.at[num, "title"], className="drink-text", style={"textAlign": "center"}), dash_table.DataTable(ingredient_df.to_dict('records'), [{"name": i, "id": i} for i in ingredient_df.columns], style_cell={"color": "#ea39b8", "backgroundColor": "#170229", "border": "solid 1px #170229", "textAlign": "left", "paddingLeft": "25px"},
                                                                                                                                                style_header={"textAlign": "center"}, style_data={'whiteSpace': 'normal', 'height': 'auto'}), dash_table.DataTable(direction_df.to_dict('records'), [{"name": i, "id": i} for i in direction_df.columns], style_cell={"color": "#ea39b8", "backgroundColor": "#170229", "border": "solid 1px #170229", "textAlign": "left", "paddingLeft": "25px"},
                                                                                                                                                style_header={"textAlign": "center"}, style_data={'whiteSpace': 'normal', 'height': 'auto'}),

if __name__ == '__main__':
    app.run(debug=True)