import commands2
import constants
import wpilib


class RobotContainer:
    """
    This class is where the bulk of the robot should be declared. Since Command-based is a
    "declarative" paradigm, very little robot logic should actually be handled in the :class:`.Robot`
    periodic methods (other than the scheduler calls). Instead, the structure of the robot (including
    subsystems, commands, and button mappings) should be declared here.
    """

    def __init__(self, robot) -> None:
        # The robot's subsystems
        # self.drivetraintrain = DriveSubsystem()
        # if commands2.TimedCommandRobot.isSimulation():
        #    self.drivetrain.simPhysics = BadSimPhysics(self.drivetrain, robot)

        # The driver's controller
        self.controller = wpilib.XboxController(constants.CONTROLLER_PORT)

        # Configure the button bindings and autos
        self.configureButtonBindings()
        # self.configureAutos()

    def configureButtonBindings(self) -> None:
        """
        Use this method to define your button->command mappings. Buttons can be created by
        instantiating a :GenericHID or one of its subclasses (Joystick or XboxController),
        and then passing it to a JoystickButton.
        """

        x_button = self.controller.button(wpilib.XboxController.Button.kX)
        # x_button.onTrue(ResetXY(x=0.0, y=0.0, headingDegrees=0.0, drivetrain=self.drivetrain))
        # x_button.whileTrue(RunCommand(self.drivetrain.setX, self.drivetrain))  # use the swerve X brake when "X" is pressed

        y_button = self.controller.button(wpilib.XboxController.Button.kY)
        # y_button.onTrue(ResetSwerveFront(self.drivetrain))

    def disablePIDSubsystems(self) -> None:
        """Disables all ProfiledPIDSubsystem and PIDSubsystem instances.
        This should be called on robot disable to prevent integral windup."""

    def getAutonomousCommand(self) -> commands2.Command:
        """
        :returns: the command to run in autonomous
        """
        # command = self.chosenAuto.getSelected()
        # return command()
        return None

    """
    def configureAutos(self):
        self.chosenAuto = wpilib.SendableChooser()
        # you can also set the default option, if needed
        self.chosenAuto.setDefaultOption("trajectory example", self.getAutonomousTrajectoryExample)
        self.chosenAuto.addOption("left blue", self.getAutonomousLeftBlue)
        self.chosenAuto.addOption("left red", self.getAutonomousLeftRed)
        wpilib.SmartDashboard.putData("Chosen Auto", self.chosenAuto)

    def getAutonomousLeftBlue(self):
        setStartPose = ResetXY(x=0.783, y=6.686, headingDegrees=+60, drivetrain=self.drivetrain)
        driveForward = commands2.RunCommand(lambda: self.drivetrain.arcadeDrive(xSpeed=1.0, rot=0.0), self.drivetrain)
        stop = commands2.InstantCommand(lambda: self.drivetrain.arcadeDrive(0, 0))

        command = setStartPose.andThen(driveForward.withTimeout(1.0)).andThen(stop)
        return command

    def getAutonomousLeftRed(self):
        setStartPose = ResetXY(x=15.777, y=4.431, headingDegrees=-120, drivetrain=self.drivetrain)
        driveForward = commands2.RunCommand(lambda: self.drivetrain.arcadeDrive(xSpeed=1.0, rot=0.0), self.drivetrain)
        stop = commands2.InstantCommand(lambda: self.drivetrain.arcadeDrive(0, 0))

        command = setStartPose.andThen(driveForward.withTimeout(2.0)).andThen(stop)
        return command

    def getAutonomousTrajectoryExample(self) -> commands2.Command:
        # Create config for trajectory
        config = TrajectoryConfig(
            AutoConstants.kMaxSpeedMetersPerSecond,
            AutoConstants.kMaxAccelerationMetersPerSecondSquared,
        )
        # Add kinematics to ensure max speed is actually obeyed
        config.setKinematics(DriveConstants.kDriveKinematics)

        # An example trajectory to follow. All units in meters.
        exampleTrajectory = TrajectoryGenerator.generateTrajectory(
            # Start at the origin facing the +X direction
            Pose2d(0, 0, Rotation2d(0)),
            # Pass through these two interior waypoints, making an 's' curve path
            [Translation2d(0.5, 0.5), Translation2d(1, -0.5)],
            # End 1.5 meters straight ahead of where we started, facing forward
            Pose2d(1.5, 0, Rotation2d(0)),
            config,
        )

        thetaController = ProfiledPIDControllerRadians(
            AutoConstants.kPThetaController,
            0,
            0,
            AutoConstants.kThetaControllerConstraints,
        )
        thetaController.enableContinuousInput(-math.pi, math.pi)

        driveController = HolonomicDriveController(
            PIDController(AutoConstants.kPXController, 0, 0),
            PIDController(AutoConstants.kPXController, 0, 0),
            thetaController,
        )

        swerveControllerCommand = commands2.SwerveControllerCommand(
            exampleTrajectory,
            self.drivetrain.getPose,  # Functional interface to feed supplier
            DriveConstants.kDriveKinematics,
            driveController,
            self.drivetrain.setModuleStates,
            (self.drivetrain,),
        )

        # Reset odometry to the starting pose of the trajectory.
        self.drivetrain.resetOdometry(exampleTrajectory.initialPose())

        # Run path following command, then stop at the end.
        return swerveControllerCommand.andThen(
            cmd.run(
                lambda: self.drivetrain.drive(0, 0, 0, False, False),
                self.drivetrain,
            )
        )
    """

    def getTestCommand(self) -> typing.Optional[commands2.Command]:
        """
        :returns: the command to run in test mode (to exercise all systems)
        """
        return None
