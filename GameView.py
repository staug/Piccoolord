import pygame
import GameResources
import GameController
import GameObject
import ConfigParser
import WorldMapLogic
import PythonExtraLib.reader

class PygameInit(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PygameInit, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        pygame.init()
        pygame.display.set_mode(GameResources.GLOBAL_WINDOW_SIZE, 0, 32)


class SceneBase:
    def __init__(self):
        PygameInit()
        self.next = self
    
    def ProcessInput(self, events, pressed_keys):
        print("uh-oh, you didn't override this in the child class")

    def Update(self):
        print("uh-oh, you didn't override this in the child class")

    def Render(self, screen):
        print("uh-oh, you didn't override this in the child class")

    def SwitchToScene(self, next_scene):
        self.next = next_scene
    
    def Terminate(self):
        self.SwitchToScene(None)



# The rest is code where you implement your game using the Scenes model 

class TitleScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
    
    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # Move to the next scene when the user pressed Enter 
                self.SwitchToScene(GameScene(controller=GameController.GameController()))
    
    def Update(self):
        pass
    
    def Render(self, screen):
        # For the sake of brevity, the title scene is a blank red screen 
        screen.fill((255, 0, 0))


class RollPlayerScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # Move to the next scene when the user pressed Enter
                self.SwitchToScene(GameScene(controller=GameController.GameController()))

    def Update(self):
        pass

    def Render(self, screen):
        # For the sake of brevity, the title scene is a blank red screen
        screen.fill((255, 0, 0))


class GameScene(SceneBase):
    def __init__(self, controller = None):
        SceneBase.__init__(self)
        self.background = None
        self.controller = controller
        if not self.controller.is_text_initialized(GameResources.TEXT_DIALOGUE):
            text_dialogue = PythonExtraLib.reader.Reader("Bienvenue",
                                            pos=(GameResources.TEXT_MARGIN,
                                                 GameResources.CAMERA_WINDOW_SIZE[1] + GameResources.TEXT_MARGIN),
                                            width=GameResources.CAMERA_WINDOW_SIZE[0]-2*GameResources.TEXT_MARGIN,
                                            font="./PythonExtraLib/monofonto.ttf",
                                            fontsize=12,
                                            height=GameResources.GLOBAL_WINDOW_SIZE[1] - GameResources.CAMERA_WINDOW_SIZE[1]-2*GameResources.TEXT_MARGIN,
                                            bg=GameResources.TEXT_BGCOLOR,
                                            fgcolor=(20,20,20))
            self.controller.add_text_display(text_dialogue, GameResources.TEXT_DIALOGUE)
        if not self.controller.is_text_initialized(GameResources.TEXT_FIGHT):
            text_fight = PythonExtraLib.reader.Reader("Bienvenue",
                                            pos=(GameResources.TEXT_MARGIN,
                                                 GameResources.CAMERA_WINDOW_SIZE[1] + GameResources.TEXT_MARGIN),
                                            width=GameResources.CAMERA_WINDOW_SIZE[0]-2*GameResources.TEXT_MARGIN,
                                            font="./PythonExtraLib/monofonto.ttf",
                                            fontsize=12,
                                            height=GameResources.GLOBAL_WINDOW_SIZE[1] - GameResources.CAMERA_WINDOW_SIZE[1]-2*GameResources.TEXT_MARGIN,
                                            bg=GameResources.TEXT_BGCOLOR,
                                            fgcolor=(255,20,20))
            self.controller.add_text_display(text_fight, GameResources.TEXT_FIGHT)
        self.current_text_display_type = GameResources.TEXT_DIALOGUE


    def ProcessInput(self, events, pressed_keys):
        self.dx = self.dy = 0
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.dy -= 1
                elif event.key == pygame.K_DOWN:
                    self.dy += 1
                elif event.key == pygame.K_LEFT:
                    self.dx -= 1
                elif event.key == pygame.K_RIGHT:
                    self.dx += 1
                elif event.key == pygame.K_c:
                    self.controller.view.camera.center(self.controller.player.pos)

            self.controller.text_display[self.current_text_display_type].simple_update(event)


    def Update(self):
        #Call the other objects take action if the player acted
        if (self.dx != 0 or self.dy != 0) and (self.controller.player.move(self.dx, self.dy)):
            self.controller.ticker.next_turn()

            if self.controller.view.camera.close_edge(self.controller.player.pos):
                self.controller.view.camera.center(self.controller.player.pos)
            for obj in self.controller.objects:
                self.controller.text("Name: {} Pos: {}".format(obj.name, obj.pos),
                                     GameResources.TEXT_DIALOGUE, add=True)

    
    def Render(self, screen):
        self.controller.view.camera.center(self.controller.player.pos)
        for obj in self.controller.objects:
            obj.draw()

        if not self.background:
            self.background = pygame.image.load('./resources/img/background_game2.png').convert_alpha()

        screen.blit(self.background, (0, 0))
        screen.blit(self.controller.view.region_view, (0,0), area=self.controller.view.camera.camera_rect)
        screen.blit(self.controller.view.explorer_map.surface, (50,50), special_flags=pygame.BLEND_RGBA_ADD)
        self.controller.text_display[self.current_text_display_type].show()




def run_game(window_size, fps, starting_scene):
    pygame.init()
    screen = pygame.display.set_mode(window_size, 0, 32)
    clock = pygame.time.Clock()

    active_scene = starting_scene

    while active_scene != None:
        pressed_keys = pygame.key.get_pressed()

        # Event filtering
        filtered_events = []
        for event in pygame.event.get():
            quit_attempt = False
            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                alt_pressed = pressed_keys[pygame.K_LALT] or \
                              pressed_keys[pygame.K_RALT]
                if event.key == pygame.K_ESCAPE:
                    quit_attempt = True
                elif event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True

            if quit_attempt:
                active_scene.Terminate()
            else:
                filtered_events.append(event)

        active_scene.ProcessInput(filtered_events, pressed_keys)
        active_scene.Update()
        active_scene.Render(screen)

        active_scene = active_scene.next

        pygame.display.flip()
        clock.tick(fps)

if __name__ == '__main__':

    run_game(GameResources.GLOBAL_WINDOW_SIZE, 30, GameScene(controller=GameController.GameController()))