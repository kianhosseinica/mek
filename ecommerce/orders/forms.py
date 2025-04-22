from django import forms
from django.forms.widgets import ClearableFileInput
from .models import RefundRequest, RefundMedia

class RefundRequestForm(forms.ModelForm):
    class Meta:
        model = RefundRequest
        fields = ["order", "order_item", "quantity", "refund_reason", "additional_comments"]
        widgets = {
            "refund_reason": forms.Select(choices=[
                ("damaged", "Product damaged"),
                ("wrong_item", "Wrong item received"),
                ("not_as_described", "Product not as described"),
                ("other", "Other"),
            ]),
            "additional_comments": forms.Textarea(attrs={"rows": 3}),
        }

class MultiClearableFileInput(ClearableFileInput):
    allow_multiple_selected = True

class RefundMediaForm(forms.ModelForm):
    """Handles multiple image/video uploads for refund requests."""
    media_files = forms.FileField(
        widget=MultiClearableFileInput(attrs={'multiple': True}),
        required=False
    )

    class Meta:
        model = RefundMedia
        fields = ["media_files"]

    def save(self, refund_request):
        """
        Custom save method to handle multiple files.
        """
        media_files = self.files.getlist('media_files')  # Get list of uploaded files
        for file in media_files:
            RefundMedia.objects.create(refund_request=refund_request, media_file=file)

from django import forms
from orders.models import Order

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }