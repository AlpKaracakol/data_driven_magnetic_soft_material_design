import numpy as np
import math
import copy



def get_magnetic_control_field(args, step = None): # open-loop or closed-loop controller setup
    """ Create your open-loop(OL) or closed-loop(CL) magnetic field controller """
        
    if args.controller_type =="open-loop":

        if not args.fitness_calc_type=="multi_func_walkNjump" and not args.fitness_calc_type=="multi_func_walkNjumpv2":
            if args.desired_shape == "max_COM_x":

                args.sim_time = 2
                
                
                
                controller_loop_bandwidth = 120
                OL_B_period = 1.
                OL_B_repeat_num = 10

                B_max = 10e-3   # 10 mT


                args.sim_time  = OL_B_repeat_num * OL_B_period


                totalStepNum = int(controller_loop_bandwidth*args.sim_time)

                is_rampUP_DOWN = 1
                ramp_steps = 0
                if is_rampUP_DOWN: 
                    ramp_ratio = 0.1
                    ramp_steps = int(int(controller_loop_bandwidth*OL_B_period)*ramp_ratio/2)*2

                    start_angle = 90
                    end_angle = 0

                    start_angle = -90
                    end_angle = 0

                    OL_B_orientation_cycle = np.linspace(start_angle*math.pi/180., end_angle*math.pi/180., int(controller_loop_bandwidth*OL_B_period)-ramp_steps)
                    OL_B_orientation_cycle = np.hstack((np.ones(int(ramp_steps/2))*start_angle*math.pi/180., OL_B_orientation_cycle, np.ones(int(ramp_steps/2))*end_angle*math.pi/180.))

                    _OL_B_orientation = OL_B_orientation_cycle

                    OL_B_orientation = copy.deepcopy(_OL_B_orientation)
                    for rep_num in range(OL_B_repeat_num-1):
                        OL_B_orientation = np.hstack((OL_B_orientation, _OL_B_orientation))

                    _OL_B_magnitude_up = np.linspace(0, B_max, int(ramp_steps/2))
                    _OL_B_magnitude_fixed = B_max * np.ones(int(controller_loop_bandwidth*OL_B_period)-int(ramp_steps))
                    _OL_B_magnitude_down = np.linspace(B_max, 0, int(ramp_steps/2))

                    _OL_B_magnitude = np.hstack((_OL_B_magnitude_up, _OL_B_magnitude_fixed, _OL_B_magnitude_down))

                    OL_B_magnitude = copy.deepcopy(_OL_B_magnitude)
                    for rep_num in range(OL_B_repeat_num-1):
                        OL_B_magnitude = np.hstack((OL_B_magnitude, _OL_B_magnitude))

                else:
                
                    OL_B_orientation_cycle = np.linspace(90*math.pi/180., 0*math.pi/180., int(controller_loop_bandwidth*OL_B_period/2))

                    _OL_B_orientation = np.hstack((OL_B_orientation_cycle, np.flip(OL_B_orientation_cycle)))

                    OL_B_orientation = copy.deepcopy(_OL_B_orientation)
                    for rep_num in range(OL_B_repeat_num-1):
                        OL_B_orientation = np.hstack((OL_B_orientation, _OL_B_orientation))

                    OL_B_magnitude = B_max * np.ones(totalStepNum)
            
            
                # B dictionary
                # TODO: later either make its own class, or combine with robot class
                OL_B = {"B_period": OL_B_period,
                        "B_orientation": OL_B_orientation,
                        "B_magnitude": OL_B_magnitude,
                        "B_controller_bandwidth": controller_loop_bandwidth,
                }
                controller = OL_B
            else:
                raise NotImplementedError
        elif args.fitness_calc_type=="multi_func_walkNjump" or args.fitness_calc_type=="multi_func_walkNjumpv2":
            if args.desired_shape == "max_COM_x" or args.desired_shape == "multi_func_walkNjump":

                args.sim_time = 5
                
                controller_loop_bandwidth = 120
                OL_B_period = 0.5
                OL_B_repeat_num = 5

                B_max = 10e-3   # 10 mT

                # OL_B_repeat_num = 4
                # B_max = 20e-3   # 10 mT


                args.sim_time  = OL_B_repeat_num * OL_B_period


                totalStepNum = int(controller_loop_bandwidth*args.sim_time)

                is_rampUP_DOWN = 1
                ramp_steps = 0
                if is_rampUP_DOWN: 
                    ramp_ratio = 0.1
                    ramp_steps = 4

                    start_angle = 90
                    end_angle = 0

                    start_angle = -90
                    end_angle = 0

                    OL_B_orientation_cycle = np.linspace(start_angle*math.pi/180., end_angle*math.pi/180., int(controller_loop_bandwidth*OL_B_period)-ramp_steps)
                    OL_B_orientation_cycle = np.hstack((np.ones(int(ramp_steps/2))*start_angle*math.pi/180., OL_B_orientation_cycle, np.ones(int(ramp_steps/2))*end_angle*math.pi/180.))

                    _OL_B_orientation = OL_B_orientation_cycle

                    OL_B_orientation = copy.deepcopy(_OL_B_orientation)
                    for rep_num in range(OL_B_repeat_num-1):
                        OL_B_orientation = np.hstack((OL_B_orientation, _OL_B_orientation))

                    _OL_B_magnitude_up = np.linspace(0, B_max, int(ramp_steps/2))
                    _OL_B_magnitude_fixed = B_max * np.ones(int(controller_loop_bandwidth*OL_B_period)-int(ramp_steps))
                    _OL_B_magnitude_down = np.linspace(B_max, 0, int(ramp_steps/2))

                    _OL_B_magnitude = np.hstack((_OL_B_magnitude_up, _OL_B_magnitude_fixed, _OL_B_magnitude_down))

                    OL_B_magnitude = copy.deepcopy(_OL_B_magnitude)
                    for rep_num in range(OL_B_repeat_num-1):
                        OL_B_magnitude = np.hstack((OL_B_magnitude, _OL_B_magnitude))

                    OL_B_magnitude[0:6] = OL_B_magnitude[0:6] * np.linspace(0, B_max, 6)

                else:
                
                    OL_B_orientation_cycle = np.linspace(90*math.pi/180., 0*math.pi/180., int(controller_loop_bandwidth*OL_B_period/2))

                    _OL_B_orientation = np.hstack((OL_B_orientation_cycle, np.flip(OL_B_orientation_cycle)))

                    OL_B_orientation = copy.deepcopy(_OL_B_orientation)
                    for rep_num in range(OL_B_repeat_num-1):
                        OL_B_orientation = np.hstack((OL_B_orientation, _OL_B_orientation))

                    OL_B_magnitude = B_max * np.ones(totalStepNum)
            
            
                # B dictionary
                # TODO: later either make its own class, or combine with robot class
                OL_B = {"B_period": OL_B_period,
                        "B_orientation": OL_B_orientation,
                        "B_magnitude": OL_B_magnitude,
                        "B_controller_bandwidth": controller_loop_bandwidth,
                }
                controller = OL_B

            if args.desired_shape == "max_COM_z":

                args.sim_time = 5
                
                controller_loop_bandwidth = 120
                OL_B_period = 0.5
                OL_B_repeat_num = 2

                B_max = 10e-3   # 10 mT

                # B_max = 20e-3   # 20 mT

                args.sim_time  = OL_B_repeat_num * OL_B_period


                totalStepNum = int(controller_loop_bandwidth*args.sim_time)

                is_rampUP_DOWN = 1
                ramp_steps = 0
                if is_rampUP_DOWN: 
                    ramp_ratio = 0.1
                    ramp_steps = 0

                    start_angle = 90
                    end_angle = 0

                    start_angle = -90
                    end_angle = 0

                    OL_B_orientation_cycle = np.linspace(start_angle*math.pi/180., end_angle*math.pi/180., int(controller_loop_bandwidth*OL_B_period)-ramp_steps)
                    OL_B_orientation_cycle = np.hstack((np.ones(int(ramp_steps/2))*start_angle*math.pi/180., OL_B_orientation_cycle, np.ones(int(ramp_steps/2))*end_angle*math.pi/180.))

                    _OL_B_orientation = OL_B_orientation_cycle

                    OL_B_orientation = copy.deepcopy(_OL_B_orientation)
                    for rep_num in range(OL_B_repeat_num-1):
                        OL_B_orientation = np.hstack((OL_B_orientation, _OL_B_orientation))

                    _OL_B_magnitude_up = np.linspace(0, B_max, int(ramp_steps/2))
                    _OL_B_magnitude_fixed = B_max * np.ones(int(controller_loop_bandwidth*OL_B_period)-int(ramp_steps))
                    _OL_B_magnitude_down = np.linspace(B_max, 0, int(ramp_steps/2))

                    _OL_B_magnitude = np.hstack((_OL_B_magnitude_up, _OL_B_magnitude_fixed, _OL_B_magnitude_down))

                    OL_B_magnitude = copy.deepcopy(_OL_B_magnitude)
                    for rep_num in range(OL_B_repeat_num-1):
                        OL_B_magnitude = np.hstack((OL_B_magnitude, _OL_B_magnitude))
                    OL_B_magnitude[0:6] = OL_B_magnitude[0:6] * np.linspace(0, B_max, 6)
                else:
                
                    OL_B_orientation_cycle = np.linspace(90*math.pi/180., 0*math.pi/180., int(controller_loop_bandwidth*OL_B_period/2))

                    _OL_B_orientation = np.hstack((OL_B_orientation_cycle, np.flip(OL_B_orientation_cycle)))

                    OL_B_orientation = copy.deepcopy(_OL_B_orientation)
                    for rep_num in range(OL_B_repeat_num-1):
                        OL_B_orientation = np.hstack((OL_B_orientation, _OL_B_orientation))

                    OL_B_magnitude = B_max * np.ones(totalStepNum)
            
            
                # B dictionary
                # TODO: later either make its own class, or combine with robot class
                OL_B = {"B_period": OL_B_period,
                        "B_orientation": OL_B_orientation,
                        "B_magnitude": OL_B_magnitude,
                        "B_controller_bandwidth": controller_loop_bandwidth,
                }
                controller = OL_B
        
        else:
                raise NotImplementedError
    
    elif args.controller_type =="closed-loop":
        "generates a random magnetic field"
        # TODO set the external magnetic field for closed loop control @Arinc
        # decide on the orientaton and magnitude of the magnetic field at the current time
        # follos the RSS paper direction
        # details at the open loop part above

        CL_B_orientation = math.pi/180.*np.random.uniform(low=0, high=180, size=(1,))
        CL_B_magnitude = np.random.uniform(low=1e-3, high=10e-3, size=(1,)) # in Tesla
        CL_B = {"B_orientation": CL_B_orientation,
                "B_magnitude": CL_B_magnitude,
                "B_controller_bandwidth": args.controller_loop_bandwidth,
                "B_step": step,
        }
        controller = CL_B
        raise NotImplementedError

    return args, controller