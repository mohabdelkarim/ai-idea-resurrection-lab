import enum

class Enum:
    def __init__(self, value):
        self.value = value

class Project:
    class Color(enum.Enum):
        blue = 1
        green = 2
        red = 3

    def __init__(self):
        self.color = None
        self.errors = {}

    def validate_inclusion(self, attribute, value, options):
        if attribute not in self.errors:
            self.errors[attribute] = []
        if value not in [v.value for v in options['in']]:
            self.errors[attribute].append(f"{value} is not included in the list")

    def validate(self, attribute, value):
        if hasattr(self, f"validate_{attribute}"):
            getattr(self, f"validate_{attribute}")(value)
        else:
            raise ValueError(f"Invalid value {value} for {attribute}")

    def validate_color(self, value):
        self.validate_inclusion('color', value, {'in': [self.Color.blue, self.Color.green, self.Color.red]})

    def set_color(self, value):
        try:
            self.color = self.Color(value)
        except ValueError:
            if 'color' in self.errors and self.errors['color']:
                pass
            else:
                raise ValueError(f"Invalid color value: {value}")

    def set_attribute(self, attribute, value):
        if attribute == 'color':
            self.validate(attribute, value)
            self.set_color(value)
        else:
            raise AttributeError(f"Unknown attribute: {attribute}")

def main():
    project = Project()
    project.set_attribute('color', 1)
    print(project.color)
    project.set_attribute('color', 4)
    try:
        project.set_attribute('color', 'orange')
    except ValueError as e:
        print(e)
    print(project.errors)

if __name__ == '__main__':
    main()