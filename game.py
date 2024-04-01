import game_control
import pygame
import config

print('Math racer', config.VERSION)
print('by Karol Pokorski')
print()


print()


pygame.init()
pygame.display.set_caption('Math racer {}'.format(config.VERSION))

clock = pygame.time.Clock()

controller = game_control.GameControl()

running = True
frame = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    controller.frame()
    pygame.display.flip()
    clock.tick(config.TARGET_FPS)

print('Thank you for playing.')
pygame.quit()
