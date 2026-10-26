"""
Modern Dark-Themed Gradio Dashboard for South African Fuel Price Tracker
"""

import gradio as gr
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data.extract import FuelExtractor
from src.data.transform import DataTransformer
from src.database.storage_db import FuelDatabase
from src.utils.config import config


class FuelDashboard:
    """Gradio-based dashboard for SA fuel price visualization"""

    def __init__(self, db_path: str = "fuel_rate.db"):
        self.db_path = db_path

    def _get_data(self, fuel_type: str = None, location: str = None, days: int = 30):
        """Fetch fuel price data from SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)

            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            query = """
                SELECT timestamp, fuel_type, price_per_liter, location, source
                FROM fuel_data
                WHERE timestamp >= ?
            """
            params = [start_date.strftime('%Y-%m-%d %H:%M:%S')]

            if fuel_type and fuel_type != "All":
                query += " AND fuel_type = ?"
                params.append(fuel_type)

            if location and location != "All":
                query += " AND location = ?"
                params.append(location)

            query += " ORDER BY timestamp ASC"

            df = pd.read_sql_query(query, conn, params=params)
            conn.close()

            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])

            return df
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()

    def _get_current_prices(self):
        """Get the most recent fuel prices for all types and locations"""
        try:
            conn = sqlite3.connect(self.db_path)

            query = """
                SELECT fuel_type, location, price_per_liter, timestamp
                FROM fuel_data
                WHERE timestamp = (SELECT MAX(timestamp) FROM fuel_data)
                ORDER BY fuel_type, location
            """

            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error fetching current prices: {e}")
            return pd.DataFrame()

    def _create_price_chart(self, df):
        """Create a sleek dark-themed line chart for fuel prices"""
        if df.empty:
            return go.Figure()

        fig = go.Figure()

        # Modern dark theme colors
        colors = {
            'Petrol 95': "#096609",      # Cyan
            'Petrol 93': "#D30B0B",      # Purple
            'Diesel 50ppm': "#620679",   # Emerald green
            'Diesel 500ppm': '#F59E0B',  # Amber
        }

        for fuel_type in df['fuel_type'].unique():
            fuel_data = df[df['fuel_type'] == fuel_type]
            color = colors.get(fuel_type, '#6366F1')

            fig.add_trace(go.Scatter(
                x=fuel_data['timestamp'].values,
                y=fuel_data['price_per_liter'],
                name=fuel_type,
                line=dict(color=color, width=3),
                mode='lines+markers',
                marker=dict(size=6, line=dict(color='white', width=1)),
                hovertemplate='<b>%{fullData.name}</b><br>' +
                             'Date: %{x}<br>' +
                             'Price: R%{y:.2f}/L<extra></extra>'
            ))

        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='#0F0F0F',
            plot_bgcolor='#1A1A1A',
            font=dict(color='#E5E7EB', family='Inter, sans-serif'),
            title=dict(
                text='Fuel Price Trends',
                font=dict(size=24, color='#FFFFFF'),
                x=0.5
            ),
            xaxis=dict(
                title='Date',
                gridcolor='#2A2A2A',
                showgrid=True
            ),
            yaxis=dict(
                title='Price (ZAR/L)',
                gridcolor='#2A2A2A',
                showgrid=True
            ),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5,
                bgcolor='rgba(26, 26, 26, 0.8)',
                bordercolor='#2A2A2A',
                borderwidth=1
            ),
            hovermode='x unified',
            margin=dict(l=20, r=20, t=60, b=20)
        )

        return fig

    def _create_comparison_chart(self, df):
        """Create a bar chart comparing current prices across regions"""
        if df.empty:
            return go.Figure()

        fig = go.Figure()

        # Get latest prices
        latest = df.groupby(['fuel_type', 'location']).last().reset_index()

        colors = {
            'Inland': "#ECCE24",    # Red
            'Coastal': "#0509D1",   # Blue
        }

        for location in latest['location'].unique():
            loc_data = latest[latest['location'] == location]
            color = colors.get(location, '#6366F1')

            fig.add_trace(go.Bar(
                x=loc_data['fuel_type'],
                y=loc_data['price_per_liter'],
                name=location,
                marker=dict(color=color, line=dict(color='white', width=1)),
                text=loc_data['price_per_liter'].round(2),
                textposition='outside',
                textfont=dict(color='#FFFFFF', size=12)
            ))

        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='#0F0F0F',
            plot_bgcolor='#1A1A1A',
            font=dict(color='#E5E7EB', family='Inter, sans-serif'),
            title=dict(
                text='Current Prices: Inland vs Coastal',
                font=dict(size=24, color='#FFFFFF'),
                x=0.5
            ),
            xaxis=dict(
                title='Fuel Type',
                gridcolor='#2A2A2A',
                tickfont=dict(color='#E5E7EB')
            ),
            yaxis=dict(
                title='Price (ZAR/L)',
                gridcolor='#2A2A2A',
                tickfont=dict(color='#E5E7EB')
            ),
            barmode='group',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5,
                bgcolor='rgba(26, 26, 26, 0.8)',
                bordercolor="#0A0A0A",
                borderwidth=1
            ),
            margin=dict(l=20, r=20, t=60, b=20)
        )

        return fig

    def _create_stats_cards(self, df):
        """Create statistics summary as HTML with improved layout"""
        if df.empty:
            return "<p style='color: #6B7280; padding: 20px;'>No data available for selected filters</p>"

        # Get the latest price for each fuel_type + location combination
        latest = df.groupby(['fuel_type', 'location']).last().reset_index()

        # Group by fuel type for better layout
        fuel_types = latest['fuel_type'].unique()

        stats_html = """
        <div style="display: flex; flex-direction: column; gap: 20px;">
        """

        for fuel in fuel_types:
            fuel_data = latest[latest['fuel_type'] == fuel]

            # Get color for this fuel type
            fuel_colors = {
            'Petrol 95': "#096609",      # Cyan
            'Petrol 93': "#D30B0B",      # Purple
            'Diesel 50ppm': "#620679",   # Emerald green
            'Diesel 500ppm': '#F59E0B',  # Amber
        }
         
            fuel_color = fuel_colors.get(fuel, '#6366F1')

            stats_html += f"""
            <div style="
                background: linear-gradient(135deg, #1A1A1A 0%, #252525 100%);
                border: 1px solid #2A2A2A;
                border-radius: 16px;
                padding: 24px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            ">
                <div style="
                    color: {fuel_color};
                    font-size: 14px;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-bottom: 16px;
                    border-bottom: 2px solid {fuel_color};
                    padding-bottom: 8px;
                ">
                    {fuel}
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px;">
            """

            for _, row in fuel_data.iterrows():
                loc = row['location']
                price = row['price_per_liter']

                # Color based on price range
                if price < 20:
                    price_color = "#18C202"  # Green
                elif price < 22:
                    price_color = '#F59E0B'  # Amber
                else:
                    price_color = "#E40D0D"  # Red

                # Region color
                region_color = "#0630B9" if loc == 'Inland' else "#CE07B3"

                stats_html += f"""
                <div style="
                    background: rgba(0, 0, 0, 0.3);
                    border: 1px solid #2A2A2A;
                    border-radius: 10px;
                    padding: 16px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    text-align: center;
                ">
                    <div style="
                        color: {region_color};
                        font-size: 11px;
                        font-weight: 600;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                        margin-bottom: 8px;
                    ">
                        {loc}
                    </div>
                    <div style="
                        color: {price_color};
                        font-size: 28px;
                        font-weight: 700;
                    ">
                        R{price:.2f}
                    </div>
                    <div style="color: #6B7280; font-size: 10px; margin-top: 4px;">
                        per litre
                    </div>
                </div>
                """

            stats_html += """
                </div>
            </div>
            """

        stats_html += "</div>"
        return stats_html

    def create_dashboard(self):
        """Create the Gradio interface"""

        # Define the update function
        def update_dashboard(fuel_type, location, days):
            df = self._get_data(fuel_type, location, days)

            # Get current prices (without filters for comparison chart)
            current_df = self._get_current_prices()

            # Use filtered data for stats cards so they update with filters
            if not df.empty:
                # Get latest prices from filtered data
                stats_df = df.groupby(['fuel_type', 'location']).last().reset_index()
            else:
                stats_df = pd.DataFrame()

            price_chart = self._create_price_chart(df)
            comparison_chart = self._create_comparison_chart(current_df)
            stats_html = self._create_stats_cards(stats_df)

            return price_chart, comparison_chart, stats_html

        # Define the refresh function to fetch live data
        def refresh_live_data():
            """Fetch fresh fuel prices from API/scraping and update database"""
            try:
                # Initialize ETL components
                extractor = FuelExtractor(
                    api_provider=config.fuel_api_provider,
                    api_key=config.fuel_api_key,
                    base_url=config.fuel_api_base_url
                )
                transformer = DataTransformer()
                db = FuelDatabase(config.get_database_path())

                # Fetch current prices
                all_raw_data = []
                fuel_types = ['Petrol 95', 'Petrol 93', 'Diesel 50ppm', 'Diesel 500ppm']
                regions = ['Inland', 'Coastal']

                for fuel_type in fuel_types:
                    for region in regions:
                        current_price = extractor._get_current_price(fuel_type=fuel_type, location=region)
                        if current_price:
                            all_raw_data.append(current_price)

                # Transform and load
                cleaned_data = []
                for data in all_raw_data:
                    cleaned = transformer._clean_price_data_valid(data)
                    if cleaned:
                        cleaned_data.append(cleaned)

                if cleaned_data:
                    inserted_count = db._insert_price_database_multiple(cleaned_data)
                    return f"✓ Successfully refreshed! Added {inserted_count} new records from {extractor.api_provider}."
                else:
                    return "✗ No data retrieved. Check API/scraping configuration."

            except Exception as e:
                return f"✗ Refresh failed: {str(e)}"

        # Custom CSS for dark theme
        custom_css = """
        .gradio-container {
            background-color: #0F0F0F !important;
        }
        .gr-button-primary {
            background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
            border: none !important;
        }
        .gr-button-primary:hover {
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        }
        """

        with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:
            gr.Markdown(
                """
                # 🇿🇦 South African Fuel Price Tracker
                """,
                elem_classes=["dark-theme"]
            )

            with gr.Row():
                fuel_dropdown = gr.Dropdown(
                    choices=["All", "Petrol 95", "Petrol 93", "Diesel 50ppm", "Diesel 500ppm"],
                    value="All",
                    label="Fuel Type",
                    interactive=True
                )
                location_dropdown = gr.Dropdown(
                    choices=["All", "Inland", "Coastal"],
                    value="All",
                    label="Region",
                    interactive=True
                )
                days_slider = gr.Slider(
                    minimum=7,
                    maximum=90,
                    value=30,
                    step=7,
                    label="Time Range (Days)",
                    interactive=True
                )
                refresh_btn = gr.Button(
                    "🔄 Refresh Live Data",
                    variant="primary",
                    size="sm"
                )

            with gr.Row():
                status_output = gr.Textbox(
                    label="Status",
                    value="Ready",
                    interactive=False
                )
                stats_output = gr.HTML(value="<p>Loading...</p>")

            with gr.Row():
                price_chart = gr.Plot(label="Price Trends")
                comparison_chart = gr.Plot(label="Regional Comparison")

            # Event handlers
            fuel_dropdown.change(
                update_dashboard,
                inputs=[fuel_dropdown, location_dropdown, days_slider],
                outputs=[price_chart, comparison_chart, stats_output]
            )
            location_dropdown.change(
                update_dashboard,
                inputs=[fuel_dropdown, location_dropdown, days_slider],
                outputs=[price_chart, comparison_chart, stats_output]
            )
            days_slider.change(
                update_dashboard,
                inputs=[fuel_dropdown, location_dropdown, days_slider],
                outputs=[price_chart, comparison_chart, stats_output]
            )

            # Refresh button - fetches live data then updates dashboard
            refresh_btn.click(
                refresh_live_data,
                outputs=[status_output]
            ).then(
                update_dashboard,
                inputs=[fuel_dropdown, location_dropdown, days_slider],
                outputs=[price_chart, comparison_chart, stats_output]
            )

            # Initial load
            demo.load(
                update_dashboard,
                inputs=[fuel_dropdown, location_dropdown, days_slider],
                outputs=[price_chart, comparison_chart, stats_output]
            )

        return demo


def main(prevent_thread_lock: bool = False, **launch_kwargs):
    """Launch the dashboard"""
    db_path = config.get_database_path()
    if not os.path.isabs(db_path):
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), db_path)
    dashboard = FuelDashboard(db_path)
    app = dashboard.create_dashboard()

    port = getattr(config, "dashboard_port", None)
    if port is None:
        port = int(os.getenv("DASHBOARD_PORT", "8501"))
    else:
        port = int(port)

    host = getattr(config, "dashboard_host", None) or os.getenv("DASHBOARD_HOST", "0.0.0.0")

    launch_opts = {
        "server_name": host,
        "server_port": port,
        "share": False,
        "prevent_thread_lock": prevent_thread_lock,
    }
    launch_opts.update(launch_kwargs)

    try:
        return app.launch(**launch_opts)
    except OSError as e:
        import warnings
        warnings.warn(f"Port {launch_opts.get('server_port', port)} is in use ({e}). Falling back to an available port...")
        print(f"Warning: Port {launch_opts.get('server_port', port)} is in use ({e}). Falling back to an available port...")
        launch_opts["server_port"] = None
        return app.launch(**launch_opts)


if __name__ == "__main__":
    main()
