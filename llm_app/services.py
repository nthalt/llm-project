import json

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


def parse_response(response_chunks, keyword):
    """
    Extracts the value associated with the keyword from the list of JSON chunks.
    Assumes each chunk is a JSON object containing a 'response' key.
    """
    response_text = ""
    for chunk in response_chunks:
        try:
            data = json.loads(chunk.decode("utf-8"))
            response_text += data.get("response", "")
        except json.JSONDecodeError:
            # Handle JSON parsing error
            print("Error decoding JSON chunk")

    # Now process the complete response text
    keyword = f"{keyword}: "
    start_index = response_text.find(keyword)

    if start_index == -1:
        return None

    start_index += len(keyword)
    end_index = response_text.find("\n", start_index)

    if end_index == -1:
        end_index = len(response_text)

    return response_text[start_index:end_index].strip()


def rewrite_property_title(property_info, model="gemma2:2b", retries=3):
    """
    Rewrites the title of the property using the specified model.
    Ensures data integrity by retrying on blank responses and handling errors.
    Uses streaming to handle large or chunked responses.
    """
    title = property_info.get("title")
    property_id = property_info.get("id")

    prompt = (
        f"Please rewrite the following property title to make it more attractive and readable while "
        f"preserving its original meaning. Ensure that the title reflects the nature and identity of "
        f"the property, but do not simply return the original title. Rephrase the title creatively while "
        f"keeping the key elements like the hotel name and location intact. Avoid changing the property "
        f"type or location information. Make sure the title is free of any extra symbols or punctuation.\n\n"
        f"Title: {title}\n\nGive only one new title and in the following format only:\nTitle: generated_title"
    )

    for attempt in range(retries):
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",  # Update with your API endpoint
                json={"prompt": prompt, "model": model},
                timeout=30,  # Timeout set to 10 seconds
                stream=True,  # Enable streaming
            )

            if response.status_code == 200:
                response_chunks = []

                # Process the response chunks as they arrive
                for chunk in response.iter_content(chunk_size=None):
                    if chunk:
                        response_chunks.append(chunk)  # Collect chunks

                response_text = parse_response(response_chunks, "Title")
                # print(f"Raw response text: {response_text}")  # Log the raw response

                new_title = response_text
                print(f"Previous title: {title}")
                print(f"New title: {new_title}")

                if new_title:
                    # Update the property title in the database
                    with transaction.atomic():
                        property_obj = Property.objects.get(property_id=property_id)
                        property_obj.title = new_title
                        property_obj.save()
                    return new_title

            else:
                # Handle non-200 responses
                print(
                    f"Unexpected response status {response.status_code} for property {property_id}."
                )

        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            # Handle request timeout or other request-related errors
            print(f"Attempt {attempt + 1} failed: {e}")

    print(
        f"Failed to rewrite title for property {property_id} after {retries} attempts."
    )
    return None


def write_property_description(property_info, model="gemma2:2b", retries=3):
    """
    Generates a description for the property based on its title using the specified model.
    Ensures data integrity by retrying on blank responses and handling errors.
    """
    title = property_info.get("title")
    property_id = property_info.get("id")

    prompt = (
        f"Write a concise, compelling description for the following hotel property. "
        f"Preserve the originality and identity of the hotel, but creatively rephrase it "
        f"to highlight its unique features. The description should be brief, around 2-3 sentences, "
        f"and make the hotel appealing to potential guests. Ensure that the description is free of any "
        f"extra symbols or punctuation. Give only one new description and in the following format only::\n\n"
        f"Description: generated_description\n\nTitle: {title}"
    )

    for attempt in range(retries):
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"prompt": prompt, "model": model},
                timeout=30,
                stream=True,
            )

            if response.status_code == 200:
                response_chunks = []

                # Process the response chunks as they arrive
                for chunk in response.iter_content(chunk_size=None):
                    if chunk:
                        response_chunks.append(chunk)

                description = parse_response(response_chunks, "Description")
                print(f"New description: {description}")  # Log the raw response

                # Remove unwanted punctuation and clean up description
                description = "".join(
                    c for c in description if c.isalnum() or c.isspace()
                ).strip()

                if description:
                    # Update the property title in the database
                    with transaction.atomic():
                        property_obj = Property.objects.get(property_id=property_id)
                        property_obj.description = description
                        property_obj.save()
                    return description

            else:
                print(
                    f"Unexpected response status {response.status_code} for property {property_id}."
                )

        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            print(f"Attempt {attempt + 1} failed: {e}")

    print(
        f"Failed to write description for property {property_id} after {retries} attempts."
    )
    return None


def generate_property_summary(property_info, model="gemma2:2b", retries=3):
    """
    Generates a summary for the property based on its title, description, location, and amenities.
    Ensures data integrity by retrying on blank responses and handling errors.
    """
    title = property_info.get("title")
    description = property_info.get("description")
    locations = property_info.get("locations")
    amenities = property_info.get("amenities")
    property_id = property_info.get("id")

    prompt = (
        f"Generate a concise, engaging summary for the following hotel property. "
        f"Use the provided information to highlight the key features, atmosphere, and appeal of the property. "
        f"The summary should be around 2-3 sentences and make the property stand out to potential guests. "
        f"Ensure that the summary is free of any extra symbols or punctuation. Give only one summary and in the following format only:\n\n"
        f"Summary: generated_summary\n\n"
        f"Title: {title}\n"
        f"Description: {description}\n"
        f"Location: {locations}\n"
        f"Amenities: {amenities}"
    )

    for attempt in range(retries):
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"prompt": prompt, "model": model},
                timeout=30,
                stream=True,
            )

            if response.status_code == 200:
                response_chunks = []
                for chunk in response.iter_content(chunk_size=None):
                    if chunk:
                        response_chunks.append(chunk)

                summary = parse_response(response_chunks, "Summary")
                summary = "".join(
                    c for c in summary if c.isalnum() or c.isspace()
                ).strip()

                if summary:
                    property_obj = Property.objects.get(property_id=property_id)
                    PropertySummary.objects.update_or_create(
                        property=property_obj, defaults={"summary": summary}
                    )
                    return summary

            else:
                print(
                    f"Unexpected response status {response.status_code} for property {property_id}."
                )

        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            print(f"Attempt {attempt + 1} failed: {e}")

    print(
        f"Failed to generate summary for property {property_id} after {retries} attempts."
    )
    return None
