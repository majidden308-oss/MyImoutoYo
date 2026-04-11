# 游戏的脚本可置于此文件中。

# 声明此游戏使用的角色。颜色参数可使角色姓名着色。

define i = Character("莫莉")
define d = Character("？？？")
define m = Character("莫于")
define q = Character("秋香姐")
define c = Character("春阳哥")

init python:
    def safe_play(filename, channel="sound", fadein=0.0):
        if renpy.loadable(filename) or renpy.loadable("audio/" + filename):
            renpy.music.play(filename, channel=channel, fadein=fadein)

label splashscreen:
    return

default opening_op_played = False
default opening_op_phase = "idle"

label before_main_menu:
    return

transform shake_screen:                  #震动模块
    xoffset -10
    linear 0.05 xoffset 10
    linear 0.05 xoffset -10
    linear 0.05 xoffset 8
    linear 0.05 xoffset -6
    linear 0.05 xoffset 4
    linear 0.05 xoffset 0

transform dream_float:
    subpixel True
    xalign 0.5
    yalign 0.5
    alpha 0.94
    ease 3.6 alpha 0.99
    ease 3.2 alpha 0.93
    repeat

transform dream_far_float:
    subpixel True
    xalign 0.5
    yalign 0.5
    alpha 0.9
    ease 4.0 alpha 0.97
    ease 3.4 alpha 0.9
    repeat

transform dream_whiteout:
    subpixel True
    xalign 0.5
    yalign 0.5
    alpha 0.9
    ease 2.2 alpha 1.0

define fade = Fade(0.5, 0.0, 0.5, color="#FFFFFF")
define dream_scene_transition = Fade(0.35, 0.0, 0.35, color="#FFFFFF")


# 游戏在此开始。

label start:

    $ renpy.music.stop(channel="main_menu_player", fadeout=0.12)

    $ persistent.menu_companion_first_memory_started = True
    $ renpy.save_persistent()

    ## ====【新增】开场动画序列 ====
    ## 添加了游戏开场动画，提升游戏的仪式感和沉浸感
    
    # 1. 黑色背景开始，然后显示游戏标题
    scene black
    show text "本游戏由Mori及其团队制作" with dissolve
    pause 1.5
    hide text with dissolve
    
    # 2. 显示游戏简介，让玩家了解故事主题
    show text "本游戏不用于商业用途，单纯为爱发电" with dissolve
    pause 2.0
    hide text with dissolve
    
    # 3. 显示制作人员信息
    show text "感谢您喜欢我们做的游戏！" with dissolve
    pause 1.5
    hide text with dissolve
    
    ## ====【转场】进入游戏正篇 ====
    # 使用淡入效果切换到第一个游戏场景
    window hide

    scene bg dream6
    with dream_scene_transition
    $ premium_gallery_unlock("bg dream6")

    $ safe_play("bgm_dream_healing.oga", channel="music", fadein=1.8)

    pause 0.2

    "......"

    "......"

    "意识像沉进了一片没有尽头的白。"

    "看不见天空，也看不见地面，四周空旷得听不见任何声音，只有某种近乎静止的光，在视野深处缓慢地流淌。"

    "我仿佛漂浮着，又像是在下坠。身体失去了重量，连时间都被拉得很长、很慢，像一滴迟迟不肯坠落的水。"

    scene bg dream
    with dream_scene_transition
    $ premium_gallery_unlock("bg dream")

    "朦胧的白光深处，渐渐浮现出一个人的轮廓。"

    "那身影纤细而安静，像是从雾里生长出来的一样，带着一种不真实的透明感。"

    "她站在那里，离我并不算远，却又像隔着一整个无法触及的彼岸。"

    scene bg dream2
    with dream_scene_transition

    d "想让你牵起我的手，可以吗"

    "那声音很轻，轻得像羽毛拂过耳侧。"

    "明明近在咫尺，却又像是从极遥远的地方传来，带着一点迟疑，一点羞怯，还有一种说不出的寂寞。"

    scene bg dream3
    with dream_scene_transition
    $ premium_gallery_unlock("bg dream3")

    "女孩的面庞像浸在一层将散未散的薄雾里。"

    "我努力想要看清她的模样，想辨认她低垂的眼睫、微启的唇角，甚至想确认她此刻是否真的在注视着我。"

    "可每当视线试图靠近，那层雾便会无声地漾开，像水面上被轻轻拨乱的月影。"

    "明明什么都看不真切，却偏偏能够感受到她言语间那一丝藏不住的羞涩。"

    "那不是刻意伪装出来的柔弱，而更像一种静静沉在心底、连她自己都不敢轻易触碰的秘密。"

    "不知为何，仅仅只是听着她的声音，胸口便泛起一阵难以言说的悸动。"

    scene bg dream4
    with dream_scene_transition

    $ renpy.music.stop(channel="music", fadeout=1.0)
    $ safe_play("erming.mp3", fadein=0.5)

    "...?!"

    "正当我下意识想朝她伸出手时，眼前的世界却骤然扭曲。"

    "刺眼的光幕毫无征兆地自两人之间升起，像一层苍白而冰冷的水面，将她的身影隔绝在彼岸。"

    "那光并不炽热，却令人本能地感到战栗。"

    "周围的一切都开始失去重量。"

    "空气、声音、连同自己的呼吸，都像被浸泡在深海里一般，变得迟缓、沉闷而遥远。"

    "女孩仍站在那片白光之后，身影摇晃得像一场随时会碎裂的幻觉。"

    "我张了张口，想喊住她，想问她是谁，想问她为什么会露出那样悲伤的神情——"

    scene bg dream5
    with dream_scene_transition

    "可喉咙却像被什么无形的东西死死扼住。"

    "所有想说出口的话，都堵在胸腔里，化作灼热又刺痛的窒息感，怎么也无法穿过唇齿。"

    "这种感觉，像是被梦本身拒绝了一样。"

    "冷汗一点点从皮肤下渗出，后背泛起寒意，连指尖都开始发麻。"

    "意识却并没有因此变得清醒，反而像陷进更深、更厚的棉絮之中。"

    "越是挣扎，越是沉沦；越想靠近，身体就越发迟钝。"

    "内心明明焦急得几乎要裂开，四肢却仿佛不再属于自己。"

    "别说迈出一步，就连抬起手指，都像隔着一整场漫长而粘稠的梦。"

    "而那女孩，只是安静地站在光的另一端。"

    "她没有后退，也没有靠近。"

    "像是在等待着什么，又像是早已知道，我根本无法真正触碰到她。"

    scene bg dream6
    with dream_scene_transition

    "下一秒，一阵彻骨的凉意猝然攀上脊背。"

    "那寒意来得毫无预兆，像有什么冰冷的手指轻轻划过皮肤，又像整个人突然坠入了没有温度的深水之中。"

    "视野在那一瞬间被白光彻底吞没。"

    "她的身影、她的声音、那句轻得仿佛随时会消散的话语，全都在耀眼的纯白中迅速远去。"

    "世界失去了边界。"

    "而我，甚至来不及抓住那只本该伸向我的手。"

    window show

    d "哈喽？喂喂喂？还活着吗"

    scene bg goodmorning
    with Dissolve(1.5)
    $ premium_gallery_unlock("bg goodmorning")

    $ safe_play("bgm_morning_gymnopedie_no1.mp3", channel="music", fadein=2.2)

    m "啊..."

    d "明明窗户都拉开了欸，难道哥哥真的死了吗"

    "腹部感到像是被巨石压住，这是鬼压床吗？"

    scene bg goodmorning2
    with dissolve

    i "太阳晒屁股了，老哥"

    "是妹妹吗..."

    "不对！！"

    "我靠！！！"
    
    "我靠不对劲！！！"

    "我感到下体传来的一阵异样感"

    scene bg goodmorning3

    i "嗯？"

    "不妙。"

    "空气像是一下子冻结了。清晨微暖的光线还停在窗帘缝隙里，房间里却先一步漫开了某种说不清的尴尬。"
    "偏偏身体的异样感丝毫没有收敛，反而在这种沉默里被衬得更加鲜明。"

    scene bg goodmorning4
    with dissolve
    $ premium_gallery_unlock("bg goodmorning4")

    m "额...不，不是你想的那样，妹妹，你先听我解释。"

    "她像是被按下了暂停键，整个人僵在原地。"
    "那张原本就白净的脸一下子染上绯色，红晕从脸颊一路烧到耳根，连睫毛都像在细细发颤。"

    scene bg goodmorning5
    with dissolve

    i "原...原来，哥哥早上会是这种状态吗..."

    i "大早上的，还真是...兴致盎然呢。"

    "完了。"

    "被妹妹撞见这种场面，已经不是一句尴尬可以形容的了。"
    "再这样僵持下去，身为哥哥的威严大概会和理智一起当场蒸发。"

    "我几乎是条件反射般把左手探向一旁，试图在彻底失控之前把眼前这场灾难抢救回来。"

    scene bg goodmorning6
    with fade

    i "噫...！"

    "可惜，动作终究还是太明显了。"
    "那一瞬间，她的视线像被针扎到一样猛地一缩，整个人都跟着弹了起来。"

    scene bg room
    with dissolve
    $ premium_gallery_unlock("bg room")

    show imouto_surprised2:
        xpos 0.60
        ypos 130
        easeout 0.18 xpos 0.70
        easeout 0.06 xpos 0.68
        easeout 0.06 xpos 0.72
        easeout 0.06 xpos 0.69
        easeout 0.06 xpos 0.71
        easeout 0.08 xpos 0.70

    "床铺轻轻一陷又猛地回弹，她几乎是连滚带爬地退了出去。"
    "发尾在空中晃了一下，慌乱得像只受惊的小动物。"

    i "哥...哥哥你，果然还是忍耐不住了吗..."

    hide imouto_surprised2

    show imouto_awkward:
        xpos 0.70
        ypos 130
        easein 0.18 xpos 0.66
        easein 0.24 xpos 0.62

    "她一边后退，一边慌慌张张地把目光移开，像是连多看我一眼都会让脸更烫几分。"

    i "早，早饭已经做好了哦..."
    i "哥哥最近压力是不是太大了...总，总之先快点出来吃饭吧。"

    hide imouto_awkward

    show imouto_shy:
        xpos 0.62
        ypos 130
        easein 0.12 xpos 0.58
        easein 0.12 xpos 0.54
        easein 0.12 xpos 0.50
        easein 0.12 xpos 0.46

    "声音越说越小，到了后半句几乎快要埋进胸口。"

    i "我...我先去外面等你了。"

    show imouto_shy:
        xpos 0.46
        ypos 130
        easein 0.14 xpos -0.60

    $ safe_play("closedoor.mp3")
    pause 0.18
    hide imouto_shy

    $ safe_play("ohno!.mp3")

    "房门合上的那一刻，世界短暂地安静了一瞬。"
    "下一秒，脑袋里像是有什么东西轰然炸开。"

    show layer master at shake_screen

    "这下子，果然彻底完蛋了吧！！"

    "敬请期待后续"

    return

    scene bg room
    with fade

    $ safe_play("wearing.mp3")

    "弥漫着淡淡洗衣粉香气的制服紧贴在皮肤上，依旧可以感到衣服上残留的阳光温撒后的温暖"

    m "洗干净的衣服穿起来真舒服啊"

    $ safe_play("opendoor.mp3")

    "心里如此想着，咔嚓一声打开了通往客厅的门"

    scene bg livingroom
    with fade
    $ premium_gallery_unlock("bg livingroom")

    $ safe_play("bgm_love_her.ogg", channel="music", fadein=1.6)

    "客厅里静悄悄的。这是父母留下来的房子，一百多平的大小，两个人住绰绰有余"

    scene bg imouto_on_sofa
    with dissolve
    $ premium_gallery_unlock("bg imouto_on_sofa")

    "一个黑色短发的女孩正坐在沙发的一边，愣愣地发呆，脸上还留有一丝淡淡的红晕"

    "她穿着米白色居家睡衣，估计是为了行动方便吧，裙摆被设计得很短，白皙的双腿给沙发压出了一个弧度"

    "一个可爱的美少女就这么毫无防备的坐在沙发上，让人忍不住想..."

    scene bg imouto_back
    with fade
    $ premium_gallery_unlock("bg imouto_back")

    "小心翼翼地绕道沙发后面，少女仍未察觉到危险即将来临，盯着墙皮不知在想些什么"

    "两侧略鼓的脸颊白嫩光滑，不自觉地就像狠狠揉一把"

    scene imouto_back_face
    with dissolve

    i "啊！！"

    "少女的身体猛地震颤一下，明显被吓了一跳"

    scene imouto_back_face2

    i "你，你干嘛....!,呜啊...别，别捏了，别捏...我的脸...!"

    "女孩试图阻止我的行为，可惜作用不大"

    scene imouto_back_face3
    with dissolve

    i "停，停下！呜……啊啊~~"

    "她快哭出来了，啊哈，还是快点停手吧"

    scene imouto_back_mad
    with dissolve

    i "哼！快点去吃饭吧！废材老哥！！"

    m "好，好的"

    scene breakfast
    with fade
    $ premium_gallery_unlock("breakfast")

    "在一阵鸡飞狗跳之后，总算还是安稳地坐到了餐桌前。"

    "映入眼帘的是一份煎得恰到好处的荷包蛋。边缘微微焦黄，蛋黄却还柔润发亮，旁边搁着昨晚剩下的小米粥和一袋还带着热气的小笼包。"

    "不用想也知道，这些多半是莫莉一大早出门买回来的。"

    "明明平时总爱赖在沙发上装作提不起劲，一到了照顾人的时候，却又细心得过分。"

    scene bg imouto_on_sofa
    with dissolve

    "而那位辛苦准备早饭的当事人，此刻正缩在沙发另一头，捂着脸颊，一副气得不想看我的样子。"

    m "莫莉。"

    i "......"

    m "还在生气？"

    i "你说呢。"

    i "一大早就从背后捏女孩子的脸，哥哥是笨蛋，还是变态，还是没救了的超级大笨蛋？"

    m "这三个选项差别是不是有点小。"

    i "重点根本不在那里啦！"

    "她鼓着脸瞪我，偏偏脸颊还因为刚才那一通折腾泛着淡淡的红。那模样实在没什么威慑力，反倒更让人觉得可爱。"

    m "好啦，是我不对。为了赔罪，我把最大的那个小笼包让给你。"

    i "谁要这种小孩子才会高兴的补偿啊。"

    "嘴上这么说着，莫莉还是慢吞吞地挪了过来，在我对面坐下。"

    "之后的时间，便在小声拌嘴和碗筷碰撞的轻响里一点点过去。"

    scene bg livingroom
    with dissolve

    "等到最后一口粥也见了底，我长长舒了口气，整个人像被抽走骨头一样往沙发上一瘫。"

    m "呵……哈……"

    "吃撑了。"

    "满足感沿着胃袋一点点漫开，连手指都懒得再动一下。我揉着肚子，像只被太阳晒化的史莱姆似的陷进沙发里，还没忍住打了个大大的哈欠。"

    i "哼~吃饱了，果然就该睡觉了呢。"

    m "赞成。今天就让我和沙发相亲相爱到中午吧。"

    i "不行啦，老哥"

    scene bg imouto_on_sofa
    with dissolve

    "莫莉几步绕到我面前，双手在空中比划来比划去，像是在努力把某个无形的赖床精从我身上驱逐出去。"

    i "不是约好每天有空都要去春阳哥那里帮忙嘛？快点起来啦。"

    m "今天可是难得的休息日欸。"

    i "休息日又不是睡死日。"

    i "而且春阳哥和秋香姐平时照顾我们那么多，你再赖下去，我都要替你不好意思了。"

    "她说得理直气壮，反倒让我没法继续装死。"

    m "好啦，好啦。这就出门。"

    "我故意拖长语调，慢吞吞地从沙发上坐起身，抓起车钥匙朝门口走去。"

    scene bg room
    with fade

    "脚刚踏出门槛，我又像突然想起什么似的停住，往外挪了两步后猛地回过头。"

    "莫莉显然没跟上我的节奏，正站在客厅中央，带着一点茫然望着我。"

    m "嗯~莫莉要乖乖看家哦。"

    "说着，我抬手揉了揉她的脑袋。"

    i "都说了，我又不是小孩子啦！"

    "她下意识抬起双手，像是想拦住我，可动作做到一半又别扭地停住了，只能气鼓鼓地瞪着我。"

    m "拜拜~"

    i "这下倒是跑得挺快。拜拜啦。"

    "身后传来少女略带不满、却依旧很轻的回应。"

    i "拜拜。"

    scene expression Solid("#f5f1ea")
    with dissolve

    "春阳哥是家附近的邻居。"

    "他和妻子秋香姐一起开了家火锅店，似乎和父母从前也有些说不清的渊源。自从我和莫莉搬回这边住之后，没少受他们照顾。"

    "店里忙起来的时候，只要我有空，也会过去搭把手。"

    "当然，推辞不过的时候，工资和吃的也一样没少拿就是了。"

    "一路胡乱哼着不知名的小调，车轮碾过清晨还没完全热起来的街道。没过多久，熟悉的招牌就已经出现在视野里。"

    scene expression Solid("#f7f1ea")
    with dissolve

    "火锅店门口已经半开着门，里头飘出隐隐的香气。"

    "秋香姐正低着头对账，听见停车的声音，立刻抬起头来。"

    q "阳儿~小于来了。"

    "店里正擦桌子的男人闻声回头，正好和迎面走进来的我撞上视线。"

    c "在外面就别这么叫我了嘛。"

    c "喂，别傻站着，赶紧过来帮忙。"

    m "一大清早就抓人干活，今天可是久违的休息日欸。"

    "嘴上抱怨着，我还是自觉去拿了抹布。"

    c "你小子别不情愿。等干完了，我给你送点好东西。"

    m "难不成是新开发的火锅底料？"

    "春阳哥明显愣了一下。"

    c "哎哟，你怎么知道？惊喜感全没了。"

    m "这两天你不是一直把自己关在厨房里捣鼓东西吗。想不知道都难。"

    q "你别说，味道我先尝过了，是真的不错。"

    q "怎么样？帮完忙，包你和莫莉这几天的伙食。"

    m "好嘞。"

    scene expression Solid("#f4ede4")
    with dissolve

    "说是干活，其实工作量并不大。"

    "店里开张不久，桌椅虽然使用得勤，倒也远没脏到夸张的地步。更何况比起真正的劳动，这更像是一种心照不宣的照顾。"

    "擦到一半，秋香姐像是忽然想起什么，抬头问了我一句。"

    q "对了，莫莉最近身体怎么样？"

    "莫莉现在看着精神得很，可她以前身体一直不算好。"

    "上高中的时候，她甚至还在学校里晕倒过几次，后来没办法，只能先办了休学。那段时间我担心得不行，还偷偷去查过是不是有人欺负她。"

    "结果没有。单纯只是她自己的身体太差。"

    m "比前阵子好多了。"

    m "最近吃饭和作息都挺规律，精神也不错，就是还不太爱出门。"

    q "那就好。"

    q "不过那孩子总闷在家里也不是办法。你这个当哥哥的，空了还是得多带她出去走走。"

    m "知道了，秋香姐。"

    "没过多久，春阳哥把最后一张桌子也收拾利落，秋香姐则从柜台后拎出一个鼓鼓囊囊的大袋子。"

    q "来，拿好。"

    "被塞得满满当当的配菜和底料一下子压进手里，沉得我手腕都跟着往下一坠。"

    m "……怎么这么重？"

    m "秋香姐，你们这是打算把我们兄妹俩养成小肥猪吗？"

    q "行了，下一锅的料都给你配好了，够你们吃好几顿。你小子还挑上了。"

    c "别身在福中不知福啊。那底料可是我新调出来的。"

    m "听起来突然有点期待，又有点不祥。"

    q "家里芝麻酱这些蘸料还有吗？要不要再给你装点？"

    m "不用不用，我先回去了。"

    m "再晚点的话，总觉得家里那位会一边等我，一边鼓着脸生闷气。"

    c "啧。你这话怎么听着这么欠揍。"

    q "好了，快回去吧。路上小心。"

    m "那我走啦。"

    q "慢走哦~"

    c "喂！我还没说完呢！"

    "店里顿时笑成一片。我趁着春阳哥发作之前，拎着那一大袋火锅料，赶紧溜出了门。"

    scene expression Solid("#ebe7e2")
    with fade

    "一个人坐回电动车上时，周围忽然安静下来。"

    "我低头看了一眼挂在车钩上的包裹，心底没来由地浮起一种不真实的温热。像是曾经也有人这样替我张罗过一整天的吃食，替我把琐碎的日子一点点填满。"

    "下一秒，那感觉又像被什么轻轻拨了一下，化成一段朦胧的影子。"

    scene expression Solid("#f2f4ef")
    with Dissolve(1.0)

    "——小于，要让着妹妹哦。"

    "一个女人的声音浮现在脑海里，温柔得像隔着很远很远的雾。"

    "——不许再带着妹妹去做危险的事，知道吗？"

    "这次像是在责备，可落进耳朵里时，却依旧让人提不起半点害怕。"

    "还有另一个低沉的男声，锋利，却本能地让人觉得安心。"

    "——这次轮到小于选了。想去哪里玩？"

    "他们在叫谁？"

    "小于……是我吗？"

    "那妹妹又是谁？"

    "念头翻涌的下一瞬，脑中像有一道光突然闪过。"

    m "……莫莉。"

    m "啊，是莫莉啊。"

    scene expression Solid("#e6eee0")
    with fade

    "恍然抬头时，眼前正好是刚刚转绿的红灯。"

    $ safe_play("car_horn.mp3")

    "刺耳的鸣笛声在耳边炸开，我下意识捏紧了车把。"

    m "先过马路。"

    "车轮滚过斑马线，我却还是有些回不过神。"

    "明明刚才还只是普通地等着红灯，回过神来，时间却像被谁偷偷剪去了一截。"

    "难道真是今天起得太早了？"

    scene expression Solid("#e1ead8")
    with dissolve

    "电动车驶进一片树荫，穿林而过的风迎面扑来，也让发热的大脑稍微冷静了些。"

    "那两个人……大概是父母吧。"

    "可说实话，除了儿时那些已经淡得快要抓不住的轮廓外，他们在我之后的人生里出现得并不多。真要说的话，反倒是和莫莉相依为命的那些年，更像是我所熟悉的日常。"

    "既然如此，为什么偏偏会在这种时候，想起这种像梦一样的片段？"

    m "……唉。"

    "想得越多，脑袋越发沉了几分。"

    "算了。比起这些无从考证的旧影子，现在更重要的，还是赶快回家。"

    "毕竟，苦恼的时候，果然还是需要可爱的妹妹来治愈才行。"

    "我重新拧动车把，带着那一大袋火锅料，朝家的方向驶去。"

    return
