#!/usr/bin/env python
# -*- coding: utf-8 -*-
#       
#       Copyright 2013 Joeph Hewitt <pyrrho12@yahoo.ca>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#       
# 
import characters
import pygame
import pygwrap
import items
import stats
import rpgmenu
import charsheet
import inspect


def give_starting_equipment( pc ):
    """Based on level and species, give and equip starting equipment."""
    # Start with the basic equipment that every character is eligible for.
    default = { items.BODY: items.clothes.NormalClothes(), items.FEET: items.shoes.NormalShoes() }

    if pc.mr_level:
        for v in pc.mr_level.starting_equipment:
            item = v()
            if pc.can_equip( item ) and item.is_better( default.get( item.slot , None ) ):
                default[ item.slot ] = item
    if pc.species:
        for v in pc.species.starting_equipment:
            item = v()
            if pc.can_equip( item ) and item.is_better( default.get( item.slot , None ) ):
                default[ item.slot ] = item

    for k,item in default.iteritems():
        if pc.can_equip( item ):
            pc.contents.append( item )
            pc.contents.equip( item )

def choose_gender( screen, redraw ):
    """Return the gender chosen by the player."""
    rpm = charsheet.RightMenu( screen , predraw = redraw )
    for g in range( 3 ):
        rpm.add_item( stats.GENDER[g], g, "Gender has no effect on a character's abilities." )
    rpm.add_alpha_keys()
    redraw.caption = "Select this character's gender."
    return rpm.query()

class ChooseSpeciesRedrawer( object ):
    def __init__( self , menu=None, predraw=None ):
        self.menu = menu
        self.predraw = predraw
    def display_species_info( self, screen, it, myrect ):
        y = myrect.y
        myimg = pygwrap.render_text( pygwrap.BIGFONT, it.name, myrect.width, justify=0, color=(240,240,240) )
        myrect = myimg.get_rect( topleft = ( myrect.x, y ) )
        screen.blit( myimg , myrect )
        y += myrect.height
        msg = it.desc
        if msg:
            myimg = pygwrap.render_text(pygwrap.SMALLFONT, msg, myrect.width, justify = -1 )
            myrect = myimg.get_rect( topleft = ( myrect.x, y ) )
            screen.blit( myimg , myrect )
            y += myrect.height + 6
        msg = it.stat_desc()
        if msg:
            myimg = pygwrap.render_text(pygwrap.ITALICFONT, msg, myrect.width, justify = 0 )
            myrect = myimg.get_rect( topleft = ( myrect.x, y ) )
            screen.blit( myimg , myrect )
    def __call__( self , screen ):
        if self.predraw:
            self.predraw( screen )
        if self.menu:
            # Display the item info in the upper display rect.
            it = self.menu.items[ self.menu.selected_item ].value
            if inspect.isclass( it ) and issubclass( it, characters.SentientSpecies ):
                self.display_species_info( screen, it, self.menu.descbox )


def choose_species( screen, predraw ):
    """Return the species chosen by the player."""
    redraw = ChooseSpeciesRedrawer( predraw=predraw )
    rpm = charsheet.RightMenu( screen , predraw = redraw )
    redraw.menu = rpm
    for s in characters.PC_SPECIES:
        rpm.add_item( s.name, s )
    rpm.sort()
    rpm.add_alpha_keys()
    redraw.caption = "Select this character's species."
    return rpm.query()

def get_possible_levels( pc, source=characters.PC_CLASSES ):
    """ Return a list of levels the PC qualifies for."""
    pl = []
    for l in source:
        if l.can_take_level( pc ):
            pl.append( l )
    return pl

class ChooseLevelRedrawer( object ):
    def __init__( self , menu=None, predraw=None ):
        self.menu = menu
        self.predraw = predraw
    def display_level_info( self, screen, it, myrect ):
        y = myrect.y
        myimg = pygwrap.render_text( pygwrap.BIGFONT, it.name, myrect.width, justify=0, color=(240,240,240) )
        myrect = myimg.get_rect( topleft = ( myrect.x, y ) )
        screen.blit( myimg , myrect )
        y += myrect.height
        msg = it.desc
        if msg:
            myimg = pygwrap.render_text(pygwrap.SMALLFONT, msg, myrect.width, justify = -1 )
            myrect = myimg.get_rect( topleft = ( myrect.x, y ) )
            screen.blit( myimg , myrect )
            y += myrect.height + 6
        msg = it.stat_desc()
        if msg:
            myimg = pygwrap.render_text(pygwrap.ITALICFONT, msg, myrect.width, justify = 0 )
            myrect = myimg.get_rect( topleft = ( myrect.x, y ) )
            screen.blit( myimg , myrect )
    def __call__( self , screen ):
        if self.predraw:
            self.predraw( screen )
        if self.menu:
            # Display the item info in the upper display rect.
            it = self.menu.items[ self.menu.selected_item ].value
            if inspect.isclass( it ) and issubclass( it, characters.Level ):
                self.display_level_info( screen, it, self.menu.descbox )


def choose_level( screen, predraw, pc ):
    """Roll stats, return the level chosen by the player."""
    level = None
    predraw.caption = "Roll your stats and choose a profession."
    redraw = ChooseLevelRedrawer( predraw=predraw )
    while not level:
        possible_levels = []
        while not possible_levels:
            pc.roll_stats()
            possible_levels = get_possible_levels( pc )

        rpm = charsheet.RightMenu( screen , predraw = redraw )
        redraw.menu = rpm
        for l in possible_levels:
            rpm.add_item( l.name, l )
        rpm.sort()
        rpm.add_alpha_keys()
        rpm.add_item( "Reroll Stats", -1 )
        rpm.set_item_by_value( -1 )

        l = rpm.query()

        if l is False:
            break
        elif l != -1:
            level = l

    return level

STARTER_HATS = ( None,
    items.hats.MageHat, items.hats.NecromancerHat, items.hats.NinjaMask, items.hats.Headband, items.hats.Bandana,
    items.hats.JauntyHat, items.hats.WoodsmansHat, items.hats.GnomeHat, items.hats.WizardHat, items.hats.WhiteHat,
    items.hats.WhiteTurban, items.hats.RedTurban, items.hats.PurpleTurban, items.hats.OrangeTurban, items.hats.BlueTurban,
    items.hats.RedCowl, items.hats.OrangeCowl, items.hats.GreenCowl, items.hats.GreyCowl, items.hats.BlueCowl,
    items.hats.GreyHat, items.hats.Coxcomb, items.hats.Coxcomb2, items.hats.TricorneHat
    )

def alter_hat( pc ):
    hat = pc.contents.get_equip( items.HEAD )
    if hat and hat.__class__ in STARTER_HATS:
        pos = STARTER_HATS.index( hat.__class__ )
    else:
        pos = 0
    pos = ( pos + 1 ) % len( STARTER_HATS )
    if hat:
        pc.contents.remove( hat )
    if pos:
        hat = STARTER_HATS[pos]()
        pc.contents.append( hat )
        pc.contents.equip( hat )


def choose_appearance( screen, redraw, pc ):
    """Alter the appearance of the character."""
    done = False
    redraw.caption = "Customize your appearance."
    rpm = charsheet.RightMenu( screen , predraw = redraw )

    rpm.add_item( "Change skin color" , 1 )

    if pc.species.HAS_HAIR:
        rpm.add_item( "Change hair" , 2 )
        if ( pc.gender != stats.FEMALE ) or isinstance( pc.species, characters.Dwarf ):
            rpm.add_item( "Change beard" , 3 )

    rpm.add_item( "Change hat" , 4 )

    rpm.add_item( "Finished" , False )

    while not done:
        l = rpm.query()

        if l is False:
            done = True
        elif l == 1:
            pc.species.alter_skin_color()
            redraw.charsheet.regenerate_avatar()
        elif l == 2:
            pc.alter_hair()
            redraw.charsheet.regenerate_avatar()
        elif l == 3:
            pc.alter_beard()
            redraw.charsheet.regenerate_avatar()
        elif l == 4:
            alter_hat( pc )
            redraw.charsheet.regenerate_avatar()



def make_character( screen ):
    """Generate and return a new player character."""
    # We're gonna use the same redrawer for this entire process.
    redraw = charsheet.MenuRedrawer( screen = screen )

    # Get gender.
    gender = choose_gender( screen , redraw )
    if gender is False:
        return None

    # Get species.
    species = choose_species( screen , redraw )
    if not species:
        return None

    pc = characters.Character( species = species(), gender = gender )
    redraw.charsheet = charsheet.CharacterSheet( pc , screen = screen )

    # Roll stats and pick a class.
    level = choose_level( screen, redraw, pc )
    if not level:
        return None

    pc.levels.append( level(1,pc) )
    give_starting_equipment( pc )
    redraw.charsheet.regenerate_avatar()

    # Customize appearance.
    choose_appearance( screen, redraw, pc )

    # Choose a name.
    redraw.caption = "Done!"
    name = pygwrap.input_string( screen, redrawer=redraw, prompt="Enter character name" )
    if name:
        pc.name = name
        pc.choose_random_spells()
        return pc
    else:
        return None

# Embrace the chaos. Or at least give it a firm handshake.

def make_and_save_character( screen ):
    pc = make_character( screen )
    if pc:
        pc.save()
    return pc

if __name__=='__main__':
    pygame.init()

    # Set the screen size.
    screen = pygame.display.set_mode( (0,0), pygame.FULLSCREEN )
#    screen = pygame.display.set_mode( (800,600) )

    pygwrap.init()
    rpgmenu.init()

    pc = make_and_save_character( screen )


