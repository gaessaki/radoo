from .radish_object import RadishObject

class RadishAddress(RadishObject):
    def __init__(
            self,
            picking_partner = None
    ):
        """
        :param line1: First line of the address
        :param line2: Second line of the address
        :param city: City of the address
        :param province: Province of the address
        :param postal: Postal code of the address
        :param country: Country of the address
        :param notes: Additional notes for the address
        """
        self.line1 = getattr(picking_partner, 'street', '') or ''
        self.line2 = getattr(picking_partner, 'street2', '') or ''
        self.city = getattr(picking_partner, 'city', '') or ''
        self.province = getattr(getattr(picking_partner, 'state_id', None), 'name', '') or ''
        self.postal = getattr(picking_partner, 'zip', '') or ''
        self.country = getattr(picking_partner, 'country_code', '') or ''
        self.notes = getattr(picking_partner, 'comment', '') or ''
        

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