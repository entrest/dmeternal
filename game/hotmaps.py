# Pathfinding algorithm.

import pygame
import random

class HotTile( object ):
    def __init__( self ):
        self.heat = 9999
        self.cost = 0
        self.block = False

class HotMap( object ):
    DELTA8 = [ (-1,-1), (0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1) ]
    EXPENSIVE = 9999
    def __init__( self, scene, hot_points, obstacles=set(), expensive=set(), limits=None, avoid_models=False ):
        """Calculate this hotmap given scene and set of hot points."""
        # Obstacles block movement.
        # Expensive tiles are avoided, if possible.
        self.scene = scene

        if avoid_models:
            obstacles = self.list_model_positions().union( obstacles )

        self.obstacles = obstacles
        self.expensive = expensive
        self.map = [[ int(self.EXPENSIVE)
            for y in range(scene.height) ]
                for x in range(scene.width) ]

        for p in hot_points:
            if len( p ) < 3:
                self.map[p[0]][p[1]] = 0
            else:
                self.map[p[0]][p[1]] = min( p[2], self.map[p[0]][p[1]] )

        if limits:
            self.lo_x = max( limits.x, 1 )
            self.hi_x = min( limits.x + limits.width + 1, scene.width - 1 )
            self.lo_y = max( limits.y, 1 )
            self.hi_y = min( limits.y + limits.height + 1, scene.height - 1 )
        else:
            self.lo_x,self.hi_x,self.lo_y,self.hi_y = 1, scene.width-1, 1, scene.height-1

        self.process_map( limits )

    def process_map( self, limits ):
        # Iterate through each of the tiles, 
        flag = True
        while flag:
            flag = False
            for y in range( self.lo_y, self.hi_y ):
                for x in range( self.lo_x, self.hi_x ):
                    p = (x,y)
                    if not self.blocks_movement( x, y ):
                        dh = 2 + self.map[x-1][y]
                        dv = 2 + self.map[x][y-1]
                        dd = 3 + self.map[x-1][y-1]
                        dp = 3 + self.map[x+1][y-1]

                        dp = min(dh,dv,dd,dp)
                        if p in self.expensive:
                            dp += 16
                        if dp < self.map[x][y]:
                            self.map[x][y] = dp
                            flag = True


            for y in range( self.hi_y-1, self.lo_y-1, -1 ):
                for x in range( self.hi_x-1, self.lo_x-1, -1 ):
                    if not self.blocks_movement( x, y ):
                        dh = 2 + self.map[x+1][y]
                        dv = 2 + self.map[x][y+1]
                        dd = 3 + self.map[x+1][y+1]
                        dp = 3 + self.map[x-1][y+1]

                        dp = min(dh,dv,dd,dp)
                        if p in self.expensive:
                            dp += 16
                        if dp < self.map[x][y]:
                            self.map[x][y] = dp
                            flag = True

    def blocks_movement( self, x, y ):
        return self.scene.map[x][y].blocks_walking() or (x,y) in self.obstacles

    def list_model_positions( self ):
        mylist = set()
        for m in self.scene.contents:
            if self.scene.is_model(m):
                mylist.add( m.pos )
        return mylist

    def downhill_dir( self, pos ):
        """Return a dx,dy tuple showing the lower heat value."""
        best_d = None
        random.shuffle( self.DELTA8 )
        heat = self.map[pos[0]][pos[1]]
        for d in self.DELTA8:
            x2 = d[0] + pos[0]
            y2 = d[1] + pos[1]
            if self.scene.on_the_map(x2,y2) and ( self.map[x2][y2] < heat ):
                heat = self.map[x2][y2]
                best_d = d
        return best_d

    def clever_downhill_dir( self, exp, pos ):
        """Return the best direction to move in, avoiding models."""
        best_d = None
        random.shuffle( self.DELTA8 )
        heat = self.map[pos[0]][pos[1]]
        for d in self.DELTA8:
            x2 = d[0] + pos[0]
            y2 = d[1] + pos[1]
            if exp.scene.on_the_map(x2,y2) and ( self.map[x2][y2] < heat ):
                target = exp.scene.get_character_at_spot( (x2,y2) )
                if not target:
                    heat = self.map[x2][y2]
                    best_d = d
        return best_d

    def mix( self, other_map, amount ):
        for y in range( self.lo_y, self.hi_y ):
            for x in range( self.lo_x, self.hi_x ):
                self.map[x][y] += other_map.map[x][y] * amount

    def show( self, x0, y0 ):
        for y in range( y0-2,y0+3):
            vals = list()
            for x in range( x0-2,x0+3):
                if self.scene.on_the_map(x,y):
                    vals.append( '{:<8}'.format( self.map[x][y] ) )
                else:
                    vals.append( "XXX" )
            print " ".join( vals )


class AvoidMap( HotMap ):
    def __init__( self, scene, hot_points, obstacles=set(), expensive=set(), limits=None, avoid_models=False ):
        """Calculate this hotmap given scene and set of hot points."""
        super( AvoidMap, self ).__init__( scene, hot_points, obstacles, expensive=expensive, avoid_models=avoid_models, limits=limits )
        for y in range( self.lo_y, self.hi_y ):
            for x in range( self.lo_x, self.hi_x ):
                if self.map[x][y] < self.EXPENSIVE:
                    self.map[x][y] *= -1.2
        self.process_map( limits )



class PointMap( HotMap ):
    def __init__( self, scene, dest, avoid_models = False, expensive=set(), limits=None ):
        myset = set()
        myset.add( dest )
        super( PointMap, self ).__init__( scene, myset, expensive=expensive, avoid_models=avoid_models, limits=limits )

class MoveMap( HotMap ):
    """Calculates movement costs to different tiles. Only calcs as far as necessary."""
    def __init__( self, scene, chara, avoid_models = False ):
        myset = set()
        myset.add( chara.pos )
        reach = ( chara.get_move() + 1 ) // 2
        super( MoveMap, self ).__init__( scene, myset, limits=pygame.Rect(chara.pos[0]-reach, chara.pos[1]-reach, reach*2+1, reach*2+1 ), avoid_models=avoid_models )


if __name__=='__main__':
    import timeit
    import maps
    import random
    import pygame


    myscene = maps.Scene( 100 , 100 )
    for x in range( 5, myscene.width ):
        for y in range( 5, myscene.height ):
            if random.randint(1,3) == 1:
                myscene.map[x][y].wall = maps.BASIC_WALL

    myset = set()
    myset.add( (23,23) )


    class OldWay( object ):
        def __init__( self, m ):
            self.m = m
        def __call__(self):
            HotMap( self.m, myset )

    class NewWay( object ):
        def __init__( self, m ):
            self.m = m
            self.myrect = pygame.Rect( 20, 20, 5, 5 )
        def __call__(self):
            HotMap( self.m, myset, limits=self.myrect )


    t1 = timeit.Timer( OldWay( myscene ) )
    t2 = timeit.Timer( NewWay( myscene ) )

    print t1.timeit(100)
    print t2.timeit(100)



