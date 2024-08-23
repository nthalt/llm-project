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

    def test_parse_response():
        test_response = "Title: Newly Renovated Hotel with Sea View"
        parsed_title = parse_response(test_response, "Title")
        print(
            f"Parsed title: {parsed_title}"
        )  # Should print "Newly Renovated Hotel with Sea View"

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
                # Rewrite the property title

                # test_parse_response()

                # new_title = rewrite_property_title(property_info)
                # print(f"new title:{new_title}")
                # if new_title:
                #     #     property.title = new_title
                #     #     property.save()
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

                # Try to generate the property description separately
                new_description = write_property_description(property_info)
                print(f"new description:{new_description}")
                if new_description:
                    # property.description = new_description
                    # property.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updated description for property {property.property_id}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Failed to update description for property {property.property_id}"
                        )
                    )
