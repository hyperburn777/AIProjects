import pandas as pd

# Load the dataset
df = pd.read_csv('0-Sandbox/wine_items.csv')

# Display column names for reference
print("Available columns:")
print(df.columns.tolist())
print()

# Filter for wine department only
wine_df = df[df['Department'] == 'WINE']
print(f"Total wine items: {wine_df.shape[0]}")

# Convert Retail column to numeric, handling non-numeric values
wine_df.loc[:, 'Retail'] = pd.to_numeric(wine_df['Retail'], errors='coerce')

# Remove rows where Retail price is missing
wine_df = wine_df[pd.Series(wine_df['Retail']).notna()]
print(f"Wine items with valid prices: {wine_df.shape[0]}")

# Calculate average wine price
average_price = wine_df['Retail'].mean()
print(f'Average wine price: ${average_price:.2f}')

# Find most common vintage
most_common_vintage = pd.Series(wine_df['Vintage']).mode().iloc[0]
vintage_count = (wine_df['Vintage'] == most_common_vintage).sum()
print(f'Most common vintage: {most_common_vintage}')
print(f'Number of wines with vintage {most_common_vintage}: {vintage_count}')

# Calculate average cost per ml
# First, convert Size column to numeric and extract ml values
size_series = pd.Series(wine_df['Size'])
size_numeric = pd.to_numeric(size_series.str.extract(r'(\d+)')[0], errors='coerce')
wine_df['Size'] = size_numeric

# Remove rows where Size is missing or invalid
wine_df_with_size = wine_df[pd.Series(wine_df['Size']).notna()].copy()
print(f"Wine items with valid size information: {wine_df_with_size.shape[0]}")

# Calculate cost per ml
wine_df_with_size['CostPerMl'] = wine_df_with_size['Retail'] / wine_df_with_size['Size']
average_cost_per_ml = wine_df_with_size['CostPerMl'].mean()
print(f'Average cost per ml: ${average_cost_per_ml:.4f}')