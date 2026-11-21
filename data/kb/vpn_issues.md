# VPN Not Connecting
Category: network | Default priority: medium

## Symptoms
VPN client shows "Connection failed", "Authentication failed" or keeps disconnecting.

## Troubleshooting steps
1. Check the internet works by opening any website.
2. Close the VPN client completely and reopen it.
3. Confirm the username is the company email and the password is not expired.
4. Switch between Wi-Fi and mobile hotspot to rule out a network block.
5. Update the VPN client to the latest version.
6. Restart the laptop and try again.

## Permitted actions
check_service_status(vpn_gateway), reset_password.

## Escalate when
The VPN gateway is down, many users are affected, or steps 1 to 6 fail.
