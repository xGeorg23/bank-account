from enum import Enum


class TransactionType(Enum): 
    TRANSFER_INTERNAL = 'TRANSFER_INTERNAL'
    TRANSFER_EXTERNAL = 'TRANSFER_EXTERNAL'