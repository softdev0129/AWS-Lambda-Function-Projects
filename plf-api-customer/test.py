import requests
import json

# Sample data
# data = [
#     {
#         "name": "John",
#         "age": 30,
#         "city": "New York",
#         "country": "USA",
#         "Hobbies": ["reading", "swimming", "hiking", "swimming"],
#         "occupation": "programmer",
#         "favorite_foods": {"Breakfast": "pancakes", "Lunch": "", "dinner": "pasta", "Snack": ""},
#         "gear": {"type": "", "material": "", "color": None},
#         "affiliations": ["", "", ""],
#         "friends": [
#             {"name": "Jane", "age": 28, "city": "New York", "country": "USA", "occupation": None},
#             {"name": "Tom", "age": 32, "city": "London", "country": "UK", "occupation": "teacher"},
#             {"name": "Jane", "age": 28, "city": "New York", "country": "USA", "occupation": None}
#         ]
#     }
# ]
response = requests.get("https://coderbyte.com/api/challenges/json/date-list")
data = response.json()


# Function to sort dictionary keys case-insensitively
def sort_dict(d):
    if isinstance(d, dict):
        return {k: sort_dict(v) for k, v in sorted(d.items(), key=lambda item: item[0].lower())}
    elif isinstance(d, list):
        return [sort_dict(i) for i in d]
    return d


sorted_data = sort_dict(data)


# Function to remove duplicate dictionaries from lists
def remove_duplicates_from_lists(d):
    if isinstance(d, list):
        unique_items = []
        seen = []
        for item in d:
            # Convert dict to a tuple of items for hashable comparison
            item_tuple = tuple(item.items()) if isinstance(item, dict) else item
            if item_tuple not in seen:
                seen.append(item_tuple)
                unique_items.append(remove_duplicates_from_lists(item))
        return unique_items
    elif isinstance(d, dict):
        return {k: remove_duplicates_from_lists(v) for k, v in d.items()}
    return d


unique_data = remove_duplicates_from_lists(sorted_data)


# Function to remove dictionary properties with all values as empty strings or None
def remove_empty_properties(d):
    if isinstance(d, dict):
        # Recursively process each item in the dictionary and remove keys with empty values
        cleaned_dict = {k: remove_empty_properties(v) for k, v in d.items()}
        # Remove keys with empty strings, None, or completely empty dictionaries/lists
        return {k: v for k, v in cleaned_dict.items() if v not in ["", None, []]}
    elif isinstance(d, list):
        # Recursively process each item in the list and remove empty items
        cleaned_list = [remove_empty_properties(i) for i in d]
        # Remove any items that are empty strings, None, empty lists, or empty dictionaries
        return [i for i in cleaned_list if i not in ["", None, []]]
    return d


cleaned_data = remove_empty_properties(unique_data)

# Print final JSON output
print(json.dumps(cleaned_data, indent=4))
