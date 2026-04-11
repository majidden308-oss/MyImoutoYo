init -6 python:
    import random
    import time
    import renpy.store as store

    MENU_COMPANION_CLICK_COOLDOWN = 0.85
    MENU_COMPANION_BUBBLE_SECONDS = 3.2
    MENU_COMPANION_TICK_SECONDS = 0.08

    def menu_companion_line(text, voice=None):
        return {
            "text": text,
            "voice": voice,
        }

    if not hasattr(store.persistent, "menu_companion_first_memory_started"):
        store.persistent.menu_companion_first_memory_started = False
    if not hasattr(store.persistent, "menu_companion_first_save_done"):
        store.persistent.menu_companion_first_save_done = False

    menu_companion_character_defs = {
        "hero": {
            "display_name": u"莫于",
            "main_image": "menu_companion_hero_base",
            "lashes_image": "menu_companion_hero_lashes",
            "closed_image": "menu_companion_hero_closed",
            "pupil_image": "menu_companion_hero_pupils",
            "pupil_range": (5.2, 3.1),
            "pupil_focus_origin": (0.69, 0.47),
            "pupil_follow_smoothing": 0.68,
            "blink_hold_seconds": 0.10,
            "blink_interval_range": (2.8, 5.4),
            "size": (1431, 922),
            "zoom": 0.92,
            "xpos": 725,
            "ypos": 245,
            "head_hover_rect": (1020, 20, 560, 390),
            "first_prompt_offset": (500, -28),
            "first_prompt_size": (520, 336),
            "first_prompt_click_rect": (96, 96, 286, 118),
            "bubble_xpos": 1670,
            "bubble_ypos": 165,
            "bubble_tail_xpos": 360,
            "dialogues": {
                "default": [
                    menu_companion_line(u"别点了"),
                    menu_companion_line(u"感谢你正在看这行字"),
                    menu_companion_line(u"别点了，我的list里就四句话"),
                    menu_companion_line(u"我好孤独"),
                ],
                "morning": [
                    menu_companion_line(u"清晨的空气不错"),
                    menu_companion_line(u"今天也许会是温柔的一天。"),
                ],
                "day": [
                    menu_companion_line(u"午后的光线正好，故事也该继续了。"),
                ],
                "night": [
                    menu_companion_line(u"晚上更适合安静地读一段故事。"),
                    menu_companion_line(u"别熬得太晚"),
                ],
                "high_affection": [
                    menu_companion_line(u"你又来看我了。这样的话，我会记住的。"),
                ],
            },
        },
    }

    def menu_companion_default_runtime():
        now = time.time()
        return {
            "last_interaction": now,
            "bubble_text": None,
            "bubble_until": 0.0,
            "last_line": None,
            "last_click_at": 0.0,
            "last_mouse": None,
            "head_hovered": False,
            "first_prompt_visible": False,
            "first_prompt_hold_until": 0.0,
            "pupil_offset": (0.0, 0.0),
            "is_blinking": False,
            "blink_until": 0.0,
            "next_blink_at": now + random.uniform(2.8, 5.4),
        }

    def menu_companion_state(character_id):
        runtime = store.menu_companion_runtime
        if character_id not in runtime:
            runtime[character_id] = menu_companion_default_runtime()
        return runtime[character_id]

    def menu_companion_display_size(character_id):
        cfg = menu_companion_character_defs[character_id]
        width, height = cfg["size"]
        zoom = cfg.get("zoom", 1.0)
        scale = min(
            float(renpy.config.screen_width) / 1920.0,
            float(renpy.config.screen_height) / 1080.0,
        )
        return int(round(width * zoom * scale)), int(round(height * zoom * scale))

    def menu_companion_render_zoom(character_id):
        cfg = menu_companion_character_defs[character_id]
        scale = min(
            float(renpy.config.screen_width) / 1920.0,
            float(renpy.config.screen_height) / 1080.0,
        )
        return cfg.get("zoom", 1.0) * scale

    def menu_companion_time_bucket():
        hour = time.localtime().tm_hour
        if 5 <= hour < 11:
            return "morning"
        if 11 <= hour < 18:
            return "day"
        return "night"

    def menu_companion_clamp(value, lower, upper):
        if value < lower:
            return lower
        if value > upper:
            return upper
        return value

    def menu_companion_soft_limit(value, exponent=1.7):
        value = menu_companion_clamp(value, -1.0, 1.0)
        if value == 0.0:
            return 0.0
        sign = -1.0 if value < 0.0 else 1.0
        return sign * pow(abs(value), exponent)

    def menu_companion_target_pupil_offset(character_id):
        cfg = menu_companion_character_defs[character_id]
        if not cfg.get("pupil_image"):
            return (0.0, 0.0)

        mouse_pos = renpy.get_mouse_pos()
        if not mouse_pos:
            return (0.0, 0.0)

        mx, my = mouse_pos
        screen_w = float(renpy.config.screen_width)
        screen_h = float(renpy.config.screen_height)
        focus_x, focus_y = cfg.get("pupil_focus_origin", (0.5, 0.5))
        range_x, range_y = cfg.get("pupil_range", (0.0, 0.0))

        dx = menu_companion_soft_limit((mx - (screen_w * focus_x)) / (screen_w * 0.62))
        dy = menu_companion_soft_limit((my - (screen_h * focus_y)) / (screen_h * 0.78))
        return (dx * range_x, dy * range_y)

    def menu_companion_current_pupil_offset(character_id):
        state = menu_companion_state(character_id)
        offset_x, offset_y = state.get("pupil_offset", (0.0, 0.0))
        scale = min(
            float(renpy.config.screen_width) / 1920.0,
            float(renpy.config.screen_height) / 1080.0,
        )
        return int(round(offset_x * scale)), int(round(offset_y * scale))

    def menu_companion_dialogue_pool(character_id):
        cfg = menu_companion_character_defs[character_id]
        dialogues = cfg.get("dialogues", {})
        pool = list(dialogues.get("default", []))
        pool.extend(dialogues.get(menu_companion_time_bucket(), []))
        affection = store.menu_companion_affection.get(character_id, 0)
        if affection >= 50:
            pool.extend(dialogues.get("high_affection", []))
        return pool or [menu_companion_line(u"...")]

    def menu_companion_first_prompt_enabled(character_id="hero"):
        return (character_id == "hero") and (not bool(getattr(store.persistent, "menu_companion_first_save_done", False)))

    def menu_companion_prepare(character_id="hero"):
        state = menu_companion_state(character_id)
        cfg = menu_companion_character_defs[character_id]
        now = time.time()
        state["last_interaction"] = now
        state["bubble_text"] = None
        state["bubble_until"] = 0.0
        state["last_mouse"] = None
        state["head_hovered"] = False
        state["first_prompt_visible"] = False
        state["first_prompt_hold_until"] = 0.0
        state["pupil_offset"] = (0.0, 0.0)
        state["is_blinking"] = False
        state["blink_until"] = 0.0
        blink_range = cfg.get("blink_interval_range", (2.8, 5.4))
        state["next_blink_at"] = now + random.uniform(blink_range[0], blink_range[1])
        renpy.restart_interaction()

    def menu_companion_cleanup(character_id="hero"):
        state = menu_companion_state(character_id)
        state["bubble_text"] = None
        state["bubble_until"] = 0.0
        state["last_mouse"] = None
        state["head_hovered"] = False
        state["first_prompt_visible"] = False
        state["first_prompt_hold_until"] = 0.0
        state["pupil_offset"] = (0.0, 0.0)
        state["is_blinking"] = False
        state["blink_until"] = 0.0

    def menu_companion_register_interaction(character_id="hero", restart=True):
        state = menu_companion_state(character_id)
        state["last_interaction"] = time.time()
        if restart:
            renpy.restart_interaction()

    def menu_companion_pick_line(character_id):
        state = menu_companion_state(character_id)
        pool = menu_companion_dialogue_pool(character_id)
        candidates = [line for line in pool if line["text"] != state["last_line"]]
        if candidates:
            return random.choice(candidates)
        return random.choice(pool)

    def menu_companion_play_voice(line_data):
        voice = line_data.get("voice")
        if not voice:
            return
        if renpy.loadable(voice):
            renpy.sound.play(voice)
            return
        if renpy.loadable("audio/" + voice):
            renpy.sound.play("audio/" + voice)

    def menu_companion_click(character_id="hero"):
        state = menu_companion_state(character_id)
        now = time.time()

        menu_companion_register_interaction(character_id, restart=False)

        if now - state["last_click_at"] < MENU_COMPANION_CLICK_COOLDOWN:
            renpy.restart_interaction()
            return

        state["last_click_at"] = now
        chosen = menu_companion_pick_line(character_id)
        state["last_line"] = chosen["text"]
        state["bubble_text"] = chosen["text"]
        state["bubble_until"] = now + MENU_COMPANION_BUBBLE_SECONDS
        menu_companion_play_voice(chosen)
        renpy.restart_interaction()

    def menu_companion_head_hover_start(character_id="hero"):
        if not menu_companion_first_prompt_enabled(character_id):
            return

        state = menu_companion_state(character_id)
        now = time.time()
        state["head_hovered"] = True

        if not state.get("first_prompt_visible", False):
            state["first_prompt_visible"] = True
            state["first_prompt_hold_until"] = now + 3.0

        renpy.restart_interaction()

    def menu_companion_head_hover_end(character_id="hero"):
        state = menu_companion_state(character_id)
        state["head_hovered"] = False

        if state.get("first_prompt_visible") and time.time() >= state.get("first_prompt_hold_until", 0.0):
            state["first_prompt_visible"] = False

        renpy.restart_interaction()

    def menu_companion_mark_first_memory_started(character_id="hero"):
        store.persistent.menu_companion_first_memory_started = True
        renpy.save_persistent()

        state = menu_companion_state(character_id)
        state["head_hovered"] = False
        state["first_prompt_visible"] = False
        state["first_prompt_hold_until"] = 0.0

    def menu_companion_mark_first_save_done(character_id="hero"):
        store.persistent.menu_companion_first_save_done = True
        renpy.save_persistent()

        state = menu_companion_state(character_id)
        state["head_hovered"] = False
        state["first_prompt_visible"] = False
        state["first_prompt_hold_until"] = 0.0

    def menu_companion_tick(character_id="hero"):
        state = menu_companion_state(character_id)
        cfg = menu_companion_character_defs[character_id]
        now = time.time()
        changed = False

        if state["bubble_text"] and now >= state["bubble_until"]:
            state["bubble_text"] = None
            changed = True

        if menu_companion_first_prompt_enabled(character_id) and state.get("first_prompt_visible"):
            if (not state.get("head_hovered")) and now >= state.get("first_prompt_hold_until", 0.0):
                state["first_prompt_visible"] = False
                changed = True

        if cfg.get("closed_image"):
            if state.get("is_blinking"):
                if now >= state.get("blink_until", 0.0):
                    state["is_blinking"] = False
                    blink_range = cfg.get("blink_interval_range", (2.8, 5.4))
                    state["next_blink_at"] = now + random.uniform(blink_range[0], blink_range[1])
                    changed = True
            elif now >= state.get("next_blink_at", 0.0):
                state["is_blinking"] = True
                state["blink_until"] = now + cfg.get("blink_hold_seconds", 0.10)
                changed = True

        if cfg.get("pupil_image"):
            mouse_pos = renpy.get_mouse_pos()
            if mouse_pos != state.get("last_mouse"):
                state["last_mouse"] = mouse_pos
                changed = True

            target_x, target_y = menu_companion_target_pupil_offset(character_id)
            current_x, current_y = state.get("pupil_offset", (0.0, 0.0))
            smoothing = cfg.get("pupil_follow_smoothing", 0.35)
            next_x = current_x + ((target_x - current_x) * smoothing)
            next_y = current_y + ((target_y - current_y) * smoothing)

            if abs(next_x - current_x) > 0.02 or abs(next_y - current_y) > 0.02:
                state["pupil_offset"] = (next_x, next_y)
                changed = True

        if changed:
            renpy.restart_interaction()

    menu_main_button_head_defs = {
        "start": {
            "image": "images/menu_companion/menu_heads/head_start.png",
        },
        "continue": {
            "image": "images/menu_companion/menu_heads/head_continue.png",
        },
        "gallery": {
            "image": "images/menu_companion/menu_heads/head_gallery.png",
        },
        "preferences": {
            "image": "images/menu_companion/menu_heads/head_settings.png",
        },
        "about": {
            "image": "images/menu_companion/menu_heads/head_about.png",
        },
        "quit": {
            "image": "images/menu_companion/menu_heads/head_quit.png",
        },
    }

    menu_nav_button_head_defs = {
        "start": menu_main_button_head_defs["start"],
        "load": menu_main_button_head_defs["continue"],
        "save": menu_main_button_head_defs["continue"],
        "preferences": menu_main_button_head_defs["preferences"],
        "gallery": menu_main_button_head_defs["gallery"],
        "history": menu_main_button_head_defs["continue"],
        "about": menu_main_button_head_defs["about"],
        "help": menu_main_button_head_defs["about"],
        "main_menu": menu_main_button_head_defs["start"],
        "title": menu_main_button_head_defs["continue"],
        "replay_end": menu_main_button_head_defs["quit"],
        "quit": menu_main_button_head_defs["quit"],
    }

    def menu_main_button_hover_start(button_id):
        if button_id not in menu_main_button_head_defs and button_id not in menu_nav_button_head_defs:
            return

        if store.main_menu_hover_avatar_leaving == button_id:
            store.main_menu_hover_avatar_leaving = None

        store.main_menu_hover_avatar = button_id
        renpy.restart_interaction()

    def menu_main_button_hover_end(button_id):
        if store.main_menu_hover_avatar != button_id:
            return

        store.main_menu_hover_avatar_leaving = button_id
        store.main_menu_hover_avatar = None
        renpy.restart_interaction()

    def menu_main_button_clear_leaving(button_id):
        if store.main_menu_hover_avatar_leaving != button_id:
            return

        store.main_menu_hover_avatar_leaving = None
        renpy.restart_interaction()


default menu_companion_runtime = {}
default menu_companion_affection = { "hero": 0 }
default main_menu_hover_avatar = None
default main_menu_hover_avatar_leaving = None

image menu_companion_hero_base = "images/menu_companion/main_menu_girl_base.png"
image menu_companion_hero_lashes = "images/menu_companion/main_menu_girl_lashes.png"
image menu_companion_hero_closed = "images/menu_companion/main_menu_girl_closed.png"
image menu_companion_hero_pupils = "images/menu_companion/main_menu_girl_pupils.png"
image menu_companion_hero_hitmask = "images/menu_companion/main_menu_girl_hitmask.png"
image menu_companion_first_start_prompt = "images/menu_companion/first_start_prompt.png"

transform menu_companion_bubble_in:
    alpha 0.0
    zoom 0.96
    yoffset 10
    ease 0.22 alpha 1.0 zoom 1.0 yoffset 0

transform menu_button_head_popup:
    alpha 0.0
    zoom 0.85
    yoffset 34
    ease 0.18 alpha 1.0 zoom 1.0 yoffset 2
    ease 0.08 zoom 1.03 yoffset -2
    ease 0.06 zoom 1.0 yoffset 0

transform menu_button_head_popdown:
    alpha 1.0
    zoom 1.0
    yoffset 0
    ease 0.18 alpha 0.0 zoom 0.9 yoffset 16

transform menu_button_head_popup_right:
    alpha 0.0
    zoom 0.85
    xoffset -12
    ease 0.18 alpha 1.0 zoom 1.0 xoffset 1
    ease 0.08 zoom 1.03 xoffset -1
    ease 0.06 zoom 1.0 xoffset 0

transform menu_button_head_popdown_right:
    alpha 1.0
    zoom 1.0
    xoffset 0
    ease 0.18 alpha 0.0 zoom 0.9 xoffset -12


screen main_menu_companion_host(character_id="hero"):
    zorder 18

    on "show" action Function(menu_companion_prepare, character_id)
    on "hide" action Function(menu_companion_cleanup, character_id)

    timer MENU_COMPANION_TICK_SECONDS repeat True action Function(menu_companion_tick, character_id)

    use main_menu_companion_character(character_id)

    $ state = menu_companion_state(character_id)
    if menu_companion_first_prompt_enabled(character_id) and state.get("first_prompt_visible"):
        use main_menu_companion_first_prompt(character_id)

    if state["bubble_text"]:
        use main_menu_companion_bubble(character_id, state["bubble_text"])


screen main_menu_companion_character(character_id="hero"):
    $ cfg = menu_companion_character_defs[character_id]
    $ display_w, display_h = menu_companion_display_size(character_id)
    $ render_zoom = menu_companion_render_zoom(character_id)
    $ body_image = cfg["main_image"]
    $ lashes_image = cfg.get("lashes_image")
    $ closed_image = cfg.get("closed_image")
    $ pupil_image = cfg.get("pupil_image")
    $ pupil_x, pupil_y = menu_companion_current_pupil_offset(character_id)
    $ state = menu_companion_state(character_id)

    fixed:
        xpos premium_sx(cfg["xpos"])
        ypos premium_sy(cfg["ypos"])
        xsize display_w
        ysize display_h

        button:
            style "menu_companion_hotspot"
            focus_mask "menu_companion_hero_hitmask"
            xsize display_w
            ysize display_h
            action Function(menu_companion_click, character_id)
            hovered Function(menu_companion_head_hover_start, character_id)
            unhovered Function(menu_companion_head_hover_end, character_id)
            fixed:
                xfill True
                yfill True

                add Transform(body_image, zoom=render_zoom) xpos 0 ypos 0

                if state.get("is_blinking") and closed_image:
                    add Transform(closed_image, zoom=render_zoom) xpos 0 ypos 0

                elif pupil_image:
                    add Transform(pupil_image, zoom=render_zoom) xpos pupil_x ypos pupil_y

                if (not state.get("is_blinking")) and lashes_image:
                    add Transform(lashes_image, zoom=render_zoom) xpos 0 ypos 0


screen main_menu_companion_bubble(character_id, bubble_text):
    $ cfg = menu_companion_character_defs[character_id]

    text bubble_text:
        style "menu_companion_bubble_text"
        xpos premium_sx(cfg.get("bubble_xpos", 1670))
        ypos premium_sy(cfg.get("bubble_ypos", 165))
        xanchor 0.5
        yanchor 1.0
        at menu_companion_bubble_in


screen main_menu_companion_first_prompt(character_id="hero"):
    $ cfg = menu_companion_character_defs[character_id]
    $ render_zoom = menu_companion_render_zoom(character_id)
    $ prompt_offset = cfg.get("first_prompt_offset", (560, 16))
    $ prompt_size = cfg.get("first_prompt_size", (520, 336))
    $ click_rect = cfg.get("first_prompt_click_rect", (96, 96, 286, 118))
    $ prompt_x = premium_sx(cfg["xpos"]) + int(round(prompt_offset[0] * render_zoom))
    $ prompt_y = premium_sy(cfg["ypos"]) + int(round(prompt_offset[1] * render_zoom))
    $ prompt_w = int(round(prompt_size[0] * render_zoom))
    $ prompt_h = int(round(prompt_size[1] * render_zoom))

    fixed:
        xpos prompt_x
        ypos prompt_y
        xsize prompt_w
        ysize prompt_h

        add Transform("menu_companion_first_start_prompt", fit="contain", xsize=prompt_w, ysize=prompt_h)

        button:
            style "menu_companion_first_prompt_hitbox"
            xpos int(round(click_rect[0] * render_zoom))
            ypos int(round(click_rect[1] * render_zoom))
            xsize int(round(click_rect[2] * render_zoom))
            ysize int(round(click_rect[3] * render_zoom))
            action Start()


screen main_menu_hover_textbutton(caption, button_action, button_id):
    fixed:
        xsize premium_sx(456)
        ysize premium_sy(88)

        if main_menu_hover_avatar == button_id and button_id in menu_main_button_head_defs:
            $ head = menu_main_button_head_defs[button_id]

            add head["image"]:
                xpos premium_sx(228)
                ypos premium_sy(18)
                xanchor 0.5
                yanchor 1.0
                at menu_button_head_popup

        elif main_menu_hover_avatar_leaving == button_id and button_id in menu_main_button_head_defs:
            $ head = menu_main_button_head_defs[button_id]

            add head["image"]:
                xpos premium_sx(228)
                ypos premium_sy(18)
                xanchor 0.5
                yanchor 1.0
                at menu_button_head_popdown

            timer 0.2 action Function(menu_main_button_clear_leaving, button_id)

        textbutton caption:
            action button_action
            style "premium_main_button"
            at menu_button_focus
            hovered Function(menu_main_button_hover_start, button_id)
            unhovered Function(menu_main_button_hover_end, button_id)


screen premium_nav_hover_textbutton(caption, button_action, button_id, sensitive=True):
    fixed:
        xsize premium_sx(470)
        ysize premium_sy(56)

        if main_menu_hover_avatar == button_id and button_id in menu_nav_button_head_defs:
            $ head = menu_nav_button_head_defs[button_id]

            add head["image"]:
                xpos premium_sx(156)
                ypos premium_sy(12)
                xanchor 0.5
                yanchor 1.0
                at menu_button_head_popup

        elif main_menu_hover_avatar_leaving == button_id and button_id in menu_nav_button_head_defs:
            $ head = menu_nav_button_head_defs[button_id]

            add head["image"]:
                xpos premium_sx(156)
                ypos premium_sy(12)
                xanchor 0.5
                yanchor 1.0
                at menu_button_head_popdown

            timer 0.2 action Function(menu_main_button_clear_leaving, button_id)

        textbutton caption:
            action button_action
            style "premium_nav_button"
            xsize premium_sx(310)
            sensitive sensitive
            hovered Function(menu_main_button_hover_start, button_id)
            unhovered Function(menu_main_button_hover_end, button_id)


style menu_companion_hotspot is button:
    background None
    hover_background None
    padding (0, 0, 0, 0)
    activate_sound None

style menu_companion_first_prompt_hitbox is button:
    background None
    hover_background None
    padding (0, 0, 0, 0)
    activate_sound None

style menu_companion_bubble_outer is default:
    background None
    padding (0, 0, 0, 0)

style menu_companion_bubble_frame is default:
    xsize premium_sx(760)
    padding (0, 0, 0, 0)
    background None

style menu_companion_bubble_text is default:
    font premium_name_font
    size premium_ss(26)
    color "#000000"
    xmaximum premium_sx(320)
    text_align 0.0
    line_spacing premium_sy(7)
    outlines []
