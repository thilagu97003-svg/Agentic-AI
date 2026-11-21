SERVICES = {
    "vpn_gateway": "running",
    "print_spooler": "running",
    "mail_server": "running",
    "wifi_controller": "running",
}


def reset_password(username: str = "user") -> str:
    return f"Temporary password sent to the registered email of {username}. Must be changed at first login."


def unlock_account(username: str = "user") -> str:
    return f"Account of {username} has been unlocked."


def check_service_status(service: str = "vpn_gateway") -> str:
    return f"Service {service} status: {SERVICES.get(service, 'unknown')}"


def restart_service(service: str = "print_spooler") -> str:
    return f"Service {service} restarted successfully."


def create_ticket(title: str, category: str, priority: str) -> str:
    return f"Ticket created: {title} [{category}/{priority}]"


def escalate_incident(reason: str) -> str:
    return f"Escalated to the L2 support team. Reason: {reason}"