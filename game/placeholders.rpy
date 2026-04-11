init python:
    def _placeholder_bg(filename, color):
        return ConditionSwitch(
            "renpy.loadable('%s')" % filename,
            Transform(
                filename,
                fit="cover",
                xysize=(config.screen_width, config.screen_height),
            ),
            "True",
            Solid(color, xysize=(config.screen_width, config.screen_height)),
        )

    def _placeholder_sprite(filename, color):
        scale = float(config.screen_height) / 1080.0
        return ConditionSwitch(
            "renpy.loadable('%s')" % filename,
            filename,
            "True",
            Solid(color, xysize=(int(round(720 * scale)), config.screen_height)),
        )

init:
    image bg dream = _placeholder_bg("images/bg_dream.png", "#18222f")
    image bg dream2 = _placeholder_bg("images/bg_dream2.png", "#223247")
    image bg dream3 = _placeholder_bg("images/bg_dream3.png", "#2c425d")
    image bg dream4 = _placeholder_bg("images/bg_dream4.png", "#364f6b")
    image bg dream5 = _placeholder_bg("images/bg_dream5.png", "#415d7a")
    image bg dream6 = _placeholder_bg("images/bg_dream6.png", "#4c6b89")

    image bg goodmorning = _placeholder_bg("images/bg_goodmorning.png", "#f7d9b9")
    image bg goodmorning2 = _placeholder_bg("images/bg_goodmorning2.png", "#f4d3b0")
    image bg goodmorning3 = _placeholder_bg("images/bg_goodmorning3.png", "#f1cda7")
    image bg goodmorning4 = _placeholder_bg("images/bg_goodmorning4.png", "#eec89f")
    image bg goodmorning5 = _placeholder_bg("images/bg_goodmorning5.png", "#ebc296")
    image bg goodmorning6 = _placeholder_bg("images/bg_goodmorning6.png", "#e8bc8d")
    image bg room = _placeholder_bg("images/bg_room.png", "#d7c7b6")
    image bg livingroom = _placeholder_bg("images/bg_livingroom.png", "#d9d1c7")
    image bg imouto_on_sofa = _placeholder_bg("images/bg_imouto_on_sofa.png", "#e6d7d0")
    image bg imouto_back = _placeholder_bg("images/bg_imouto_back.png", "#d6c6c0")
    image breakfast = _placeholder_bg("images/breakfast.png", "#f2e0b8")

    image imouto_surprised = _placeholder_sprite("images/imouto_surprised.png", "#f5cad6")
    image imouto_surprised2 = _placeholder_sprite("images/imouto_surprised2.png", "#f2c3d1")
    image imouto_awkward = _placeholder_sprite("images/imouto_awkward.png", "#efbfd0")
    image imouto_shy = _placeholder_sprite("images/imouto_shy.png", "#e9b5ca")

    image imouto_back_face = Solid("#dcb6c4")
    image imouto_back_face2 = Solid("#d6aebe")
    image imouto_back_face3 = Solid("#d0a6b8")
    image imouto_back_mad = Solid("#ca9eb2")

    image imouto_sofa_mad = Solid("#dcb8c1")
    image imouto_sofa_shy = Solid("#e2c1cb")
    image imouto_sofa_shy2 = Solid("#e6c9d1")
    image imouto_sofa_shy3 = Solid("#ead1d7")
    image imouto_sofa_shy4 = Solid("#eed9dd")
    image imouto_sofa_shy5 = Solid("#f2e1e4")
    image imouto_sofa_shy6 = Solid("#f6e9eb")
