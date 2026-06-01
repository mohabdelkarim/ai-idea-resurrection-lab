from flask import Flask, Blueprint

app = Flask(__name__)

# Create a parent blueprint
parent_blueprint = Blueprint('parent', __name__)

# Create sub-blueprints
sub_blueprint1 = Blueprint('sub1', __name__)
sub_blueprint2 = Blueprint('sub2', __name__)

# Define routes for sub-blueprints
@sub_blueprint1.route('/sub1')
def sub1():
    return 'Sub-blueprint 1'

@sub_blueprint2.route('/sub2')
def sub2():
    return 'Sub-blueprint 2'

# Define a route for the parent blueprint
@parent_blueprint.route('/parent')
def parent():
    return 'Parent blueprint'

# Enhance the parent blueprint to register sub-blueprints
class EnhancedBlueprint(Blueprint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sub_blueprints = []

    def register_blueprint(self, blueprint, **options):
        url_prefix = options.get('url_prefix')
        if url_prefix is None:
            url_prefix = blueprint.url_prefix
        if 'url_prefix' in options:
            del options['url_prefix']

        self.sub_blueprints.append((blueprint, url_prefix, options))

    def register_with_app(self, app):
        for blueprint, url_prefix, options in self.sub_blueprints:
            app.register_blueprint(blueprint, url_prefix=url_prefix, **options)
        super().register_with_app(app)

# Update the parent blueprint to use the enhanced class
parent_blueprint = EnhancedBlueprint('parent', __name__)

# Register sub-blueprints with the parent blueprint
parent_blueprint.register_blueprint(sub_blueprint1, url_prefix='/parent/sub1')
parent_blueprint.register_blueprint(sub_blueprint2, url_prefix='/parent/sub2')

# Register the parent blueprint with the app
parent_blueprint.register_with_app(app)

if __name__ == '__main__':
    app.run(debug=True)