import requests
from django.db import transaction
from properties.models import Property

from llm_app.models import PropertySummary


def fetch_property_info(property_id, print_output=False):
    """
    Fetches information about a property by its ID and optionally prints the details.

    Args:
        property_id (int): The ID of the property to fetch.
        print_output (bool): Whether to print the fetched information.

    Returns:
        dict or None: A dictionary containing the property information or None if the property does not exist.
    """
    try:
        # Fetch property by ID
        property_obj = Property.objects.select_related().get(property_id=property_id)

        # Collect information
        info = {
            "id": property_obj.property_id,
            "title": property_obj.title,
            "description": property_obj.description,
            "locations": list(
                property_obj.locations.values("name", "type", "latitude", "longitude")
            ),
            "amenities": list(property_obj.amenities.values_list("name", flat=True)),
            "create_date": property_obj.create_date,
            "update_date": property_obj.update_date,
        }

        # Optionally print the information
        if print_output:
            print("Fetched property information:")
            print(f"ID: {info['id']}")
            print(f"Title: {info['title']}")
            print(f"Description: {info['description']}")
            print(f"Create Date: {info['create_date']}")
            print(f"Update Date: {info['update_date']}")
            print("Locations:")
            for location in info["locations"]:
                print(
                    f"  Name: {location['name']}, Type: {location['type']}, Latitude: {location['latitude']}, Longitude: {location['longitude']}"
                )
            print("Amenities:")
            for amenity in info["amenities"]:
                print(f"  {amenity}")

        return info

    except Property.DoesNotExist:
        print(f"Property with ID {property_id} does not exist.")
        return None


def rewrite_property_title(property_info, model="gemma2", retries=3):
    """
    Rewrites the title of the property using the specified Ollama model.
    Ensures data integrity by retrying on blank responses and handling errors.
    """
    title = property_info.get("title")
    property_id = property_info.get("id")

    prompt = f"Rewrite the title for the following property:\nTitle: {title}"

    for attempt in range(retries):
        try:
            response = requests.post(
                "http://localhost:11434/api/gemma2",  # Assuming Ollama API runs locally on this endpoint
                json={"prompt": prompt},
                timeout=10,  # Timeout set to 10 seconds
            )
            if response.status_code == 200 and response.json():
                data = response.json()
                new_title = data.get("title")
                if new_title:
                    # Update the property title in the database
                    with transaction.atomic():
                        property_obj = Property.objects.get(property_id=property_id)
                        property_obj.title = new_title
                        property_obj.save()
                    return new_title
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            # Handle request timeout or other request-related errors
            print(f"Attempt {attempt + 1} failed: {e}")

    print(
        f"Failed to rewrite title for property {property_id} after {retries} attempts."
    )
    return None


def generate_property_summary(property_info, model="gemma2"):
    """
    Generates a summary using the Ollama model and saves it to the PropertySummary table.
    """
    prompt = (
        f"Generate a summary for the following property information:\n"
        f"Title: {property_info.get('title')}\n"
        f"Description: {property_info.get('description')}\n"
        f"Location: {property_info.get('locations')}\n"
        f"Amenities: {property_info.get('amenities')}\n"
    )

    response = requests.post(
        "http://localhost:11434/api/gemma2",  # Assuming Ollama API runs locally
        json={"prompt": prompt},
    )

    if response.status_code == 200 and response.json().get("summary"):
        summary = response.json().get("summary")
        property_obj = Property.objects.get(property_id=property_info["id"])
        PropertySummary.objects.update_or_create(
            property=property_obj, defaults={"summary": summary}
        )
    else:
        # Retry if the response is blank
        generate_property_summary(property_info, model)
