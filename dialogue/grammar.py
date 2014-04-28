import collections

""" The grammar/token expander takes generic tokens and expands them into
    appropriate words or sentences. With the exception of hard coded plot based
    dialogue lines, it's this system which decides what gets said.

    Grammar entries generally should not include a long list of synonyms; that
    falls more under the purview of _how_ a thing is said, and therefore should
    be included in the personalizer.

"""

#
# Uppercase tokens should expand to a complete sentence
# Lowercase tokens should not
# A standard offer token is generally the context tags of the offer separated
#  by underspaces.
# A standard reply token is generally two offer tokens separated by a colon.
#

def absorb( gram, othergram ):
    for k,v in othergram.iteritems():
        if k not in gram:
            gram[k] = list()
        gram[k] += v

def base_grammar( pc, npc, explo ):
    # Build a default grammar with the required elements.
    mygram = collections.defaultdict(list)
    absorb( mygram, GRAM_DATABASE )
    mygram["[pc]"].append( str( pc ) )
    mygram["[npc]"].append( str( npc ) )
    mygram["[scene]"].append( str( explo.scene ) )
    mygram["[city]"].append( str( explo.camp.current_root_scene() ) )

    return mygram

GRAM_DATABASE = {
    "[acquaintance]": ["friend","brother","sister","cousin","lover","priest",
        "aunt","uncle","father","mother","guildmate","apprentice","teacher"
        ],
    "[adjective]": ["[positive_adjective]","[negative_adjective]","[neutral_adjective]"
        ],
    "[BESTWISHES]": ["May fortune smile on you."
        ],
    "[GOODLUCK]": ["Good luck with that.","Good luck.",
        "Good luck. [BESTWISHES]",
        ],
    "[HELLO]": ["Hello.","Hello [pc]."
        ],
    "[HELLO_INFO]": ["[HELLO] Do you want to know something useful?",
        "You look like the curious type. Would you like to know something?",
        "They say that information is the greatest weapon. I have something you may want to know."
        ],
    "[HELLO_INFO_PERSONAL]": [ "I have a secret. I'm not sure I should be saying this, but..."
        ],
    "[HELLO_INFO:INFO]": [ "Alright, tell me about it.",
        ],
    "[HELLO:INFO_PERSONAL]": [ "What's the matter?",
        ],
    "[HELLO:INFO]": [ "I am looking for information.",
        ],
    "[HELLO_MISC]": ["[HELLO]","[HELLO] [HOWAREYOU]", "[HELLO] [RUMOUR]"
        ],
    "[HELLO_SERVICE]": [ "Welcome to [scene].",
        "[HELLO] Can I help you with anything?"
        ],
    "[HELLO_SERVICE_INN]": [ "[HELLO_SERVICE]",
        "Welcome to [scene]. Are you planning to stay the night?"
        ],
    "[HELLO_SERVICE_HEALING]": [ "[HELLO_SERVICE]",
        "Welcome to the temple. Do you need any healing?"
        ],
    "[HELLO:SERVICE]": [ "I need your services.",
        ],
    "[HELLO:SERVICE_INN]": [ "I would like to book a room.",
        "We need to rest here for the night."
        ],
    "[HELLO:SERVICE_HEALING]": [ "[HELLO:SERVICE]",
        "We need some healing."
        ],
    "[HELLO_SHOP]": [ "Welcome to my store.", "Welcome to [scene].",
        "[HELLO] Do you need to buy anything?", "Welcome to [scene]. [RUMOUR]",
        "Welcome to [scene]. [HOWAREYOU]",
        ],
    "[HELLO_SHOP_BLACKMARKET]": [ "[HELLO_SHOP]",
        "Looking for something out of the ordinary? I have it all right here, and I promise you will not find it anywhere else.",
        ],
    "[HELLO_SHOP_GENERAL]": [ "[HELLO_SHOP]",
        "Whatever you need, I probably have it in stock. If you do not see it right now, come back tomorrow.",
        ],
    "[HELLO_SHOP_MAGIC]": [ "[HELLO_SHOP]",
        "[HELLO] We have a fine supply of magic goods.",
        ],
    "[HELLO_SHOP_WEAPON]": [ "[HELLO_SHOP]",
        "Looking for a new [weapon]? I have just what you need.",
        "[HELLO] I have the best weapons in [city]."
        ],
    "[HELLO:SHOP]": [ "I would like to see your wares.",
        "Shall we barter?"
        ],
    "[HELLO:SHOP_BLACKMARKET]": [ "[HELLO:SHOP]",
        "I will take a look at your wares.",
        "Show me the good stuff."
        ],
    "[HELLO:SHOP_GENERAL]": [ "[HELLO:SHOP]",
        "We could use some new equipment.",
        "I need to buy something"
        ],
    "[HELLO:SHOP_MAGIC]": [ "[HELLO:SHOP]",
        "I need some new [magicgoods].",
        ],
    "[HELLO:SHOP_WEAPON]": [ "[HELLO:SHOP]",
        "I need a new [weapon].",
        ],
    "[HELLO_TRAINING]": [ "[HELLO] You look like you could use some training.",
        ],
    "[HELLO_TRAINING:TRAINING]": [ "[HELLO:TRAINING]",
        "Can you teach me?"
        ],
    "[HELLO:TRAINING]": [ "I was wondering if you could train me.",
        ],
    "[HOWAREYOU]": ["How are you doing?","I trust your adventure is going well."
        ],
    "[magicgoods]": ["spells","potions","scrolls","magic"],
    "[monster]": ["beast","demon","dragon","giant","goblin","ghost","monster"
        ],
    "[monsters]": ["beasts","demons","dragons","giants","goblins","ghosts",
        "monsters"
        ],
    "[negative_adjective]": ["awful","bad","creepy","dour","execrable","foolish",
        "ghastly","hideous","ineffectual","lazy","malodorous","sad","accursed",
        "vicious","ugly","pathetic"
        ],
    "[neutral_adjective]": [ "red","orange", "yellow", "blue", "green", "purple",
        "brown", "grey", "pink", "black", "white", "big", "small", "old", "young",
        "hot","cold","warm","cool",
        ],
    "[pc]": ["[positive_adjective] adventurers", "adventurers"
        ],
    "[positive_adjective]": ["awesome","beautiful","bold","brave","cheerful",
        "good","happy","incredible","just","noble","perfect","smart", "virtuous",
        "gentle"
        ],
    "[RUMOUR]": [ "My [acquaintance] [verbed] a [thing].",
        ],
    "[rumourleadin]": [ "I heard that", "I think that", "As far as I know",
        "My [acquaintance] said that", "You should know", "It seems that",
        "They say that","They say","Someone told me that","I believe",
        "It is rumored that","People say that","Everyone knows that",
        "Everyone says that","I heard a rumor that","I heard someone say that",
        "You may have heard that","It is common knowledge that",
        "It has been said that","I often hear that","Someone said that",
        "In my opinion,","In my humble opinion,"
        ],
    "[SERVICE_INN]": [ "", "I will get a room prepared for you right away.",
        ],
    "[SERVICE_TEMPLE]": [ "", "Remember that it is better to give than to receive, which is why we insist that you pay up front.",
        ],
    "[SHOP]": [ "", "Take a look around. Let me know if you need any help."
        ],
    "[SHOP_GENERAL]": [ "[SHOP]","Remember, you get what you pay for."
        ],
    "[SHOP_MAGIC]": [ "[SHOP]","Knowledge is power. Some knowledge is more powerful than others.",
        "Look through the [magicgoods]. Prices should be marked.",
        ],
    "[SHOP_WEAPON]": [ "[SHOP]","You will be happy to own a good [weapon] the next time you see a [monster].",
        ],
    "[thing]": [ "[weapon]","[monster]","[adjective] [monster]"
        ],
    "[TRAINING]": [ "", "Let me show you how it is done."
        ],
    "[verbed]": ["saw","fought","bought","found","married","made","discovered",
        "wrestled","visited","remembered","painted", "rescued"
        ],
    "[weapon]": [ "weapon", "sword", "axe", "bow", "mace", "staff", "spear"
        ],
    }




