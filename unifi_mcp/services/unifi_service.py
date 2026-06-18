"""
UniFi service coordinator for the consolidated tool interface.

Routes actions to appropriate domain services and handles authentication.
"""

import logging

from fastmcp.tools.base import ToolResult
from mcp.types import TextContent

from ..client import UnifiControllerClient
from ..models.enums import CLIENT_ACTIONS, DEVICE_ACTIONS, MONITORING_ACTIONS, NETWORK_ACTIONS
from ..models.params import UnifiParams
from .client_service import ClientService
from .device_service import DeviceService
from .monitoring_service import MonitoringService
from .network_service import NetworkService

logger = logging.getLogger(__name__)


class UnifiService:
    """Main service coordinator for the unified UniFi tool.

    Routes actions to appropriate domain services while maintaining
    a clean separation of concerns.
    """

    def __init__(self, client: UnifiControllerClient):
        """Initialize the UniFi service coordinator.

        Args:
            client: UniFi controller client for API operations
        """
        self.client = client

        # Initialize domain services
        self.device_service = DeviceService(client)
        self.client_service = ClientService(client)
        self.network_service = NetworkService(client)
        self.monitoring_service = MonitoringService(client)

    async def execute_action(self, params: UnifiParams) -> ToolResult:
        """Execute the specified action by routing to the appropriate service.

        Args:
            params: Validated parameters containing action and arguments

        Returns:
            ToolResult with action response
        """
        try:
            # Route to appropriate domain service
            if params.action in DEVICE_ACTIONS:
                return await self.device_service.execute_action(params)
            elif params.action in CLIENT_ACTIONS:
                return await self.client_service.execute_action(params)
            elif params.action in NETWORK_ACTIONS:
                return await self.network_service.execute_action(params)
            elif params.action in MONITORING_ACTIONS:
                return await self.monitoring_service.execute_action(params)
            else:
                return self._create_error_result(
                    f"Unknown action: {params.action}"
                )

        except Exception as e:
            logger.error(f"Error executing action {params.action}: {e}")
            return self._create_error_result(str(e))

    @staticmethod
    def _create_error_result(message: str, raw_data=None) -> ToolResult:
        """Create standardized error ToolResult.

        Args:
            message: Human-readable error message
            raw_data: Optional raw data to include

        Returns:
            ToolResult with error information
        """
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: {message}")],
            structured_content={"error": message, "raw": raw_data}
        )
