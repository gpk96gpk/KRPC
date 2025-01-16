import krpc
import time

# Countdown...
print('3...')
time.sleep(1)
print('2...')
time.sleep(1)
print('1...')
time.sleep(1)
print('Begin Deorbit Maneuver!')

conn = krpc.connect(name='Deorbit')
vessel = conn.space_center.active_vessel

def is_within_tolerance(current_direction, target_direction, tolerance):
    return all(abs(c - t) <= tolerance for c, t in zip(current_direction, target_direction))

# Set up streams for telemetry
ut = conn.add_stream(getattr, conn.space_center, 'ut')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')

# Point retrograde
vessel.auto_pilot.engage()
vessel.auto_pilot.target_direction = (0, 0, -1)
vessel.control.rcs = True
vessel.control.sas = True

# Wait until the vessel is oriented within the tolerance of the target direction
target_direction = (0, 0, -1)
tolerance = 0.1
while True:
    current_direction = vessel.flight().direction
    print(current_direction)
    print(zip(current_direction, target_direction))
    print(all(abs(c - t) <= tolerance for c, t in zip(current_direction, target_direction)))
    print(is_within_tolerance(current_direction, target_direction, tolerance))
    if is_within_tolerance(current_direction, target_direction, tolerance):
        break
    time.sleep(1)

print("Vessel is oriented within tolerance of the target direction")

# Throttle up
vessel.control.throttle = 1.0
print("Throttling up")

# Activate the third stage
vessel.control.activate_next_stage()
print("Third stage activated")

#Activate the parachutes
vessel.control.activate_next_stage()
vessel.auto_pilot.target_direction = (0, 0, 0)
print("Parachutes deployed")
