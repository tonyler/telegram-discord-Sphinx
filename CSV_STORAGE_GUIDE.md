# CSV Storage Guide

The application supports CSV file storage as an alternative to PostgreSQL, making it easy to view and edit data in Excel, Google Sheets, or any spreadsheet application.

## How It Works

Instead of using a PostgreSQL database, all user data is stored in two CSV files:

1. `data/users.csv` - Stores user records
2. `data/bindings.csv` - Stores social media account bindings

## CSV File Structure

### users.csv

| Column | Description | Example |
|--------|-------------|---------|
| id | Unique user ID | 1 |
| created_at | When user was created | 2025-01-15T10:30:00 |
| updated_at | Last update timestamp | 2025-01-15T10:30:00 |

**Example:**
```csv
id,created_at,updated_at
1,2025-01-15T10:30:00.123456,2025-01-15T10:30:00.123456
2,2025-01-15T11:00:00.789012,2025-01-15T11:00:00.789012
```

### bindings.csv

| Column | Description | Example |
|--------|-------------|---------|
| id | Unique binding ID | 1 |
| user_id | ID of the user | 1 |
| platform | Platform name | discord |
| platform_user_id | User's ID on the platform | 123456789 |
| platform_username | Username on platform | johndoe |
| access_token | OAuth2 access token | ya29.a0Af... |
| refresh_token | OAuth2 refresh token | 1//0gX... |
| created_at | When binding was created | 2025-01-15T10:30:00 |
| updated_at | Last update timestamp | 2025-01-15T10:30:00 |

**Example:**
```csv
id,user_id,platform,platform_user_id,platform_username,access_token,refresh_token,created_at,updated_at
1,1,discord,123456789,johndoe,access_token_here,,2025-01-15T10:30:00,2025-01-15T10:30:00
2,1,telegram,987654321,johndoe_tg,,,2025-01-15T10:35:00,2025-01-15T10:35:00
3,2,discord,111222333,janedoe,access_token_here,,2025-01-15T11:00:00,2025-01-15T11:00:00
4,2,twitter,444555666,janedoe_x,access_token_here,refresh_token_here,2025-01-15T11:05:00,2025-01-15T11:05:00
```

## Configuration

Set these values in your `.env` file:

```env
STORAGE_BACKEND=csv
CSV_DATA_DIR=data
```

## Opening CSV Files

### Excel
1. Navigate to the `data/` directory
2. Double-click `users.csv` or `bindings.csv`
3. Excel will open the file automatically

### Google Sheets
1. Go to Google Sheets
2. Click File > Import
3. Upload `users.csv` or `bindings.csv`
4. Select "Comma" as the separator

### LibreOffice Calc
1. Open LibreOffice Calc
2. Click File > Open
3. Select the CSV file
4. Choose "Comma" as the field separator

## Viewing Data

You can easily:
- Sort by any column
- Filter users by creation date
- Search for specific usernames
- See which platforms each user has bound
- Export to other formats (XLSX, PDF, etc.)

## Editing Data

You can manually edit the CSV files, but follow these rules:

1. **Never change IDs** - IDs must remain unique and unchanged
2. **Don't modify column headers** - Keep the first row exactly as is
3. **Use proper date format** - ISO 8601: `YYYY-MM-DDTHH:MM:SS.ffffff`
4. **Keep unique constraints** - Each `(platform, platform_user_id)` pair must be unique in bindings.csv
5. **Maintain relationships** - Every `user_id` in bindings.csv must exist in users.csv

## Safe Editing Examples

### Add a manual user (advanced)
1. Open `users.csv`
2. Add a new row with next ID number
3. Use current timestamp for both dates

### Update a username
1. Open `bindings.csv`
2. Find the binding row
3. Update `platform_username` column
4. Update `updated_at` to current timestamp

### Remove a binding
1. Open `bindings.csv`
2. Delete the entire row of the binding
3. Save the file

## Data Backup

Always backup CSV files before manual editing:

```bash
cp data/users.csv data/users.csv.backup
cp data/bindings.csv data/bindings.csv.backup
```

## Thread Safety

The CSV storage implementation uses file locking to prevent data corruption when multiple requests occur simultaneously. However, avoid editing CSV files while the application is running.

## Migration Between Storage Backends

### From CSV to SQL

```bash
# Export your CSV data
# Stop the application
# Change STORAGE_BACKEND to "sql" in .env
# Write migration script to import CSV to PostgreSQL
```

### From SQL to CSV

```bash
# Export SQL data to CSV format
# Stop the application
# Change STORAGE_BACKEND to "csv" in .env
# Place exported CSV files in data/ directory
```

## Advantages of CSV Storage

- No database server required
- Easy to view and understand data
- Can edit with familiar spreadsheet tools
- Simple to backup (just copy files)
- Easy to share and inspect
- Perfect for personal/small deployments

## Limitations

- Not suitable for high-traffic applications
- Manual editing can break data integrity
- No built-in database features (indexes, complex queries)
- Limited concurrent write performance

## Troubleshooting

### File not found error
- Ensure `data/` directory exists
- Check `CSV_DATA_DIR` in `.env` matches actual directory

### Data not updating
- Stop the application before manual edits
- Check file permissions
- Verify CSV format is correct

### Duplicate ID errors
- IDs must be unique within each file
- Use next available number for new rows
- Never reuse deleted IDs while app is running
