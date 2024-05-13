#! /usr/bin/env python3

import sys
import pygame

import forcedimension_core as fdsdk
from forcedimension_core import dhd
from forcedimension_core.dhd import DHDError
from forcedimension_core.dhd.os_independent import kbGet, kbHit

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

running = True

b = 5  # damping coefficient in [N][s]/[m]
k = 150  # spring constant in [N]/[m]

# Storage buffers
pos = [0.0, 0.0, 0.0]
v = [0.0, 0.0, 0.0]
f = [0.0, 0.0, 0.0]

# Try to open the first available device
if (ID := dhd.open()) == -1:
    print(f"Error: {dhd.errorGetLastStr()}")
    sys.exit(1)

if (name := dhd.getSystemName()) is not None:
    print(isinstance(name, str))  # prints "True"
    print(name)

try:

    # Make closing a gripper be an emulated as a button on button ID 0.
    if dhd.emulateButton(True, ID) == -1:
        if dhd.errorGetLast() != fdsdk.constants.ErrorNum.NOT_AVAILABLE:
            raise fdsdk.util.errno_to_exception(dhd.errorGetLast())(
                op='forcedimension_core.dhd.emulateButton', ID=ID
            )
    # Run until button 0 is pressed (typically the center or only button)
    # or q is pressed on the keyboard
    while running:
        # Did the user click the window close button?

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # Fill the background with white
        if (dhd.getPosition(out=pos, ID=ID) == -1):
            raise fdsdk.util.errno_to_exception(dhd.errorGetLast())(
                op='forcedimension_core.dhd.getPosition', ID=ID
            )

        # Try to get the velocity
        if (dhd.getLinearVelocity(out=v, ID=ID) == -1):
            raise fdsdk.util.errno_to_exception(dhd.errorGetLast())(
                op='forcedimension_core.dhd.getLinearVelocity', ID=ID
            )
        if(btn_state == True):
            # Set the dynamics to be a spring-mass damper
            f[0] = -k * pos[0] - b * v[0]
            f[1] = -k * pos[1] - b * v[1]
            f[2] = -k * pos[2] - b * v[2]

        # Try to set the force
        if (dhd.setForce(f, ID=ID) == -1):
            raise fdsdk.util.errno_to_exception(dhd.errorGetLast())(
                op='forcedimension_core.dhd.setForce', ID=ID
            )

        if (btn_state := dhd.getButton(index=0, ID=ID)) == -1:
            raise fdsdk.util.errno_to_exception(dhd.errorGetLast())(
                op='forcedimension_core.dhd.getButton', ID=ID
            )
        screen.fill((255, 255, 255))
        # Draw a solid blue circle in the center
        pygame.draw.circle(screen, (0, 0, 255), (250, 250), 75)
        # Flip the display
        pygame.display.flip()

except DHDError as ex:
    print(str(ex))
finally:
    # On error, close the device and gracefully exit
    dhd.close(ID)
    sys.exit(1)
    pygame.quit()