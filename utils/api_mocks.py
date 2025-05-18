import json
from typing import Dict, Any, Optional, Callable
from playwright.sync_api import Route, Request
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class APIMockHandler:
    """
    Handles API mocking for various endpoints.
    Provides methods to mock different API responses and handle route interception.
    """

    def __init__(self):
        self._mock_responses: Dict[str, Dict[str, Any]] = {
            "phone_verification": {
                "url_pattern": "**/api/v2/phone_one_time_passwords**",
                "response": {
                    "status": 200,
                    "body": {
                        "internationalPhoneNumber": "",
                        "nationalPhoneNumber": "",
                        "success": True,
                        "deliveryMethod": "TEXT",
                        "codeLength": 6
                    }
                }
            },
            # Add more mock responses here as needed
        }

    def get_mock_handler(self, mock_type: str) -> Optional[Callable[[Route], None]]:
        """
        Get a mock handler function for the specified mock type.
        
        Args:
            mock_type: The type of mock to get (e.g., 'phone_verification')
            
        Returns:
            A callable that handles the route interception, or None if mock type not found
        """
        mock_config = self._mock_responses.get(mock_type)
        if not mock_config:
            logger.warning(f"No mock configuration found for type: {mock_type}")
            return None

        def mock_handler(route: Route) -> None:
            """Handle the route interception with the configured response."""
            try:
                logger.info(f"Intercepting request to: {route.request.url}")
                
                # Get the response configuration
                response = mock_config["response"]
                
                # If the response contains dates, standardize them
                if isinstance(response.get("body"), dict):
                    for key, value in response["body"].items():
                        if isinstance(value, str) and "/" in value:
                            # Try to extract and standardize date
                            extracted_date = self.extract_date_from_text(value)
                            if extracted_date:
                                response["body"][key] = extracted_date
                
                route.fulfill(
                    status=response["status"],
                    body=json.dumps(response["body"])
                )
                logger.info(f"Successfully mocked response for: {mock_type}")
            except Exception as e:
                logger.error(f"Error handling mock for {mock_type}: {e}")
                # Fallback to original request if mock fails
                route.continue_()

        return mock_handler

    def setup_mock(self, page, mock_type: str) -> bool:
        """
        Set up a mock for the specified type.
        
        Args:
            page: The Playwright page object
            mock_type: The type of mock to set up
            
        Returns:
            bool: True if mock was set up successfully, False otherwise
        """
        try:
            mock_config = self._mock_responses.get(mock_type)
            if not mock_config:
                logger.warning(f"No mock configuration found for type: {mock_type}")
                return False

            handler = self.get_mock_handler(mock_type)
            if not handler:
                return False

            page.route(mock_config["url_pattern"], handler)
            logger.info(f"Successfully set up mock for: {mock_type}")
            return True

        except Exception as e:
            logger.error(f"Error setting up mock for {mock_type}: {e}")
            return False

    def remove_mock(self, page, mock_type: str) -> bool:
        """
        Remove a mock for the specified type.
        
        Args:
            page: The Playwright page object
            mock_type: The type of mock to remove
            
        Returns:
            bool: True if mock was removed successfully, False otherwise
        """
        try:
            mock_config = self._mock_responses.get(mock_type)
            if not mock_config:
                logger.warning(f"No mock configuration found for type: {mock_type}")
                return False

            page.unroute(mock_config["url_pattern"])
            logger.info(f"Successfully removed mock for: {mock_type}")
            return True

        except Exception as e:
            logger.error(f"Error removing mock for {mock_type}: {e}")
            return False

    def add_mock_response(self, mock_type: str, url_pattern: str, response: Dict[str, Any]) -> None:
        """
        Add a new mock response configuration.
        
        Args:
            mock_type: The type of mock to add
            url_pattern: The URL pattern to match
            response: The response configuration
        """
        self._mock_responses[mock_type] = {
            "url_pattern": url_pattern,
            "response": response
        }
        logger.info(f"Added new mock configuration for: {mock_type}")

    def get_mock_config(self, mock_type: str) -> Optional[Dict[str, Any]]:
        """
        Get the configuration for a specific mock type.
        
        Args:
            mock_type: The type of mock to get
            
        Returns:
            The mock configuration if found, None otherwise
        """
        return self._mock_responses.get(mock_type) 