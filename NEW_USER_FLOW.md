# New User Flow Documentation

The app has been restructured to provide a cleaner, more intuitive user experience with Discord as the primary authentication method.

## User Journey

### 1. Landing Page (Unauthenticated)
**URL:** `http://localhost:8000/`

**What users see:**
- Clean welcome message
- Single "Sign in with Discord" button
- Explanation that Discord is used for authentication
- Note that account is auto-created on first sign-in

**What happens:**
- If user already has a session → automatically redirected to `/dashboard`
- If no session → stays on landing page

### 2. Discord Authentication
**User clicks "Sign in with Discord"**

**Flow:**
1. Redirected to Discord OAuth page
2. User logs into Discord and authorizes the app
3. App receives authorization code
4. App exchanges code for access token
5. App fetches user's Discord profile
6. **If first time:** Creates new user account + Discord binding
7. **If returning:** Updates Discord binding with new tokens
8. **Sets session cookie** (7-day expiry, httponly, secure)
9. Redirects to `/dashboard`

**Key feature:** Discord binding can be refreshed/re-authenticated anytime

### 3. Dashboard (Authenticated)
**URL:** `http://localhost:8000/dashboard`

**What users see:**
- User ID display
- Sign Out button
- Requirements box showing:
  - ✓ or ✗ for Discord (Required)
  - ✓ or ✗ for Additional platform (Telegram or X)
  - Status message indicating completion level
- Three binding cards:
  - **Discord** - Shows connected status, username, ID
  - **Telegram** - Shows status, allows connection/re-authentication
  - **X (Twitter)** - Shows status, allows connection/re-authentication

**Status Messages:**
1. **All 3 platforms connected:**
   - "✓ All platforms connected! You have maximum community access."

2. **Discord + 1 other (minimum met):**
   - "⚠ Minimum requirements met. Connect more platforms for additional benefits!"

3. **Only Discord or incomplete:**
   - "✗ Please connect the required accounts to participate fully."

### 4. Connecting Additional Platforms

#### Telegram
**User clicks "Connect Telegram" button**

**Flow:**
1. User is authenticated (session required)
2. Redirected to Telegram OAuth with state parameter
3. User authorizes via Telegram app
4. Telegram redirects back with auth data
5. App verifies HMAC signature
6. **If already bound to this user:** Updates username
7. **If bound to different user:** Error message
8. **If not bound:** Creates new binding
9. Redirects to `/dashboard?success=telegram`

**Button changes:**
- Before binding: "Connect Telegram" (grey)
- After binding: "Re-authenticate Telegram" (blue)

#### X (Twitter)
**User clicks "Connect X" button**

**Flow:**
1. User is authenticated (session required)
2. App generates PKCE code verifier and challenge
3. Redirected to Twitter OAuth with challenge
4. User authorizes via Twitter
5. Twitter redirects back with authorization code
6. App exchanges code + verifier for tokens
7. **If already bound to this user:** Updates tokens and username
8. **If bound to different user:** Error message
9. **If not bound:** Creates new binding
10. Redirects to `/dashboard?success=twitter`

**Button changes:**
- Before binding: "Connect X" (grey)
- After binding: "Re-authenticate X" (blue)

### 5. Re-authentication

Users can re-authenticate ANY platform at ANY time:

**Discord Re-authentication:**
- Click "Re-authenticate Discord" on dashboard
- Goes through OAuth flow
- Updates access/refresh tokens
- Session remains valid
- Returns to dashboard

**Telegram Re-authentication:**
- Only available if already connected
- Click "Re-authenticate Telegram"
- Goes through OAuth flow
- Updates binding information
- Returns to dashboard

**Twitter Re-authentication:**
- Only available if already connected
- Click "Re-authenticate X"
- Goes through OAuth + PKCE flow
- Updates tokens and username
- Returns to dashboard

### 6. Sign Out
**User clicks "Sign Out" button**

**What happens:**
1. POST request to `/auth/logout`
2. Session cookie is cleared
3. User redirected to landing page
4. All bindings remain in database
5. User can sign back in anytime with Discord

## Technical Details

### Session Management
- **Cookie Name:** `session`
- **Duration:** 7 days
- **Security:** httponly, samesite=lax
- **Signed:** Using `SECRET_KEY` from environment
- **Content:** Encrypted user_id

### Route Protection
- **Public routes:** `/`, `/auth/discord`, `/auth/discord/callback`
- **Protected routes:** `/dashboard`, `/auth/telegram`, `/auth/twitter`, `/auth/me`
- **Auto-redirect:** If authenticated user visits `/`, redirects to `/dashboard`

### API Endpoints

#### GET `/auth/me`
**Requires:** Authentication (session cookie)

**Returns:**
```json
{
  "user_id": 1,
  "bindings": {
    "discord": {
      "username": "johndoe",
      "platform_user_id": "123456789",
      "bound": true
    },
    "telegram": {
      "username": "johndoe_tg",
      "platform_user_id": "987654321",
      "bound": true
    }
  },
  "is_complete": true,
  "all_platforms_bound": false
}
```

#### POST `/auth/logout`
**Requires:** No authentication needed

**Action:** Clears session cookie

**Returns:**
```json
{
  "message": "Logged out successfully"
}
```

## Key Improvements

### 1. Clearer User Flow
- Discord is clearly the authentication method
- Dashboard is the central account management hub
- No confusion about which platform to start with

### 2. Better Account Visibility
- See all connected accounts in one place
- Clear status indicators (✓ connected, ✗ not connected)
- Visual feedback on requirements

### 3. Re-authentication Support
- Users can refresh OAuth tokens
- Update usernames if changed on platforms
- No need to unbind and rebind

### 4. Flexible Requirements Display
- Shows 3 levels of completion
- Encourages connecting all platforms
- But still allows minimum participation

### 5. Security Enhancements
- Session-based authentication
- Automatic session expiry
- Protected routes require authentication
- OAuth state tokens prevent CSRF

## Example User Scenarios

### New User "Alice"
1. Visits app for first time
2. Clicks "Sign in with Discord"
3. Authorizes Discord → Account created, session started
4. Lands on dashboard → Sees Discord ✓, Telegram ✗, Twitter ✗
5. Status: "Please connect required accounts"
6. Clicks "Connect Telegram"
7. Authorizes Telegram → Returns to dashboard
8. Now sees Discord ✓, Telegram ✓, Twitter ✗
9. Status: "Minimum requirements met. Connect more platforms!"
10. Can now participate in community

### Returning User "Bob"
1. Visits app → Automatically redirected to dashboard (session still valid)
2. Sees all his connected accounts
3. Wants to refresh Discord token
4. Clicks "Re-authenticate Discord"
5. Goes through Discord OAuth
6. Returns to dashboard with updated token

### User "Carol" Updates Username
1. Changes username on Twitter
2. Visits dashboard
3. Clicks "Re-authenticate X"
4. Goes through Twitter OAuth
5. Dashboard now shows updated username

## Database/CSV Impact

### On First Discord Login
**users.csv:**
```csv
1,2025-01-15T10:00:00,2025-01-15T10:00:00
```

**bindings.csv:**
```csv
1,1,discord,discord_user_id,johndoe,access_token,refresh_token,2025-01-15T10:00:00,2025-01-15T10:00:00
```

### After Adding Telegram
**bindings.csv:**
```csv
1,1,discord,discord_user_id,johndoe,access_token,refresh_token,2025-01-15T10:00:00,2025-01-15T10:00:00
2,1,telegram,telegram_user_id,johndoe_tg,,,2025-01-15T10:05:00,2025-01-15T10:05:00
```

### After Re-authenticating Discord
**bindings.csv (Discord row updated):**
```csv
1,1,discord,discord_user_id,johndoe,new_access_token,new_refresh_token,2025-01-15T10:00:00,2025-01-15T11:30:00
2,1,telegram,telegram_user_id,johndoe_tg,,,2025-01-15T10:05:00,2025-01-15T10:05:00
```

Note: `updated_at` timestamp changes on re-authentication.

## Migration from Old Flow

If you had the old version:
- Existing users and bindings remain intact
- Users just need to sign in with Discord to create session
- All existing bindings will show on dashboard
- No data migration needed
