# CodeCityAI - GitHub OAuth Login Flow

## Complete OAuth Flow Diagram

```
1. User clicks "Login" button on Home page
   ↓
2. User redirected to: http://localhost:5000/login
   ↓
3. Backend redirects to GitHub OAuth authorization page:
   https://github.com/login/oauth/authorize?
   client_id=YOUR_CLIENT_ID&
   scope=repo,user:email&
   redirect_uri=http://localhost:5000/callback
   ↓
4. User sees GitHub authorization dialog
   - User reviews permissions
   - User clicks "Authorize CodeCityAI"
   ↓
5. GitHub redirects to: http://localhost:5000/callback?code=AUTH_CODE
   ↓
6. Backend exchanges code for access token with GitHub
   POST https://github.com/login/oauth/access_token
   ↓
7. Backend receives access token
   ↓
8. Backend redirects to React app with token:
   http://localhost:5173?token=ACCESS_TOKEN
   ↓
9. React app receives token and:
   - Saves to localStorage
   - Sets isAuthenticated = true
   - Shows sidebar (only for authenticated users)
   - Redirects to dashboard (codecity route)
   ↓
10. User is now logged in and sees the dashboard
```

## Key Features Implemented

✅ **Real GitHub OAuth Flow**
- Users see the GitHub authorization window
- All permissions are transparent and user-controlled

✅ **Error Handling**
- Invalid credentials detected
- Clear error messages shown
- Users know if configuration is missing

✅ **Token Persistence**
- Token saved to localStorage
- User stays logged in on page refresh
- Logout clears token and redirects to home

✅ **Protected Routes**
- Sidebar only visible when authenticated
- Dashboard inaccessible without login
- Home page always accessible

✅ **Navbar Features**
- Logout button visible when authenticated
- Can manage session from navbar

## User Journey

### First Time User (No Login)
1. Opens http://localhost:5173
2. Sees Home page with Login/Signup buttons
3. NO sidebar visible
4. Clicks Login → redirected to GitHub
5. Authorizes app
6. Get token → dashboard loads with sidebar visible

### Returning User (Has Token in localStorage)
1. Opens http://localhost:5173
2. App checks localStorage for token
3. Token found → automatically authenticated
4. Redirects to last page (or codecity)
5. Sidebar visible, logged in

### After Logout
1. User clicks Logout in navbar
2. Token deleted from localStorage
3. Redirects to Home page
4. Sidebar hidden, must login again

## What to Check If Not Working

### Login Button Does Nothing
- [ ] Check developer console for errors
- [ ] Verify GITHUB_CLIENT_ID is set in .env
- [ ] Restart Flask server after updating .env
- [ ] Check http://localhost:5000/auth-check

### Can See GitHub Authorization Window?
- If YES: OAuth is working! ✓
- If NO: Check Client ID configuration

### Authorization Fails
- [ ] Wrong Client Secret in .env
- [ ] Redirect URI mismatch in GitHub app settings
- [ ] Check app.py console for error messages

### Token Not Persisting
- [ ] Check browser localStorage (DevTools)
- [ ] Check if token is being set after OAuth callback
- [ ] Check redirect URL includes token parameter

## Testing Commands

```bash
# Check if backend is running
curl http://localhost:5000/

# Check if OAuth is configured
curl http://localhost:5000/auth-check

# Start Flask server
python app.py

# Start React dev server
cd ceo && npm run dev
```

## Important Notes

- **Redirect URI MUST be exactly**: http://localhost:5000/callback
- **Client ID and Secret** are different in development vs production
- **Token** is your GitHub access token - keep it secure
- **Sidebar** is conditionally rendered based on `isAuthenticated` state
- **Home page** is rendered WITHOUT AppLayout (no sidebar, no navbar with logout button)
