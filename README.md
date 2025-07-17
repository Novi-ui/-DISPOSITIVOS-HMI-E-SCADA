# HMI Simulation - Drilling Machine

This project simulates an HMI (Human-Machine Interface) for an automatic drilling machine, as described in the requirements. It uses Python and Tkinter for the GUI.

## Features
- Login with user levels (Operator, Administrator, Maintenance, Parameter Editor)
- Main menu with navigation
- Alarms (discrete and analog)
- Parameters (speed, positions)
- Recipe management (add, edit, remove)
- Maintenance (motors and safety devices status)
- Simulated PLC data and logic

## How to Run
1. Make sure you have Python 3 installed.
2. Run the application:
   ```
   python main.py
   ```

Tkinter is included with standard Python installations.

## User Credentials
- **Operator:** operador / 123
- **Administrator:** admin / admin
- **Maintenance:** manut / manut
- **Parameter Editor:** editor / edit

## Project Structure
- `main.py`: Main application file with all screens and logic.
- `README.md`: This file.

## Notes
- This is a simulation for educational purposes. In a real HMI/SCADA system, you would use industrial software (e.g., Siemens TIA Portal, WinCC) and connect to real PLC hardware.
- All data is simulated in memory.