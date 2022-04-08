import math
from wpimath.geometry import Pose2d, Rotation2d, Translation2d

# in meters
kTrackWidth = 0.6096

kWheelRadius = 0.1524 / 2
kPulsePerRevolution = 360
kDistancePerPulse = (2 * math.pi * kWheelRadius) / kPulsePerRevolution


# The max velocity and acceleration for our autonomous.
kMaxSpeedMetersPerSecond = 4
kMaxAccelerationMetersPerSecondSquared = 1
kMaxVoltage = 10

# with ball.. 0.05, otherwise 1 is fine
# kMaxCentripetalAcceleration = 1
kMaxCentripetalAcceleration = 0.05

# sysid filtered results (git 172d5c42, window size=10)
kS_linear = 1.0898
kV_linear = 3.1382
kA_linear = 1.7421

kS_angular = 2.424
kV_angular = 3.3557
kA_angular = 1.461

rdeg = Rotation2d.fromDegrees

# All of these are in meters to make pathplanner easy
kPose_StartTopStraight = Pose2d(6.48, 5.3, rdeg(147))
# kPose_StartTopAligned = Pose2d(6.6, 5.18, rdeg(135))
# kPose_StartMiddleOut = Pose2d(6.18, 4.2, rdeg(180))
# kPose_StartMiddleIn = Pose2d(6.18, 4.2, rdeg(0))
kPose_StartBottomLeft = Pose2d(6.96, 2.62, rdeg(-155))
kPose_StartBottomRight = Pose2d(7.6, 2.0, rdeg(-90))

# ball positions
kPose_BallTopRed = Pose2d(6.07, 7.24, rdeg(90))
kPose_BallTopBlue = Pose2d(5.04, 6.18, rdeg(147))
# kPos_BallMidRed = Pose2d(4.53, 3.27)
# kPos_BallMidBlue = Pose2d(5.16, 1.91)
kPose_BallBotBlue = Pose2d(7.64, 0.36, rdeg(-155))
# kPos_BallBotRed = Pose2d(9.13, 0.39, rdeg(-56))

# .. this isn't achievable without reverse
kPos_BallTech = Pose2d(1.2, 1.2, rdeg(-130))

# shooting positions
kPose_ShootTop = Pose2d(6.6, 5.2, rdeg(-35))
kPose_ShootMid = Pose2d(6.2, 4.5, rdeg(0))

# only used for simulation
kStartingPose = kPose_StartTopStraight
