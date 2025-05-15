import pandas as pd
import numpy as np
import re

input_file = "/home/ubuntu/cleaned_deduplicated_keywords.csv"
output_file = "/home/ubuntu/keywords_with_intent.csv"

print(f"Loading cleaned keywords from {input_file}")
df = pd.read_csv(input_file)

print(f"Shape of dataframe before intent classification: {df.shape}")
print(f"Columns: {df.columns.tolist()}")

# Define intent markers (case-insensitive)
# These are examples and can be expanded significantly
intent_markers = {
    "transactional": [
        r"buy", r"purchase", r"order", r"hire", r"quote", r"price", r"cost of", r"pricing", r"service(s)?", r"agency", r"studio", r"company", r"provider(s)?", r"vendor(s)?", r"for hire", r"near me", # "near me" can also be local, but often transactional in service context
        r"cheap", r"affordable", r"best price"
    ],
    "commercial": [
        r"best", r"top", r"review(s)?", r"compare", r"comparison", r"vs", r"alternative(s)?",
        r"software", r"platform", r"tool(s)?", r"solution(s)?", r"examples", r"showcase", r"portfolio"
    ],
    "informational": [
        r"what is", r"what are", r"how to", r"why", r"when", r"guide", r"tutorial", r"learn", r"tips", r"ideas",
        r"benefits of", r"meaning of", r"definition", r"explain", r"free", r"template(s)?", r"resource(s)?"
    ],
    "local": [
        # More specific geo terms might be extracted separately if a geo column exists
        # For now, simple markers. More robust local would involve NLP/NER for locations.
        r"near me", # Repeated here, but transactional often takes precedence for services
        r"in [a-z]+ city", r"[a-z]+ city", # Very basic city pattern
        # Common geo-modifiers (e.g., city names, states) would ideally be identified more systematically
        # For this exercise, we'll rely on simpler keyword matches or assume a geo column if present.
        # Example: "vfx studio london", "video production new york"
        # This part would need significant improvement for real-world geo-targeting.
        # We will assume for now that if a keyword contains a known city/region it is local.
        # This is a placeholder for a more robust geo-location identification.
        r"london", r"new york", r"los angeles", r"toronto", r"vancouver", r"chicago", # Example cities
        r"uk", r"usa", r"canada", r"ca" # Example countries/states (CA could be Canada or California)
    ]
}

def classify_intent(keyword_str):
    if not isinstance(keyword_str, str):
        return "unknown" # Or some other default for non-string inputs
    
    keyword_lower = keyword_str.lower()

    # Check for Local intent first if it has strong geo signals
    # More specific geo terms (city names, states) would be better here
    # This is a simplified approach
    local_geo_terms = ["london", "new york", "los angeles", "toronto", "vancouver", "chicago", "montreal", "california", "texas", "florida", "ontario", "quebec", "british columbia", "uk", "usa", "canada"]
    for term in local_geo_terms:
        if f" {term} " in keyword_lower or keyword_lower.startswith(term + " ") or keyword_lower.endswith(" " + term):
            # Check if it's also strongly transactional
            for pattern in intent_markers["transactional"]:
                if re.search(pattern, keyword_lower):
                    return "local_transactional" # Could be a sub-category
            return "local"

    # Prioritize Transactional
    for pattern in intent_markers["transactional"]:
        if re.search(pattern, keyword_lower):
            return "transactional"
    
    # Then Commercial
    for pattern in intent_markers["commercial"]:
        if re.search(pattern, keyword_lower):
            return "commercial"

    # Then Informational
    for pattern in intent_markers["informational"]:
        if re.search(pattern, keyword_lower):
            return "informational"
            
    # Default or fallback (could be commercial or informational based on context)
    # For VFX studio, many unclassified might still be commercial investigation
    if "vfx" in keyword_lower or "visual effects" in keyword_lower or "animation" in keyword_lower or "video production" in keyword_lower or "motion graphics" in keyword_lower:
        return "commercial" # Default for industry-specific terms not caught by others
        
    return "informational" # General fallback

# Check if 'search_intent' column already exists. If not, create it.
if "search_intent" not in df.columns:
    df["search_intent"] = df["keyword"].apply(classify_intent)
    print("Created and populated \"search_intent\" column.")
else:
    # If it exists, fill NaN values or re-classify based on requirements
    # For this task, we assume it's missing and we are creating it.
    # If it exists and has values, we might only want to fill NaNs:
    # df["search_intent"] = df["search_intent"].fillna(df["keyword"].apply(classify_intent))
    # Or, if we need to re-classify all based on new rules:
    df["search_intent"] = df["keyword"].apply(classify_intent)
    print("Re-classified existing \"search_intent\" column.")

print("Value counts for search_intent:")
print(df["search_intent"].value_counts(dropna=False))

print(f"Shape of dataframe after intent classification: {df.shape}")
print(f"First 5 rows with search_intent:\n{df.head().to_string()}")

# Save the dataframe with intent classification
df.to_csv(output_file, index=False)
print(f"Data with search intent saved to {output_file}")

