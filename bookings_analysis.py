
import streamlit as st
import pandas as pd

# Title
st.title('Revenue Analysis Widget')

# File upload
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    # Load the data
    @st.cache_data
    def load_data():
        df = pd.read_csv(uploaded_file)
        
        # Calculate fields
        df['Bookings'] = df['Rental QLC'] + df['Rental YLC'] + df['Upfront']
        df['Expected Bookings'] = df['Bookings'] * df['Effective Win Rate']
        df['Close Half'] = df['Close Quarter'].apply(lambda x: 'H1' if 'Q1' in x or 'Q2' in x else 'H2')
        return df

    df = load_data()

    # Sidebar filters
    st.sidebar.header('Filters')
    channel = st.sidebar.multiselect('Channel', options=df['Channel'].unique(), default=df['Channel'].unique())
    cet = st.sidebar.multiselect('CET', options=df['CET'].unique(), default=df['CET'].unique())
    nam_iv = st.sidebar.multiselect('NAM IV', options=df['NAM IV'].unique(), default=df['NAM IV'].unique())
    segment = st.sidebar.multiselect('Segment', options=df['Segment'].unique(), default=df['Segment'].unique())
    gtm_tactic = st.sidebar.multiselect('GTM Tactic Name', options=df['GTM Tactic Name'].unique(), default=df['GTM Tactic Name'].unique())
    close_quarter = st.sidebar.multiselect('Close Quarter', options=df['Close Quarter'].unique(), default=df['Close Quarter'].unique())
    close_half = st.sidebar.multiselect('Close Half', options=df['Close Half'].unique(), default=df['Close Half'].unique())

    # Apply filters
    filtered_df = df[
        df['Channel'].isin(channel) &
        df['CET'].isin(cet) &
        df['NAM IV'].isin(nam_iv) &
        df['Segment'].isin(segment) &
        df['GTM Tactic Name'].isin(gtm_tactic) &
        df['Close Quarter'].isin(close_quarter) &
        df['Close Half'].isin(close_half)
    ]

    # Calculate metrics for filtered data
    won_or_ungrowth = filtered_df[filtered_df['Forecast'].isin(['Won', 'Ungrowth'])]
    won = filtered_df[filtered_df['Forecast'] == 'Won']
    ungrowth = filtered_df[filtered_df['Forecast'] == 'Ungrowth']
    non_ungrowth = filtered_df[filtered_df['Forecast'] != 'Ungrowth']

    # Total Bookings = Bookings where Forecast = Won OR Ungrowth
    total_bookings = won_or_ungrowth['Bookings'].sum()

    # Total Bookings excl. Ungrowth = Bookings where Forecast = Won
    total_bookings_excl_ungrowth = won['Bookings'].sum()

    # Total Expected Bookings = Bookings * Effective Win Rate
    total_expected_bookings = filtered_df['Expected Bookings'].sum()

    # Total Expected Bookings excl. Ungrowth = Bookings * Effective Win Rate where Forecast does not = Ungrowth
    total_expected_bookings_excl_ungrowth = non_ungrowth['Expected Bookings'].sum()

    # Cloud Bookings = Bookings where Forecast is Won or Ungrowth AND Cloud Bookings Kicker is not equal to 0
    cloud_bookings = won_or_ungrowth[won_or_ungrowth['Cloud Bookings Kicker'] != 0]['Bookings'].sum()

    # Cloud Bookings Excl. Ungrowth = Bookings where Forecast is Won AND Cloud Bookings Kicker is not equal to 0
    cloud_bookings_excl_ungrowth = won[won['Cloud Bookings Kicker'] != 0]['Bookings'].sum()

    # Rental Percentage = Bookings where Forecast is Won or Ungrowth AND (Rental QLC OR Rental YLC is not = to 0)
    rental_bookings = won_or_ungrowth[(won_or_ungrowth['Rental QLC'] != 0) | (won_or_ungrowth['Rental YLC'] != 0)]['Bookings'].sum()
    rental_percentage = (rental_bookings / won_or_ungrowth['Bookings'].sum()) * 100 if won_or_ungrowth['Bookings'].sum() > 0 else 0

    # Rental Percentage Excl. Ungrowth = Bookings where Forecast is Won AND (Rental QLC OR Rental YLC is not = to 0)
    rental_bookings_excl_ungrowth = won[(won['Rental QLC'] != 0) | (won['Rental YLC'] != 0)]['Bookings'].sum()
    rental_percentage_excl_ungrowth = (rental_bookings_excl_ungrowth / won['Bookings'].sum()) * 100 if won['Bookings'].sum() > 0 else 0

    # Total Ungrowth = Bookings where Forecast = Ungrowth
    total_ungrowth = ungrowth['Bookings'].sum()

    # Cloud Ungrowth = Bookings where Forecast = Ungrowth AND Cloud Bookings Kicker is not = 0
    cloud_ungrowth = ungrowth[ungrowth['Cloud Bookings Kicker'] != 0]['Bookings'].sum()

    # On Prem Ungrowth = Total Ungrowth - Cloud Ungrowth
    on_prem_ungrowth = total_ungrowth - cloud_ungrowth

    # Cloud Bookings Percentage = Cloud Bookings / Bookings where Forecast is Won or Ungrowth
    cloud_bookings_percentage = (cloud_bookings / won_or_ungrowth['Bookings'].sum()) * 100 if won_or_ungrowth['Bookings'].sum() > 0 else 0

    # Cloud Expected Bookings = Bookings * Effective Win Rate where Cloud Booking Kicker is not equal to 0
    cloud_expected_bookings = filtered_df[filtered_df['Cloud Bookings Kicker'] != 0]['Expected Bookings'].sum()

    # Cloud Expected Bookings Percentage = Cloud Expected Bookings / Expected Bookings
    expected_bookings_total = filtered_df['Expected Bookings'].sum()
    cloud_expected_bookings_percentage = (cloud_expected_bookings / expected_bookings_total) * 100 if expected_bookings_total > 0 else 0

    # ACV = SUM of Won opportunities / Count of opportunities where Forecast = Won
    acv = won['Bookings'].sum() / len(won) if len(won) > 0 else 0

    # Display metrics
    st.header('Metrics')
    st.write(f"**ACV:** {acv:,.2f}")
    st.write(f"**Total Bookings:** {total_bookings:,.2f}")
    st.write(f"**Total Bookings excl. Ungrowth:** {total_bookings_excl_ungrowth:,.2f}")
    st.write(f"**Total Expected Bookings:** {total_expected_bookings:,.2f}")
    st.write(f"**Total Expected Bookings excl. Ungrowth:** {total_expected_bookings_excl_ungrowth:,.2f}")
    st.write(f"**Cloud Bookings:** {cloud_bookings:,.2f}")
    st.write(f"**Cloud Bookings Excl. Ungrowth:** {cloud_bookings_excl_ungrowth:,.2f}")
    st.write(f"**Cloud Bookings Percentage:** {cloud_bookings_percentage:.2f}%")
    st.write(f"**Cloud Expected Bookings:** {cloud_expected_bookings:,.2f}")
    st.write(f"**Cloud Expected Bookings Percentage:** {cloud_expected_bookings_percentage:.2f}%")
    st.write(f"**Rental Percentage:** {rental_percentage:.2f}%")
    st.write(f"**Rental Percentage Excl. Ungrowth:** {rental_percentage_excl_ungrowth:.2f}%")
    st.write(f"**Total Ungrowth:** {total_ungrowth:,.2f}")
    st.write(f"**Cloud Ungrowth:** {cloud_ungrowth:,.2f}")
    st.write(f"**On Prem Ungrowth:** {on_prem_ungrowth:,.2f}")

    # Show filtered data
    st.header('Filtered Data')
    st.dataframe(filtered_df[['Customer', 'Channel', 'CET', 'Close Quarter', 'Close Half', 'Forecast', 'Bookings', 'Expected Bookings']])
else:
    st.info("Please upload a CSV file to get started.")
