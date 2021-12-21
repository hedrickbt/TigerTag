class ArgumentException(Exception):
    pass


class Pluggable:
    def get_prop(self, prop_name: str, default=None, additional_message=''):
        if prop_name in self.props:
            return self.props[prop_name]
        if default is not None:
            return default
        raise ArgumentException(
            f'The {prop_name} property has not been set for the {self.name} '
            f'({self.name, __name__}.{type(self).__name__}). {additional_message}'
        )