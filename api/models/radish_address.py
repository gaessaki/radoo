from .radish_object import RadishObject

class RadishAddress(RadishObject):
    def __init__(
            self,
            picking_partner
    ):
        """
        :param picking_partner: Partner record of the picking
        """
        self.line1 = picking_partner.street or ''
        self.line2 = picking_partner.street2 or ''
        self.city = picking_partner.city or ''
        self.province = picking_partner.state_id.name or ''
        self.postal = picking_partner.zip or ''
        self.country = picking_partner.country_id.name or ''
        self.notes = picking_partner.comment or ''
        

    def toJSON(self):
        return {
            'line1': self.line1,
            'line2': self.line2,
            'city': self.city,
            'province': self.province,
            'postal': self.postal,
            'country': self.country,
            'notes': self.notes
        }