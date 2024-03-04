from django import forms


FORMAT_CHOICES = (
    ('csv', 'csv'),
    ('json', 'json'),
    ('xls', 'xls'),
)


class ScrapForm(forms.Form):
    key_word = forms.CharField(max_length=55)
    from_page = forms.IntegerField()
    to_page = forms.IntegerField()
    export_format = forms.ChoiceField(choices=FORMAT_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
