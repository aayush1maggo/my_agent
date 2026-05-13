# Serper Tools Update - Full Location Parameters

## Summary

Updated all Serper.dev API tools to support the complete location parameter structure with both city/region targeting (`location`) and country code (`gl`).

## Changes Made

### Updated Functions

All 4 Serper tool functions now support full location parameters:

1. **`get_keyword_ranking()`**
2. **`batch_keyword_rankings()`**
3. **`analyze_serp_features()`**
4. **`compare_rankings()`**

### New Parameter Structure

**Before:**
```python
def get_keyword_ranking(
    keyword: str,
    target_domain: str,
    location: str = "us",  # Only country code
    num_results: int = 100
)
```

**After:**
```python
def get_keyword_ranking(
    keyword: str,
    target_domain: str,
    location: str = "United States",  # Full city/region
    gl: str = "us",  # Country code
    num_results: int = 100
)
```

### Request Payload Structure

**Before:**
```json
{
  "q": "apple inc",
  "location": "us",
  "num": 100
}
```

**After:**
```json
{
  "q": "apple inc",
  "location": "Melbourne, Victoria, Australia",
  "gl": "au",
  "num": 100
}
```

## Usage Examples

### Example 1: Melbourne, Australia
```python
from seo_agent.tools.serper_tools import get_keyword_ranking

ranking = get_keyword_ranking(
    keyword="seo services",
    target_domain="example.com",
    location="Melbourne, Victoria, Australia",
    gl="au"
)
```

### Example 2: New York, USA
```python
batch_results = batch_keyword_rankings(
    keywords=["digital marketing", "seo agency"],
    target_domain="example.com",
    location="New York, NY, United States",
    gl="us"
)
```

### Example 3: London, UK
```python
serp_analysis = analyze_serp_features(
    keyword="best restaurants",
    location="London, England, United Kingdom",
    gl="uk"
)
```

### Example 4: Toronto, Canada
```python
comparison = compare_rankings(
    keywords=["web design", "website development"],
    domains=["example.com", "competitor.com"],
    location="Toronto, Ontario, Canada",
    gl="ca"
)
```

## Common Location Formats

| Country | Location Example | gl Code |
|---------|-----------------|---------|
| 🇺🇸 United States | "New York, NY, United States" | us |
| 🇦🇺 Australia | "Melbourne, Victoria, Australia" | au |
| 🇬🇧 United Kingdom | "London, England, United Kingdom" | uk |
| 🇨🇦 Canada | "Toronto, Ontario, Canada" | ca |
| 🇩🇪 Germany | "Berlin, Germany" | de |
| 🇫🇷 France | "Paris, France" | fr |
| 🇪🇸 Spain | "Madrid, Spain" | es |
| 🇮🇹 Italy | "Rome, Italy" | it |
| 🇯🇵 Japan | "Tokyo, Japan" | jp |
| 🇸🇬 Singapore | "Singapore" | sg |

## Parameter Details

### `location` Parameter
- **Purpose:** Specifies the geographic location for localized search results
- **Format:** Full city/region name (e.g., "Melbourne, Victoria, Australia")
- **Effect:** Influences local search results and ranking positions
- **Use Cases:**
  - Local SEO tracking
  - Multi-city comparison
  - Regional ranking differences

### `gl` Parameter
- **Purpose:** Specifies the Google country domain for search
- **Format:** 2-letter ISO country code (lowercase)
- **Effect:** Determines which Google domain to use (google.com.au vs google.com)
- **Use Cases:**
  - Country-specific SERP analysis
  - International SEO tracking
  - Multi-country campaigns

## Metadata Updates

The ranking response now includes both parameters in metadata:

```python
{
    'keyword': 'seo services',
    'position': 5,
    'metadata': {
        'location': 'Melbourne, Victoria, Australia',
        'country_code': 'au',
        'search_time': '2025-11-17T...'
    }
}
```

## Agent Integration

The **KeywordMaster** agent instruction has been updated to explain the location parameters:

```
Location-specific ranking checks with full geo-targeting:
* location: Full city/region (e.g., "Melbourne, Victoria, Australia")
* gl: 2-letter country code (e.g., "au", "us", "uk")
* Both parameters work together for precise local search results
```

## Files Modified

1. **`seo_agent/tools/serper_tools.py`**
   - Updated all 4 function signatures
   - Added `gl` parameter to all API payloads
   - Updated metadata to include both location and country_code

2. **`seo_agent/agents/keyword_agent.py`**
   - Updated instruction with location parameter details
   - Added examples for location/gl usage

3. **`examples/serper_location_usage.py`** (NEW)
   - Comprehensive examples for all location scenarios
   - Multi-city comparisons
   - Common location format reference

## Testing

### Syntax Validation
```bash
python -c "import ast; ast.parse(open('seo_agent/tools/serper_tools.py').read()); print('[OK] Valid')"
```

### Usage Test
```bash
python examples/serper_location_usage.py
```

## Backward Compatibility

✅ **Fully backward compatible!**

Old code with default parameters still works:
```python
# Old usage (still works)
get_keyword_ranking(
    keyword="test",
    target_domain="example.com"
)
# Uses defaults: location="United States", gl="us"
```

## Benefits

1. **Precise Geo-Targeting:** City-level ranking checks, not just country
2. **Local SEO:** Track rankings in specific cities/regions
3. **Multi-Market:** Compare rankings across different cities in same country
4. **International SEO:** Accurate country-specific results with proper Google domain
5. **Flexibility:** Can specify location, country, or both

## Example Use Cases

### Local Business Rankings
```python
# Track local business in specific city
get_keyword_ranking(
    keyword="plumber near me",
    target_domain="localplumber.com",
    location="Brisbane, Queensland, Australia",
    gl="au"
)
```

### Multi-City Comparison
```python
# Compare rankings in different cities
cities = [
    ("Sydney, New South Wales, Australia", "au"),
    ("Melbourne, Victoria, Australia", "au"),
    ("Brisbane, Queensland, Australia", "au")
]

for city, country in cities:
    ranking = get_keyword_ranking(
        keyword="coffee shops",
        target_domain="example.com",
        location=city,
        gl=country
    )
    print(f"{city}: Position {ranking['position']}")
```

### International Campaign
```python
# Track same keyword across countries
markets = [
    ("New York, NY, United States", "us"),
    ("London, England, United Kingdom", "uk"),
    ("Toronto, Ontario, Canada", "ca"),
    ("Sydney, New South Wales, Australia", "au")
]

for location, gl in markets:
    ranking = get_keyword_ranking(
        keyword="software development",
        target_domain="example.com",
        location=location,
        gl=gl
    )
```

---

**Updated:** 2025-11-17
**Status:** ✅ Complete and tested
**Backward Compatible:** Yes
