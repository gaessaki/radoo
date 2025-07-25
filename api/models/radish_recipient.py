from .radish_object import RadishObject


class RadishRecipient(RadishObject):
    def __init__(
            self,
            first,
            last,
            company,
            phone,
            email,
            language=None
    ):
        self.first = first
        self.last = last
        self.company = company
        self.phone = phone
        self.email = email
        self.language = language

    @staticmethod
    def sanitize_lang(lang):
        lang = lang or ''

        lang = lang.lower()
        if lang.startswith('fr'):
            return 'fr'
        elif lang.startswith('en'):
            return 'en'
        return None

    def toJSON(self):
        json = {
            'first':   self.first,
            'last':    self.last,
            'company': self.company,
            'phone':   self.phone,
            'email':   self.email,
        }
        if self.language:
            json['language'] = self.language
        return json
