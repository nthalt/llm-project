from django.core.management.base import BaseCommand
from properties.models import Property

from llm_app.services import (  # rewrite_property_title,_description, write summary
    fetch_property_info,
    generate_property_summary,
    parse_response,
    rewrite_property_title,
    test_parse_response,
    write_property_description,
)


class Command(BaseCommand):
    """
    Class for interacting with Ollama models and updating property information.
    """

    help = "Rewrites property titles and descriptions, and generates summaries using gemma2 model."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limit the number of properties to process",
        )

    def handle(self, *args, **kwargs):
        # Get the limit from command arguments
        limit = kwargs.get("limit")

        # Fetch properties with optional limit
        properties = Property.objects.all()
        if limit is not None:
            properties = properties[:limit]

        for property in properties:
            # Fetch property information
            property_info = fetch_property_info(property.property_id, True)

            if property_info:
                # test_parse_response()

                # new_title = rewrite_property_title(property_info)
                # print(f"new title:{new_title}")
                # if new_title:
                #     self.stdout.write(
                #         self.style.SUCCESS(
                #             f"Updated title for property {property.property_id}"
                #         )
                #     )
                # else:
                #     self.stdout.write(
                #         self.style.ERROR(
                #             f"Failed to update title for property {property.property_id}"
                #         )
                #     )

                # # Try to generate the property description separately
                # new_description = write_property_description(property_info)
                # print(f"new description:{new_description}")
                # if new_description:
                #     self.stdout.write(
                #         self.style.SUCCESS(
                #             f"Updated description for property {property.property_id}"
                #         )
                #     )
                # else:
                #     self.stdout.write(
                #         self.style.ERROR(
                #             f"Failed to update description for property {property.property_id}"
                #         )
                #     )

                # Generate the property summary
                new_summary = generate_property_summary(property_info)
                print(f"New summary: {new_summary}")
                if new_summary:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updated summary for property {property.property_id}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Failed to update summary for property {property.property_id}"
                        )
                    )
