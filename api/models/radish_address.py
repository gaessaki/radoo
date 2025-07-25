from .radish_object import RadishObject


class RadishAddress(RadishObject):
    def __init__(
            self,
            line1,
            line2,
            city,
            province,
            postal,
            country,
            notes,
    ):
        self.line1 = line1 or ''
        self.line2 = line2 or ''
        self.city = city or ''
        self.province = province or ''
        self.postal = postal or ''
        self.country = country or ''
        self.notes = notes or ''

    def toJSON(self):
        return {
            'line1':    self.line1,
            'line2':    self.line2,
            'city':     self.city,
            'province': self.province,
            'postal':   self.postal,
            'country':  self.country,
            'notes':    self.notes
        }
