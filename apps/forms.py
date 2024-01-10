from django import forms

from apps.models import Class, Instance, InstanceInstanceConnection, RAW_TYPE_CHOICES, PropertyType, \
    type_limitation_template


class ClassForm(forms.ModelForm):
    name = forms.CharField(
        max_length=50,
        label='Class Name',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Animal'
            }
        ),
        help_text='Enter the name of the class'
    )

    class Meta:
        model = Class
        fields = ['name']

    def clean(self):
        cleaned_data = super(ClassForm, self).clean()
        name = cleaned_data.get("name")
        exist_class = Class.objects.filter(name=name)
        if exist_class.exists():
            self.add_error('name', f'The class with name {name} already exists')
        return cleaned_data


class InstanceForm(forms.ModelForm):
    name = forms.CharField(
        max_length=50,
        label='Instance Name',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Alpaca'
            }
        ),
        help_text='Enter the name of the instance'
    )

    class_instance = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        ),
        help_text='Select the class that this instance will be in'
    )

    class Meta:
        model = Instance
        fields = ['name', 'class_instance']

    def clean(self):
        cleaned_data = super(InstanceForm, self).clean()
        name = cleaned_data.get("name")
        class_instance = cleaned_data.get("class_instance")
        exist_instance = Instance.objects.filter(name=name, class_instance=class_instance)
        if exist_instance.exists():
            raise forms.ValidationError(
                f"The instance with name {name} already exists in {class_instance}",
                code='invalid'
            )
        return cleaned_data


class InstanceInstanceConnectionForm(forms.ModelForm):
    name = forms.CharField(
        max_length=50,
        label='Connection Name',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Eats'
            }
        ),
        help_text='Enter the name of the connection'
    )

    first_instance_class = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        label='From Class',
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        ),
        help_text='Select the first class that this connection will be in'
    )

    second_instance_class = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        label='To Class',
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        ),
        help_text='Select the second class that this connection will be in'
    )

    class Meta:
        model = InstanceInstanceConnection
        fields = ['name', 'first_instance_class', 'second_instance_class']

    def clean(self):
        cleaned_data = super(InstanceInstanceConnectionForm, self).clean()
        first_instance_class = cleaned_data.get("first_instance_class")
        second_instance_class = cleaned_data.get("second_instance_class")
        exist_connection = InstanceInstanceConnection.objects.filter(first_instance_class=first_instance_class, second_instance_class=second_instance_class)
        if exist_connection.exists():
            raise forms.ValidationError(
                f"The connection between {first_instance_class} and {second_instance_class} already exists ({exist_connection.first().name})",
                code='invalid'
            )
        return cleaned_data


class PropertyTypeForm(forms.ModelForm):
    name = forms.CharField(
        max_length=50,
        label='Property Type Name',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'haveLegs'
            }
        ),
        help_text='Enter the name of the property type'
    )

    class_instance = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        label='Class',
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        ),
        help_text='Select the class that can have this property type'
    )

    raw_type = forms.ChoiceField(
        choices=RAW_TYPE_CHOICES,
        label='Raw Type',
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        ),
        help_text='Select the raw type of the property type'
    )

    limitation = forms.JSONField(
        label='Limitation',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control'
            }
        ),
        required=False,
        help_text='Enter the limitation of the property type in JSON format, if want to use default, leave it blank'
    )

    class Meta:
        model = PropertyType
        fields = ['name', 'class_instance', 'raw_type', 'limitation']

    def clean(self):
        cleaned_data = super(PropertyTypeForm, self).clean()
        name = cleaned_data.get("name")
        raw_type = cleaned_data.get("raw_type")
        class_instance = cleaned_data.get("class_instance")
        exist_property_type = PropertyType.objects.filter(name=name, class_instance=class_instance, raw_type=raw_type)
        if exist_property_type.exists():
            raise forms.ValidationError(
                f"The property type with name {name} already exists in {class_instance} with raw type {raw_type}",
                code='invalid'
            )
        # check if the limitation is valid
        limitation = cleaned_data.get("limitation")
        if limitation:
            # no duplication key in JSON
            if len(limitation) != len(set(limitation.keys())):
                self.add_error('limitation', f'The limitation must not have duplication key')
            # remove the key that is not allowed from template
            need_remove = []
            for key in limitation.keys():
                if key not in type_limitation_template[raw_type].keys():
                    need_remove.append(key)
            for key in need_remove:
                limitation.pop(key)
            if raw_type == 'string':
                allowed_key = type_limitation_template['string'].keys()
                for key in limitation.keys():
                    if key not in allowed_key:
                        self.add_error('limitation', f'The limitation key {key} is not allowed for raw type {raw_type}')
                if 'min_length' in limitation:
                    if not isinstance(limitation['min_length'], int):
                        self.add_error('limitation', f'The limitation min_length must be an integer')
                if 'max_length' in limitation:
                    if not isinstance(limitation['max_length'], int):
                        self.add_error('limitation', f'The limitation max_length must be an integer')
            elif raw_type == 'number':
                if 'min_value' in limitation:
                    if not isinstance(limitation['min_value'], int):
                        self.add_error('limitation', f'The limitation min_value must be an integer')
                if 'max_value' in limitation:
                    if not isinstance(limitation['max_value'], int):
                        self.add_error('limitation', f'The limitation max_value must be an integer')
            elif raw_type == 'float':
                if 'min_value' in limitation:
                    if not isinstance(limitation['min_value'], float) and not isinstance(limitation['min_value'], int):
                        self.add_error('limitation', f'The limitation min_value must be a float or integer')
                if 'max_value' in limitation:
                    if not isinstance(limitation['max_value'], float) and not isinstance(limitation['max_value'], int):
                        self.add_error('limitation', f'The limitation max_value must be a float or integer')
                if 'decimal_places' in limitation:
                    if not isinstance(limitation['decimal_places'], int):
                        self.add_error('limitation', f'The limitation decimal_places must be an integer')
            elif raw_type == 'instance':
                if 'class_id' in limitation:
                    if not isinstance(limitation['class_id'], int):
                        self.add_error('limitation', f'The limitation class_id must be an integer')
                    try:
                        Class.objects.get(id=limitation['class_id'])
                    except Class.DoesNotExist:
                        self.add_error('limitation', f'The limitation class_id must be an existing class id')
            elif raw_type == 'instance_list':
                if 'allow_class_id_list' in limitation:
                    if not isinstance(limitation['allow_class_id_list'], list):
                        self.add_error('limitation', f'The limitation allow_class_id_list must be a list')
                    else:
                        for class_id in limitation['allow_class_id_list']:
                            if not isinstance(class_id, int):
                                self.add_error('limitation', f'The limitation allow_class_id_list must be a list of integer')
                            try:
                                Class.objects.get(id=class_id)
                            except Class.DoesNotExist:
                                self.add_error('limitation', f'The limitation allow_class_id_list ({class_id}) must be an existing class id')
        else:
            # replace the limitation with default
            cleaned_data['limitation'] = type_limitation_template[raw_type]
        return cleaned_data


class ObjectPropertyStringForm(forms.Form):
    value = forms.CharField(
        max_length=255,
        label='Value',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        ),
        help_text='Enter the value of the property'
    )

    def __init__(self, *args, **kwargs):
        self.min_length = kwargs.pop('min_length')
        self.max_length = kwargs.pop('max_length')
        self.initial_value = kwargs.pop('initial_value')
        if self.initial_value:
            self.base_fields['value'].initial = self.initial_value
        if self.max_length:
            self.base_fields['value'].max_length = self.max_length
        super(ObjectPropertyStringForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ObjectPropertyStringForm, self).clean()
        value = cleaned_data.get("value")
        if len(value) < self.min_length:
            self.add_error('value', f'The value must not be shorter than {self.min_length}')
        if len(value) > self.max_length:
            self.add_error('value', f'The value must not be longer than {self.max_length}')
        return cleaned_data


class ObjectPropertyNumberForm(forms.Form):
    value = forms.IntegerField(
        label='Value',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        ),
        help_text='Enter the value of the property'
    )

    def __init__(self, *args, **kwargs):
        self.min_value = kwargs.pop('min_value')
        self.max_value = kwargs.pop('max_value')
        self.initial_value = kwargs.pop('initial_value')
        if self.initial_value:
            self.base_fields['value'].initial = self.initial_value
        super(ObjectPropertyNumberForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ObjectPropertyNumberForm, self).clean()
        value = cleaned_data.get("value")
        if value < self.min_value or value > self.max_value:
            self.add_error('value', f'The value must be between {self.min_value} and {self.max_value}')
        return cleaned_data


class ObjectPropertyFloatForm(forms.Form):
    value = forms.FloatField(
        label='Value',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        ),
        help_text='Enter the value of the property'
    )

    def __init__(self, *args, **kwargs):
        self.min_value = kwargs.pop('min_value')
        self.max_value = kwargs.pop('max_value')
        self.decimal_places = kwargs.pop('decimal_places')
        self.initial_value = kwargs.pop('initial_value')
        if self.initial_value:
            self.base_fields['value'].initial = self.initial_value
        super(ObjectPropertyFloatForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ObjectPropertyFloatForm, self).clean()
        value = cleaned_data.get("value")
        if value < self.min_value or value > self.max_value:
            self.add_error('value', f'The value must be between {self.min_value} and {self.max_value}')
        # change decimal places
        cleaned_data['value'] = round(value, self.decimal_places)
        return cleaned_data


class ObjectPropertyBooleanForm(forms.Form):
    value = forms.BooleanField(
        label='Value',
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-control'
            }
        ),
        help_text='Enter the value of the property'
    )

    def __init__(self, *args, **kwargs):
        self.initial_value = kwargs.pop('initial_value')
        if self.initial_value:
            self.base_fields['value'].initial = self.initial_value
        super(ObjectPropertyBooleanForm, self).__init__(*args, **kwargs)


class ObjectPropertyDateForm(forms.Form):
    value = forms.DateField(
        label='Value',
        widget=forms.DateInput(
            attrs={
                'class': 'form-control'
            }
        ),
        help_text='Enter the value of the property'
    )

    def __init__(self, *args, **kwargs):
        self.initial_value = kwargs.pop('initial_value')
        if self.initial_value:
            self.base_fields['value'].initial = self.initial_value
        super(ObjectPropertyDateForm, self).__init__(*args, **kwargs)


class ObjectPropertyDateTimeForm(forms.Form):
    value = forms.DateTimeField(
        label='Value',
        widget=forms.DateTimeInput(
            attrs={
                'class': 'form-control'
            }
        ),
        help_text='Enter the value of the property'
    )

    def __init__(self, *args, **kwargs):
        self.initial_value = kwargs.pop('initial_value')
        if self.initial_value:
            self.base_fields['value'].initial = self.initial_value
        super(ObjectPropertyDateTimeForm, self).__init__(*args, **kwargs)


class ObjectPropertyMarkdownForm(forms.Form):
    # TODO: Change this to markdown editor
    value = forms.CharField(
        label='Value',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control'
            }
        ),
        help_text='Enter the value of the property'
    )

    def __init__(self, *args, **kwargs):
        self.initial_value = kwargs.pop('initial_value')
        if self.initial_value:
            self.base_fields['value'].initial = self.initial_value
        super(ObjectPropertyMarkdownForm, self).__init__(*args, **kwargs)


class ObjectPropertyImageForm(forms.Form):
    value = forms.ImageField(
        label='Value',
        widget=forms.FileInput(
            attrs={
                'class': 'form-control'
            }
        ),
        help_text='Enter the value of the property'
    )


class ObjectPropertyFileForm(forms.Form):
    value = forms.FileField(
        label='Value',
        widget=forms.FileInput(
            attrs={
                'class': 'form-control'
            }
        ),
        help_text='Enter the value of the property'
    )


class ObjectPropertyInstanceForm(forms.Form):
    value = forms.ModelChoiceField(
        queryset=Instance.objects.all(),
        label='Value',
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        ),
        help_text='Select the value of the property'
    )

    def __init__(self, *args, **kwargs):
        self.class_id = kwargs.pop('class_id')
        self.initial_value = kwargs.pop('initial_value')
        if self.initial_value:
            self.base_fields['value'].initial = self.initial_value
        if self.class_id != 0:
            self.base_fields['value'].help_text = f'Select the value of the property (only instance in {Class.objects.get(id=self.class_id)} will be shown)'
            self.base_fields['value'].queryset = Instance.objects.filter(class_instance__id=self.class_id)
        super(ObjectPropertyInstanceForm, self).__init__(*args, **kwargs)


class ObjectPropertyInstanceListForm(forms.Form):
    value = forms.ModelMultipleChoiceField(
        queryset=Instance.objects.all(),
        label='Value',
        widget=forms.SelectMultiple(
            attrs={
                'class': 'form-control'
            }
        ),
        help_text='Select the value of the property'
    )

    def __init__(self, *args, **kwargs):
        self.class_id_list = kwargs.pop('class_id_list')
        self.initial_value = kwargs.pop('initial_value')
        if self.initial_value:
            self.base_fields['value'].initial = self.initial_value
        if self.class_id_list:
            self.base_fields['value'].help_text = f'Select the value of the property (only instance in {Class.objects.filter(id__in=self.class_id_list)} will be shown)'
        self.base_fields['value'].queryset = Instance.objects.filter(class_instance__id__in=self.class_id_list)
        super(ObjectPropertyInstanceListForm, self).__init__(*args, **kwargs)
