# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 16:47:39 2024

@author: zj
"""

import torch as th

from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

class FeatureExtractor(BaseFeaturesExtractor):
    """
    Feature extractor to help learn the JSBSim environment. 
    
    ### Position
    This extractor converts the position to relative cylindrical coordinates. Raw
    altitude is also preserved since it's necessary to avoid crashing. 
    
    The distance to the goal is normalized as 1/(1+distance*scale). 'Scale' is a 
    constant that we have set to 1e-3 (meters to kilometers). The rest of the
    equation bounds the value between 0 and 1. Additionally it approaches 0 as
    distance goes to infinity. This means the impact of distance on the network
    diminishes as it increases. The intuition behind this is that the policy 
    should depend more on relative bearing at greater distance (e.g. just turn to
    face the goal and fly straight.)


    ### Velocities and angular rates
    Velocities are left unchanged since mach, alpha are already pretty 
    well scaled. Angular rates are also left unchanged since they are unlikely to
    grow too large in practice due to the low-level regulator.

    ### Angles
    All angles (attitude, relative bearing, alpha, beta) are converted to sine-
    cosine pairs. This makes sure that pi and -pi are the same in the feature 
    space and will produce the same output.  
    """
    def __init__(self, observation_space):
        super().__init__(observation_space, 15)

    def forward(self, observations):
        # Unpack
        position = observations[:,:3]
        mach = observations[:,3:4]
        alpha_beta = observations[:,4:5]
        angular_rates = observations[:,5:8]
        phi_theta = observations[:,8:10]
        psi =  observations[:,10:11]
        goal = observations[:,11:]

        # Transform position
        displacement = goal - position
        distance = th.sqrt(th.sum(displacement[:,:2]**2, 1, True))
        dz = displacement[:,2:3]
        altitude = position[:,2:3]
        abs_bearing = th.atan2(displacement[:,1:2], displacement[:,0:1])
        rel_bearing = abs_bearing - psi

        # We normalize distance this way to bound it between 0 and 1
        dist_norm = 1/(1+distance*1e-3)

        # Normalize these by approximate flight ceiling
        dz_norm = dz/5000 #15000
        alt_norm = altitude/5000

        # Angles to Sine/Cosine pairs
        cab, sab = th.cos(alpha_beta), th.sin(alpha_beta)
        cpt, spt = th.cos(phi_theta), th.sin(phi_theta)
        cr, sr = th.cos(rel_bearing), th.sin(rel_bearing)
        #print(th.concat([dist_norm, dz_norm, alt_norm, mach, angular_rates, cab, sab, cpt, spt, cr, sr], 1).shape)
        return th.concat([dist_norm, dz_norm, alt_norm, mach, angular_rates, cab, sab, cpt, spt, cr, sr], 1)
