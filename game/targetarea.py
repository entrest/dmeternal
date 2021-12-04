import pfov
import animobs

# Each of the classes here describes a targeting type. Instantiation can set
# targeting details such as range, whether the center tile is included in a
# radius, and so on.
# Each must include the following stuff:
#  AUTOMATIC: if True, no targeting need take place- just call the effect drawer.
#  reach: Tells how far away this effect this effect can be targeted.
#  get_area: Method that calculates the set of tiles.
#  delay_from: Negative for delay from origin, positive for delay from target.

class Cone( object ):
    """A cone originating from originator."""
    AUTOMATIC = False
    def __init__( self, reach=10, delay_from=-1 ):
        self.reach = reach
        self.delay_from = delay_from
    def get_area( self, camp, origin, target ):
        return pfov.Cone( camp.scene, origin, target ).tiles
    def get_targets( self, camp, origin ):
        tiles = pfov.PointOfView( camp.scene, origin[0], origin[1], self.reach ).tiles
        tiles.remove( origin )
        return tiles
    def pc_select_area( self, explo, origin, caption=None ):
        explo.select_area( origin, self, caption )

class Blast( object ):
    """A circular area centered on target."""
    AUTOMATIC = False
    def __init__( self, radius=3, reach=10, delay_from=0 ):
        self.radius = radius
        self.reach = reach
        self.delay_from = delay_from
    def get_area( self, camp, origin, target ):
        return pfov.PointOfView( camp.scene, target[0], target[1], self.radius ).tiles
    def get_targets( self, camp, origin ):
        return pfov.PointOfView( camp.scene, origin[0], origin[1], self.reach ).tiles

class Line( object ):
    """A line from caster to target."""
    AUTOMATIC = False
    def __init__( self, reach=10, delay_from=-1 ):
        self.reach = reach
        self.delay_from = delay_from
    def get_area( self, camp, origin, target ):
        tiles = animobs.get_line( origin[0], origin[1], target[0], target[1] )
        tiles.remove( origin )
        return tiles
    def get_targets( self, camp, origin ):
        tiles = pfov.PointOfView( camp.scene, origin[0], origin[1], self.reach ).tiles
        tiles.remove( origin )
        return tiles

class SelfOnly( object ):
    """Just the originator."""
    AUTOMATIC = True
    def __init__( self, delay_from=0 ):
        self.delay_from = delay_from
    def get_area( self, camp, origin, target ):
        return ( origin, )

class SelfCentered( object ):
    """A circle centered on originator."""
    AUTOMATIC = True
    def __init__( self, radius=6, exclude_middle=False, delay_from=0 ):
        self.radius = radius
        self.exclude_middle = exclude_middle
        self.delay_from = delay_from
    def get_area( self, camp, origin, target ):
        tiles = pfov.PointOfView( camp.scene, origin[0], origin[1], self.radius ).tiles
        if self.exclude_middle:
            tiles.remove( origin )
        return tiles

class SingleTarget( object ):
    """Just the target tile."""
    AUTOMATIC = False
    def __init__( self, reach=10, delay_from=0 ):
        self.reach = reach
        self.delay_from = delay_from
    def get_area( self, camp, origin, target ):
        tiles = set()
        tiles.add( target )
        return tiles
    def get_targets( self, camp, origin ):
        return pfov.PointOfView( camp.scene, origin[0], origin[1], self.reach ).tiles

class SinglePartyMember( SingleTarget ):
    """Just the target tile, which must be a party member."""
    AUTOMATIC = False
    def __init__( self, delay_from=0 ):
        self.delay_from = delay_from
    def get_area( self, camp, origin, target ):
        tiles = set()
        tiles.add( target )
        return tiles
    def get_targets( self, camp, origin ):
        tiles = set()
        for pc in camp.party:
            tiles.add( pc.pos )
        return tiles

class AllPartyMembers( object ):
    """Target all party members."""
    AUTOMATIC = True
    def __init__( self, delay_from=-1 ):
        self.delay_from = delay_from
    def get_area( self, camp, origin, target ):
        tiles = set()
        for pc in camp.party:
            tiles.add( pc.pos )
        return tiles

