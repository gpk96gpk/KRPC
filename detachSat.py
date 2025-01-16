import krpc
import time
#import deorbit

# Countdown...
print('3...')
time.sleep(1)
print('2...')
time.sleep(1)
print('1...')
time.sleep(1)
print('Begin Satellite Detachment!')

conn = krpc.connect(name='Detach Satellite')
vessel = conn.space_center.active_vessel

# Find the docking port
docking_port = None
for part in vessel.parts.all:
    if part.docking_port is not None and part.docking_port.state == conn.space_center.DockingPortState.docked:
        docking_port = part.docking_port
        break

if docking_port is None:
    print("No docked satellite found.")
else:
    # Undock the satellite
    docking_port.undock()
    print("Satellite detached successfully!")

# Switch to the detached vessel and perform maneuvers
time.sleep(5)

print("Switched to the detached satellite.")

# Use RCS to move the satellite away from the main vessel
vessel.control.rcs = True
vessel.control.left = 1.0

time.sleep(5)
vessel.control.left = 0.0
vessel.control.rcs = False
print("Moved the detached satellite away from the main vessel.")

# Deploy solar panels
for part in vessel.parts.solar_panels:
    part.deployed = True
print("Solar panels deployed on the detached satellite.")

# # Deploy antennas
# for part in vessel.parts.antennas:
#     part.deployed = True
# print("Antennas deployed on the detached satellite.")

# Deploy science experiments
for part in vessel.parts.experiments:
    part.deployed = True
print("Science experiments deployed on the detached satellite.")

print("Satellite detachment complete.")

# Switch back to the main vessel
conn.space_center.active_vessel = vessel
print("Switched back to the main vessel.")

# Start the deorbit script
# deorbit.main()