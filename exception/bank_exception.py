class AccountFrozenError(Exception): 
    pass

class AccountClosedError(Exception): 
    pass

class InvalidOperationError(Exception): 
    pass

class InsufficientFundsError(Exception): 
    pass

class ValidationError(Exception): 
    pass

class NotFoundError(Exception): 
    pass

class NightOperationError(Exception): 
    pass

class BlockedError(Exception): 
    pass

class TransactionError(Exception):
    pass

class TransactionProcessingError(Exception):
    pass
class TransactionFailedError(Exception):
    pass