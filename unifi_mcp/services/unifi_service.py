"""
UniFi service coordinator for the consolidated tool interface.

Routes actions to appropriate domain services and handles authentication.
"""

import logging

from fastmcp.tools.base import ToolResult
from mcp.types import TextContent

from ..client import UnifiControllerClient
from ..models.enums import AUTH_ACTIONS, CLIENT_ACTIONS, DEVICE_ACTIONS, MONITORING_ACTIONS, NETWORK_ACTIONS, UnifiAction
from ..models.params import UnifiParams
from .base import BaseService
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
            elif params.action in AUTH_ACTIONS:
                return await self._handle_auth_action(params)
            else:
                return self._create_error_result(
                    f"Unknown action: {params.action}"
                )

        except Exception as e:
            logger.error(f"Error executing action {params.action}: {e}")
            return self._create_error_result(str(e))

    async def _handle_auth_action(self, params: UnifiParams) -> ToolResult:
        """Handle authentication-related actions.

        Args:
            params: Validated parameters containing action and arguments

        Returns:
            ToolResult with authentication response
        """
        if params.action == UnifiAction.GET_USER_INFO:
            return await self._get_user_info()
        else:
            return self._create_error_result(
                f"Authentication action {params.action} not supported"
            )

    async def _get_user_info(self) -> ToolResult:
        """Get the authenticated UniFi controller admin account.

        Returns:
            ToolResult with the controller `self` admin record
        """
        try:
            # /s/default/self returns the admin account this session is logged in as.
            # (The old implementation reported MCP-caller OAuth claims, which are
            #  absent under simple Bearer auth -> always "Not authenticated".)
            result = await self.client._make_request("GET", "/self", site_name="default")

            if isinstance(result, dict) and "error" in result:
                return ToolResult(
                    content=[TextContent(type="text", text=f"Error: {result.get('error','unknown error')}")],
                    structured_content={"authenticated": False, "error": result.get('error','unknown error')}
                )

            admin = BaseService.first_record(result)

            # An empty /self record means we did not get an authenticated admin back.
            if not admin:
                return ToolResult(
                    content=[TextContent(type="text", text="Error: Not authenticated (empty /self response)")],
                    structured_content={"authenticated": False, "error": "Empty /self response"}
                )

            user_info = {
                "authenticated": True,
                "admin_id": admin.get("admin_id") or admin.get("id"),
                "name": admin.get("name"),
                "email": admin.get("email"),
                "is_super": admin.get("is_super"),
                "last_site_name": admin.get("last_site_name"),
            }

            display = user_info.get("name") or user_info.get("email") or "Unknown"
            return ToolResult(
                content=[TextContent(type="text", text=f"Controller admin: {display}")],
                structured_content=user_info
            )

        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return ToolResult(
                content=[TextContent(type="text", text=f"Error: {e!s}")],
                structured_content={
                    "error": f"Failed to get user info: {e!s}",
                    "authenticated": False
                }
            )

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
