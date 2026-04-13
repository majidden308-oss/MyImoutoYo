init -10 python:
    import os
    import renpy.store as store
    import renpy.ui as ui
    import random
    import time

    PREMIUM_BASE_WIDTH = 1920.0
    PREMIUM_BASE_HEIGHT = 1080.0

    def premium_sx(value):
        return int(round(float(value) * renpy.config.screen_width / PREMIUM_BASE_WIDTH))

    def premium_sy(value):
        return int(round(float(value) * renpy.config.screen_height / PREMIUM_BASE_HEIGHT))

    def premium_ss(value):
        scale = min(
            renpy.config.screen_width / PREMIUM_BASE_WIDTH,
            renpy.config.screen_height / PREMIUM_BASE_HEIGHT,
        )
        return int(round(float(value) * scale))

    if "premium_opening_op_seen" not in renpy.session:
        renpy.session["premium_opening_op_seen"] = False

    if not hasattr(store, "_premium_launch_started_at"):
        store._premium_launch_started_at = None

    if not hasattr(store, "_premium_playtime_last_sync_at"):
        store._premium_playtime_last_sync_at = None

    if not hasattr(store, "_premium_playtime_last_saved_at"):
        store._premium_playtime_last_saved_at = None

    if not hasattr(store, "_premium_notebook_input_lock_until"):
        store._premium_notebook_input_lock_until = 0.0

    if not hasattr(store, "_premium_menu_bg_offset_x"):
        store._premium_menu_bg_offset_x = 0.0

    if not hasattr(store, "_premium_menu_bg_offset_y"):
        store._premium_menu_bg_offset_y = 0.0

    if not hasattr(store, "_premium_story_history_snap_to_end"):
        store._premium_story_history_snap_to_end = False

    if not hasattr(store.persistent, "premium_total_playtime_seconds"):
        store.persistent.premium_total_playtime_seconds = 0.0

    if not hasattr(store.persistent, "premium_gallery_seen"):
        store.persistent.premium_gallery_seen = []

    def premium_total_playtime_value():
        raw = getattr(store.persistent, "premium_total_playtime_seconds", 0.0)
        if raw is None:
            return 0.0
        try:
            return float(raw)
        except (TypeError, ValueError):
            return 0.0

    def premium_ensure_session_started():
        if getattr(store, "_premium_launch_started_at", None) is None:
            now = time.time()
            store._premium_launch_started_at = now
            store._premium_playtime_last_sync_at = now
            store._premium_playtime_last_saved_at = now

    def premium_playtime_tick():
        premium_ensure_session_started()
        now = time.time()
        last_sync = getattr(store, "_premium_playtime_last_sync_at", None)

        if last_sync is None:
            store._premium_playtime_last_sync_at = now
            return

        delta = max(0.0, now - last_sync)
        if delta <= 0.0:
            return

        store.persistent.premium_total_playtime_seconds = premium_total_playtime_value() + delta
        store._premium_playtime_last_sync_at = now

        last_saved = getattr(store, "_premium_playtime_last_saved_at", None)
        if last_saved is None or (now - last_saved) >= 15.0:
            renpy.save_persistent()
            store._premium_playtime_last_saved_at = now

    def premium_flush_playtime():
        premium_playtime_tick()
        renpy.save_persistent()
        store._premium_playtime_last_saved_at = time.time()

    def premium_status_now_text():
        premium_ensure_session_started()
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def premium_status_playtime_text():
        premium_ensure_session_started()
        total_seconds = int(premium_total_playtime_value())
        elapsed = max(0, total_seconds)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)

    def premium_status_window_scale():
        return 0.65

    def premium_status_window_width():
        return int(round(premium_sx(400) * premium_status_window_scale()))

    def premium_status_window_height():
        return int(round(premium_sy(491) * premium_status_window_scale()))

    def premium_preferences():
        return getattr(store, "_preferences", None)

    def premium_pref_skip_unseen_enabled():
        prefs = premium_preferences()
        return bool(getattr(prefs, "skip_unseen", False))

    def premium_pref_after_choices_enabled():
        prefs = premium_preferences()
        return bool(getattr(prefs, "skip_after_choices", False))

    def premium_pref_transitions_enabled():
        prefs = premium_preferences()
        return bool(getattr(prefs, "transitions", 2))

    def premium_pref_all_mute_enabled():
        prefs = premium_preferences()
        if prefs is None:
            return False
        return bool(prefs.get_mute("main"))

    def premium_pref_check_mark(enabled):
        return u"✓" if enabled else u"✕"

    premium_window_resolution_presets = [
        (1280, 720, u"1280 x 720"),
        (1600, 900, u"1600 x 900"),
        (1920, 1080, u"1920 x 1080"),
        (2560, 1440, u"2560 x 1440"),
    ]

    def premium_current_window_resolution():
        try:
            return renpy.get_physical_size()
        except Exception:
            return (renpy.config.screen_width, renpy.config.screen_height)

    def premium_window_resolution_matches(width, height):
        current_width, current_height = premium_current_window_resolution()
        return int(current_width) == int(width) and int(current_height) == int(height)

    def premium_window_resolution_summary():
        width, height = premium_current_window_resolution()
        return u"当前窗口：{} x {}".format(int(width), int(height))

    def premium_set_window_resolution(width, height):
        renpy.set_physical_size((int(width), int(height)))
        renpy.restart_interaction()

    def premium_ease_out_cubic(t):
        return 1.0 - pow(1.0 - t, 3.0)

    def premium_ease_in_out_cubic(t):
        if t < 0.5:
            return 4.0 * t * t * t
        return 1.0 - pow(-2.0 * t + 2.0, 3.0) / 2.0

    def premium_notebook_width():
        return premium_sx(490)

    def premium_notebook_height():
        return premium_sy(736)

    def premium_notebook_base_width():
        return premium_sx(575)

    def premium_notebook_base_height():
        return premium_sy(861)

    def premium_notebook_content_scale():
        return float(premium_notebook_width()) / float(premium_notebook_base_width())

    def premium_notebook_x():
        return int((renpy.config.screen_width - premium_notebook_width()) / 2)

    def premium_notebook_open_y():
        return premium_sy(12)

    def premium_notebook_closed_y():
        return premium_sy(74) - premium_notebook_height()

    def premium_notebook_reset_state():
        store.main_menu_notebook_hovered = False
        store.main_menu_notebook_open = False
        store.main_menu_notebook_y = float(premium_notebook_closed_y())
        renpy.restart_interaction()

    def premium_notebook_set_hovered(value):
        new_value = bool(value)
        old_value = bool(getattr(store, "main_menu_notebook_hovered", False))
        store.main_menu_notebook_hovered = new_value

        if new_value and not old_value:
            if renpy.loadable("audio/notebook_hover_paper_pcm.wav"):
                renpy.music.play("audio/notebook_hover_paper_pcm.wav", channel="sound", loop=False)

    def premium_notebook_is_animating():
        current = float(getattr(store, "main_menu_notebook_y", premium_notebook_closed_y()))
        target = float(premium_notebook_open_y() if getattr(store, "main_menu_notebook_hovered", False) else premium_notebook_closed_y())
        return abs(target - current) >= 0.5

    def premium_notebook_tick():
        current = float(getattr(store, "main_menu_notebook_y", premium_notebook_closed_y()))
        target = float(premium_notebook_open_y() if getattr(store, "main_menu_notebook_hovered", False) else premium_notebook_closed_y())
        delta = target - current

        if abs(delta) < 0.5:
            next_y = target
        else:
            next_y = current + (delta * 0.36)

        store.main_menu_notebook_y = next_y
        store.main_menu_notebook_open = abs(next_y - premium_notebook_open_y()) < 6.0

    def premium_notebook_input_locked():
        return time.time() < getattr(store, "_premium_notebook_input_lock_until", 0.0)

    def premium_notebook_begin_load(slot):
        store.main_menu_notebook_loading_slot = slot
        renpy.restart_interaction()

    def premium_prepare_notebook_load_transition():
        renpy.config.after_load_transition = premium_load_in_transition

    def premium_main_menu_background_target_offset():
        mouse_pos = renpy.get_mouse_pos()
        if not mouse_pos:
            return (0, 0)

        mx, my = mouse_pos
        sw = max(float(config.screen_width), 1.0)
        sh = max(float(config.screen_height), 1.0)
        dx = ((mx / sw) - 0.5) * 2.0
        dy = ((my / sh) - 0.5) * 2.0
        return (
            int(round(-dx * premium_sx(2))),
            int(round(-dy * premium_sy(1))),
        )

    def premium_reset_main_menu_background_offset():
        store._premium_menu_bg_offset_x = 0.0
        store._premium_menu_bg_offset_y = 0.0

    def premium_tick_main_menu_background_offset():
        target_x, target_y = premium_main_menu_background_target_offset()
        current_x = float(getattr(store, "_premium_menu_bg_offset_x", 0.0))
        current_y = float(getattr(store, "_premium_menu_bg_offset_y", 0.0))

        # Ease toward the mouse target instead of snapping directly to it.
        store._premium_menu_bg_offset_x = current_x + ((target_x - current_x) * 0.14)
        store._premium_menu_bg_offset_y = current_y + ((target_y - current_y) * 0.14)
        renpy.restart_interaction()

    def premium_main_menu_background_offset():
        return (
            int(round(float(getattr(store, "_premium_menu_bg_offset_x", 0.0)))),
            int(round(float(getattr(store, "_premium_menu_bg_offset_y", 0.0)))),
        )

    def premium_story_history_open():
        store.premium_dialogue_history_visible = True
        store._premium_story_history_snap_to_end = True
        renpy.restart_interaction()

    def premium_story_history_close():
        store.premium_dialogue_history_visible = False
        renpy.restart_interaction()

    def premium_story_history_scroll_amount(adjustment):
        page = float(getattr(adjustment, "page", 0.0) or 0.0)
        step = float(getattr(adjustment, "step", 0.0) or 0.0)
        return max(step, page * 0.16, float(premium_sy(84)))

    def premium_story_history_is_at_bottom(adjustment):
        if adjustment is None:
            return True

        current = float(getattr(adjustment, "value", 0.0) or 0.0)
        maximum = max(0.0, float(getattr(adjustment, "range", 0.0) or 0.0))
        return current >= (maximum - 2.0)

    def premium_story_history_scroll(adjustment, direction):
        if adjustment is None:
            return

        amount = premium_story_history_scroll_amount(adjustment)
        current = float(getattr(adjustment, "value", 0.0) or 0.0)
        maximum = max(0.0, float(getattr(adjustment, "range", 0.0) or 0.0))
        target = max(0.0, min(maximum, current + (amount * float(direction))))

        try:
            adjustment.change(target)
        except Exception:
            adjustment.value = target

        renpy.restart_interaction()

    def premium_story_history_scroll_down_or_close(adjustment):
        if premium_story_history_is_at_bottom(adjustment):
            premium_story_history_close()
            return

        premium_story_history_scroll(adjustment, 1.0)

    def premium_story_history_viewport_height():
        return max(1.0, float(renpy.config.screen_height - premium_sy(30)))

    def premium_story_history_text_width():
        return max(120.0, float(
            renpy.config.screen_width
            - premium_sx(36)
            - premium_sx(28)
            - premium_sx(20)
            - premium_sx(20)
        ))

    def premium_story_history_estimated_lines(text, font_size):
        normalized = (text or u"").replace("{nw}", u"").replace("{fast}", u"")
        normalized = normalized.replace("{p}", "\n").replace("{w}", "")
        segments = normalized.split("\n")
        approx_chars_per_line = max(8, int(premium_story_history_text_width() / max(1.0, float(font_size) * 0.92)))
        line_total = 0

        for segment in segments:
            segment_length = max(1, len(segment))
            line_total += max(1, int((segment_length + approx_chars_per_line - 1) / approx_chars_per_line))

        return max(1, line_total)

    def premium_story_history_entry_estimated_height(who, what):
        vertical_padding = premium_sy(16) * 2
        spacing = premium_sy(8)
        body_font = premium_ss(29)
        body_line_height = body_font + premium_sy(10) + premium_sy(4)
        total_height = vertical_padding
        body_lines = premium_story_history_estimated_lines(what, body_font)
        total_height += body_lines * body_line_height

        if who:
            name_font = premium_ss(34)
            total_height += name_font + spacing

        return float(total_height)

    def premium_story_history_entry_alpha(entry_top, entry_height, adjustment):
        if adjustment is None:
            return 1.0

        viewport_height = premium_story_history_viewport_height()
        visible_top = float(getattr(adjustment, "value", 0.0) or 0.0)
        visible_bottom = visible_top + viewport_height
        fade_height = min(float(premium_sy(220)), viewport_height * 0.42)
        fade_start = visible_bottom - fade_height
        entry_bottom = entry_top + entry_height

        if entry_bottom <= fade_start:
            return 1.0

        if entry_top >= visible_bottom:
            return 0.0

        focus_y = min(entry_bottom, visible_bottom)
        ratio = (focus_y - fade_start) / max(1.0, fade_height)
        ratio = max(0.0, min(1.0, ratio))
        return max(0.0, 1.0 - pow(ratio, 1.45))

    def premium_story_history_snap_to_end(adjustment):
        if (adjustment is None) or (not getattr(store, "_premium_story_history_snap_to_end", False)):
            return

        maximum = max(0.0, float(getattr(adjustment, "range", 0.0) or 0.0))

        try:
            adjustment.change(maximum)
        except Exception:
            adjustment.value = maximum

        store._premium_story_history_snap_to_end = False
        renpy.restart_interaction()

    def premium_main_menu_background_displayable():
        return Solid("#FFFFFF")

    PREMIUM_MENU_PLAYER_FALLBACK_COVER = "images/song_covers/love_her.png"

    premium_menu_player_track_meta = {
        "audio/bgm_dream_healing.oga": {
            "title": "Dream Healing",
        },
        "audio/bgm_home_wholesome.ogg": {
            "title": "Home Wholesome",
        },
        "audio/bgm_love_her.ogg": {
            "title": "Love Her",
            "artist": "Loyalty Freak Music",
            "cover": "images/song_covers/love_her.png",
            "duration": 145.0,
            "source": "https://commons.wikimedia.org/wiki/File:Loyalty_Freak_Music_-_04_-_Love_Her.ogg",
        },
        "audio/bgm_morning_midsommar.oga": {
            "title": "Morning Midsommar",
        },
        "audio/bgm_morning_gymnopedie_no1.mp3": {
            "title": "Morning Gymnopedie No. 1",
        },
        "audio/bgm_old_saga.ogg": {
            "title": "Old Saga",
            "artist": "Loyalty Freak Music",
            "cover": "images/song_covers/old_saga.png",
            "duration": 150.0,
            "source": "https://commons.wikimedia.org/wiki/File:Loyalty_Freak_Music_-_02_-_Old_Saga.ogg",
        },
    }

    premium_menu_player_track_order = [
        "audio/bgm_old_saga.ogg",
        "audio/bgm_love_her.ogg",
        "audio/bgm_dream_healing.oga",
        "audio/bgm_morning_midsommar.oga",
        "audio/bgm_morning_gymnopedie_no1.mp3",
        "audio/bgm_home_wholesome.ogg",
    ]

    def premium_menu_player_default_title(audio_path):
        filename = os.path.basename(audio_path)
        stem = os.path.splitext(filename)[0]
        if stem.startswith("bgm_"):
            stem = stem[4:]
        return " ".join(part.capitalize() for part in stem.split("_") if part)

    def premium_menu_player_resolve_cover(track):
        cover = track.get("cover") or PREMIUM_MENU_PLAYER_FALLBACK_COVER
        if cover and renpy.loadable(cover):
            return cover
        return PREMIUM_MENU_PLAYER_FALLBACK_COVER

    def premium_menu_player_build_tracks():
        order_index = dict((path, idx) for idx, path in enumerate(premium_menu_player_track_order))
        audio_paths = []

        for path in renpy.list_files():
            normalized = path.replace("\\", "/")
            lowered = normalized.lower()
            if (not lowered.startswith("audio/bgm_")) or (not lowered.endswith((".ogg", ".oga", ".mp3", ".wav"))):
                continue
            audio_paths.append(normalized)

        def sort_key(audio_path):
            meta = premium_menu_player_track_meta.get(audio_path, {})
            return (
                0 if audio_path in order_index else 1,
                order_index.get(audio_path, 999),
                (meta.get("title") or premium_menu_player_default_title(audio_path)).lower(),
                audio_path.lower(),
            )

        tracks = []
        for audio_path in sorted(set(audio_paths), key=sort_key):
            meta = premium_menu_player_track_meta.get(audio_path, {})
            track = {
                "title": meta.get("title") or premium_menu_player_default_title(audio_path),
                "artist": meta.get("artist") or "Game OST",
                "audio": audio_path,
                "cover": meta.get("cover") or PREMIUM_MENU_PLAYER_FALLBACK_COVER,
                "duration": float(meta.get("duration", 0.0) or 0.0),
                "source": meta.get("source"),
            }
            track["cover"] = premium_menu_player_resolve_cover(track)
            tracks.append(track)

        return tracks

    premium_menu_player_tracks = premium_menu_player_build_tracks()

    def premium_menu_player_channel():
        return "main_menu_player"

    def premium_menu_player_is_actively_playing():
        return bool(renpy.music.get_playing(premium_menu_player_channel()))

    def premium_menu_player_track_count():
        return len(premium_menu_player_tracks)

    def premium_menu_player_track():
        count = premium_menu_player_track_count()
        if count <= 0:
            return None
        raw_index = getattr(store, "main_menu_player_index", 0)
        try:
            index = int(raw_index) % count
        except (TypeError, ValueError):
            index = 0
        store.main_menu_player_index = index
        return premium_menu_player_tracks[index]

    def premium_menu_player_format_time(seconds):
        try:
            total = max(0, int(seconds))
        except (TypeError, ValueError):
            total = 0
        return "{:02d}:{:02d}".format(total // 60, total % 60)

    def premium_menu_player_duration():
        track = premium_menu_player_track()
        if not track:
            return 0.0
        return float(track.get("duration", 0.0))

    def premium_menu_player_progress():
        if getattr(store, "main_menu_player_is_playing", True):
            pos = renpy.music.get_pos(channel=premium_menu_player_channel())
            if pos is not None:
                return max(0.0, float(pos))
        return max(0.0, float(getattr(store, "main_menu_player_paused_pos", 0.0) or 0.0))

    def premium_menu_player_progress_ratio():
        duration = premium_menu_player_duration()
        if duration <= 0.0:
            return 0.0
        return min(1.0, max(0.0, premium_menu_player_progress() / duration))

    def premium_menu_player_duration_text():
        duration = premium_menu_player_duration()
        if duration <= 0.0:
            return "--:--"
        return premium_menu_player_format_time(duration)

    def premium_menu_player_volume_value():
        raw = getattr(store, "main_menu_player_volume", 0.6)
        try:
            return min(1.0, max(0.0, float(raw)))
        except (TypeError, ValueError):
            return 0.6

    def premium_menu_player_apply_volume():
        renpy.music.set_volume(premium_menu_player_volume_value(), 0.0, premium_menu_player_channel())

    def premium_menu_player_play_current(from_pos=None, fadein=0.18):
        track = premium_menu_player_track()
        if not track:
            return
        audio_path = track["audio"]
        start_at = max(0.0, float(from_pos or 0.0))
        playable = audio_path
        if start_at > 0.05:
            playable = "<from {:.2f}>{}".format(start_at, audio_path)
        renpy.music.play(playable, channel=premium_menu_player_channel(), loop=False, fadein=max(0.0, float(fadein or 0.0)))
        premium_menu_player_apply_volume()
        store.main_menu_player_is_playing = True
        store.main_menu_player_paused_pos = start_at
        store.main_menu_player_last_pos = start_at

    def premium_menu_player_pause():
        current = renpy.music.get_pos(channel=premium_menu_player_channel())
        if current is not None:
            store.main_menu_player_paused_pos = max(0.0, float(current))
            store.main_menu_player_last_pos = store.main_menu_player_paused_pos
        renpy.music.stop(channel=premium_menu_player_channel(), fadeout=0.12)
        store.main_menu_player_is_playing = False
        renpy.restart_interaction()

    def premium_menu_player_toggle_pause():
        if getattr(store, "main_menu_player_is_playing", True) and renpy.music.get_playing(premium_menu_player_channel()):
            premium_menu_player_pause()
        else:
            premium_menu_player_play_current(getattr(store, "main_menu_player_paused_pos", 0.0))
            renpy.restart_interaction()

    def premium_menu_player_change(step):
        count = premium_menu_player_track_count()
        if count <= 0:
            return
        store.main_menu_player_index = (int(getattr(store, "main_menu_player_index", 0)) + int(step)) % count
        store.main_menu_player_paused_pos = 0.0
        store.main_menu_player_last_pos = 0.0
        premium_menu_player_play_current(0.0)
        renpy.restart_interaction()

    def premium_menu_player_next():
        premium_menu_player_change(1)

    def premium_menu_player_previous():
        premium_menu_player_change(-1)

    def premium_menu_player_toggle_panel():
        store.main_menu_player_open = not bool(getattr(store, "main_menu_player_open", False))
        if store.main_menu_player_open:
            store.main_menu_player_page = "now_playing"
            store.main_menu_player_previous_page = "now_playing"
        renpy.restart_interaction()

    def premium_menu_player_show_menu():
        store.main_menu_player_previous_page = getattr(store, "main_menu_player_page", "now_playing")
        store.main_menu_player_page = "track_list"
        renpy.restart_interaction()

    def premium_menu_player_back():
        current = getattr(store, "main_menu_player_page", "now_playing")
        if current != "now_playing":
            store.main_menu_player_page = getattr(store, "main_menu_player_previous_page", "now_playing")
            store.main_menu_player_previous_page = "now_playing"
        renpy.restart_interaction()

    def premium_menu_player_select_track(index):
        count = premium_menu_player_track_count()
        if count <= 0:
            return
        store.main_menu_player_index = int(index) % count
        store.main_menu_player_paused_pos = 0.0
        store.main_menu_player_last_pos = 0.0
        store.main_menu_player_page = "now_playing"
        store.main_menu_player_previous_page = "now_playing"
        premium_menu_player_play_current(0.0)
        renpy.restart_interaction()

    def premium_menu_player_adjust_volume(delta):
        current = premium_menu_player_volume_value()
        try:
            step = float(delta)
        except (TypeError, ValueError):
            step = 0.0
        store.main_menu_player_volume = min(1.0, max(0.0, current + step))
        premium_menu_player_apply_volume()

    def premium_menu_player_init():
        if premium_menu_player_track_count() <= 0:
            return
        if premium_should_play_opening_op():
            return
        if getattr(store, "main_menu_player_is_playing", True):
            if renpy.music.get_playing(premium_menu_player_channel()) is None:
                premium_menu_player_play_current(getattr(store, "main_menu_player_paused_pos", 0.0), fadein=4.0)
        else:
            renpy.restart_interaction()

    def premium_menu_player_cleanup():
        if getattr(store, "main_menu_player_is_playing", True):
            current = renpy.music.get_pos(channel=premium_menu_player_channel())
            if current is not None:
                store.main_menu_player_paused_pos = max(0.0, float(current))
                store.main_menu_player_last_pos = store.main_menu_player_paused_pos
        renpy.music.stop(channel=premium_menu_player_channel(), fadeout=0.12)

    def premium_menu_player_tick():
        if premium_menu_player_track_count() <= 0:
            return
        if not getattr(store, "main_menu_player_is_playing", True):
            return

        current = renpy.music.get_pos(channel=premium_menu_player_channel())
        if current is not None:
            current = max(0.0, float(current))
            store.main_menu_player_last_pos = current
            store.main_menu_player_paused_pos = current
            return

        if renpy.music.get_playing(premium_menu_player_channel()) is None:
            last_pos = float(getattr(store, "main_menu_player_last_pos", 0.0) or 0.0)
            paused_pos = float(getattr(store, "main_menu_player_paused_pos", 0.0) or 0.0)

            if last_pos <= 0.35 and paused_pos <= 0.35 and (not premium_should_play_opening_op()):
                premium_menu_player_play_current(paused_pos, fadein=4.0)
                return

        if (renpy.music.get_playing(premium_menu_player_channel()) is None) and (float(getattr(store, "main_menu_player_last_pos", 0.0) or 0.0) > 0.35):
            store.main_menu_player_paused_pos = 0.0
            store.main_menu_player_last_pos = 0.0
            premium_menu_player_change(1)

    def premium_should_play_opening_op():
        return False

    def premium_finish_opening_op():
        renpy.session["premium_opening_op_seen"] = True
        store.opening_op_phase = "done"
        store.opening_op_played = True
        premium_menu_player_init()
        renpy.restart_interaction()

    premium_gallery_items = [
        ("梦境序章", "bg dream"),
        ("梦中牵手", "bg dream3"),
        ("白光尽头", "bg dream6"),
        ("晨间卧室", "bg goodmorning"),
        ("清晨余韵", "bg goodmorning4"),
        ("房间演出", "bg room"),
        ("客厅全景", "bg livingroom"),
        ("沙发近景", "bg imouto_on_sofa"),
        ("背后视角", "bg imouto_back"),
        ("早餐特写", "breakfast"),
    ]

    def premium_gallery_seen_set():
        raw = getattr(store.persistent, "premium_gallery_seen", [])
        if isinstance(raw, set):
            return set(raw)
        if isinstance(raw, (list, tuple)):
            return set(raw)
        return set()

    def premium_gallery_unlock(scene_name):
        seen = premium_gallery_seen_set()
        if scene_name in seen:
            return
        seen.add(scene_name)
        store.persistent.premium_gallery_seen = sorted(seen)
        renpy.save_persistent()

    def premium_gallery_unlocked(scene_name):
        return scene_name in premium_gallery_seen_set()

    renpy.music.register_channel(
        "main_menu_op",
        mixer="music",
        loop=False,
        stop_on_mute=True,
        tight=False,
        buffer_queue=False,
        movie=True,
        framedrop=True,
    )

    renpy.music.register_channel(
        "main_menu_player",
        mixer="music",
        loop=False,
        stop_on_mute=True,
        tight=True,
    )

    def update_main_menu_op_state():
        playing = renpy.music.is_playing("main_menu_op") or (renpy.music.get_playing("main_menu_op") is not None)

        if store.opening_op_played:
            return

        if store.opening_op_phase == "idle":
            if playing:
                store.opening_op_phase = "playing"
                renpy.restart_interaction()
            return

        if store.opening_op_phase == "playing" and (not playing):
            store.opening_op_phase = "done"
            store.opening_op_played = True
            renpy.restart_interaction()


define premium_menu_fade = Dissolve(0.32)
define premium_soft_dissolve = Dissolve(0.4)
define premium_pixel_dissolve = Pixellate(0.28, 6)
define premium_flash_white = Fade(0.04, 0.0, 0.22, color="#fffdf8")
define premium_bloom_flash = Fade(0.06, 0.0, 0.28, color="#fff2df")
define premium_load_in_transition = Fade(0.0, 0.0, 0.42, color="#FFFFFF")
define premium_body_font = "fonts/NotoSerifCJKsc-Regular.otf"
define premium_ui_font = "fonts/NotoSansCJKsc-Regular.otf"
define premium_name_font = "fonts/LXGWWenKai-Regular.ttf"
define premium_symbol_font = "fonts/NotoSansSymbols2-Regular.ttf"
define premium_main_menu_op_cutoff = 2.92

define config.enter_transition = premium_menu_fade
define config.exit_transition = premium_menu_fade
define config.intra_transition = premium_menu_fade
define config.window_show_transition = Dissolve(0.22)
define config.window_hide_transition = Dissolve(0.18)

image main_menu_op_blank = Solid("#0000")

image main_menu_op_movie = Movie(
    channel="main_menu_op",
    play="images/op.webm",
    mask=None,
    loop=False,
    image="main_menu_op_blank",
)

default main_menu_status_window_visible = True
default main_menu_notebook_hovered = False
default main_menu_notebook_open = False
default main_menu_notebook_y = 0.0
default main_menu_notebook_loading_slot = None
default main_menu_player_open = False
default main_menu_player_index = 0
default main_menu_player_is_playing = True
default main_menu_player_paused_pos = 0.0
default main_menu_player_last_pos = 0.0
default main_menu_player_volume = 0.6
default main_menu_player_page = "now_playing"
default main_menu_player_previous_page = "now_playing"
default premium_dialogue_history_visible = False

transform ui_fade_in:
    alpha 0.0
    ease 0.32 alpha 1.0

transform ui_fade_out:
    alpha 1.0
    ease 0.24 alpha 0.0

transform menu_panel_in:
    alpha 0.0
    zoom 0.97
    yoffset 26
    ease 0.34 alpha 1.0 zoom 1.0 yoffset 0

transform slide_panel_left:
    alpha 0.0
    xoffset -60
    ease 0.32 alpha 1.0 xoffset 0

transform slide_panel_right:
    alpha 0.0
    xoffset 60
    ease 0.32 alpha 1.0 xoffset 0

transform scale_in_soft:
    alpha 0.0
    zoom 0.94
    ease 0.28 alpha 1.0 zoom 1.0

transform alpha_dissolve_soft:
    alpha 0.0
    ease 0.4 alpha 1.0

transform premium_story_history_fade:
    on show:
        alpha 0.0
        yoffset premium_sy(18)
        parallel:
            ease 0.24 alpha 1.0
        parallel:
            ease 0.24 yoffset 0
    on hide:
        alpha 1.0
        yoffset 0
        parallel:
            ease 0.18 alpha 0.0
        parallel:
            ease 0.18 yoffset premium_sy(12)

transform premium_story_history_backdrop_fade:
    on show:
        alpha 0.0
        ease 0.22 alpha 1.0
    on hide:
        alpha 1.0
        ease 0.16 alpha 0.0

transform blur_fade_soft:
    alpha 0.0
    zoom 1.03
    ease 0.35 alpha 1.0 zoom 1.0

transform main_menu_blur_in_left:
    alpha 0.0
    blur 18
    zoom 1.02
    xoffset -34
    ease 0.72 alpha 1.0 blur 0 zoom 1.0 xoffset 0

transform main_menu_blur_in_right:
    alpha 0.0
    blur 20
    zoom 1.02
    xoffset 34
    ease 0.82 alpha 1.0 blur 0 zoom 1.0 xoffset 0

transform main_menu_blur_in_soft:
    alpha 0.0
    blur 12
    zoom 1.01
    ease 0.64 alpha 1.0 blur 0 zoom 1.0

transform main_menu_dream_in:
    alpha 0.0
    blur 36
    zoom 1.05
    yoffset 28
    ease 2.35 alpha 1.0 blur 0 zoom 1.0 yoffset 0

transform main_menu_dream_companion_in:
    alpha 0.0
    blur 42
    zoom 1.08
    xoffset 58
    yoffset 26
    ease 2.65 alpha 1.0 blur 0 zoom 1.0 xoffset 0 yoffset 0

transform main_menu_dream_ui_in:
    alpha 0.0
    blur 24
    zoom 1.03
    yoffset 18
    ease 2.1 alpha 1.0 blur 0 zoom 1.0 yoffset 0

transform main_menu_white_haze_out:
    alpha 0.38
    ease 2.8 alpha 0.0

transform song_player_panel_show:
    alpha 0.0
    zoom 0.98
    yoffset -14
    ease 0.28 alpha 1.0 zoom 1.0 yoffset 0

transform breathe_glow:
    alpha 0.28
    block:
        ease 1.8 alpha 0.48
        ease 1.8 alpha 0.24
        repeat

transform logo_fade_in:
    alpha 0.0
    yoffset -18
    ease 0.5 alpha 1.0 yoffset 0

transform menu_bg_drift_far:
    subpixel True
    xoffset -24
    block:
        ease 9.0 xoffset 18
        ease 9.0 xoffset -24
        repeat

transform menu_bg_drift_near:
    subpixel True
    xoffset 20
    alpha 0.2
    zoom 1.03
    block:
        ease 7.0 xoffset -18
        ease 7.0 xoffset 20
        repeat

transform menu_button_breathe:
    block:
        ease 2.2 yoffset -1
        ease 2.2 yoffset 1
        repeat

transform menu_button_focus:
    on idle:
        ease 0.18 zoom 1.0
    on hover:
        ease 0.18 zoom 1.02
    on activate:
        ease 0.08 zoom 1.0

transform glass_button_hover:
    on idle:
        ease 0.2 zoom 1.0
    on hover:
        ease 0.2 zoom 1.03

transform slot_hover_focus:
    on idle:
        ease 0.2 zoom 1.0
    on hover:
        ease 0.2 zoom 1.02

transform thumb_hover_zoom:
    on idle:
        ease 0.2 zoom 1.0
    on hover:
        ease 0.2 zoom 1.06

transform character_enter_left:
    alpha 0.0
    xoffset -120
    yoffset 28
    ease 0.32 alpha 1.0 xoffset 0 yoffset 0
    ease 0.12 yoffset -10
    ease 0.12 yoffset 0

transform character_enter_right:
    alpha 0.0
    xoffset 120
    yoffset 28
    ease 0.32 alpha 1.0 xoffset 0 yoffset 0
    ease 0.12 yoffset -10
    ease 0.12 yoffset 0

transform character_exit_left:
    alpha 1.0
    xoffset 0
    ease 0.24 alpha 0.0 xoffset -120

transform character_exit_right:
    alpha 1.0
    xoffset 0
    ease 0.24 alpha 0.0 xoffset 120

transform petal_fall(xpos=0.1, delay=0.0, drift=90):
    xalign xpos
    yoffset -140
    rotate 0
    alpha 0.0
    pause delay
    block:
        linear 0.8 alpha 0.65
        parallel:
            ease 7.2 yoffset 1180
        parallel:
            ease 3.6 xoffset drift
            ease 3.6 xoffset (-drift)
        parallel:
            linear 7.2 rotate 220
        linear 0.4 alpha 0.0
        yoffset -140
        repeat

transform light_particle(xpos=0.5, ypos=0.5, delay=0.0, rise=40):
    xalign xpos
    yalign ypos
    alpha 0.0
    pause delay
    block:
        ease 1.6 alpha 0.35 yoffset (-rise)
        ease 1.8 alpha 0.12 yoffset 0
        repeat

transform bokeh_glimmer(xpos=0.5, ypos=0.5, delay=0.0):
    xalign xpos
    yalign ypos
    alpha 0.0
    pause delay
    block:
        ease 1.3 alpha 0.16 zoom 1.0
        ease 1.5 alpha 0.05 zoom 1.15
        repeat

transform gallery_unlock:
    alpha 0.0
    zoom 0.92
    ease 0.3 alpha 1.0 zoom 1.0

transform chapter_title_appear:
    alpha 0.0
    yoffset 32
    ease 0.45 alpha 1.0 yoffset 0

transform main_menu_notebook_loadout_blur:
    alpha 1.0
    blur 0.0
    ease 0.28 alpha 0.72 blur 14.0

transform main_menu_notebook_whiteout:
    alpha 0.0
    ease 0.28 alpha 1.0


screen premium_ambient_fx():
    fixed:
        add Solid("#fff7f0") xsize 520 ysize 220 xalign 0.08 yalign 0.08 at bokeh_glimmer(0.08, 0.08, 0.0)
        add Solid("#ffe9f4") xsize 420 ysize 180 xalign 0.86 yalign 0.18 at bokeh_glimmer(0.86, 0.18, 0.5)
        add Solid("#fff1d8") xsize 300 ysize 140 xalign 0.72 yalign 0.82 at bokeh_glimmer(0.72, 0.82, 0.9)

        add Solid("#ffe0eb") xsize 12 ysize 12 at light_particle(0.18, 0.32, 0.0, 24)
        add Solid("#fff5df") xsize 9 ysize 9 at light_particle(0.72, 0.24, 0.6, 32)
        add Solid("#fff3ea") xsize 10 ysize 10 at light_particle(0.84, 0.44, 1.1, 28)
        add Solid("#ffe7f0") xsize 8 ysize 8 at light_particle(0.34, 0.68, 0.9, 22)

        add Solid("#f6cbd7") xsize 14 ysize 10 at petal_fall(0.12, 0.0, 60)
        add Solid("#ffdbe8") xsize 16 ysize 11 at petal_fall(0.28, 1.4, 80)
        add Solid("#f2c3d2") xsize 13 ysize 9 at petal_fall(0.58, 0.7, 70)
        add Solid("#ffe5ef") xsize 14 ysize 10 at petal_fall(0.84, 2.1, 55)


screen premium_menu_shell(title, scroll=None, yinitial=0.0, spacing=22):
    tag menu
    modal True
    $ shell_back_action = ShowMenu("main_menu") if main_menu else Return()

    use premium_playtime_tracker

    add Solid("#FFFFFF")

    frame:
        style "premium_nav_frame"
        at slide_panel_left

        vbox:
            spacing 32

            text "my imouto yo":
                style "premium_brand_text"

            use premium_nav_hover_textbutton(_("开始游戏"), Start(), "start")
            use premium_nav_hover_textbutton(_("读取游戏"), ShowMenu("load"), "load")
            use premium_nav_hover_textbutton(_("设置"), ShowMenu("preferences"), "preferences")
            use premium_nav_hover_textbutton(_("画廊"), ShowMenu("cg_gallery"), "gallery")
            use premium_nav_hover_textbutton(_("历史"), ShowMenu("history"), "history", sensitive=(not main_menu))
            use premium_nav_hover_textbutton(_("关于"), ShowMenu("about"), "about")
            use premium_nav_hover_textbutton(_("帮助"), ShowMenu("help"), "help", sensitive=(renpy.variant("pc") or (renpy.variant("web") and not renpy.variant("mobile"))))

            if not main_menu and not _in_replay:
                use premium_nav_hover_textbutton(_("返回标题"), MainMenu(), "title")
            elif _in_replay:
                use premium_nav_hover_textbutton(_("结束回放"), EndReplay(confirm=True), "replay_end")

            if renpy.variant("pc"):
                use premium_nav_hover_textbutton(_("退出游戏"), Quit(confirm=not main_menu), "quit")

    frame:
        style "premium_content_frame"
        at slide_panel_right

        vbox:
            spacing 20

            hbox:
                xfill True

                vbox:
                    spacing 6

                    text title:
                        style "premium_menu_title"
                        at chapter_title_appear

                textbutton _("返回"):
                    style "premium_back_button"
                    action shell_back_action

            if scroll == "viewport":
                viewport:
                    style "premium_viewport"
                    yinitial yinitial
                    scrollbars "vertical"
                    mousewheel True
                    draggable True
                    pagekeys True
                    side_yfill True

                    vbox:
                        spacing spacing
                        transclude

            elif scroll == "vpgrid":
                vpgrid:
                    cols 1
                    style "premium_viewport"
                    yinitial yinitial
                    scrollbars "vertical"
                    mousewheel True
                    draggable True
                    pagekeys True
                    side_yfill True
                    spacing spacing
                    transclude

            else:
                transclude

    use portable_pet_menu_shell


screen say(who, what):
    use premium_playtime_tracker

    key "mousedown_4" action If(
        premium_dialogue_history_visible,
        NullAction(),
        Function(premium_story_history_open),
    )
    key "mousedown_5" action If(
        premium_dialogue_history_visible,
        NullAction(),
        RollForward(),
    )

    if not premium_dialogue_history_visible:
        window:
            id "window"

            if who is not None:
                window:
                    id "namebox"
                    style "namebox"

                    text who id "who"

            text what id "what"

    if (not premium_dialogue_history_visible) and (not renpy.variant("small")):
        add SideImage() xalign 0.0 yalign 1.0

    use premium_story_history_overlay


screen premium_story_history_overlay():
    zorder 140
    default history_yadjust = ui.adjustment()

    showif premium_dialogue_history_visible:
        key "dismiss" action Function(premium_story_history_close)
        key "K_ESCAPE" action Function(premium_story_history_close)
        key "mousedown_4" action Function(premium_story_history_scroll, history_yadjust, -1.0)
        key "mousedown_5" action Function(premium_story_history_scroll_down_or_close, history_yadjust)

        button:
            style "premium_story_history_backdrop_button"
            action NullAction()
            at premium_story_history_backdrop_fade

        frame:
            style "premium_story_history_panel"
            at premium_story_history_fade

            timer 0.01 action Function(premium_story_history_snap_to_end, history_yadjust)

            fixed:
                xfill True
                yfill True

                viewport:
                    style "premium_story_history_viewport"
                    yadjustment history_yadjust
                    scrollbars None
                    draggable True
                    mousewheel False
                    pagekeys True

                    vbox:
                        xfill True
                        spacing premium_sy(14)
                        $ history_entry_top = 0.0

                        if _history_list:
                            for h in _history_list:
                                $ what = renpy.filter_text_tags(h.what, allow=gui.history_allow_tags)
                                $ entry_height = premium_story_history_entry_estimated_height(h.who, what)
                                frame:
                                    style "premium_story_history_entry"
                                    at Transform(alpha=premium_story_history_entry_alpha(history_entry_top, entry_height, history_yadjust))

                                    vbox:
                                        xfill True
                                        spacing premium_sy(8)

                                        if h.who:
                                            text h.who:
                                                style "premium_story_history_name"
                                                substitute False

                                        text what:
                                            style "premium_story_history_text"
                                            substitute False

                                $ history_entry_top += entry_height + premium_sy(14)
                        else:
                            frame:
                                style "premium_story_history_entry"

                                text _("尚无对话历史记录。"):
                                    style "premium_story_history_text"


style window:
    xalign 0.5
    xfill True
    yalign gui.textbox_yalign
    ysize premium_sy(336)
    background Transform("gui/textbox_black_fade.png", xsize=config.screen_width, ysize=premium_sy(336))

style namebox:
    xpos premium_sx(304)
    xanchor gui.name_xalign
    xsize premium_sx(440)
    ypos premium_sy(0)
    ysize premium_sy(82)
    background None
    padding (premium_sx(28), premium_sy(16), premium_sx(28), premium_sy(16))

style say_label:
    properties gui.text_properties("name", accent=False)
    size premium_ss(40)
    color "#000000"
    outlines [(1, "#FFFFFF", 0, 0)]
    xalign gui.name_xalign
    yalign 0.5

style namebox_label is say_label

style say_dialogue:
    properties gui.text_properties("dialogue")
    size premium_ss(36)
    color "#000000"
    outlines [(1, "#FFFFFF", 0, 0)]
    xpos premium_sx(304)
    xsize premium_sx(1360)
    ypos premium_sy(96)
    line_spacing premium_sy(12)
    adjust_spacing False

style say_thought is say_dialogue


screen choice(items):
    style_prefix "choice"

    vbox:
        style "premium_choice_vbox"
        at scale_in_soft

        for item in items:
            textbutton item.caption action item.action style "premium_choice_button" at menu_button_focus


screen quick_menu():
    zorder 100

    if quick_menu and (not premium_dialogue_history_visible):
        hbox:
            style_prefix "quick"
            style "quick_menu"

            textbutton _("回退") action Rollback()
            textbutton _("历史") action ShowMenu("history")
            textbutton _("快进") action Skip() alternate Skip(fast=True, confirm=True)
            textbutton _("自动") action Preference("auto-forward", "toggle")
            textbutton _("保存") action ShowMenu("save")
            textbutton _("快存") action [QuickSave(), Function(menu_companion_mark_first_save_done)]
            textbutton _("快读") action QuickLoad()
            textbutton _("设置") action ShowMenu("preferences")


screen navigation():
    null


screen main_menu():
    tag menu
    modal True
    on "show" action [SetVariable("main_menu_status_window_visible", True), SetVariable("main_menu_notebook_loading_slot", None), Function(premium_notebook_reset_state), Function(premium_ensure_session_started), Function(premium_menu_player_init), Function(premium_reset_main_menu_background_offset)]
    on "hide" action Function(premium_menu_player_cleanup)
    key "dismiss" action NullAction()

    use premium_playtime_tracker

    add Solid("#FFFFFF")

    if premium_should_play_opening_op():
        use main_menu_op_overlay
    else:
        fixed:
            xfill True
            yfill True
            at main_menu_dream_in
            if main_menu_notebook_loading_slot is not None:
                at main_menu_notebook_loadout_blur

            timer 0.05 repeat True action Function(premium_tick_main_menu_background_offset)

            $ bg_x, bg_y = premium_main_menu_background_offset()

            add premium_main_menu_background_displayable() xpos (-premium_sx(24) + bg_x) ypos (-premium_sy(16) + bg_y)

            fixed:
                xfill True
                yfill True
                at main_menu_dream_companion_in
                use main_menu_companion_host("hero")

            fixed:
                xfill True
                yfill True
                at main_menu_dream_ui_in

            use main_menu_song_player_widget
            use main_menu_song_player_panel
            use main_menu_status_window_panel
            use main_menu_notebook_drawer
            use main_menu_settings_entry

            add Solid("#FFFFFF") at main_menu_white_haze_out

        if main_menu_notebook_loading_slot is not None:
            use main_menu_notebook_load_overlay


screen main_menu_settings_entry():
    zorder 225

    button:
        style "main_menu_corner_gear_button"
        xpos premium_sx(26)
        ypos config.screen_height - premium_sy(94)
        action ShowMenu("main_menu_settings")

        text "⚙":
            style "main_menu_corner_gear_button_text"
            xalign 0.5
            yalign 0.46


screen main_menu_settings():
    tag menu
    modal True
    default pref_tab = "display"
    key "dismiss" action ShowMenu("main_menu")
    key "K_ESCAPE" action ShowMenu("main_menu")

    use premium_playtime_tracker

    add Solid("#FFFFFF")

    fixed:
        xfill True
        yfill True

        vbox:
            xpos premium_sx(56)
            ypos premium_sy(44)
            xsize config.screen_width - premium_sx(112)
            spacing premium_sy(20)

            frame:
                style "premium_page_header"

                hbox:
                    xfill True
                    yalign 0.5

                    vbox:
                        spacing premium_sy(4)

                        text _("设置"):
                            style "premium_pref_title"

                        text _("在这里更改基础设置"):
                            style "premium_pref_body"

                    null width 0 xfill True

                    textbutton _("返回"):
                        action ShowMenu("main_menu")
                        style "premium_page_button"

            hbox:
                spacing premium_sx(12)
                at scale_in_soft

                textbutton _("显示"):
                    action SetScreenVariable("pref_tab", "display")
                    style "premium_tab_button"
                    sensitive pref_tab != "display"
                    selected pref_tab == "display"

                textbutton _("音量"):
                    action SetScreenVariable("pref_tab", "audio")
                    style "premium_tab_button"
                    sensitive pref_tab != "audio"
                    selected pref_tab == "audio"

            use main_menu_settings_pref_content(pref_tab)


screen main_menu_settings_pref_content(pref_tab):
    if pref_tab == "display":
        hbox:
            spacing premium_sx(22)

            if renpy.variant("pc") or renpy.variant("web"):
                frame:
                    style "premium_pref_card"
                    xsize premium_sx(540)
                    at slide_panel_left

                    vbox:
                        spacing 14
                        text _("显示模式") style "premium_pref_title"
                        textbutton _("窗口模式") action Preference("display", "window") style "premium_pref_button"
                        textbutton _("全屏模式") action Preference("display", "fullscreen") style "premium_pref_button"

                        if renpy.variant("pc"):
                            null height premium_sy(8)
                            text _("窗口分辨率") style "premium_pref_label"
                            text "[premium_window_resolution_summary()]":
                                style "premium_pref_status"

                            hbox:
                                spacing premium_sx(10)

                                textbutton _("1280 x 720"):
                                    action [Preference("display", "window"), Function(premium_set_window_resolution, 1280, 720)]
                                    style "premium_pref_button"
                                    sensitive not premium_window_resolution_matches(1280, 720)

                                textbutton _("1600 x 900"):
                                    action [Preference("display", "window"), Function(premium_set_window_resolution, 1600, 900)]
                                    style "premium_pref_button"
                                    sensitive not premium_window_resolution_matches(1600, 900)

                            hbox:
                                spacing premium_sx(10)

                                textbutton _("1920 x 1080"):
                                    action [Preference("display", "window"), Function(premium_set_window_resolution, 1920, 1080)]
                                    style "premium_pref_button"
                                    sensitive not premium_window_resolution_matches(1920, 1080)

                                textbutton _("2560 x 1440"):
                                    action [Preference("display", "window"), Function(premium_set_window_resolution, 2560, 1440)]
                                    style "premium_pref_button"
                                    sensitive not premium_window_resolution_matches(2560, 1440)

            frame:
                style "premium_pref_card"
                xfill True
                at slide_panel_right

                vbox:
                    spacing 14
                    text _("文本与节奏") style "premium_pref_title"
                    text _("文字速度") style "premium_pref_label"
                    bar value Preference("text speed") style "premium_slider"
                    text _("自动前进") style "premium_pref_label"
                    bar value Preference("auto-forward time") style "premium_slider"

    elif pref_tab == "audio":
        vbox:
            spacing premium_sy(18)

            frame:
                style "premium_pref_card"
                xfill True

                vbox:
                    spacing 14
                    text _("音乐音量") style "premium_pref_title"
                    bar value Preference("music volume") style "premium_slider"

            frame:
                style "premium_pref_card"
                xfill True

                vbox:
                    spacing 14
                    text _("音效音量") style "premium_pref_title"
                    bar value Preference("sound volume") style "premium_slider"
                    if config.sample_sound:
                        textbutton _("试听音效") action Play("sound", config.sample_sound) style "premium_pref_button"

            frame:
                style "premium_pref_card"
                xfill True

                vbox:
                    spacing 14
                    text _("语音音量") style "premium_pref_title"
                    bar value Preference("voice volume") style "premium_slider"
                    if config.sample_voice:
                        textbutton _("试听语音") action Play("voice", config.sample_voice) style "premium_pref_button"

screen main_menu_song_player_widget():
    zorder 230
    on "show" action Function(premium_menu_player_init)
    timer 0.2 repeat True action Function(premium_menu_player_tick)

    $ track = premium_menu_player_track()
    $ playing = premium_menu_player_is_actively_playing()
    $ bar_x = config.screen_width - 407
    $ bar_y = 24

    if track:
        fixed:
            xpos bar_x
            ypos bar_y
            xsize 361
            ysize 52

            add "gui/song_player/strip.png"
            add Solid("#FFFFFF") xpos 224 ypos 0 xsize 137 ysize 38

            text track["title"]:
                style "premium_song_player_strip_title"
                xpos 48
                ypos 20
                yanchor 0.5
                xmaximum 176

            button:
                style "premium_song_player_hitbox"
                xpos 2
                ypos 2
                xsize 36
                ysize 36
                action Function(premium_menu_player_toggle_panel)

            button:
                style "premium_song_player_hitbox"
                xpos 232
                ypos 2
                xsize 40
                ysize 34
                action Function(premium_menu_player_previous)
                text "<<" style "premium_song_player_icon_text" xalign 0.5 yalign 0.5

            button:
                style "premium_song_player_hitbox"
                xpos 279
                ypos 2
                xsize 32
                ysize 34
                action Function(premium_menu_player_toggle_pause)
                text ("||" if playing else ">") style "premium_song_player_icon_text" xalign 0.5 yalign 0.5

            button:
                style "premium_song_player_hitbox"
                xpos 319
                ypos 2
                xsize 40
                ysize 34
                action Function(premium_menu_player_next)
                text ">>" style "premium_song_player_icon_text" xalign 0.5 yalign 0.5


screen main_menu_song_player_panel():
    zorder 235
    modal True

    if getattr(store, "main_menu_player_open", False):
        $ track = premium_menu_player_track()
        $ ratio = premium_menu_player_progress_ratio()
        $ panel_x = config.screen_width - 845
        $ panel_y = 96
        $ current_page = getattr(store, "main_menu_player_page", "now_playing")

        if track:
            button:
                style "premium_song_player_hitbox"
                xpos 0
                ypos 0
                xsize config.screen_width
                ysize config.screen_height
                action NullAction()

            drag:
                drag_name "main_menu_song_player_panel"
                draggable True
                drag_raise True
                drag_handle (0, 0, 514, 470)
                xpos panel_x
                ypos panel_y
                xsize 514
                ysize 831
                at song_player_panel_show

                fixed:
                    xsize 514
                    ysize 831

                    add "gui/song_player/panel.png"

                    fixed:
                        xpos 34
                        ypos 42
                        xsize 236
                        ysize 462
                        clipping True

                        if current_page == "track_list":
                            viewport:
                                xpos 12
                                ypos 104
                                xsize 212
                                ysize 344
                                mousewheel True
                                draggable True
                                scrollbars None

                                vbox:
                                    xsize 212
                                    spacing 18

                                    for i, song in enumerate(premium_menu_player_tracks):
                                        button:
                                            style "premium_song_player_panel_track_button"
                                            action Function(premium_menu_player_select_track, i)
                                            xalign 0.5
                                            xsize 166
                                            ysize 126

                                            fixed:
                                                xsize 166
                                                ysize 126

                                                add Transform(song["cover"], fit="cover", xsize=88, ysize=88):
                                                    xalign 0.5
                                                    ypos 0

                                                text song["title"]:
                                                    style "premium_song_player_track_cover_title"
                                                    xalign 0.5
                                                    ypos 96
                                                    xmaximum 156
                        else:
                            fixed:
                                xpos 26
                                ypos 82
                                xsize 182
                                ysize 182
                                clipping True

                                add Transform(track["cover"], fit="cover", xsize=182, ysize=182) xpos 0 ypos 0

                            text track["title"]:
                                style "premium_song_player_panel_title"
                                xpos 20
                                ypos 280
                                xmaximum 196
                                ymaximum 64

                            fixed:
                                xpos 20
                                ypos 372
                                xsize 196
                                ysize 10

                                add Solid("#ECE8E2") xpos 0 ypos 0 xsize 196 ysize 10
                                add Solid("#1A1A1A") xpos 0 ypos 0 xsize int(round(196 * ratio)) ysize 10

                            text premium_menu_player_format_time(premium_menu_player_progress()):
                                style "premium_song_player_progress_text"
                                xpos 20
                                ypos 390

                            text premium_menu_player_duration_text():
                                style "premium_song_player_progress_text"
                                xpos 216
                                ypos 390
                                xanchor 1.0

                    button:
                        style "premium_song_player_panel_hitbox"
                        xpos 0
                        ypos 0
                        xsize 514
                        ysize 48
                        action Function(premium_menu_player_toggle_panel)

                    button:
                        style "premium_song_player_panel_hitbox"
                        xpos 46
                        ypos 536
                        xsize 86
                        ysize 46
                        action Function(premium_menu_player_show_menu)

                    button:
                        style "premium_song_player_panel_hitbox"
                        xpos 216
                        ypos 536
                        xsize 92
                        ysize 46
                        action Function(premium_menu_player_back)

                    button:
                        style "premium_song_player_panel_hitbox"
                        xpos 130
                        ypos 542
                        xsize 88
                        ysize 62
                        action Function(premium_menu_player_adjust_volume, 0.1)

                    button:
                        style "premium_song_player_panel_hitbox"
                        xpos 132
                        ypos 698
                        xsize 84
                        ysize 54
                        action Function(premium_menu_player_adjust_volume, -0.1)

                    button:
                        style "premium_song_player_panel_hitbox"
                        xpos 58
                        ypos 612
                        xsize 84
                        ysize 64
                        action Function(premium_menu_player_previous)

                    button:
                        style "premium_song_player_panel_hitbox"
                        xpos 206
                        ypos 612
                        xsize 88
                        ysize 64
                        action Function(premium_menu_player_next)

                    button:
                        style "premium_song_player_panel_hitbox"
                        xpos 108
                        ypos 584
                        xsize 122
                        ysize 122
                        action Function(premium_menu_player_toggle_pause)

                    button:
                        style "premium_song_player_panel_hitbox"
                        xpos 182
                        ypos 756
                        xsize 106
                        ysize 56
                        action Function(premium_menu_player_toggle_panel)


screen main_menu_status_window_panel():
    zorder 220

    if main_menu_status_window_visible:
        drag:
            drag_name "main_menu_status_window"
            draggable True
            drag_raise True
            drag_handle (0, 0, premium_status_window_width(), premium_status_window_height())
            xpos premium_sx(28)
            ypos premium_sy(20)
            xsize premium_status_window_width()
            ysize premium_status_window_height()

            fixed:
                xsize premium_sx(400)
                ysize premium_sy(491)
                at Transform(zoom=premium_status_window_scale())

                add Transform("gui/main_menu_status_window.png", xsize=premium_sx(400), ysize=premium_sy(491))

                textbutton "×":
                    style "premium_status_window_close_button"
                    action SetVariable("main_menu_status_window_visible", False)
                    xpos premium_sx(360)
                    ypos premium_sy(4)

                vbox:
                    xpos premium_sx(32)
                    ypos premium_sy(84)
                    spacing premium_sy(28)

                    vbox:
                        spacing premium_sy(6)
                        text _("游戏时长"):
                            style "premium_status_window_label"
                        text "[premium_status_playtime_text()]":
                            style "premium_status_window_value"

                    vbox:
                        spacing premium_sy(6)
                        text _("当前时间"):
                            style "premium_status_window_label"
                        text "[premium_status_now_text()]":
                            style "premium_status_window_value"

                    vbox:
                        spacing premium_sy(6)
                        text _("版本号"):
                            style "premium_status_window_label"
                        text "Ver. [config.version]":
                            style "premium_status_window_value"


screen main_menu_notebook_drawer():
    zorder 240
    $ notebook_has_save = any(bool(FileTime(slot, format=_("%Y-%m-%d %H:%M"), empty="")) for slot in range(1, 7))

    if notebook_has_save:
        if premium_notebook_is_animating():
            timer 0.033 repeat True action Function(premium_notebook_tick)

        $ notebook_y = int(round(getattr(store, "main_menu_notebook_y", premium_notebook_closed_y())))
        $ notebook_fully_open = abs(notebook_y - premium_notebook_open_y()) < premium_sy(10)
        $ slide_span = float(premium_notebook_open_y() - premium_notebook_closed_y())
        $ slide_progress = 0.0 if slide_span == 0 else max(0.0, min(1.0, (float(notebook_y) - premium_notebook_closed_y()) / slide_span))
        $ tab_alpha = 1.0 - slide_progress
        $ notebook_base_w = premium_notebook_base_width()
        $ notebook_base_h = premium_notebook_base_height()
        $ notebook_content_scale = premium_notebook_content_scale()

        mousearea:
            area (premium_notebook_x(), notebook_y, premium_notebook_width(), premium_notebook_height())
            hovered Function(premium_notebook_set_hovered, True)
            unhovered Function(premium_notebook_set_hovered, False)

        fixed:
            xpos premium_notebook_x()
            ypos notebook_y
            xsize premium_notebook_width()
            ysize premium_notebook_height()

            add Transform("gui/main_menu_notebook.png", xsize=premium_notebook_width(), ysize=premium_notebook_height())

            fixed:
                xsize notebook_base_w
                ysize notebook_base_h
                at Transform(zoom=notebook_content_scale)

                if notebook_fully_open:
                    button:
                        style "premium_notebook_blank_close"
                        xpos premium_sx(12)
                        ypos premium_sy(12)
                        xsize notebook_base_w - premium_sx(24)
                        ysize premium_sy(132)
                        action NullAction()

                    button:
                        style "premium_notebook_blank_close"
                        xpos premium_sx(32)
                        ypos premium_sy(665)
                        xsize premium_sx(510)
                        ysize premium_sy(160)
                        action NullAction()

                else:
                    button:
                        style "premium_notebook_blank_close"
                        xpos 0
                        ypos notebook_base_h - premium_sy(92)
                        xsize notebook_base_w
                        ysize premium_sy(92)
                        action NullAction()

                    text _("存档"):
                        style "premium_notebook_tab_text"
                        xpos (notebook_base_w // 2)
                        ypos notebook_base_h - premium_sy(54)
                        xanchor 0.5
                        at Transform(alpha=tab_alpha)

                grid 2 3:
                    xpos premium_sx(36)
                    ypos premium_sy(120)
                    spacing premium_sx(18)

                    for slot in range(1, 7):
                        $ save_time = FileTime(slot, format=_("%Y-%m-%d %H:%M"), empty="")
                        $ save_name = FileSaveName(slot)
                        $ has_save = bool(save_time)
                        $ slot_action = Function(premium_notebook_begin_load, slot) if has_save else NullAction()

                        if has_save:
                            button:
                                style "premium_notebook_slot_button"
                                sensitive (notebook_fully_open and (not premium_notebook_input_locked()))
                                action slot_action

                                fixed:
                                    xsize premium_sx(242)
                                    ysize premium_sy(170)

                                    add FileScreenshot(slot):
                                        xpos premium_sx(11)
                                        ypos premium_sy(11)
                                        xsize premium_sx(220)
                                        ysize premium_sy(114)

                                    text save_time:
                                        style "premium_notebook_slot_time"
                                        xpos premium_sx(18)
                                        ypos premium_sy(101)

                                    if save_name:
                                        text save_name:
                                            style "premium_notebook_slot_title"
                                            xpos premium_sx(16)
                                            ypos premium_sy(136)


screen main_menu_notebook_load_overlay():
    zorder 480
    modal True

    $ pending_slot = main_menu_notebook_loading_slot

    if pending_slot is not None:
        add Solid("#FFFFFF") at main_menu_notebook_whiteout
        timer 0.28 action [Function(premium_prepare_notebook_load_transition), SetVariable("main_menu_notebook_loading_slot", None), FileLoad(pending_slot, confirm=False)]


screen premium_playtime_tracker():
    zorder -100
    on "show" action Function(premium_ensure_session_started)
    on "hide" action Function(premium_flush_playtime)
    timer 1.0 repeat True action Function(premium_playtime_tick)


screen main_menu_op_overlay():
    zorder 500

    on "show" action SetVariable("opening_op_phase", "playing")
    on "hide" action Stop("main_menu_op")

    add Transform("main_menu_op_movie", fit="contain", xysize=(config.screen_width, config.screen_height)):
        xalign 0.5
        yalign 0.5

    timer premium_main_menu_op_cutoff action Function(premium_finish_opening_op)
screen game_menu(title, scroll=None, yinitial=0.0, spacing=22):
    use premium_menu_shell(title, scroll=scroll, yinitial=yinitial, spacing=spacing)


screen save():
    tag menu
    use file_slots(_("保存"))


screen load():
    tag menu
    use file_slots(_("读取游戏"))


screen file_slots(title):
    default page_name_value = FilePageNameInputValue(pattern=_("第 {} 页"), auto=_("自动存档"), quick=_("快速存档"))

    use premium_menu_shell(title):
        vbox:
            spacing 26

            frame:
                style "premium_page_header"
                at scale_in_soft

                hbox:
                    xfill True
                    yalign 0.5

                    button:
                        style "premium_page_label_button"
                        action page_name_value.Toggle()
                        key_events True

                        input:
                            style "premium_page_label_text"
                            value page_name_value

                    hbox:
                        spacing 10
                        xalign 1.0

                        textbutton _("<") action FilePagePrevious() style "premium_page_button"
                        if config.has_autosave:
                            textbutton _("自动") action FilePage("auto") style "premium_page_button"
                        if config.has_quicksave:
                            textbutton _("快速") action FilePage("quick") style "premium_page_button"
                        for page in range(1, 7):
                            textbutton "[page]" action FilePage(page) style "premium_page_button"
                        textbutton _(">") action FilePageNext() style "premium_page_button"

            grid gui.file_slot_cols gui.file_slot_rows:
                xalign 0.5
                spacing 22

                for i in range(gui.file_slot_cols * gui.file_slot_rows):
                    $ slot = i + 1
                    $ slot_action = [FileAction(slot), Function(menu_companion_mark_first_save_done)] if title == _("保存") else FileAction(slot)

                    button:
                        style "premium_slot_button"
                        at slot_hover_focus
                        action slot_action
                        key "save_delete" action FileDelete(slot)

                        fixed:
                            xsize premium_sx(376)
                            ysize premium_sy(248)

                            add Solid("#fff7f6") xpos 0 ypos 0 xsize premium_sx(376) ysize premium_sy(248) alpha 0.035
                            add FileScreenshot(slot):
                                xpos premium_sx(16)
                                ypos premium_sy(16)
                                xsize premium_sx(344)
                                ysize premium_sy(194)

                            frame:
                                style "premium_slot_overlay"

                                vbox:
                                    spacing 4
                                    xfill True

                                    text FileTime(slot, format=_("{#file_time}%Y-%m-%d %H:%M"), empty=_("空存档位")):
                                        style "premium_slot_time"

                                    text FileSaveName(slot):
                                        style "premium_slot_name"


screen preferences():
    tag menu
    default pref_tab = "display"

    use premium_menu_shell(_("设置"), scroll="viewport"):
        vbox:
            spacing 24

            hbox:
                spacing 12
                at scale_in_soft

                textbutton _("显示") action SetScreenVariable("pref_tab", "display") style "premium_tab_button"
                textbutton _("快进") action SetScreenVariable("pref_tab", "flow") style "premium_tab_button"
                textbutton _("音量") action SetScreenVariable("pref_tab", "audio") style "premium_tab_button"
                textbutton _("体验") action SetScreenVariable("pref_tab", "fx") style "premium_tab_button"

            if pref_tab == "display":
                hbox:
                    spacing 22

                    if renpy.variant("pc") or renpy.variant("web"):
                        frame:
                            style "premium_pref_card"
                            at slide_panel_left

                            vbox:
                                spacing 14
                                text _("显示模式") style "premium_pref_title"
                                textbutton _("窗口模式") action Preference("display", "window") style "premium_pref_button"
                                textbutton _("全屏模式") action Preference("display", "fullscreen") style "premium_pref_button"

                                if renpy.variant("pc"):
                                    null height premium_sy(8)
                                    text _("窗口分辨率") style "premium_pref_label"
                                    text "[premium_window_resolution_summary()]":
                                        style "premium_pref_status"

                                    hbox:
                                        spacing premium_sx(10)

                                        textbutton _("1280 x 720"):
                                            action [Preference("display", "window"), Function(premium_set_window_resolution, 1280, 720)]
                                            style "premium_pref_button"
                                            sensitive not premium_window_resolution_matches(1280, 720)

                                        textbutton _("1600 x 900"):
                                            action [Preference("display", "window"), Function(premium_set_window_resolution, 1600, 900)]
                                            style "premium_pref_button"
                                            sensitive not premium_window_resolution_matches(1600, 900)

                                    hbox:
                                        spacing premium_sx(10)

                                        textbutton _("1920 x 1080"):
                                            action [Preference("display", "window"), Function(premium_set_window_resolution, 1920, 1080)]
                                            style "premium_pref_button"
                                            sensitive not premium_window_resolution_matches(1920, 1080)

                                        textbutton _("2560 x 1440"):
                                            action [Preference("display", "window"), Function(premium_set_window_resolution, 2560, 1440)]
                                            style "premium_pref_button"
                                            sensitive not premium_window_resolution_matches(2560, 1440)

                    frame:
                        style "premium_pref_card"
                        at slide_panel_right

                        vbox:
                            spacing 14
                            text _("文本与节奏") style "premium_pref_title"
                            text _("文字速度") style "premium_pref_label"
                            bar value Preference("text speed") style "premium_slider"
                            text _("自动前进") style "premium_pref_label"
                            bar value Preference("auto-forward time") style "premium_slider"

            elif pref_tab == "flow":
                frame:
                    style "premium_pref_card"
                    at slide_panel_right

                    vbox:
                        spacing 18
                        text _("快进设置") style "premium_pref_title"
                        text _("下面三项会影响按住 Ctrl 或开启快进时的表现。") style "premium_pref_body"

                        vbox:
                            spacing 8
                            button:
                                action Preference("skip", "toggle")
                                style "premium_pref_button"
                                xfill True

                                hbox:
                                    xfill True
                                    yalign 0.5

                                    text _("是否跳过未读对话"):
                                        style "premium_pref_button_text"

                                    null:
                                        xfill True

                                    text "[premium_pref_check_mark(premium_pref_skip_unseen_enabled())]":
                                        style "premium_pref_toggle_mark"

                            text _("开启后，没看过的对白也会被快进跳过去。") style "premium_pref_body"

                        vbox:
                            spacing 8
                            button:
                                action Preference("after choices", "toggle")
                                style "premium_pref_button"
                                xfill True

                                hbox:
                                    xfill True
                                    yalign 0.5

                                    text _("遇到选项后是否继续快进"):
                                        style "premium_pref_button_text"

                                    null:
                                        xfill True

                                    text "[premium_pref_check_mark(premium_pref_after_choices_enabled())]":
                                        style "premium_pref_toggle_mark"

                            text _("开启后，做完选项后会继续自动快进；关闭后会停下来等你看。") style "premium_pref_body"

            elif pref_tab == "audio":
                vbox:
                    spacing 18

                    hbox:
                        spacing premium_sx(22)

                        if config.has_music:
                            frame:
                                style "premium_pref_card"
                                xfill True

                                vbox:
                                    spacing 14
                                    text _("音乐音量") style "premium_pref_title"
                                    bar value Preference("music volume") style "premium_slider"

                        if config.has_sound:
                            frame:
                                style "premium_pref_card"
                                xfill True

                                vbox:
                                    spacing 14
                                    text _("音效音量") style "premium_pref_title"
                                    bar value Preference("sound volume") style "premium_slider"
                                    if config.sample_sound:
                                        textbutton _("试听音效") action Play("sound", config.sample_sound) style "premium_pref_button"

                        if config.has_voice:
                            frame:
                                style "premium_pref_card"
                                xfill True

                                vbox:
                                    spacing 14
                                    text _("语音音量") style "premium_pref_title"
                                    bar value Preference("voice volume") style "premium_slider"
                                    if config.sample_voice:
                                        textbutton _("试听语音") action Play("voice", config.sample_voice) style "premium_pref_button"

                    if config.has_music or config.has_sound or config.has_voice:
                        button:
                            action Preference("all mute", "toggle")
                            style "premium_pref_button"
                            xfill True

                            hbox:
                                xfill True
                                yalign 0.5

                                text _("全部静音"):
                                    style "premium_pref_button_text"

                                null:
                                    xfill True

                                text "[premium_pref_check_mark(premium_pref_all_mute_enabled())]":
                                    style "premium_pref_toggle_mark"

            else:
                frame:
                    style "premium_pref_card"
                    at blur_fade_soft

                    vbox:
                        spacing 18
                        text _("画面体验") style "premium_pref_title"

                        vbox:
                            spacing 8
                            button:
                                action Preference("transitions", "toggle")
                                style "premium_pref_button"
                                xfill True

                                hbox:
                                    xfill True
                                    yalign 0.5

                                    text _("场景切换时显示过渡动画"):
                                        style "premium_pref_button_text"

                                    null:
                                        xfill True

                                    text "[premium_pref_check_mark(premium_pref_transitions_enabled())]":
                                        style "premium_pref_toggle_mark"

                            text _("开启后，切换场景时会保留淡入淡出等过渡效果；关闭后切换会更直接。") style "premium_pref_body"

                        text _("更改会立即生效。") style "premium_pref_body"


screen history():
    tag menu
    predict False

    use premium_menu_shell(_("历史"), scroll="viewport", yinitial=1.0, spacing=18):
        if _history_list:
            for h in _history_list:
                frame:
                    style "premium_history_card"
                    at alpha_dissolve_soft

                    vbox:
                        spacing 8

                        if h.who:
                            text h.who:
                                style "premium_history_name"
                                substitute False

                        $ what = renpy.filter_text_tags(h.what, allow=gui.history_allow_tags)
                        text what:
                            style "premium_history_text"
                            substitute False
        else:
            frame:
                style "premium_history_card"
                text _("尚无对话历史记录。") style "premium_history_text"


screen about():
    tag menu

    use premium_menu_shell(_("关于"), scroll="viewport"):
        frame:
            style "premium_info_card"
            at scale_in_soft

            vbox:
                spacing 12

                text "[config.name!t]":
                    style "premium_pref_title"

                text _("版本 [config.version!t]"):
                    style "premium_pref_body"

                if gui.about:
                    text "[gui.about!t]":
                        style "premium_pref_body"

                text _("引擎：{a=https://www.renpy.org/}Ren'Py{/a} [renpy.version_only]"):
                    style "premium_pref_body"

                text _("最后更新于 2026-04-06"):
                    style "premium_pref_body"


screen help():
    tag menu
    default device = "keyboard"

    use premium_menu_shell(_("帮助"), scroll="viewport"):
        vbox:
            spacing 18

            hbox:
                spacing 12

                textbutton _("键盘") action SetScreenVariable("device", "keyboard") style "premium_tab_button"
                textbutton _("鼠标") action SetScreenVariable("device", "mouse") style "premium_tab_button"
                if GamepadExists():
                    textbutton _("手柄") action SetScreenVariable("device", "gamepad") style "premium_tab_button"

            frame:
                style "premium_info_card"

                if device == "keyboard":
                    use premium_keyboard_help
                elif device == "mouse":
                    use premium_mouse_help
                else:
                    use premium_gamepad_help


screen premium_help_row(key_text, desc_text):
    hbox:
        spacing 24
        xfill True

        text key_text:
            style "premium_help_key"

        text desc_text:
            style "premium_help_desc"


screen premium_keyboard_help():
    vbox:
        spacing 14

        use premium_help_row("Enter", "推进文本并确认当前按钮。")
        use premium_help_row("Space", "在没有选项时继续下一句。")
        use premium_help_row("Arrow Keys", "在菜单中移动焦点。")
        use premium_help_row("Esc", "打开系统菜单。")
        use premium_help_row("Ctrl", "按住时快进文本。")
        use premium_help_row("Tab", "切换自动快进。")
        use premium_help_row("Page Up", "回看上一句对话。")
        use premium_help_row("Page Down", "前进到后一条记录。")
        use premium_help_row("H", "隐藏界面。")
        use premium_help_row("S", "截图。")


screen premium_mouse_help():
    vbox:
        spacing 14

        use premium_help_row("Left Click", "推进文本并激活按钮。")
        use premium_help_row("Right Click", "打开系统菜单。")
        use premium_help_row("Middle Click", "隐藏界面。")
        use premium_help_row("Wheel Up", "回看上一句对话。")
        use premium_help_row("Wheel Down", "前进到后一条记录。")


screen premium_gamepad_help():
    vbox:
        spacing 14

        use premium_help_row("A / Cross", "确认与推进。")
        use premium_help_row("B / Circle", "返回菜单。")
        use premium_help_row("D-Pad", "移动菜单焦点。")
        use premium_help_row("Shoulders", "切换菜单页。")


screen cg_gallery():
    tag menu
    default gallery_page = 0
    $ items_per_page = 6
    $ page_count = int((len(premium_gallery_items) + items_per_page - 1) / items_per_page)
    $ current_items = premium_gallery_items[gallery_page * items_per_page:(gallery_page + 1) * items_per_page]

    use premium_menu_shell(_("CG 画廊")):
        vbox:
            spacing 24

            grid 3 2:
                spacing 22
                xalign 0.5

                for title, scene_name in current_items:
                    $ unlocked = premium_gallery_unlocked(scene_name)
                    $ gallery_action = ShowMenu("cg_viewer", scene_name=scene_name, title=title) if unlocked else NullAction()
                    $ gallery_status = _("已解锁") if unlocked else _("未解锁")

                    button:
                        style "premium_gallery_thumb"
                        action gallery_action
                        at thumb_hover_zoom

                        fixed:
                            xsize premium_sx(360)
                            ysize premium_sy(220)

                            if unlocked:
                                add Transform(scene_name, fit="cover", xsize=premium_sx(360), ysize=premium_sy(220)) at gallery_unlock
                            else:
                                add Solid("#1f1719")

                            add Solid("#fff4ef") xpos 0 ypos premium_sy(170) xsize premium_sx(360) ysize premium_sy(50) alpha 0.14

                            vbox:
                                xpos premium_sx(20)
                                ypos premium_sy(168)
                                spacing 0

                                text gallery_status:
                                    style "premium_gallery_status"

            hbox:
                spacing 12
                xalign 0.5

                textbutton _("上一页") action SetScreenVariable("gallery_page", max(0, gallery_page - 1)) style "premium_page_button"
                text _("[gallery_page + 1] / [page_count]"):
                    style "premium_menu_meta"
                textbutton _("下一页") action SetScreenVariable("gallery_page", min(page_count - 1, gallery_page + 1)) style "premium_page_button"


screen cg_viewer(scene_name, title):
    tag menu
    modal True

    add Solid("#0A0A0A")

    frame:
        style "premium_viewer_frame"
        at scale_in_soft

        vbox:
            spacing 14

            add Transform(scene_name, fit="contain", xysize=(premium_sx(1480), premium_sy(760))):
                xalign 0.5

            textbutton _("返回画廊") action ShowMenu("cg_gallery") style "premium_back_button"


screen chapter_title_card(title, subtitle=""):
    modal True
    zorder 120

    add Solid("#100808c8")

    frame:
        style "premium_chapter_frame"
        at chapter_title_appear

        vbox:
            spacing 12
            xalign 0.5

            text title:
                style "premium_chapter_title"

            if subtitle:
                text subtitle:
                    style "premium_chapter_subtitle"


screen confirm(message, yes_action, no_action):
    modal True
    zorder 200
    style_prefix "confirm"

    add Solid("#100808c8")

    frame:
        vbox:
            xalign 0.5
            yalign 0.5
            spacing 45

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            hbox:
                xalign 0.5
                spacing 150

                textbutton _("是") action yes_action
                textbutton _("否") action no_action

    key "game_menu" action no_action


style premium_say_panel is default:
    xpos premium_sx(130)
    xsize premium_sx(1660)
    ypos premium_sy(742)
    ysize premium_sy(232)
    padding (premium_sx(56), premium_sy(40), premium_sx(56), premium_sy(32))
    background None

style premium_namebox is default:
    xpos premium_sx(176)
    ypos premium_sy(690)
    xminimum premium_sx(220)
    padding (premium_sx(30), premium_sy(18), premium_sx(30), premium_sy(16))
    background None

style premium_say_name is default:
    font premium_name_font
    size premium_ss(36)
    bold False
    color "#FFFFFF"
    outlines [(2, "#111111", 0, 0)]
    text_align 0.5

style premium_say_dialogue is default:
    font premium_body_font
    size premium_ss(33)
    color "#FFFFFF"
    line_spacing premium_sy(12)
    outlines [(2, "#111111", 0, 0)]

style premium_choice_vbox is vbox:
    xalign 0.5
    ypos premium_sy(380)
    spacing premium_sy(18)

style premium_choice_button is button:
    xminimum premium_sx(980)
    yminimum premium_sy(72)
    padding (premium_sx(42), premium_sy(18), premium_sx(42), premium_sy(18))
    background Frame("g/button/idle_background.png", Borders(20, 20, 20, 20), tile=False)
    hover_background Frame("gui/button/hover_background.png", Borders(20, 20, 20, 20), tile=False)

style premium_choice_button_text is button_text:
    font premium_ui_font
    size premium_ss(30)
    color "#F8F3F7"
    hover_color "#7A7A7A"
    xalign 0.5
    text_align 0.5
    outlines [(2, "#2B2330", 0, 0)]

style premium_nav_frame is default:
    xpos premium_sx(52)
    ypos premium_sy(54)
    xsize premium_sx(370)
    ysize premium_sy(972)
    padding (premium_sx(30), premium_sy(34), premium_sx(30), premium_sy(34))
    background Solid("#FFFFFF")

style premium_content_frame is default:
    xpos premium_sx(462)
    ypos premium_sy(54)
    xsize premium_sx(1400)
    ysize premium_sy(972)
    padding (premium_sx(42), premium_sy(34), premium_sx(42), premium_sy(30))
    background Solid("#FFFFFF")

style premium_brand_text is default:
    font premium_body_font
    size premium_ss(18)
    color "#000000"
    bold False

style premium_nav_button is button:
    xfill True
    yminimum premium_sy(56)
    padding (premium_sx(22), premium_sy(14), premium_sx(22), premium_sy(14))
    background Frame("gui/button/idle_background.png", Borders(12, 12, 12, 12), tile=False)
    hover_background Frame("gui/button/hover_background.png", Borders(12, 12, 12, 12), tile=False)
    hover_sound "audio/1.ogg"

style premium_nav_button_text is button_text:
    font premium_body_font
    size premium_ss(24)
    color "#111111"
    hover_color "#7A7A7A"
    outlines []

style premium_menu_title is default:
    font premium_name_font
    size premium_ss(52)
    bold False
    color "#000000"
    outlines []

style premium_back_button is button:
    xalign 1.0
    padding (premium_sx(24), premium_sy(12), premium_sx(24), premium_sy(12))
    background Frame("gui/button/idle_background.png", Borders(10, 10, 10, 10), tile=False)
    hover_background Frame("gui/button/hover_background.png", Borders(10, 10, 10, 10), tile=False)

style premium_back_button_text is button_text:
    font premium_body_font
    size premium_ss(22)
    color "#111111"
    hover_color "#7A7A7A"
    outlines []

style premium_logo_text is default:
    font premium_name_font
    size premium_ss(82)
    bold True
    color "#143A47"
    outlines [(2, "#EAF8FC", 0, 0)]

style premium_menu_showcase is default:
    xpos premium_sx(1080)
    ypos premium_sy(136)
    xsize premium_sx(610)
    ysize premium_sy(760)
    padding (premium_sx(42), premium_sy(40), premium_sx(42), premium_sy(40))
    background Frame("gui/frame.png", Borders(18, 18, 18, 18), tile=False)

style premium_showcase_lead is default:
    font premium_name_font
    size premium_ss(32)
    bold True
    color "#2d181f"
    outlines [(1, "#fff4ee", 0, 0)]

style premium_showcase_body is default:
    font premium_ui_font
    size premium_ss(24)
    color "#53343d"
    line_spacing premium_sy(4)

style premium_main_button is button:
    xalign 0.5
    xminimum premium_sx(456)
    xmaximum premium_sx(456)
    yminimum premium_sy(88)
    ymaximum premium_sy(88)
    padding (premium_sx(34), premium_sy(20), premium_sx(34), premium_sy(20))
    background Frame("gui/button/main_menu_card_idle.png", Borders(30, 30, 30, 30), tile=False)
    hover_background Frame("gui/button/main_menu_card_hover.png", Borders(30, 30, 30, 30), tile=False)
    activate_background Frame("gui/button/main_menu_card_press.png", Borders(30, 30, 30, 30), tile=False)
    insensitive_background Frame("gui/button/main_menu_card_idle.png", Borders(30, 30, 30, 30), tile=False)
    hover_sound "audio/1.ogg"

style premium_main_button_text is button_text:
    font premium_body_font
    size premium_ss(29)
    bold False
    kerning 0.5
    antialias True
    color "#3B2D38"
    hover_color "#7A7A7A"
    activate_color "#2A212A"
    xalign 0.5
    text_align 0.5
    outlines [(1, "#FFFDFE", 0, 0)]
    hover_outlines [(1, "#FFFDFE", 0, 0), (2, "#FFF7FD44", 0, 0)]
    activate_outlines [(1, "#FFFDFE", 0, 0)]

style premium_menu_meta is default:
    font premium_body_font
    size premium_ss(18)
    color "#111111"

style premium_menu_meta_small is default:
    font premium_body_font
    size premium_ss(14)
    color "#111111"

style premium_status_window_label is default:
    font premium_name_font
    size premium_ss(24)
    color "#111111"
    outlines []

style premium_status_window_value is default:
    font premium_body_font
    size premium_ss(22)
    color "#111111"
    outlines []

style premium_status_window_close_button is button:
    background None
    hover_background None
    padding (premium_sx(8), premium_sy(2), premium_sx(8), premium_sy(2))

style premium_status_window_close_button_text is button_text:
    font premium_ui_font
    size premium_ss(26)
    color "#111111"
    hover_color "#7A7A7A"
    outlines []

style main_menu_corner_gear_button is button:
    xsize premium_sx(56)
    ysize premium_sy(56)
    background None
    hover_background None
    padding (0, 0, 0, 0)

style main_menu_corner_gear_button_text is default:
    font premium_ui_font
    size premium_ss(28)
    color "#111111"
    hover_color "#7A7A7A"
    outlines []

style premium_notebook_tab_text is default:
    font premium_name_font
    size premium_ss(30)
    color "#111111"
    outlines []

style premium_notebook_slot_button is button:
    background Frame("gui/button/slot_idle_background.png", Borders(14, 14, 14, 14), tile=False)
    hover_background Frame("gui/button/slot_hover_background.png", Borders(14, 14, 14, 14), tile=False)
    activate_background Frame("gui/button/slot_hover_background.png", Borders(14, 14, 14, 14), tile=False)
    insensitive_background Frame("gui/button/slot_idle_background.png", Borders(14, 14, 14, 14), tile=False)
    padding (0, 0, 0, 0)
    activate_sound None

style premium_notebook_slot_title is default:
    font premium_body_font
    size premium_ss(16)
    color "#111111"
    outlines []
    xmaximum premium_sx(208)

style premium_notebook_slot_time is default:
    font premium_name_font
    size premium_ss(19)
    color "#FFFFFF"
    outlines [(1, "#000000", 0, 0)]

style premium_notebook_empty_text is default:
    font premium_name_font
    size premium_ss(24)
    color "#555555"
    outlines []

style premium_notebook_blank_close is button:
    background None
    hover_background None
    activate_background None
    padding (0, 0, 0, 0)
    activate_sound None

style premium_viewport is default:
    xfill True

style premium_page_header is default:
    padding (premium_sx(22), premium_sy(18), premium_sx(22), premium_sy(18))
    background Frame("gui/frame.png", Borders(12, 12, 12, 12), tile=False)

style premium_page_label_button is button:
    xminimum premium_sx(280)
    padding (premium_sx(18), premium_sy(10), premium_sx(18), premium_sy(10))
    background Frame("gui/button/idle_background.png", Borders(10, 10, 10, 10), tile=False)
    hover_background Frame("gui/button/hover_background.png", Borders(10, 10, 10, 10), tile=False)

style premium_page_label_text is input:
    font premium_body_font
    size premium_ss(24)
    color "#111111"
    xalign 0.5
    text_align 0.5

style premium_page_button is button:
    padding (premium_sx(14), premium_sy(10), premium_sx(14), premium_sy(10))
    background Frame("gui/button/idle_background.png", Borders(10, 10, 10, 10), tile=False)
    hover_background Frame("gui/button/hover_background.png", Borders(10, 10, 10, 10), tile=False)

style premium_page_button_text is button_text:
    font premium_body_font
    size premium_ss(20)
    color "#111111"
    hover_color "#7A7A7A"
    outlines []

style premium_slot_button is button:
    xsize premium_sx(376)
    ysize premium_sy(248)
    padding (0, 0, 0, 0)
    background Frame("gui/button/slot_idle_background.png", Borders(14, 14, 14, 14), tile=False)
    hover_background Frame("gui/button/slot_hover_background.png", Borders(14, 14, 14, 14), tile=False)

style premium_slot_overlay is default:
    xpos premium_sx(16)
    ypos premium_sy(166)
    xsize premium_sx(344)
    ysize premium_sy(66)
    padding (premium_sx(14), premium_sy(8), premium_sx(14), premium_sy(8))
    background Frame("gui/frame.png", Borders(10, 10, 10, 10), tile=False)

style premium_slot_time is default:
    font premium_body_font
    size premium_ss(18)
    color "#111111"
    outlines []

style premium_slot_name is default:
    font premium_name_font
    size premium_ss(20)
    bold False
    color "#000000"
    outlines []

style premium_tab_button is button:
    padding (premium_sx(20), premium_sy(12), premium_sx(20), premium_sy(12))
    background Frame("gui/button/idle_background.png", Borders(10, 10, 10, 10), tile=False)
    hover_background Frame("gui/button/hover_background.png", Borders(10, 10, 10, 10), tile=False)
    insensitive_background Frame("gui/button/idle_background.png", Borders(10, 10, 10, 10), tile=False)
    selected_insensitive_background Frame("gui/button/idle_background.png", Borders(10, 10, 10, 10), tile=False)

style premium_tab_button_text is button_text:
    font premium_body_font
    size premium_ss(22)
    color "#111111"
    hover_color "#7A7A7A"
    insensitive_color "#666666"
    selected_insensitive_color "#666666"
    outlines []

style premium_pref_card is default:
    xfill True
    padding (premium_sx(28), premium_sy(24), premium_sx(28), premium_sy(24))
    background Frame("gui/frame.png", Borders(14, 14, 14, 14), tile=False)

style premium_pref_title is default:
    font premium_name_font
    size premium_ss(30)
    bold False
    color "#000000"
    outlines []

style premium_pref_label is default:
    font premium_body_font
    size premium_ss(22)
    color "#111111"

style premium_pref_body is default:
    font premium_body_font
    size premium_ss(22)
    color "#111111"
    line_spacing premium_sy(6)

style premium_pref_status is default:
    font premium_name_font
    size premium_ss(18)
    color "#6A5A50"
    outlines []

style premium_pref_button is button:
    padding (premium_sx(18), premium_sy(14), premium_sx(18), premium_sy(14))
    background Frame("gui/button/idle_background.png", Borders(10, 10, 10, 10), tile=False)
    hover_background Frame("gui/button/hover_background.png", Borders(10, 10, 10, 10), tile=False)

style premium_pref_button_text is button_text:
    font premium_body_font
    size premium_ss(22)
    color "#111111"
    hover_color "#7A7A7A"
    outlines []

style premium_pref_toggle_mark is default:
    font premium_symbol_font
    size premium_ss(28)
    color "#111111"
    outlines []

style premium_slider is bar:
    ysize premium_sy(30)

style premium_story_history_backdrop_button is button:
    xfill True
    yfill True
    padding (0, 0, 0, 0)
    background Solid("#FFFFFF66")
    hover_background Solid("#FFFFFF66")

style premium_story_history_panel is default:
    xfill True
    yfill True
    padding (premium_sx(36), premium_sy(30), premium_sx(28), 0)
    background None

style premium_story_history_viewport is default:
    xfill True
    yfill True

style premium_story_history_entry is default:
    xfill True
    padding (premium_sx(20), premium_sy(16), premium_sx(20), premium_sy(16))
    background None

style premium_story_history_name is default:
    font premium_name_font
    size premium_ss(34)
    bold False
    color "#111111"
    outlines []

style premium_story_history_text is default:
    font premium_body_font
    size premium_ss(29)
    color "#111111"
    line_spacing premium_sy(10)
    outlines []

style premium_history_card is default:
    xfill True
    padding (premium_sx(24), premium_sy(20), premium_sx(24), premium_sy(20))
    background Frame("gui/frame.png", Borders(12, 12, 12, 12), tile=False)

style premium_history_name is default:
    font premium_name_font
    size premium_ss(26)
    bold False
    color "#000000"
    outlines []

style premium_history_text is default:
    font premium_body_font
    size premium_ss(23)
    color "#111111"
    line_spacing premium_sy(6)

style premium_info_card is default:
    xfill True
    padding (premium_sx(28), premium_sy(24), premium_sx(28), premium_sy(24))
    background Frame("gui/frame.png", Borders(14, 14, 14, 14), tile=False)

style premium_help_key is default:
    font premium_body_font
    xminimum premium_sx(220)
    size premium_ss(24)
    bold False
    color "#000000"
    outlines []

style premium_help_desc is default:
    font premium_body_font
    size premium_ss(22)
    color "#111111"
    line_spacing premium_sy(2)

style premium_gallery_thumb is button:
    xsize premium_sx(360)
    ysize premium_sy(220)
    padding (0, 0, 0, 0)
    background Frame("gui/button/slot_idle_background.png", Borders(14, 14, 14, 14), tile=False)
    hover_background Frame("gui/button/slot_hover_background.png", Borders(14, 14, 14, 14), tile=False)

style premium_gallery_title is default:
    font premium_name_font
    size premium_ss(22)
    bold False
    color "#000000"
    outlines []

style premium_gallery_status is default:
    font premium_body_font
    size premium_ss(16)
    color "#111111"

style premium_viewer_frame is default:
    xalign 0.5
    yalign 0.52
    xsize premium_sx(1560)
    ysize premium_sy(920)
    padding (premium_sx(26), premium_sy(24), premium_sx(26), premium_sy(24))
    background Frame("gui/frame.png", Borders(18, 18, 18, 18), tile=False)

style premium_chapter_frame is default:
    xalign 0.5
    yalign 0.5
    xsize premium_sx(900)
    ysize premium_sy(220)
    padding (premium_sx(40), premium_sy(30), premium_sx(40), premium_sy(30))
    background Frame("gui/frame.png", Borders(16, 16, 16, 16), tile=False)

style premium_chapter_title is default:
    font premium_name_font
    size premium_ss(56)
    bold True
    color "#fff8f3"
    xalign 0.5
    text_align 0.5
    outlines [(2, "#764954", 0, 0)]

style premium_chapter_subtitle is default:
    font premium_ui_font
    size premium_ss(24)
    color "#ead3c7"
    xalign 0.5
    text_align 0.5

style premium_song_player_hitbox is button:
    background None
    hover_background None
    padding (0, 0, 0, 0)
    activate_sound None

style premium_song_player_panel_hitbox is premium_song_player_hitbox:
    activate_sound "audio/song_player_panel_click.ogg"

style premium_song_player_strip_title is default:
    font premium_name_font
    size premium_ss(16)
    color "#111111"
    outlines []

style premium_song_player_panel_title is default:
    font premium_name_font
    size premium_ss(21)
    color "#111111"
    outlines []

style premium_song_player_panel_artist is default:
    font premium_ui_font
    size premium_ss(18)
    color "#444444"
    outlines []

style premium_song_player_progress_text is default:
    font premium_ui_font
    size premium_ss(16)
    color "#222222"
    outlines []

style premium_song_player_icon_text is default:
    font premium_ui_font
    size premium_ss(17)
    color "#222222"
    outlines []
    text_align 0.5

style premium_song_player_track_button is button:
    xfill True
    background None
    hover_background None
    padding (0, 0, 0, 0)
    activate_sound None

style premium_song_player_panel_track_button is premium_song_player_track_button:
    activate_sound "audio/song_player_panel_click.ogg"

style premium_song_player_track_title is default:
    font premium_name_font
    size premium_ss(18)
    color "#111111"
    outlines []

style premium_song_player_track_artist is default:
    font premium_ui_font
    size premium_ss(14)
    color "#444444"
    outlines []

style premium_song_player_track_cover_title is default:
    font premium_name_font
    size premium_ss(16)
    color "#111111"
    outlines []
    text_align 0.5
    xalign 0.5


