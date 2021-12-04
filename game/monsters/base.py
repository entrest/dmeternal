from .. import characters
from .. import stats
from .. import image
from .. import items
import random
from .. import spells
from .. import context

# NPC CLASSES

class Peasant( characters.Level ):
    name = 'Peasant'
    desc = ''
    requirements = {}
    statline = stats.StatMod( { stats.PHYSICAL_ATTACK: 3, stats.NATURAL_DEFENSE: 3,
        stats.MAGIC_ATTACK: 3, stats.MAGIC_DEFENSE: 3, stats.AWARENESS: 4} )
    HP_DIE = 6
    MP_DIE = 4
    XP_VALUE = 50
    legal_equipment = ( items.MACE, items.DAGGER, items.STAFF, \
        items.BOW, items.ARROW, items.SHIELD, items.SLING, \
        items.BULLET, items.CLOTHES, items.HAT, \
        items.GLOVE, items.SANDALS, items.SHOES, items.BOOTS, items.CLOAK )
    starting_equipment = (items.clothes.PeasantGarb,items.maces.Club)
    TAGS = (context.GEN_KINGDOM,)

class Merchant( characters.Level ):
    name = 'Merchant'
    desc = ''
    requirements = { stats.INTELLIGENCE: 7, stats.CHARISMA: 7 }
    statline = stats.StatMod( { stats.PHYSICAL_ATTACK: 4, stats.NATURAL_DEFENSE: 4,
        stats.MAGIC_ATTACK: 3, stats.MAGIC_DEFENSE: 4, stats.AWARENESS: 4} )
    HP_DIE = 8
    MP_DIE = 4
    XP_VALUE = 100
    legal_equipment = ( items.SWORD, items.AXE, items.MACE, items.DAGGER, items.STAFF, \
        items.BOW, items.ARROW, items.SLING, \
        items.BULLET, items.CLOTHES, items.HAT, \
        items.GLOVE, items.SANDALS, items.SHOES, \
        items.BOOTS, items.CLOAK, items.WAND )
    starting_equipment = (items.clothes.MerchantGarb,items.daggers.Dirk)
    FRIENDMOD = {characters.Thief: -3, characters.Ninja: -3}
    TAGS = (context.GEN_KINGDOM,)

class Innkeeper( characters.Level ):
    name = 'Innkeeper'
    desc = ''
    requirements = { stats.PIETY: 7, stats.CHARISMA: 7 }
    statline = stats.StatMod( { stats.PHYSICAL_ATTACK: 4, stats.NATURAL_DEFENSE: 4,
        stats.MAGIC_ATTACK: 3, stats.MAGIC_DEFENSE: 4, stats.AWARENESS: 4} )
    HP_DIE = 8
    MP_DIE = 4
    XP_VALUE = 100
    legal_equipment = ( items.SWORD, items.AXE, items.MACE, items.DAGGER, items.STAFF, \
        items.BOW, items.ARROW, items.SLING, \
        items.BULLET, items.CLOTHES, items.HAT, \
        items.GLOVE, items.SANDALS, items.SHOES, \
        items.BOOTS, items.CLOAK, items.WAND )
    starting_equipment = (items.clothes.NormalClothes,items.daggers.Dirk)

# UNLISTED NPC CLASSES

class Elder( characters.Level ):
    name = 'Elder'
    desc = 'The person will will probably give you a quest or something.'
    requirements = { stats.TOUGHNESS: 8, stats.REFLEXES: 8, stats.INTELLIGENCE: 13, stats.PIETY: 13, stats.CHARISMA: 13 }
    statline = stats.StatMod( { stats.PHYSICAL_ATTACK: 3, stats.MAGIC_ATTACK: 5, stats.MAGIC_DEFENSE: 5, \
        stats.NATURAL_DEFENSE: 5, stats.AWARENESS: 3 } )
    spell_circles = ( spells.SOLAR, spells.FIRE, spells.AIR, spells.WATER, spells.EARTH )
    HP_DIE = 4
    MP_DIE = 16
    LEVELS_PER_GEM = 1
    GEMS_PER_AWARD = 2
    legal_equipment = ( items.STAFF, items.CLOTHES, \
        items.GLOVE, items.SANDALS, items.SHOES, \
        items.BOOTS, items.CLOAK )
    starting_equipment = ( items.staves.Quarterstaff, items.clothes.MageRobe )


# MONSTER CLASSES

class Humanoid( characters.Level ):
    name = 'Humanoid'
    desc = ''
    statline = stats.StatMod( { stats.PHYSICAL_ATTACK: 4, stats.NATURAL_DEFENSE: 4,
        stats.MAGIC_ATTACK: 4, stats.MAGIC_DEFENSE: 3, stats.AWARENESS: 3} )
    HP_DIE = 8
    MP_DIE = 8
    XP_VALUE = 100
    FULL_HP_AT_FIRST = False


class Spellcaster( characters.Level ):
    name = 'Spellcaster'
    desc = ''
    statline = stats.StatMod( { stats.PHYSICAL_ATTACK: 3, stats.NATURAL_DEFENSE: 4,
        stats.MAGIC_ATTACK: 5, stats.MAGIC_DEFENSE: 4, stats.AWARENESS: 3} )
    HP_DIE = 4
    MP_DIE = 12
    XP_VALUE = 100
    FULL_HP_AT_FIRST = False

class Beast( characters.Level ):
    name = 'Beast'
    desc = ''
    statline = stats.StatMod( { stats.PHYSICAL_ATTACK: 5, stats.NATURAL_DEFENSE: 4,
        stats.MAGIC_ATTACK: 3, stats.MAGIC_DEFENSE: 3, stats.AWARENESS: 4} )
    HP_DIE = 10
    MP_DIE = 6
    XP_VALUE = 115
    FULL_HP_AT_FIRST = False

class Terror( characters.Level ):
    name = 'Monster'
    desc = ''
    statline = stats.StatMod( { stats.PHYSICAL_ATTACK: 5, stats.NATURAL_DEFENSE: 4,
        stats.MAGIC_ATTACK: 5, stats.MAGIC_DEFENSE: 4, stats.AWARENESS: 4} )
    HP_DIE = 10
    MP_DIE = 10
    XP_VALUE = 200

class Leader( characters.Level ):
    name = 'Leader'
    desc = ''
    statline = stats.StatMod( { stats.PHYSICAL_ATTACK: 5, stats.NATURAL_DEFENSE: 4,
        stats.MAGIC_ATTACK: 4, stats.MAGIC_DEFENSE: 5, stats.AWARENESS: 4} )
    HP_DIE = 8
    MP_DIE = 8
    XP_VALUE = 175


class Defender( characters.Level ):
    name = 'Defender'
    desc = ''
    statline = stats.StatMod( { stats.PHYSICAL_ATTACK: 4, stats.NATURAL_DEFENSE: 5,
        stats.RESIST_FIRE: 4, stats.RESIST_COLD: 4, stats.RESIST_LIGHTNING: 4, stats.RESIST_ACID: 4,
        stats.MAGIC_ATTACK: 4, stats.MAGIC_DEFENSE: 4, stats.AWARENESS: 3} )
    HP_DIE = 12
    MP_DIE = 6
    XP_VALUE = 150

class Undead( characters.Level ):
    name = 'Undead'
    desc = ''
    statline = stats.StatMod( { stats.PHYSICAL_ATTACK: 3, stats.NATURAL_DEFENSE: 4,
        stats.MAGIC_ATTACK: 4, stats.MAGIC_DEFENSE: 3, stats.AWARENESS: 3} )
    HP_DIE = 12
    MP_DIE = 8
    XP_VALUE = 125
    FULL_HP_AT_FIRST = False


# Monster Monster Monster Monster Monster

class NPCharacter( characters.Character ):
    """The only difference? NPCs don't get saving grace until -10HP."""
    def is_dead( self ):
        return not self.is_alright()
    @property
    def ENC_LEVEL( self ):
        return self.rank()


class Monster( NPCharacter ):
    SPRITENAME = "monster_default.png"
    statline = { stats.STRENGTH: 12, stats.TOUGHNESS: 12, stats.REFLEXES: 12, \
        stats.INTELLIGENCE: 12, stats.PIETY: 12, stats.CHARISMA: 12 }
    ATTACK = None
    MOVE_POINTS = 10
    ENC_LEVEL = 1
    TECHNIQUES = ()
    TREASURE = None

    def __init__( self, team = None ):
        statline = self.statline.copy()
        super(Monster, self).__init__( name=self.name, statline=statline )
        self.team = team
        self.techniques += self.TECHNIQUES
        if self.TREASURE:
            self.TREASURE( self )
        self.init_monster()
        for t in range( random.randint(1,4) ):
            self.statline[ random.choice( stats.PRIMARY_STATS ) ] += 1

    def init_monster( self ):
        """Initialize this monster's levels."""
        pass

    def generate_avatar( self ):
        # Generate an image for this character.
        return image.Image( self.SPRITENAME, frame_width = 54, frame_height = 54 )

    def desc( self ):
        return "L"+str( self.rank())+" "+str(self.mr_level)

    def get_move( self ):
        return self.MOVE_POINTS


