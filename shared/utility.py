import re
from rest_framework.exceptions import ValidationError


email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

phone_regex = re.compile(r"^(?:\+998)?(?:1[257]|20|33|50|55|70|71|77|88|9[0-57-9])\d{7}$")

def check_email_or_phone(email_or_phone):

    if re.fullmatch(email_regex, email_or_phone):
        return 'email'
        
    if re.fullmatch(phone_regex, email_or_phone):
        return 'phone'

    raise ValidationError({"detail": "Email yoki telefon raqami noto'g'ri kiritildi!"})