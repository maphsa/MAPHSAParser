class MAPHSAParserException(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class MAPHSAMissingSourceException(Exception):

    def __init__(self, message):
        super().__init__(message)


class MAPHSAMissingMappingException(MAPHSAParserException):

    def __init__(self, message, missing_value):
        self.message = message
        self.missing_value = missing_value
        super().__init__(self.message)


class MAPHSAParseInsertionException(MAPHSAParserException):

    def __init__(self, message, query=None, parse_data=None):
        self.message = message
        self.query = query if query else None
        self.parse_data = parse_data if parse_data else None
        super().__init__(self.message)
