define PORTABLE_PET_SPEED = 100
define PORTABLE_PET_MOVE_MARGIN_X = 100
define PORTABLE_PET_MOVE_MARGIN_Y = 100
define PORTABLE_PET_DRAG_WIDTH = 440
define PORTABLE_PET_DRAG_HEIGHT = 480
define PORTABLE_PET_MENU_BOUNDS = (500, 120, 1780, 950)

image portable_pet_anim_special:
    anchor (0.2, 0.0)
    "images/portable_pet/idle_1.png"
    pause 0.7
    "images/portable_pet/idle_2.png"
    pause 0.15
    "images/portable_pet/idle_3.png"
    pause 0.15
    "images/portable_pet/idle_4.png"
    pause 0.15
    "images/portable_pet/idle_5.png"
    pause 0.7

image portable_pet_anim_idle = "images/portable_pet/pet_idle.png"

image portable_pet_anim_walk_left:
    "images/portable_pet/pet_walk_left_1.png"
    pause 0.2
    "images/portable_pet/pet_walk_left_2.png"
    pause 0.2
    repeat

image portable_pet_anim_walk_right:
    "images/portable_pet/pet_walk_right_1.png"
    pause 0.2
    "images/portable_pet/pet_walk_right_2.png"
    pause 0.2
    repeat

image portable_pet_anim_climb:
    anchor (0.35, 0.0)
    "images/portable_pet/pet_climb_1.png"
    pause 0.3
    "images/portable_pet/pet_climb_2.png"
    pause 0.3
    repeat

image portable_pet_anim_fly_left:
    "images/portable_pet/pet_fly_left_1_fixed.png"
    pause 0.15
    "images/portable_pet/pet_fly_left_2_fixed.png"
    pause 0.15
    repeat

image portable_pet_anim_fly_right:
    "images/portable_pet/pet_fly_right_1_fixed.png"
    pause 0.15
    "images/portable_pet/pet_fly_right_2_fixed.png"
    pause 0.15
    repeat

image portable_pet_action_happy:
    "images/portable_pet/happy_fixed_1.png"
    pause 0.12
    "images/portable_pet/happy_fixed_2.png"
    pause 0.14
    "images/portable_pet/happy_fixed_3.png"
    pause 0.12
    "images/portable_pet/happy_fixed_4.png"
    pause 2.2

image portable_pet_action_angry:
    "images/portable_pet/angry_2_aligned.png"
    pause 0.18
    "images/portable_pet/angry_3_aligned.png"
    pause 0.18
    "images/portable_pet/angry_4_aligned.png"
    pause 0.18
    "images/portable_pet/angry_5_aligned.png"
    pause 0.18
    "images/portable_pet/angry_6_aligned.png"
    pause 0.18
    "images/portable_pet/angry_5_aligned.png"
    pause 0.18
    "images/portable_pet/angry_4_aligned.png"
    pause 0.18
    "images/portable_pet/angry_3_aligned.png"
    pause 0.18
    repeat

image portable_pet_action_sleepy:
    "images/portable_pet/sleepy_1.png"
    pause 0.4
    "images/portable_pet/sleepy_2.png"
    pause 4.0
    "images/portable_pet/sleepy_3.png"
    pause 0.4

default portable_pet_enabled = True

init python:
    import math
    import random
    import time

    class PortablePetBehavior:
        def __init__(self):
            curr_time = time.time()
            self.bounds = (0.0, 0.0, float(config.screen_width), float(config.screen_height))
            self.x = config.screen_width / 2.0
            self.y = config.screen_height / 2.0
            self.render_x = self.x
            self.render_y = self.y
            self.current_image = "portable_pet_anim_idle"

            self.next_decision_time = curr_time
            self.idle_start_time = curr_time
            self.video_end_time = 0
            self.move_start_time = curr_time
            self.move_end_time = 0
            self.move_duration = 0.0
            self.move_from_x = self.x
            self.move_from_y = self.y

            self.is_moving = False
            self.is_special_playing = False
            self.is_dragging = False
            self.is_playing_click_anim = False
            self.click_anim_end_time = 0

            self.click_actions = [
                "portable_pet_action_happy",
                "portable_pet_action_angry",
                "portable_pet_action_sleepy",
            ]
            self.dialogues = [
                "喵。",
                "我喜欢吃巧克力味的大福。",
                "我喜欢喝酸一点的果汁。",
                "你觉得我可爱吗？",
                "别点了。",
                "最近你过得还好吗？",
                "很感谢你正在阅读这行字！",
                "我腰好疼，最近坐得有点久了。",
            ]

        def set_bounds(self, bounds, snap=False):
            left, top, right, bottom = bounds
            self.bounds = (float(left), float(top), float(right), float(bottom))

            self.x, self.y = self.clamp_target(self.x, self.y)
            self.render_x, self.render_y = self.clamp_target(self.render_x, self.render_y)

            if snap:
                self.move_from_x = self.render_x = self.x
                self.move_from_y = self.render_y = self.y
                self.is_moving = False
                self.move_duration = 0.0
                self.move_start_time = time.time()
                self.move_end_time = self.move_start_time

        def clamp_target(self, target_x, target_y):
            half_w = PORTABLE_PET_DRAG_WIDTH / 2.0
            half_h = PORTABLE_PET_DRAG_HEIGHT / 2.0
            left, top, right, bottom = self.bounds

            min_x = max(left + PORTABLE_PET_MOVE_MARGIN_X, left + half_w)
            max_x = min(right - PORTABLE_PET_MOVE_MARGIN_X, right - half_w)
            min_y = max(top + PORTABLE_PET_MOVE_MARGIN_Y, top + half_h)
            max_y = min(bottom - PORTABLE_PET_MOVE_MARGIN_Y, bottom - half_h)

            return (
                min(max(target_x, min_x), max_x),
                min(max(target_y, min_y), max_y),
            )

        def sync_render_position(self, curr_time=None):
            if self.is_dragging:
                return

            if curr_time is None:
                curr_time = time.time()

            if self.is_moving and self.move_duration > 0:
                progress = min(1.0, max(0.0, (curr_time - self.move_start_time) / self.move_duration))
                self.render_x = self.move_from_x + ((self.x - self.move_from_x) * progress)
                self.render_y = self.move_from_y + ((self.y - self.move_from_y) * progress)
            else:
                self.render_x = self.x
                self.render_y = self.y

        def stop_motion(self):
            self.sync_render_position()
            self.x = self.render_x
            self.y = self.render_y
            self.is_moving = False
            self.move_duration = 0.0
            self.move_start_time = time.time()
            self.move_end_time = self.move_start_time
            self.move_from_x = self.render_x
            self.move_from_y = self.render_y

        def begin_move(self, target_x, target_y, image_name):
            target_x, target_y = self.clamp_target(target_x, target_y)
            distance = math.hypot(target_x - self.render_x, target_y - self.render_y)

            self.x = target_x
            self.y = target_y
            self.current_image = image_name
            self.move_from_x = self.render_x
            self.move_from_y = self.render_y

            if distance < 1:
                self.stop_motion()
                self.current_image = "portable_pet_anim_idle"
                self.idle_start_time = time.time()
                return

            self.is_moving = True
            self.move_duration = max(0.35, distance / float(PORTABLE_PET_SPEED))
            self.move_start_time = time.time()
            self.move_end_time = self.move_start_time + self.move_duration

        def on_click(self):
            renpy.sound.stop(channel="sound")
            self.stop_motion()
            self.is_special_playing = False
            self.is_playing_click_anim = True
            self.current_image = random.choice(self.click_actions)
            self.click_anim_end_time = time.time() + 3.0
            renpy.show_screen("portable_pet_dialogue_screen", txt=random.choice(self.dialogues))
            self.idle_start_time = time.time()
            renpy.restart_interaction()

        def start_drag(self, drags):
            self.stop_motion()
            self.is_dragging = True
            self.is_special_playing = False
            self.is_playing_click_anim = False
            self.current_image = "portable_pet_anim_idle"
            self.idle_start_time = time.time()

        def update_drag(self, drags):
            if not drags:
                return

            drag = drags[0]
            self.render_x = drag.x + (drag.w / 2.0)
            self.render_y = drag.y + (drag.h / 2.0)
            self.x, self.y = self.clamp_target(self.render_x, self.render_y)
            self.render_x = self.x
            self.render_y = self.y
            self.idle_start_time = time.time()

        def end_drag(self, drags, drop):
            self.update_drag(drags)
            self.is_dragging = False
            self.current_image = "portable_pet_anim_idle"
            self.idle_start_time = time.time()
            self.next_decision_time = time.time() + random.uniform(5.0, 15.0)
            renpy.restart_interaction()

        def on_drag_click(self, drag):
            self.is_dragging = False
            self.on_click()

        def decide_next_move(self):
            choice = random.choice(["walk", "climb", "fly", "stay"])
            left, top, right, bottom = self.bounds

            if choice == "stay":
                self.stop_motion()
                self.current_image = "portable_pet_anim_idle"
                self.idle_start_time = time.time()
                return

            if choice == "walk":
                new_x = random.randint(int(left + PORTABLE_PET_MOVE_MARGIN_X), int(right - PORTABLE_PET_MOVE_MARGIN_X))
                image_name = "portable_pet_anim_fly_right" if new_x > self.render_x else "portable_pet_anim_fly_left"
                self.begin_move(new_x, self.render_y, image_name)
            elif choice == "climb":
                new_y = random.randint(int(top + PORTABLE_PET_MOVE_MARGIN_Y), int(bottom - PORTABLE_PET_MOVE_MARGIN_Y))
                self.begin_move(self.render_x, new_y, "portable_pet_anim_climb")
            else:
                new_x = random.randint(int(left + PORTABLE_PET_MOVE_MARGIN_X), int(right - PORTABLE_PET_MOVE_MARGIN_X))
                new_y = random.randint(int(top + PORTABLE_PET_MOVE_MARGIN_Y), int(bottom - PORTABLE_PET_MOVE_MARGIN_Y))
                image_name = "portable_pet_anim_fly_right" if new_x > self.render_x else "portable_pet_anim_fly_left"
                self.begin_move(new_x, new_y, image_name)

        def trigger_special_video(self):
            self.stop_motion()
            self.is_special_playing = True
            self.current_image = "portable_pet_anim_special"
            self.video_end_time = time.time() + 3.0
            renpy.restart_interaction()

        def update(self):
            curr_time = time.time()
            self.sync_render_position(curr_time)

            if self.is_dragging:
                return

            if self.is_playing_click_anim:
                if curr_time > self.click_anim_end_time:
                    self.is_playing_click_anim = False
                    self.current_image = "portable_pet_anim_idle"
                    renpy.restart_interaction()
                return

            if self.is_special_playing:
                if curr_time > self.video_end_time:
                    self.is_special_playing = False
                    self.current_image = "portable_pet_anim_idle"
                    self.idle_start_time = curr_time
                    renpy.restart_interaction()
                return

            if self.is_moving:
                if curr_time > self.move_end_time:
                    self.is_moving = False
                    self.render_x = self.x
                    self.render_y = self.y
                    self.current_image = "portable_pet_anim_idle"
                    self.idle_start_time = curr_time
                    renpy.restart_interaction()
                return

            if curr_time - self.idle_start_time > 7.0:
                self.trigger_special_video()
                return

            if curr_time > self.next_decision_time:
                self.decide_next_move()
                self.next_decision_time = curr_time + random.uniform(5.0, 15.0)
                renpy.restart_interaction()

    portable_pet_behavior = PortablePetBehavior()

    def portable_pet_prepare_menu_shell():
        portable_pet_behavior.set_bounds((0, 0, config.screen_width, config.screen_height), snap=True)
        portable_pet_behavior.next_decision_time = time.time() + random.uniform(1.5, 4.0)

    def portable_pet_prepare_fullscreen():
        portable_pet_behavior.set_bounds((0, 0, config.screen_width, config.screen_height), snap=True)

screen portable_pet_main_menu():
    if portable_pet_enabled:
        on "show" action Function(portable_pet_prepare_fullscreen)
        use portable_pet_screen

screen portable_pet_menu_shell():
    zorder 120

    if portable_pet_enabled:
        on "show" action Function(portable_pet_prepare_menu_shell)
        use portable_pet_screen

screen portable_pet_screen():
    zorder 1000

    if portable_pet_enabled:
        if not portable_pet_behavior.is_dragging:
            timer 0.1 repeat True action Function(portable_pet_behavior.update)

        draggroup:
            drag:
                draggable True
                droppable False
                drag_raise True
                drag_offscreen (-120, 120, -120, 120)
                focus_mask True
                xpos int(portable_pet_behavior.render_x - (PORTABLE_PET_DRAG_WIDTH / 2))
                ypos int(portable_pet_behavior.render_y - (PORTABLE_PET_DRAG_HEIGHT / 2))
                activated portable_pet_behavior.start_drag
                dragging portable_pet_behavior.update_drag
                dragged portable_pet_behavior.end_drag
                clicked portable_pet_behavior.on_drag_click

                fixed:
                    xsize PORTABLE_PET_DRAG_WIDTH
                    ysize PORTABLE_PET_DRAG_HEIGHT

                    add portable_pet_behavior.current_image:
                        xalign 0.5
                        yalign 1.0

screen portable_pet_dialogue_screen(txt):
    zorder 150

    $ bubble_width = min(520, int(config.screen_width * 0.24))
    $ bubble_x = int(portable_pet_behavior.render_x)
    $ bubble_y = int(portable_pet_behavior.render_y - (PORTABLE_PET_DRAG_HEIGHT / 2) - 20)
    $ half_width = int(bubble_width / 2)
    $ bubble_x = max(half_width + 20, min(config.screen_width - half_width - 20, bubble_x))
    $ bubble_y = max(40, bubble_y)

    frame:
        xpos bubble_x
        ypos bubble_y
        xanchor 0.5
        yanchor 1.0
        xsize bubble_width
        background Frame(Solid("#000000a0"), 4, 4)
        padding (15, 15)

        text "[txt]":
            size 26
            color "#ffffff"
            text_align 0.5
            xalign 0.5
            xmaximum bubble_width - 30

    timer 3.0 action Hide("portable_pet_dialogue_screen")
    dismiss action Hide("portable_pet_dialogue_screen")
