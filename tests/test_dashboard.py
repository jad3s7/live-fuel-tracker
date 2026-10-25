"""
Test script to verify dashboard functionality
"""

import sys
sys.path.insert(0, '/home/jades/WeThinkCode/Data/live-fuel-tracker/src')

import socket
import pytest
import gradio as gr
from visualization.dashboard import FuelDashboard, main
from utils.config import config
import pandas as pd

def test_dashboard():
    print("=" * 60)
    print("Testing Dashboard Functionality")
    print("=" * 60)

    dashboard = FuelDashboard(db_path="/home/jades/WeThinkCode/Data/live-fuel-tracker/fuel_rate.db")

    # Test 1: Get all data
    print("\n[1/5] Testing data retrieval (all data)...")
    df = dashboard._get_data()
    print(f"✓ Retrieved {len(df)} records")
    if not df.empty:
        print(f"  Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"  Fuel types: {df['fuel_type'].unique().tolist()}")
        print(f"  Locations: {df['location'].unique().tolist()}")
    else:
        print("✗ No data retrieved!")
        return False

    # Test 2: Filter by fuel type
    print("\n[2/5] Testing fuel type filter (Petrol 95)...")
    df_petrol = dashboard._get_data(fuel_type="Petrol 95")
    print(f"✓ Retrieved {len(df_petrol)} Petrol 95 records")
    if len(df_petrol) > 0:
        assert all(df_petrol['fuel_type'] == 'Petrol 95'), "Filter failed!"
        print("  Filter working correctly")
    else:
        print("✗ No Petrol 95 data found")

    # Test 3: Filter by location
    print("\n[3/5] Testing location filter (Inland)...")
    df_inland = dashboard._get_data(location="Inland")
    print(f"✓ Retrieved {len(df_inland)} Inland records")
    if len(df_inland) > 0:
        assert all(df_inland['location'] == 'Inland'), "Filter failed!"
        print("  Filter working correctly")
    else:
        print("✗ No Inland data found")

    # Test 4: Combined filters
    print("\n[4/5] Testing combined filters (Petrol 95 + Inland)...")
    df_combined = dashboard._get_data(fuel_type="Petrol 95", location="Inland")
    print(f"✓ Retrieved {len(df_combined)} records")
    if len(df_combined) > 0:
        assert all(df_combined['fuel_type'] == 'Petrol 95'), "Fuel filter failed!"
        assert all(df_combined['location'] == 'Inland'), "Location filter failed!"
        print("  Combined filters working correctly")
    else:
        print("✗ No data for combined filters")

    # Test 5: Chart generation
    print("\n[5/5] Testing chart generation...")
    try:
        price_chart = dashboard._create_price_chart(df)
        print(f"✓ Price chart created with {len(price_chart.data)} traces")

        current_df = dashboard._get_current_prices()
        comparison_chart = dashboard._create_comparison_chart(current_df)
        print(f"✓ Comparison chart created with {len(comparison_chart.data)} traces")

        stats_html = dashboard._create_stats_cards(current_df)
        print(f"✓ Stats cards HTML generated ({len(stats_html)} characters)")
    except Exception as e:
        print(f"✗ Chart generation failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("✓ All dashboard tests passed!")
    print("=" * 60)
    print("\nThe dashboard should work properly in the browser.")
    print("Test these interactions:")
    print("  1. Change fuel type dropdown")
    print("  2. Change region dropdown")
    print("  3. Adjust time range slider")
    print("  4. Hover over charts for details")
    print("=" * 60)


def test_dashboard_config_port_and_host(monkeypatch):
    """Verify environment variable handling for DASHBOARD_PORT and DASHBOARD_HOST"""
    monkeypatch.setenv("DASHBOARD_PORT", "8555")
    monkeypatch.setenv("DASHBOARD_HOST", "127.0.0.1")
    assert config.dashboard_port == 8555
    assert config.dashboard_host == "127.0.0.1"


def test_dashboard_main_port_fallback():
    """Verify that if requested port is blocked, main() catches OSError and falls back to an available port"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 8501))
    sock.listen(1)

    app = None
    try:
        app, local_url, _ = main(prevent_thread_lock=True, server_name="127.0.0.1", server_port=8501)
        assert app is not None
        assert local_url is not None
        assert "8501" not in local_url
    finally:
        if app:
            app.close()
        sock.close()


def test_dashboard_launch_briefly():
    """Test launching dashboard briefly in non-blocking mode to ensure clean binding"""
    app, local_url, _ = main(prevent_thread_lock=True, server_name="127.0.0.1", server_port=8501)
    try:
        assert app is not None
        assert "8501" in local_url
    finally:
        app.close()


if __name__ == "__main__":
    test_dashboard()
