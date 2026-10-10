# Spatial and Kinematic Math

## Conventions
The site frame is `(x forward, y left, z up)`. A rover pose is `(x, y, yaw)` and maps rover coordinates by `R(yaw)p + t`. Camera height is measured from the flat ground plane; roll is assumed small and ignored.

## Pinhole projection
For a pixel `(u,v)`, normalized coordinates are `l=(u-cx)/fx` and `q=(v-cy)/fy`. With a downward camera pitch `theta`, the ground-ray coordinates are `forward=cos(theta)-sin(theta)q` and `down=sin(theta)+cos(theta)q`. The ray intersects ground at `s=h/down`, producing `(x,y)=(s*forward,s*l)`. `down<=0` is above-horizon and rejected. A sloped ground uses `z=h-a*x-b*y` and solves the intersection by a short vectorized fixed-point iteration.

## Jacobian and uncertainty
The implementation computes `J_p = d(x,y)/d(u,v)` by the analytic ray equations (the public verification helper uses central differences). Pose uncertainty uses `J_q=[[1,0,-sin(yaw)x-cos(yaw)y],[0,1,cos(yaw)x-sin(yaw)y]]`. Thus `Sigma_site = R J_p Sigma_pixel J_p^T R^T + J_q Sigma_pose J_q^T`. The reported scalar sigma is the square root of the largest eigenvalue; ellipse axes are square roots of both eigenvalues.

## Odometry
Each frame receives true incremental translation and yaw-rate, plus zero-mean Gaussian velocity/yaw noise. A slowly wandering bias is integrated when drift is enabled. The estimator integrates measurements in its current heading and grows covariance by process noise and bias-growth terms. It is deterministic for `SEED`.

## Fusion
For a static hazard, independent sightings are combined in information form: `Sigma=(Sigma_old^-1+Sigma_meas^-1)^-1` and `p=Sigma(Sigma_old^-1 p_old+Sigma_meas^-1 p_meas)`. A Mahalanobis gate rejects incompatible associations. This reduces variance and therefore repeated-sighting error when the track identity is maintained.

## Assumptions and sensitivity
Known intrinsics, known camera height and pitch, flat ground, small roll, static hazards, and locally Gaussian errors are assumed. Run `python -m localize.sensitivity` to quantify violations. The script evaluates a 5 cm height error, a 10 degree slope, and both combined for representative points; its output is the measured mean position error in metres and is included in the generated evaluation artifacts.
