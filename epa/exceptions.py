class AdminWebsiteError(Exception):
    """
    Base class
    """
    def __init__(self, message='', error=None):
        '''
        Constructor
        @param message
        @param error
        '''
        self.message = message
        self.error = error


class PersistenceError(AdminWebsiteError):
    """
    DB related exception
    """
    def __init__(self, *args, **kwargs):
        '''
        Constructor
        call super constructor
        '''
        super(PersistenceError, self).__init__(*args, **kwargs)


class RestServiceCallError(AdminWebsiteError):
    """
    Rest call related exception
    """
    def __init__(self, *args, **kwargs):
        '''
        Constructor
        call super constructor
        '''
        super(RestServiceCallError, self).__init__(*args, **kwargs)
