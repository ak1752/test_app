# Revenue Analysis Dashboard

A Flask web application for analyzing bookings data with interactive filters.

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000

## Deployment Options

### Option 1: Render.com (Recommended - Free Tier Available)

1. Create a GitHub repository and push this code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/revenue-analysis.git
   git push -u origin main
   ```

2. Go to [render.com](https://render.com) and sign up/log in

3. Click "New" → "Web Service"

4. Connect your GitHub repo

5. Render will auto-detect the `render.yaml` - just click "Create Web Service"

6. Wait ~2 minutes for deployment. You'll get a URL like `https://revenue-analysis-xxxx.onrender.com`

### Option 2: Railway.app

1. Push code to GitHub (same as above)

2. Go to [railway.app](https://railway.app) and sign up

3. Click "New Project" → "Deploy from GitHub repo"

4. Select your repository

5. Railway auto-detects Python and deploys. You'll get a URL immediately.

### Option 3: PythonAnywhere (Free Tier)

1. Create account at [pythonanywhere.com](https://www.pythonanywhere.com)

2. Go to "Web" tab → "Add a new web app"

3. Choose Flask and Python 3.11

4. Upload files via "Files" tab

5. Configure WSGI file to point to your app

## Using with 3DEXPERIENCE

Once deployed, copy your URL (e.g., `https://revenue-analysis-xxxx.onrender.com`) and paste it into the "Run your App" → "Edit Preferences" → "Web App Url" field.

## Important Notes

- **Data Privacy**: Uploaded files are stored temporarily on the server. For sensitive data, consider adding authentication or hosting internally.
- **Session Storage**: Data is stored in server memory and temporary files. Sessions expire after server restart.
- **File Size**: Maximum upload size is 50MB.

## IT Handoff Notes

For internal S3/infrastructure hosting:

- This is a standard Flask WSGI application
- Can run behind nginx/Apache with gunicorn
- Requires Python 3.9+ and the packages in `requirements.txt`
- No database required (uses file-based sessions)
- Consider adding authentication for production use
