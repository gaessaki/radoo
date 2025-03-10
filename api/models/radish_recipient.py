from .radish_object import RadishObject

class RadishRecipient(RadishObject):
    def __init__(
            self,
            picking_partner
    ):
        """
        :param picking_partner: Partner record of the picking
        """
        self.first = picking_partner.name or picking_partner.commercial_company_name or ''
        self.last = ''
        self.company = picking_partner.commercial_company_name
        self.phone = picking_partner.phone
        self.email = picking_partner.email

    def toJSON(self):
        return {
            'first': self.first,
            'last': self.last,
            'company': self.company,
            'phone': self.phone,
            'email': self.email,
        }