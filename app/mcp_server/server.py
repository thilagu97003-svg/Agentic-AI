from mcp.server.mcpserver import MCPServer
from app.mcp_server import tools

mcp = MCPServer("it-helpdesk-tools")


@mcp.tool()
def reset_password(username: str) -> str:
    """Send a temporary password to the user's registered email."""
    return tools.reset_password(username)


@mcp.tool()
def unlock_account(username: str) -> str:
    """Unlock a locked user account after identity verification."""
    return tools.unlock_account(username)


@mcp.tool()
def check_service_status(service: str) -> str:
    """Check the status of an IT service such as vpn_gateway or print_spooler."""
    return tools.check_service_status(service)


@mcp.tool()
def restart_service(service: str) -> str:
    """Restart an allowed IT service such as print_spooler."""
    return tools.restart_service(service)


@mcp.tool()
def create_ticket(title: str, category: str, priority: str) -> str:
    """Create a support ticket."""
    return tools.create_ticket(title, category, priority)


@mcp.tool()
def escalate_incident(reason: str) -> str:
    """Escalate an incident to the L2 support team."""
    return tools.escalate_incident(reason)


if __name__ == "__main__":
    mcp.run()