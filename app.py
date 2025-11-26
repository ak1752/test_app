from flask import Flask, render_template, request, session, jsonify
import pandas as pd
import os
import uuid

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def process_dataframe(df):
    """Add calculated columns to the dataframe."""
    df['Bookings'] = df['Rental QLC'] + df['Rental YLC'] + df['Upfront']
    df['Expected Bookings'] = df['Bookings'] * df['Effective Win Rate']
    df['Close Half'] = df['Close Quarter'].apply(lambda x: 'H1' if 'Q1' in str(x) or 'Q2' in str(x) else 'H2')
    return df


def calculate_metrics(filtered_df):
    """Calculate all metrics from filtered dataframe."""
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

    # Total Expected Bookings excl. Ungrowth
    total_expected_bookings_excl_ungrowth = non_ungrowth['Expected Bookings'].sum()

    # Cloud Bookings
    cloud_bookings = won_or_ungrowth[won_or_ungrowth['Cloud Bookings Kicker'] != 0]['Bookings'].sum()

    # Cloud Bookings Excl. Ungrowth
    cloud_bookings_excl_ungrowth = won[won['Cloud Bookings Kicker'] != 0]['Bookings'].sum()

    # Rental Percentage
    rental_bookings = won_or_ungrowth[
        (won_or_ungrowth['Rental QLC'] != 0) | (won_or_ungrowth['Rental YLC'] != 0)
    ]['Bookings'].sum()
    rental_percentage = (rental_bookings / won_or_ungrowth['Bookings'].sum()) * 100 if won_or_ungrowth['Bookings'].sum() > 0 else 0

    # Rental Percentage Excl. Ungrowth
    rental_bookings_excl_ungrowth = won[
        (won['Rental QLC'] != 0) | (won['Rental YLC'] != 0)
    ]['Bookings'].sum()
    rental_percentage_excl_ungrowth = (rental_bookings_excl_ungrowth / won['Bookings'].sum()) * 100 if won['Bookings'].sum() > 0 else 0

    # Total Ungrowth
    total_ungrowth = ungrowth['Bookings'].sum()

    # Cloud Ungrowth
    cloud_ungrowth = ungrowth[ungrowth['Cloud Bookings Kicker'] != 0]['Bookings'].sum()

    # On Prem Ungrowth
    on_prem_ungrowth = total_ungrowth - cloud_ungrowth

    # Cloud Bookings Percentage
    cloud_bookings_percentage = (cloud_bookings / won_or_ungrowth['Bookings'].sum()) * 100 if won_or_ungrowth['Bookings'].sum() > 0 else 0

    # Cloud Expected Bookings
    cloud_expected_bookings = filtered_df[filtered_df['Cloud Bookings Kicker'] != 0]['Expected Bookings'].sum()

    # Cloud Expected Bookings Percentage
    expected_bookings_total = filtered_df['Expected Bookings'].sum()
    cloud_expected_bookings_percentage = (cloud_expected_bookings / expected_bookings_total) * 100 if expected_bookings_total > 0 else 0

    # ACV
    acv = won['Bookings'].sum() / len(won) if len(won) > 0 else 0

    return {
        'acv': acv,
        'total_bookings': total_bookings,
        'total_bookings_excl_ungrowth': total_bookings_excl_ungrowth,
        'total_expected_bookings': total_expected_bookings,
        'total_expected_bookings_excl_ungrowth': total_expected_bookings_excl_ungrowth,
        'cloud_bookings': cloud_bookings,
        'cloud_bookings_excl_ungrowth': cloud_bookings_excl_ungrowth,
        'cloud_bookings_percentage': cloud_bookings_percentage,
        'cloud_expected_bookings': cloud_expected_bookings,
        'cloud_expected_bookings_percentage': cloud_expected_bookings_percentage,
        'rental_percentage': rental_percentage,
        'rental_percentage_excl_ungrowth': rental_percentage_excl_ungrowth,
        'total_ungrowth': total_ungrowth,
        'cloud_ungrowth': cloud_ungrowth,
        'on_prem_ungrowth': on_prem_ungrowth,
    }


@app.route('/')
def index():
    """Upload page."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    """Handle file upload."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Please upload a CSV file'}), 400
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'{file_id}.csv')
    file.save(filepath)
    
    # Store file_id in session
    session['file_id'] = file_id
    
    return jsonify({'success': True, 'redirect': '/dashboard'})


@app.route('/dashboard')
def dashboard():
    """Main dashboard page."""
    file_id = session.get('file_id')
    if not file_id:
        return render_template('index.html', error='Please upload a file first')
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'{file_id}.csv')
    if not os.path.exists(filepath):
        return render_template('index.html', error='File not found. Please upload again.')
    
    # Load and process data
    df = pd.read_csv(filepath)
    df = process_dataframe(df)
    
    # Get unique values for filters
    filters = {
        'channels': sorted(df['Channel'].dropna().unique().tolist()),
        'cets': sorted(df['CET'].dropna().unique().tolist()),
        'nam_ivs': sorted(df['NAM IV'].dropna().unique().tolist()),
        'segments': sorted(df['Segment'].dropna().unique().tolist()),
        'gtm_tactics': sorted(df['GTM Tactic Name'].dropna().unique().tolist()),
        'close_quarters': sorted(df['Close Quarter'].dropna().unique().tolist()),
        'close_halves': sorted(df['Close Half'].dropna().unique().tolist()),
    }
    
    return render_template('dashboard.html', filters=filters)


@app.route('/api/data', methods=['POST'])
def get_data():
    """API endpoint to get filtered data and metrics."""
    file_id = session.get('file_id')
    if not file_id:
        return jsonify({'error': 'No file uploaded'}), 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'{file_id}.csv')
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 400
    
    # Load and process data
    df = pd.read_csv(filepath)
    df = process_dataframe(df)
    
    # Get filter values from request
    filters = request.json or {}
    
    # Apply filters
    filtered_df = df.copy()
    
    if filters.get('channels'):
        filtered_df = filtered_df[filtered_df['Channel'].isin(filters['channels'])]
    if filters.get('cets'):
        filtered_df = filtered_df[filtered_df['CET'].isin(filters['cets'])]
    if filters.get('nam_ivs'):
        filtered_df = filtered_df[filtered_df['NAM IV'].isin(filters['nam_ivs'])]
    if filters.get('segments'):
        filtered_df = filtered_df[filtered_df['Segment'].isin(filters['segments'])]
    if filters.get('gtm_tactics'):
        filtered_df = filtered_df[filtered_df['GTM Tactic Name'].isin(filters['gtm_tactics'])]
    if filters.get('close_quarters'):
        filtered_df = filtered_df[filtered_df['Close Quarter'].isin(filters['close_quarters'])]
    if filters.get('close_halves'):
        filtered_df = filtered_df[filtered_df['Close Half'].isin(filters['close_halves'])]
    
    # Calculate metrics
    metrics = calculate_metrics(filtered_df)
    
    # Prepare table data
    display_columns = ['Customer', 'Channel', 'CET', 'Close Quarter', 'Close Half', 'Forecast', 'Bookings', 'Expected Bookings']
    table_data = filtered_df[display_columns].round(2).to_dict('records')
    
    return jsonify({
        'metrics': metrics,
        'table_data': table_data,
        'row_count': len(filtered_df)
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
