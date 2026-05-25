import pandas as pd

df = pd.read_csv("data/processed/amazon_fashion.csv")
print(f"Current items: {len(df)}")

amazon = df[df['category'].isin(['Fashion','Electronics','Beauty'])].copy()
nigerian = df[df['category'].isin(['Books','Food','Restaurants'])].copy()

samples = []
for domain, group in amazon.groupby('category'):
    group = group.copy()
    if 'review_count' in group.columns:
        group['review_count'] = pd.to_numeric(group['review_count'], errors='coerce').fillna(0)
        sampled = group.nlargest(60, 'review_count')
    else:
        sampled = group.head(60)
    samples.append(sampled)

final = pd.concat(samples + [nigerian], ignore_index=True)
final.to_csv("data/processed/amazon_fashion.csv", index=False)
print(f"Reduced to: {len(final)} items")
print(final['category'].value_counts())