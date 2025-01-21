from flask import Flask, jsonify
from http import HTTPStatus
from typing import Dict, Any

def create_app(test_config: Dict[str, Any] = None) -> Flask:
    """Create and configure the Flask application.
    
    Args:
        test_config: Configuration dictionary for testing purposes.
        
    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)

    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY='dev',  # Change this in production!
        DATABASE_URL='postgresql://localhost:5432/test_gen_db'
    )

    if test_config is not None:
        # Override config with test config if provided
        app.config.update(test_config)

    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({'status': 'healthy'}), HTTPStatus.OK

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), HTTPStatus.NOT_FOUND

    return app