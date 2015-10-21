__author__ = 'ratcave'

def motive_camera_vislight_configure():
    import motive
    for cam in motive.get_cams():

            # All cameras should have frame rate changed.
            cam.frame_rate = 30

            if 'Prime 13' in cam.name:
                cam.set_settings(videotype=0, exposure=33000, threshold=80, intensity=0)  #check if 480 corresponds to these thousands described in motive
                cam.image_gain = 8  # 8 is the maximum image gain setting
                cam.set_filter_switch(False)
            else:
                cam.set_settings(0, cam.exposure, cam.threshold, cam.intensity)