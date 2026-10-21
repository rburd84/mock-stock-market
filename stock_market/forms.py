from django import forms
from django.contrib.auth.forms import UserCreationForm


class BootstrapUserCreationForm(UserCreationForm):
    """
    Customized registration form that extends Django's native UserCreationForm
    to automatically inject premium Bootstrap style definitions directly into widgets.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Loop through Django's auto-generated fields and append custom layout attributes
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'type': 'text',
                'class': 'form-control form-control-lg',  # Injects custom CSS classes into {{ field }}
                'placeholder': f'Enter {field_name.replace("1", "").replace("2", "")}'
            })
