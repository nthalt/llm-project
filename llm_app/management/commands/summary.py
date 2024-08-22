from django.core.management.base import BaseCommand
from properties.models import Property

from llm_app.services import (  # rewrite_property_title,_description, write summary
    fetch_property_info,
    generate_property_summary,
    rewrite_property_title,
)


class Command(BaseCommand):
    """
    class for interacting with ollama models and updating property information
    """

    help = "Rewrites property titles and descriptions, and generates summaries using gemma2 model."

    def handle(self, *args, **kwargs):
        # Iterate over all properties
        properties = Property.objects.all()

        for property in properties:
            # Fetch property information
            property_info = fetch_property_info(property.property_id)

            if property_info:
                # Rewrite the property title
                new_title = rewrite_property_title(property_info)

                if new_title:
                    property.title = new_title
                    property.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updated title for property {property.property_id}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Failed to update title for property {property.property_id}"
                        )
                    )

    # def handle(self, *args, **kwargs):
    #     # Fetch all properties
    #     properties = Property.objects.all()

    #     for property_obj in properties:
    #         property_info = fetch_property_info(property_obj.property_id)

    #         # if property_info:
    #         #     # Rewrite title and description
    #         #     new_title, new_description = rewrite_property_title_description(
    #         #         property_info
    #         #     )

    #     #         if new_title and new_description:
    #     #             # Update property with new title and description
    #     #             property_obj.title = new_title
    #     #             property_obj.description = new_description
    #     #             property_obj.save()

    #     #         # Generate summary and save to PropertySummary table
    #     #         generate_property_summary(property_info)

    #     # self.stdout.write(self.style.SUCCESS("Successfully processed all properties."))
