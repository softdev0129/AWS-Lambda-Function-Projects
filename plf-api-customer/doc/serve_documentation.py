import json
import markdown
from utils.build_response import build_response


class ServeDocumentation:
    def __init__(self):
        self.readme_path = 'README.md'
        self.openapi_path = 'doc/open-api.yml'

    def serve_documentation(self):
        try:
            # Read the README.md file
            with open(self.readme_path, 'r') as file:
                markdown_content = file.read()

            # Convert Markdown to HTML
            html_content = markdown.markdown(markdown_content)

            # Return the HTML content
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/html'
                },
                'body': html_content
            }
        except Exception as e:
            return build_response(500, {'error': str(e)})

    def serve_openapi(self):
        try:
            # Read the openapi.yaml file
            with open(self.openapi_path, 'r') as file:
                yaml_content = file.read()

            # Return the YAML content
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/x-yaml'
                },
                'body': yaml_content
            }
        except Exception as e:
            return build_response(500, {'error': str(e)})
