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

        current_partner = picking_partner
        self.phone = current_partner.phone
        self.email = current_partner.email
        while current_partner and (not self.phone or not self.email):
            if not self.phone:
                self.phone = current_partner.phone
            if not self.email:
                self.email = current_partner.email

            current_partner = current_partner.parent_id

    def toJSON(self):
        return {
            'first':   self.first,
            'last':    self.last,
            'company': self.company,
            'phone':   self.phone,
            'email':   self.email,
        }
