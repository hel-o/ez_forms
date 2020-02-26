### Easy form for Flask without any dependencies.

### Based on django forms and WTForms

### Python 3.x

Just clone this repo to your project module and use it.

### Example with Flask:
```python
from flask import request, jsonify, g
from ez_form import form_check_for_result

@app.route('/contact-form', methods=['POST'])
def post_some_view():
    form = ContactForm(request.get_json(), some_extra_value=g.some_extra_value)
    result, status = form_check_for_result(form)
    return jsonify(result), status


# forms.py
import ez_form


class ContactForm(ez_form.BaseForm):
    name = ez_form.TextField(required=True)
    gender = ez_form.ChoiceField(choices=('M', 'F'), required=True)
    age = ez_form.IntegerField(min_value=18)
    
    def validate_business(self):
        # TODO: some database query...
        some_extra_value = self.kwargs['some_extra_value']
        print(f'the value: {some_extra_value}')
        
        # print values:
        print(self.name.data)
        print(self.gender.data)

        # Some dummy validation:
        if self.age.data > 150:
            self.add_error('age', 'You are to old')

    def save(self) -> Dict:
        # TODO: save to database:
        some_extra_value = self.kwargs['some_extra_value']
        print(f'the value: {some_extra_value}')
        return {'id': 1}
```
