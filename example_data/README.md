# Example CSV Data

This directory contains example CSV files showing the structure and format of the data.

## Files

- `users.csv` - Example user records
- `bindings.csv` - Example social account bindings

## Example Scenarios

### User 1 (ID: 1)
- Discord: johndoe (ID: 123456789012345678)
- Telegram: johndoe_tg (ID: 987654321)
- Status: Valid (Discord + Telegram)

### User 2 (ID: 2)
- Discord: janedoe (ID: 234567890123456789)
- Twitter: janedoe_x (ID: 3456789012)
- Status: Valid (Discord + Twitter)

## Field Descriptions

### users.csv
- `id`: Unique user identifier (auto-incrementing)
- `created_at`: ISO 8601 timestamp when user was created
- `updated_at`: ISO 8601 timestamp of last update

### bindings.csv
- `id`: Unique binding identifier (auto-incrementing)
- `user_id`: References user.id
- `platform`: One of: discord, telegram, twitter
- `platform_user_id`: The user's ID on that platform
- `platform_username`: The user's display name on that platform
- `access_token`: OAuth2 access token (may be empty for Telegram)
- `refresh_token`: OAuth2 refresh token (optional)
- `created_at`: ISO 8601 timestamp when binding was created
- `updated_at`: ISO 8601 timestamp of last update

## Notes

- Real access tokens are much longer than shown in examples
- Telegram bindings don't store access_token or refresh_token
- Each (platform, platform_user_id) combination must be unique
- Every user must have exactly one Discord binding
- Every user must have at least one additional platform binding
