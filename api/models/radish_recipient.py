from .radish_object import RadishObject

class RadishRecipient(RadishObject):
    def __init__(
            self,
            picking_partner = None
    ):
        """
        :param first: First name of the recipient
        :param last: Last name of the recipient
        :param company: Company name of the recipient, if any
        :param phone: Phone number of the recipient
        """
        self.first = getattr(picking_partner, 'name', '') or ''
        self.last = ''
        self.company = getattr(picking_partner, 'company_name', '') or ''
        self.phone = getattr(picking_partner, 'phone', '') or ''

    def toJSON(self):
        return {
            'first': self.first,
            'last': self.last,
            'company': self.company,
            'phone': self.phone
        }