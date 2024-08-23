from django.db import models
from properties.models import Property


class PropertySummary(models.Model):
    """
    Model to store the LLM-generated summaries for properties
    """

    property = models.OneToOneField(
        Property, on_delete=models.CASCADE, related_name="summary"
    )
    summary = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Summary for {self.property.title}"
