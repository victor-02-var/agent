# GitHub OAuth Setup Guide

## Prerequisites

You need to create a GitHub OAuth Application to enable login functionality.

## Step 1: Create GitHub OAuth App

1. Go to GitHub Settings → Developer settings → OAuth Apps
   - URL: https://github.com/settings/developers

2. Click "New OAuth App"

3. Fill in the following details:
   - **Application name**: CodeCityAI (or your app name)
   - **Homepage URL**: http://localhost:5000
   - **Authorization callback URL**: http://localhost:5000/callback

4. Click "Register application"

## Step 2: Get Your Credentials

After registering, you'll see:
- **Client ID**: Copy this
- **Client Secret**: Click "Generate a new client secret" and copy it

## Step 3: Configure Environment Variables

Create or update your `.env` file in the project root with:

```env
GITHUB_CLIENT_ID=your_client_id_here
GITHUB_CLIENT_SECRET=your_client_secret_here
```

## Step 4: Verify Setup

1. Start your Flask backend:
   ```bash
   python app.py
   ```

2. Check if OAuth is configured:
   ```bash
   curl http://localhost:5000/auth-check
   ```

   You should see:
   ```json
   {
     "configured": true,
     "client_id": "your_client_id",
     "message": "GitHub OAuth is configured"
   }
   ```

## Step 5: Test the Flow

1. Open React app: http://localhost:5173
2. Click "Login" button
3. You should be redirected to GitHub's authorization page
4. Authorize the app
5. You'll be redirected back to the dashboard with your token

## Troubleshooting

### "GitHub OAuth credentials not configured"
- Make sure `.env` file exists in project root
- Check that `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` are set
- Restart the Flask server after updating `.env`

### "Invalid client_id"
- Check that your Client ID in `.env` matches the one from GitHub
- Make sure there are no extra spaces or quotes

### "Redirect URI mismatch"
- Verify the redirect URL in GitHub app settings is exactly: `http://localhost:5000/callback`
- Check that Flask server is running on port 5000

### Authorization window doesn't appear
- Make sure you're clicking the Login/Signup buttons
- Check browser console for any errors
- Verify CLIENT_ID is set correctly

## For Production

When deploying to production:

1. Change the callback URL in GitHub app settings to your production domain
2. Update `.env` with production domain URLs
3. Use HTTPS instead of HTTP
4. Store secrets securely (use environment variables in your hosting platform)

Example for production:
```env
GITHUB_CLIENT_ID=your_production_client_id
GITHUB_CLIENT_SECRET=your_production_client_secret
CALLBACK_URL=https://yourdomain.com/callback
```
