import math
import time
import krpc
# import detachSat

turn_start_altitude = 250
turn_end_altitude = 45000
target_altitude = 150000

conn = krpc.connect(name='Launch into orbit')
vessel = conn.space_center.active_vessel

# Set up streams for telemetry
ut = conn.add_stream(getattr, conn.space_center, 'ut')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')
stage_2_resources = vessel.resources_in_decouple_stage(stage=2, cumulative=False)
srb_fuel = conn.add_stream(stage_2_resources.amount, 'SolidFuel')

def is_within_tolerance(current_direction, target_direction, tolerance):
    return all(abs(c - t) <= tolerance for c, t in zip(current_direction, target_direction))


# Pre-launch setup
vessel.control.sas = False
vessel.control.rcs = False
vessel.control.throttle = 1.0

# Countdown...
print('Begin Launch Sequence!')
time.sleep(1)
print('3...')
time.sleep(1)
print('2...')
time.sleep(1)
print('1...')
time.sleep(1)
print('Launch!')

# Activate the first stage
vessel.control.activate_next_stage()
vessel.auto_pilot.engage()
vessel.auto_pilot.target_pitch_and_heading(90, 90)

# Main ascent loop
srbs_separated = False
turn_angle = 0
while True:
    print(apoapsis())

    # Gravity turn
    if altitude() > turn_start_altitude and altitude() < turn_end_altitude:
        frac = ((altitude() - turn_start_altitude) /
                (turn_end_altitude - turn_start_altitude))
        new_turn_angle = frac * 90
        if abs(new_turn_angle - turn_angle) > 0.5:
            turn_angle = new_turn_angle
            vessel.auto_pilot.target_pitch_and_heading(90-turn_angle, 90)
    
    # Decrease throttle when approching orbit
    if apoapsis()/periapsis() > 0.9:
        vessel.control.throttle = 0.25

    # Separate SRBs when finished
    if not srbs_separated:
        if srb_fuel() < 0.1:
            vessel.control.activate_next_stage()
            srbs_separated = True
            vessel.control.rcs = True
            print('SRBs separated')

    # Decrease throttle when approaching target apoapsis
    if apoapsis() > target_altitude*0.9:
        print('Approaching target apoapsis')
        break

# Disable engines when target apoapsis is reached
vessel.control.throttle = 0.25
while apoapsis() < target_altitude:
    pass
print('Target apoapsis reached')
vessel.control.throttle = 0.0

# Wait until out of atmosphere
print('Coasting out of atmosphere')
while altitude() < 70500:
    pass

# Plan circularization burn (using vis-viva equation)
print('Planning circularization burn')
mu = vessel.orbit.body.gravitational_parameter
r = vessel.orbit.apoapsis
a1 = vessel.orbit.semi_major_axis
a2 = r
v1 = math.sqrt(mu*((2./r)-(1./a1)))
v2 = math.sqrt(mu*((2./r)-(1./a2)))
delta_v = v2 - v1
node = vessel.control.add_node(
    ut() + vessel.orbit.time_to_apoapsis, prograde=delta_v)

# Calculate burn time (using rocket equation)
F = vessel.available_thrust
Isp = vessel.specific_impulse * 9.82
m0 = vessel.mass
m1 = m0 / math.exp(delta_v/Isp)
flow_rate = F / Isp
burn_time = (m0 - m1) / flow_rate

# Orientate ship
print('Orientating ship for circularization burn')
vessel.auto_pilot.reference_frame = node.reference_frame
vessel.auto_pilot.target_direction = (0, 1, 0)
vessel.auto_pilot.wait()

# Wait until burn
print('Waiting until circularization burn')
burn_ut = ut() + vessel.orbit.time_to_apoapsis - (burn_time/2.)
lead_time = 5
conn.space_center.warp_to(burn_ut - lead_time)

# Execute burn
print('Ready to execute burn')
time_to_apoapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
while time_to_apoapsis() - (burn_time/2.) > 0:
    pass
print('Executing burn')
vessel.control.throttle = 1.0
time.sleep(burn_time * 0.9)
print('Fine tuning')
vessel.control.throttle = 0.05
remaining_burn = conn.add_stream(node.remaining_burn_vector, node.reference_frame)
while remaining_burn()[1] > 0.1:  # Fine-tune until the remaining burn is very small
    print(f"Remaining burn: {remaining_burn()[1]}")
    time.sleep(0.1)  # Sleep for a short duration to allow for fine adjustments
vessel.control.throttle = 0.0
node.remove()

# Open cargo bay doors using action group 1
vessel.control.set_action_group(1, True)
print('Cargo bay doors opened')

# Orient ship Retrograde
vessel.auto_pilot.engage()
vessel.auto_pilot.target_direction = (0, 0, -1)
tolerance = 0.1
while True:
    current_direction = vessel.flight().direction
    if is_within_tolerance(current_direction, (0, 0, -1), tolerance):
        break
    time.sleep(1)
print("Ship oriented retrograde")


# Turn on SAS
vessel.control.sas = True



print('Launch complete')

# print('3...')
# time.sleep(1)
# print('2...')
# time.sleep(1)
# print('1...')
# time.sleep(1)
# print('Begin Satellite Detachment!')

# conn = krpc.connect(name='Detach Satellite')
# vessel = conn.space_center.active_vessel

# # Find the docking port
# docking_port = None
# for part in vessel.parts.all:
#     if part.docking_port is not None and part.docking_port.state == conn.space_center.DockingPortState.docked:
#         docking_port = part.docking_port
#         break

# if docking_port is None:
#     print("No docked satellite found.")
# else:
#     # Undock the satellite
#     docking_port.undock()
#     print("Satellite detached successfully!")

#     # Switch to the detached vessel and perform maneuvers
#     time.sleep(5)
#     detached_vessel = docking_port.docked_vessel
#     conn.space_center.active_vessel = detached_vessel
#     print("Switched to the detached satellite.")

#     # Maintain Satellite orientation
#     detached_vessel.auto_pilot.engage()
#     detached_vessel.auto_pilot.target_direction = (0, 0, 1)
#     print("Maintaining satellite orientation.")

#     # Use RCS to move the satellite away from the main vessel
#     detached_vessel.control.rcs = True
#     detached_vessel.control.sas = True
#     detached_vessel.control.up = 1.0
#     detached_vessel.control.left = 1.0
#     time.sleep(5)
#     detached_vessel.control.up = 0.0
#     detached_vessel.control.left = 0.0
#     detached_vessel.control.rcs = False
#     print("Moved the detached satellite away from the main vessel.")

#     # Deploy solar panels
#     for part in detached_vessel.parts.solar_panels:
#         part.deployed = True
#     print("Solar panels deployed on the detached satellite.")

#     # Deploy antennas
#     for part in detached_vessel.parts.antennas:
#         part.deployed = True
#     print("Antennas deployed on the detached satellite.")

#     # Deploy science experiments
#     for part in detached_vessel.parts.experiments:
#         part.deployed = True
#     print("Science experiments deployed on the detached satellite.")

#     print("Satellite detachment complete.")

#     # Switch back to the main vessel
#     conn.space_center.active_vessel = vessel
#     print("Switched back to the main vessel.")


# print('3...')
# time.sleep(1)
# print('2...')
# time.sleep(1)
# print('1...')
# time.sleep(1)
# print('Begin Deorbit Maneuver!')

# conn = krpc.connect(name='Deorbit')
# vessel = conn.space_center.active_vessel

# def is_within_tolerance(current_direction, target_direction, tolerance):
#     return all(abs(c - t) <= tolerance for c, t in zip(current_direction, target_direction))

# # Set up streams for telemetry
# ut = conn.add_stream(getattr, conn.space_center, 'ut')
# altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
# apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
# periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')

# # Point retrograde
# vessel.auto_pilot.engage()
# vessel.auto_pilot.target_direction = (0, 0, -1)
# vessel.control.rcs = True
# vessel.control.sas = True

# # Wait until the vessel is oriented within the tolerance of the target direction
# target_direction = (0, 0, -1)
# tolerance = 0.1
# while True:
#     current_direction = vessel.flight().direction
#     print(current_direction)
#     print(zip(current_direction, target_direction))
#     print(all(abs(c - t) <= tolerance for c, t in zip(current_direction, target_direction)))
#     print(is_within_tolerance(current_direction, target_direction, tolerance))
#     if is_within_tolerance(current_direction, target_direction, tolerance):
#         break
#     time.sleep(1)

# print("Vessel is oriented within tolerance of the target direction")

# # Throttle up
# vessel.control.throttle = 1.0
# print("Throttling up")

# # Activate the third stage
# vessel.control.activate_next_stage()
# print("Third stage activated")

# # Shutdown engines
# vessel.control.throttle = 0
# print("Engines shutdown")

# #Activate the parachutes
# vessel.control.activate_next_stage()
# vessel.auto_pilot.target_direction = (0, 0, 0)
# print("Parachutes deployed")

# # Detach satellite
# # time.sleep(30)
# # detachSat.main()