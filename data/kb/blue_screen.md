# Blue Screen of Death (BSOD)
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
