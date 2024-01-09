import pandas as pd
from bs4 import BeautifulSoup
import locale

# Setting locale to 'en_US' for formatting numbers with commas
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

def convert_tvl_to_number(tvl_text):
    tvl_text = tvl_text.replace('$', '').replace(',', '').strip().lower()
    multiplier = 1
    if 'm' in tvl_text:
        multiplier = 1e6
        tvl_text = tvl_text.replace('m', '')
    elif 'b' in tvl_text:
        multiplier = 1e9
        tvl_text = tvl_text.replace('b', '')
    return float(tvl_text) * multiplier

def extract_crv_percentage(crv_text):
    try:
        crv_text = crv_text.split('CRV')[0].strip()
        crv_text = crv_text.split('→')[-1].strip().replace('%', '').strip()
        return float(crv_text) / 100
    except (ValueError, IndexError):
        return 0.0  # Return 0 if the CRV percentage cannot be extracted

def extract_pool_name(td):
    # Extracts and formats the pool name from a td tag
    pool_text = td.get_text().strip()
    return ' '.join(pool_text.split())

file_path = "Curve pools.txt"
with open(file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, 'html.parser')
tr_tags = soup.find_all('tr')

# Print the table header
print(f"{'Row #':<10} | {'Pool Name':<30} | {'CRV %':<10} | {'TVL':<20} | {'CRV % * TVL':<20}")
print('-' * 92)

crv_percentages = []
tvls = []
pool_names = []
crv_times_tvl = []

row_num = 1
for tr in tr_tags:
    td_tags = tr.find_all('td')
    if td_tags:
        # Adjust the index as per the actual HTML structure to extract pool name
        pool_name_index = 1  # Adjust this index based on the actual HTML structure
        if len(td_tags) > pool_name_index:
            pool_name = extract_pool_name(td_tags[pool_name_index])
            pool_names.append(pool_name)

            crv_percentage = 0
            tvl_value = 0

            if len(td_tags) >= 3:
                crv_text = td_tags[-3].get_text()
                crv_percentage = extract_crv_percentage(crv_text)
                crv_percentages.append(crv_percentage)

            if len(td_tags) >= 1:
                tvl_text = td_tags[-1].get_text()
                tvl_value = convert_tvl_to_number(tvl_text)
                tvls.append(tvl_value)

            crv_tvl_product = crv_percentage * tvl_value
            crv_times_tvl.append(crv_tvl_product)

            formatted_tvl = locale.format_string("%d", int(tvl_value), grouping=True)
            formatted_crv_tvl_product = locale.format_string("%.2f", crv_tvl_product, grouping=True)
            print(f"{row_num:<10} | {pool_name:<30} | {crv_percentage*100:<10.2f}% | ${formatted_tvl:<20} | ${formatted_crv_tvl_product:<20}")
            row_num += 1

# Calculate the total CRV emitted
total_crv_emitted = sum((crv_percentage / 100) * tvl for crv_percentage, tvl in zip(crv_percentages, tvls))
print(f"Total CRV tokens emitted: {total_crv_emitted}")

# Create a DataFrame
df = pd.DataFrame({
    'Row #': range(1, len(crv_percentages) + 1),
    'Pool Name': pool_names,
    'CRV %': crv_percentages,
    'TVL': tvls,
    'CRV % * TVL': crv_times_tvl
})

# Convert TVL and CRV % * TVL to formatted strings with commas
df['TVL'] = df['TVL'].apply(lambda x: f"{x:,}")
df['CRV % * TVL'] = df['CRV % * TVL'].apply(lambda x: f"{x:,.2f}")

# Save to CSV file
output_file = 'curve_pools.csv'
df.to_csv(output_file, index=False)

print(f"Data has been saved to {output_file}")
