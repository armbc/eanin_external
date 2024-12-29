from django import forms


class BootStrap:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs:
                old_class = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = "{} form-control".format(old_class)
                field.widget.attrs["placeholder"] = field.label
            else:
                field.widget.attrs = {"class": "form-control col-md-1", "placeholder": field.label}


class BootStrapModelForm(BootStrap, forms.ModelForm):
    pass


class BootStrapForm(BootStrap, forms.Form):
    pass
