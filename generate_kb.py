from pathlib import Path

KB = {
"vpn_issues.md": """# VPN Not Connecting
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
""",
"wifi_issues.md": """# Wi-Fi Not Connecting or Slow
Category: network | Default priority: medium

## Symptoms
No internet, "Connected, no internet", very slow speed, frequent drops.

## Troubleshooting steps
1. Turn Wi-Fi off and on, or toggle Airplane mode.
2. Forget the network and connect again with the password.
3. Restart the router or move closer to it.
4. Run Windows Network Troubleshooter.
5. Open Command Prompt and run: ipconfig /release then ipconfig /renew.
6. Run: ipconfig /flushdns.
7. Update the Wi-Fi adapter driver in Device Manager.

## Escalate when
Other devices on the same network also have no internet, which means a network outage.
""",
"password_reset.md": """# Forgot Password or Password Expired
Category: access | Default priority: medium

## Symptoms
User cannot log in, password rejected, "password expired" message.

## Self-service steps
1. Go to the company password portal and choose "Forgot password".
2. Verify identity with the registered email or mobile OTP.
3. Set a new password: minimum 12 characters, one uppercase, one number, one symbol.
4. Do not reuse the last 5 passwords.

## Permitted actions
reset_password (only after identity verification, sends a temporary password to the registered email).

## Escalate when
The user has no access to the registered email or mobile, or suspects the account is compromised.
""",
"account_locked.md": """# Account Locked Out
Category: access | Default priority: medium

## Symptoms
"Your account has been locked" after several wrong password attempts.

## Troubleshooting steps
1. Wait 15 minutes, the account unlocks automatically.
2. Make sure Caps Lock is off and the keyboard language is correct.
3. Check saved passwords on phone or mail apps, old passwords there cause repeated lockouts.
4. Request an unlock.

## Permitted actions
unlock_account (after identity verification).

## Escalate when
The account locks again within one hour, which may indicate a security attack.
""",
"email_outlook.md": """# Outlook or Email Problems
Category: software | Default priority: low

## Symptoms
Outlook not opening, not syncing, stuck on "Disconnected", cannot send mail.

## Troubleshooting steps
1. Check the internet connection.
2. Close Outlook and start it in safe mode: Windows + R, type outlook /safe.
3. Check the mailbox is not full (storage limit).
4. Remove and re-add the account in Control Panel, Mail.
5. Repair Office from Settings, Apps, Microsoft Office, Modify, Quick Repair.

## Escalate when
Webmail also fails, which means a mail server issue.
""",
"printer_issues.md": """# Printer Not Printing
Category: hardware | Default priority: low

## Symptoms
Job stuck in queue, printer offline, blank pages, paper jam.

## Troubleshooting steps
1. Check the printer is on and connected to the same network.
2. Clear the print queue: open Services, restart "Print Spooler".
3. Set the correct printer as default and untick "Use Printer Offline".
4. Remove the printer and add it again.
5. For paper jam, power off, remove paper gently and restart.

## Permitted actions
restart_service(print_spooler).

## Escalate when
Hardware fault such as an error light or strange noise.
""",
"slow_laptop.md": """# Laptop Running Slow
Category: hardware | Default priority: low

## Symptoms
Laptop hangs, apps take long to open, fan noise, high CPU or memory.

## Troubleshooting steps
1. Restart the laptop, many issues clear after a restart.
2. Open Task Manager (Ctrl + Shift + Esc) and end heavy unused apps.
3. Disable unnecessary startup apps in Task Manager, Startup tab.
4. Free disk space, keep at least 15 percent free.
5. Run Windows Update and an antivirus scan.
6. Close extra browser tabs.

## Escalate when
Slowness continues after all steps, as hardware upgrade (RAM or SSD) may be needed.
""",
"software_install.md": """# Software Installation Request
Category: software | Default priority: low

## Rules
1. Only approved software from the company software catalog can be installed.
2. Install requests need manager approval.
3. Admin rights are not given to normal users.

## Steps
1. Open the Software Center and search for the app.
2. If available, click Install.
3. If not available, raise a request with software name, version and business reason.

## Permitted actions
create_ticket (software request).

## Escalate when
The software is not in the approved catalog, send to the security team for review.
""",
"blue_screen.md": """# Blue Screen of Death (BSOD)
Category: hardware | Default priority: high

## Symptoms
Blue screen with a stop code, laptop restarts suddenly.

## Troubleshooting steps
1. Note the stop code, for example MEMORY_MANAGEMENT or CRITICAL_PROCESS_DIED.
2. Disconnect external devices such as USB drives and docks.
3. Restart and boot into Safe Mode if it repeats.
4. Uninstall the last installed driver or update.
5. Run: sfc /scannow in Command Prompt as administrator.

## Escalate when
It happens more than twice in a day. Create a high priority incident for hardware diagnosis.
""",
"disk_space.md": """# Disk Full or Low Storage
Category: hardware | Default priority: low

## Symptoms
"Low disk space" warning, cannot save files or install updates.

## Troubleshooting steps
1. Run Disk Cleanup and delete temporary files.
2. Empty the Recycle Bin and the Downloads folder.
3. Uninstall unused applications.
4. Move large files to OneDrive or shared storage.
5. Turn on Storage Sense in Windows Settings.

## Escalate when
The disk is still above 95 percent after cleanup.
""",
"mfa_issues.md": """# MFA or OTP Not Working
Category: access | Default priority: high

## Symptoms
No OTP received, authenticator code rejected, new phone setup.

## Troubleshooting steps
1. Check the phone time is set to automatic, wrong time makes codes invalid.
2. Check the phone has network signal for SMS codes.
3. Wait 60 seconds and request a new code.
4. For a lost or new phone, MFA reset needs identity verification.

## Escalate when
The user lost the phone. This always goes to the Security team as a high priority incident.
""",
"teams_zoom.md": """# Teams or Zoom Audio and Video Problems
Category: software | Default priority: low

## Symptoms
Microphone not working, camera not detected, no sound in meetings.

## Troubleshooting steps
1. In the app, open Settings, Devices and select the right mic and camera.
2. Check Windows Privacy settings allow microphone and camera access for apps.
3. Close other apps using the camera.
4. Restart the app, then the laptop.
5. Update the app and the audio driver.

## Escalate when
The device is not detected in Device Manager, which may be a hardware fault.
""",
"security_incident.md": """# Suspicious Email or Possible Malware
Category: security | Default priority: critical

## Symptoms
Phishing email clicked, unknown pop-ups, files renamed or encrypted, strange login alerts.

## Immediate steps
1. Disconnect the device from Wi-Fi and network.
2. Do not delete anything and do not restart.
3. Change the password from another safe device.
4. Report to the Security team immediately.

## Permitted actions
escalate_incident (critical). Never try to fix this automatically.

## Escalate when
Always escalate, this is a critical incident.
""",
}

out = Path("data/kb")
out.mkdir(parents=True, exist_ok=True)
for name, text in KB.items():
    (out / name).write_text(text.strip() + "\n", encoding="utf-8")
print(f"Created {len(KB)} KB files in {out}")