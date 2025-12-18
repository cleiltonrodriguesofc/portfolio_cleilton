from django import forms

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def to_python(self, data):
        if not data:
            return None
        if isinstance(data, list):
            return [super(MultipleFileField, self).to_python(d) for d in data]
        return super().to_python(data)

class UploadNotesForm(forms.Form):
    ASSET_TYPES = [
        ('Fundos e Acoes', 'Ações, FIIs e ETFs'),
        ('Futuros', 'Futuros (Mini Índice/Dólar)'),
    ]
    
    asset_type = forms.ChoiceField(choices=ASSET_TYPES, label="Tipo de Ativo")
    # Use MultipleFileField + required=False (to handle list manually if needed, or rely on custom to_python)
    # Actually, if to_python returns a list, clean() might complain if it expects something else?
    # Standard Form clean doesn't care type as long as Field cleans it.
    files = MultipleFileField(
        widget=MultipleFileInput(attrs={'multiple': True}),
        label="Selecione as Notas (PDF)"
    )
