# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
# Assuming "spacex_launch_dash.csv" exists in the same directory
try:
    spacex_df = pd.read_csv("spacex_launch_dash.csv")
except FileNotFoundError:
    print("Error: spacex_launch_dash.csv not found. Please ensure the file is in the correct directory.")
    # Create a dummy dataframe for layout generation if file not found
    spacex_df = pd.DataFrame({
        'Launch Site': ['CCAFS LC-40', 'VAFB SLC-4E', 'KSC LC-39A', 'CCAFS SLC-40'],
        'Payload Mass (kg)': [500, 600, 700, 800],
        'class': [0, 1, 1, 0],
        'Booster Version Category': ['v1.0', 'v1.1', 'FT', 'v1.0']
    })

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Get unique launch sites for dropdown options
launch_sites = spacex_df['Launch Site'].unique()
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
               [{'label': site, 'value': site} for site in launch_sites]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',  # Default value
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,  # Slider starting point
        max=10000,  # Slider ending point
        step=1000,  # Slider interval
        # Dynamically set marks if desired, e.g., {i: f'{i}' for i in range(0, 10001, 1000)}
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        value=[min_payload, max_payload]  # Default selected range
    ),
    html.Br(), # Added break for spacing

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Calculate total successes for all sites
        # Option 1: Pie chart of overall Success vs Failure
        # success_counts = spacex_df['class'].value_counts().reset_index()
        # success_counts.columns = ['class', 'count']
        # fig = px.pie(success_counts, values='count', names='class',
        #              title='Total Launch Success vs Failure Rate for All Sites',
        #              labels={'class':'Outcome (1=Success, 0=Failure)'})

        # Option 2: Pie chart showing success count distribution per site (as requested for 'ALL')
        # Filter for successful launches and count per site
        successful_df = spacex_df[spacex_df['class'] == 1]
        site_success_counts = successful_df.groupby('Launch Site').size().reset_index(name='Success Count')
        fig = px.pie(site_success_counts, values='Success Count', names='Launch Site',
                     title='Total Successful Launches by Site')
        return fig
    else:
        # Filter dataframe for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Calculate success (1) vs failure (0) counts for the site
        site_outcome_counts = filtered_df['class'].value_counts().reset_index()
        site_outcome_counts.columns = ['class', 'count']
        # Map class values to labels for clarity
        site_outcome_counts['Outcome'] = site_outcome_counts['class'].map({1: 'Success', 0: 'Failure'})

        fig = px.pie(site_outcome_counts, values='count', names='Outcome',
                     title=f'Launch Success vs Failure Rate for site {entered_site}',
                     color='Outcome', # Optional: color by outcome
                     color_discrete_map={'Success':'green', 'Failure':'red'}) # Optional: specific colors
        return fig

# TASK 4: Callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id="payload-slider", component_property="value")]
)
def get_scatter_chart(entered_site, payload_range):
    # Filter based on payload range slider
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]

    if entered_site == 'ALL':
        # Plot all sites within the payload range
        fig = px.scatter(filtered_df,
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category',
                         title='Payload vs. Launch Outcome for All Sites (Colored by Booster Version)',
                         labels={'class': 'Launch Outcome (1=Success, 0=Failure)'})
        return fig
    else:
        # Filter further for the specific site
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(site_filtered_df,
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category',
                         title=f'Payload vs. Launch Outcome for site {entered_site} (Colored by Booster Version)',
                         labels={'class': 'Launch Outcome (1=Success, 0=Failure)'})
        return fig

# Run the app
if __name__ == '__main__':
    # Changed run_server to run, kept debug=True for development
    app.run(debug=True)