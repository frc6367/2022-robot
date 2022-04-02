import math

# in meters
kTrackWidth = 0.6096

kWheelRadius = 0.1524 / 2
kPulsePerRevolution = 360
kDistancePerPulse = (2 * math.pi * kWheelRadius) / kPulsePerRevolution


# The max velocity and acceleration for our autonomous.
kMaxSpeedMetersPerSecond = 3
kMaxAccelerationMetersPerSecondSquared = 3
kMaxVoltage = 10

# sysid filtered results (git 172d5c42, window size=10)
kS_linear = 1.0898
kV_linear = 3.1382
kA_linear = 1.7421

kS_angular = 2.424
kV_angular = 3.3557
kA_angular = 1.461
