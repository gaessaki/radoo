from .radish_object import RadishObject
from .radish_address import RadishAddress
from .radish_recipient import RadishRecipient

class RadishOrder(RadishObject):
    def __init__(
            self,
            order_ref: str,
            recipient: RadishRecipient,
            address: RadishAddress
    ):
        """
        :param order_ref: The order reference
        :param recipient: Recipient information
        :param address: Address of delivery
        """
        self.order_ref = order_ref
        self.recipient = recipient
        self.address = address

    def toJSON(self):
        return {
            'order_ref': self.order_ref,
            'recipient': self.recipient.toJSON(),
            'address': self.address.toJSON()
        }