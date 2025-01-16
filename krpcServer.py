# import krpc

# def main():
#     # Modify the address and port if your kRPC server is running on a different address or port
#     conn = krpc.connect(address='127.0.0.1', rpc_port=50000, stream_port=50001)
#     print(conn.krpc.get_status().version)
    
#     # Check if there is an active vessel
#     if conn.space_center.active_vessel is None:
#         print("No active vessel found. Please ensure you have an active vessel in the game.")
#         return
    
#     vessel = conn.space_center.active_vessel
#     refframe = vessel.orbit.body.reference_frame
#     position = conn.add_stream(vessel.position, refframe)
    
#     while True:
#         print(position())

# if __name__ == '__main__':
#     main()

#############################################################################################################################################################################

# import krpc
# conn = krpc.connect(name='Hello World')
# vessel = conn.space_center.active_vessel
# print(vessel.name)



# import krpc
# import time
# import math


# conn = krpc.connect(name='Sub-orbital flight')
# vessel = conn.space_center.active_vessel
# vessel.auto_pilot.target_pitch_and_heading(90, 90)
# vessel.auto_pilot.engage()
# vessel.control.throttle = 1
# time.sleep(1)
# print('Launch!')
# vessel.control.activate_next_stage()
# fuel_amount = conn.get_call(vessel.resources.amount, 'SolidFuel')
# expr = conn.krpc.Expression.less_than(
#     conn.krpc.Expression.call(fuel_amount),
#     conn.krpc.Expression.constant_float(0.1))
# event = conn.krpc.add_event(expr)
# with event.condition:
#     event.wait()
# print('Booster separation')
# vessel.control.activate_next_stage()
# mean_altitude = conn.get_call(getattr, vessel.flight(), 'mean_altitude')
# expr = conn.krpc.Expression.greater_than(
#     conn.krpc.Expression.call(mean_altitude),
#     conn.krpc.Expression.constant_double(10000))
# event = conn.krpc.add_event(expr)
# with event.condition:
#     event.wait()
# print('Gravity turn')
# vessel.auto_pilot.target_pitch_and_heading(60, 90)
# liquid_fuel_amount = conn.get_call(vessel.resources.amount, 'LiquidFuel')
# apoapsis_altitude = conn.get_call(getattr, vessel.orbit, 'apoapsis_altitude')
# expr = conn.krpc.Expression.greater_than(
#     conn.krpc.Expression.call(apoapsis_altitude),
#     conn.krpc.Expression.constant_double(100000))
# event = conn.krpc.add_event(expr)
# with event.condition:
#     event.wait()

# print('Launch stage separation')
# #vessel.control.throttle = 0
# time.sleep(1)
# vessel.control.activate_next_stage()
# vessel.auto_pilot.disengage()
# srf_altitude = conn.get_call(getattr, vessel.flight(), 'surface_altitude')
# expr = conn.krpc.Expression.less_than(
#     conn.krpc.Expression.call(srf_altitude),
#     conn.krpc.Expression.constant_double(1000))
# event = conn.krpc.add_event(expr)
# with event.condition:
#     event.wait()

# vessel.control.activate_next_stage()
# while vessel.flight(vessel.orbit.body.reference_frame).vertical_speed < -0.1:
#     print('Altitude = %.1f meters' % vessel.flight().surface_altitude)
#     time.sleep(1)
# print('Landed!')

import krpc

node = vessel.control.add_node(
    ut() + vessel.orbit.time_to_apoapsis, prograde=delta_v)

conn = krpc.connect(name='Hello World')
remaining_burn = conn.add_stream(node.remaining_burn_vector, node.reference_frame)
print(remaining_burn())