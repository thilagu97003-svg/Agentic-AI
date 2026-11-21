# Printer Not Printing
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
