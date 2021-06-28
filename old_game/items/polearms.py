from .. import stats
from . import Item,Attack,POLEARM,LANCE


class Spear( Item ):
    true_name = "Spear"
    true_desc = ""
    itemtype = POLEARM
    avatar_image = "avatar_polearm.png"
    avatar_frame = 0
    attackdata = Attack( (1,8,0), element = stats.RESIST_PIERCING )
    mass = 90

class Trident( Item ):
    true_name = "Trident"
    true_desc = ""
    itemtype = POLEARM
    avatar_image = "avatar_polearm.png"
    avatar_frame = 18
    attackdata = Attack( (1,10,0), element = stats.RESIST_PIERCING )
    mass = 95

class Pike( Item ):
    true_name = "Pike"
    true_desc = "Longer than the average spear, this weapon is used to keep foes at a distance."
    itemtype = POLEARM
    avatar_image = "avatar_polearm.png"
    avatar_frame = 11
    attackdata = Attack( (1,8,0), double_handed=True, element=stats.RESIST_PIERCING, reach=2 )
    mass = 100

class Ranseur( Item ):
    true_name = "Ranseur"
    true_desc = "A long spear whose triple-pronged head may be used for parrying."
    itemtype = POLEARM
    avatar_image = "avatar_polearm.png"
    avatar_frame = 19
    attackdata = Attack( (1,8,0), double_handed=True, element=stats.RESIST_PIERCING, reach=2 )
    statline = stats.StatMod({ stats.PHYSICAL_DEFENSE: 5 })
    mass = 140

class Partisan( Item ):
    true_name = "Partisan"
    true_desc = "A long spear with three blades. It is often used by palace guards."
    itemtype = POLEARM
    avatar_image = "avatar_polearm.png"
    avatar_frame = 17
    attackdata = Attack( (1,10,0), double_handed=True, element=stats.RESIST_PIERCING, reach=2 )
    statline = stats.StatMod({ stats.PHYSICAL_DEFENSE: 10 })
    mass = 155

class Voulge( Item ):
    true_name = "Voulge"
    true_desc = ""
    itemtype = POLEARM
    avatar_image = "avatar_polearm.png"
    avatar_frame = 3
    attackdata = Attack( (1,10,0), double_handed = True, element = stats.RESIST_SLASHING )
    mass = 110

class Halbard( Item ):
    true_name = "Halbard"
    true_desc = ""
    itemtype = POLEARM
    avatar_image = "avatar_polearm.png"
    avatar_frame = 1
    attackdata = Attack( (1,12,0), double_handed = True, element = stats.RESIST_SLASHING, reach=2 )
    mass = 150

class Glaive( Item ):
    true_name = "Glaive"
    true_desc = ""
    itemtype = POLEARM
    avatar_image = "avatar_polearm.png"
    avatar_frame = 2
    attackdata = Attack( (2,6,0), double_handed = True, element = stats.RESIST_SLASHING, reach=2 )
    mass = 150


# Gonna stick the lances in here too, since there aren't many of them.

class Lance( Item ):
    true_name = "Lance"
    true_desc = "A long spear designed for jousting."
    itemtype = LANCE
    avatar_image = "avatar_polearm.png"
    avatar_frame = 8
    attackdata = Attack( (1,10,0), double_handed=False, element=stats.RESIST_PIERCING, reach=2 )
    mass = 130

class HeavyLance( Item ):
    true_name = "Heavy Lance"
    true_desc = "A long spear designed for jousting."
    itemtype = LANCE
    avatar_image = "avatar_polearm.png"
    avatar_frame = 9
    attackdata = Attack( (2,8,0), double_handed=False, element=stats.RESIST_PIERCING, reach=2 )
    mass = 165

