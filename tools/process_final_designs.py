import sys
import os

# Appending repo's root dir in the python path to enable subsequent imports

sys.path.append(os.getcwd() + "/..")

from tools.data_analysis import get_robots_ready_for_experiment

def main():

    path_to_files = "../data/inds2process"
    path_to_save = "../data/inds_processed"

    get_robots_ready_for_experiment(path_to_files=path_to_files, 
                                    path_to_save=path_to_save, 
                                    render_desiredShape=0, 
                                    convert_to_dxf=0,
                                    prep_3Dfabrication=1, 
                                    print_mag_profile=0, 
                                    draw_robots=0, 
                                    render_robots=0,
                                    render_final=0,
                                    render_holder=0)



if __name__ == "__main__":

    main()
    
    