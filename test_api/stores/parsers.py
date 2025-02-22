from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ValidationError, ParseError


class TypeValidationParser(JSONParser):
    def parse(self, stream, media_type=None, parser_context=None):
        print("Media type received:", media_type)
        print("Parser context:", parser_context)
        print("Stream content:", stream.read())
        stream.seek(0)  # Reset stream position after reading

        data = super().parse(stream, media_type, parser_context)
        print("Parsed data:", data)
        other_errors = self.check_string_or_int(data)
        if other_errors:
            raise ValidationError(other_errors)
        return data

    def check_string_or_int(request):
        print("checking string or int")
        string_fields = ["name", "address", "city", "state_abbrv"]
        allowed_types = (str, int)
        print(request.data)
        fields = [field for field in string_fields if field in request.data]
        errors = []
        for field in fields:
            # print(field)
            values = request.data.getlist(field)
            # print(values)
            if len(values) > 1 or type(values[0]) not in allowed_types:
                print(field)
                print(values)
                print([type(value) for value in values])
                errors.append({field: "Not a valid string or int."})
        return errors
