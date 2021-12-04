import characters
import teams
import hotmaps
import pygwrap
import pygame
import maps
import collections
import image
import pfov
import random
import stats
import rpgmenu
import animobs
import effects
import enchantments
import aibrain
import services

class TacticsRedraw( object ):
    def __init__( self, chara, comba, explo, hmap = None ):
        self.chara = chara
        self.comba = comba
        self.explo = explo
        self.hmap = hmap
        self.rect = pygame.Rect( 32, 32, 300, 15 )
        self.gems = image.Image( "sys_counters.png", 10, 16 )

    def __call__( self, screen ):
        self.explo.view( screen )
        pygwrap.default_border.render( screen, self.rect )
        pygwrap.draw_text( screen, pygwrap.SMALLFONT, str( self.chara ), self.rect )
        ap = min( self.chara.get_move() - self.comba.ap_spent[ self.chara ], 24 )
        if self.hmap and self.comba.scene.on_the_map( *self.explo.view.mouse_tile ):
            apr = ap - self.hmap.map[self.explo.view.mouse_tile[0]][self.explo.view.mouse_tile[1]]
        else:
            apr = ap

        if ap > 0:
            mydest = pygame.Rect( self.rect.x + 180, self.rect.y, 32, 32 )
            pygwrap.draw_text( screen, pygwrap.ITALICFONT, "AP:", mydest )
            for t in range( 1, (ap+3)//2 ):
                mydest.x = self.rect.x + 198 + t * 8
                if t <= ( apr + 1 ) //2:
                    if apr >= t * 2:
                        self.gems.render( screen, mydest, 1 )
                    else:
                        self.gems.render( screen, mydest, 6 )
                else:
                    self.gems.render( screen, mydest, 5 )

class CombatStat( object ):
    """Keep track of some stats that only matter during combat."""
    def __init__( self ):
        self.paralysis = 0
        self.confusion = 0
        self.asleep = False
        self.silent = False
        self.aoo_readied = False
        self.attacks_so_far = 0
    def can_act( self ):
        return self.paralysis < 1 and not self.asleep

# This is a complex effect- Check if target is undead. If so, first apply an
# enchantment. Then, make skill roll to cause 20-120 solar damage and paralysis.
# If that skill roll fails, make an easier skill roll to just cause paralysis.
HOLY_SIGN_EFFECT = effects.TargetIs( effects.UNDEAD, on_true = ( \
    effects.Enchant(enchantments.HolySignMark,anim=animobs.YellowSparkle,children=( \
      effects.OpposedRoll(stats.HOLY_SIGN, stats.CHARISMA, -70, stats.MAGIC_DEFENSE, stats.PIETY, on_success = (
        effects.HealthDamage( (20,6,0), stats.PIETY, element=stats.RESIST_SOLAR, anim=animobs.YellowExplosion, on_success= (effects.Paralyze(max_duration=6),) )
      ,), on_failure = (
        effects.OpposedRoll(stats.HOLY_SIGN, stats.CHARISMA, 5, stats.MAGIC_DEFENSE, stats.PIETY, on_success = (
            effects.Paralyze(max_duration=8)
    # Is there an obfuscated Python competition?
    ,)),)),)),))

class Combat( object ):
    def __init__( self, camp, monster_zero ):
        self.active = []
        self.scene = camp.scene
        self.camp = camp
        self.ap_spent = collections.defaultdict( int )
        self.cstat = collections.defaultdict( CombatStat )
        self.no_quit = True

        self.activate_monster( monster_zero )

        # Sort based on initiative roll.
        self.active.sort( key = characters.roll_initiative, reverse=True )

    def activate_monster( self, monster_zero ):
        for m in self.scene.contents:
            if isinstance( m, characters.Character ) and m.is_alright() and m not in self.active:
                if m in self.camp.party:
                    self.active.append( m )
                elif self.scene.distance( m.pos, monster_zero.pos ) < 5:
                    self.active.append( m )
                elif m.team and m.team == monster_zero.team:
                    self.active.append( m )

    def num_enemies( self ):
        """Return the number of active, hostile characters."""
        n = 0
        for m in self.active:
            if isinstance( m, characters.Character ) and m.is_alright() and m.is_hostile( self.camp ):
                n += 1
        return n

    def can_act( self, chara ):
        """Return True if the provided character can act right now."""
        return chara.is_alright() and self.ap_spent[ chara ] < chara.get_move() and self.cstat[chara].can_act()

    def still_fighting( self ):
        """Keep playing as long as there are enemies, players, and no quit."""
        return self.num_enemies() and self.camp.first_living_pc() and self.no_quit and not pygwrap.GOT_QUIT and not self.camp.destination


    def get_threatened_area( self, chara ):
        area = set()
        for m in self.active:
            if m.is_alright() and m.is_enemy( self.camp, chara ) and m.can_attack_of_opportunity() and self.cstat[m].aoo_readied and self.cstat[m].can_act():
                x,y = m.pos
                for d in self.scene.DELTA8:
                    area.add( (x + d[0], y + d[1] ) )
        return area

    def opportunity_to_attack( self, explo, target ):
        """Enemies with attacks of opportunity can attack this target."""
        for m in self.active[:]:
            if m.is_alright() and m.is_enemy( self.camp, target ) and m.can_attack_of_opportunity() and self.cstat[m].aoo_readied and self.cstat[m].can_act() and self.scene.distance(m.pos,target.pos) <= 1:
                self.attack( explo, m, target, attack_of_opportunity=True )
                self.cstat[m].aoo_readied = False
                # If the target is killed, everyone else can stop piling on.
                if not target.is_alright():
                    break

    def step( self, explo, chara, hmap, do_bump=False ):
        """Move chara according to hmap, return True if movement ended."""
        # See if the movement starts in a threatened area- may be attacked if it ends
        # in a threatened area as well.
        threat_area = self.get_threatened_area( chara )
        started_in_threat = chara.pos in threat_area

        best_d = hmap.clever_downhill_dir( explo, chara.pos )

        if best_d:
            x2 = best_d[0] + chara.pos[0]
            y2 = best_d[1] + chara.pos[1]
            target = self.scene.get_character_at_spot( (x2,y2) )

            if explo.scene.map[x2][y2].blocks_walking():
                if do_bump:
                    explo.bump_tile( (x2,y2), chara )
                    self.end_turn( chara )
                return True
            elif not target:
                # Move the character.
                chara.pos = (x2,y2)
                self.ap_spent[ chara ] += 1 + abs(best_d[0]) + abs(best_d[1])

                # Suffer any field effects.
                fld = self.scene.get_field_at_spot( chara.pos )
                if fld:
                    fld.invoke( explo )

                # Maybe take an attack of opportunity.
                if chara.is_alright() and started_in_threat and chara.pos in threat_area and not chara.hidden:
                    self.opportunity_to_attack( explo, chara )
                return False
            else:
                return target
        else:
            return True


    def move_player_to_spot( self, explo, chara, pos, redraw=None ):
        result = None
        if not redraw:
            redraw = explo.view
        explo.view.overlays.clear()
        if self.scene.on_the_map( *pos ):
            hmap = hotmaps.PointMap( self.scene, pos, avoid_models=True )

            while self.ap_spent[ chara ] < chara.get_move():
                result = self.step( explo, chara, hmap, do_bump=True )
                self.scene.update_party_position( explo.camp.party )
                if result:
                    break

                redraw( explo.screen )
                pygame.display.flip()
                pygwrap.anim_delay()

        return result

    def attack( self, explo, chara, target, redraw=None, attack_of_opportunity=False ):
        """Perform chara's attack against target."""
        # Determine number of attacks. If have moved one step or less, can make full attack.
        if attack_of_opportunity:
            # One attack at a +0 modifier
            num_attacks = [0]
        elif self.ap_spent[chara] <= 3:
            num_attacks = chara.series_of_attacks()
        else:
            # One attack at a +0 modifier
            num_attacks = [0]
        for a in num_attacks:
            if chara.can_attack() and target.is_alright():
                # The attack modifier is based on whether this is the character's
                # first, second, etc attack and also if the target is being ganged
                # up on.
                at_fx = chara.get_attack_effect( roll_mod = a + self.cstat[target].attacks_so_far * 5 )
                at_anim = chara.get_attack_shot_anim()
                if at_anim:
                    opening_shot = at_anim( chara.pos, target.pos )
                else:
                    opening_shot = None
                explo.invoke_effect( at_fx, chara, (target.pos,), opening_shot )
                chara.spend_attack_price()
                # A hidden character will likely be revealed if the target survived.
                if target.is_alright() and chara.hidden and random.randint(1,100) + target.get_stat(stats.AWARENESS) + target.get_stat_bonus(stats.INTELLIGENCE) > chara.get_stat(stats.STEALTH) + chara.get_stat_bonus(stats.REFLEXES):
                    chara.hidden = False
                # Record the fact that this target has been attacked.
                self.cstat[target].attacks_so_far += 1
            else:
                break
        if ( target.is_alright() and target.can_attack_of_opportunity() and self.cstat[target].can_act() 
         and self.scene.distance(target.pos,chara.pos) <= target.get_attack_reach() and not attack_of_opportunity ):
            # Target may be able to counterattack.
            if random.randint(1,100) <= min( target.get_stat( stats.COUNTER_ATTACK ), 95 ):
                self.attack( explo, target, chara, redraw, True )
        if not attack_of_opportunity:
            self.end_turn( chara )


    def move_to_attack( self, explo, chara, target, redraw=None ):
        result = None
        if not redraw:
            redraw = explo.view
        explo.view.overlays.clear()
        if self.scene.on_the_map( *target.pos ):
            attack_positions = pfov.AttackReach( self.scene, target.pos[0], target.pos[1], chara.get_attack_reach() ).tiles
            # Remove the positions of models from the goal tiles, so they will be avoided.
            for m in self.scene.contents:
                if self.scene.is_model(m) and m.pos in attack_positions and m is not chara:
                    attack_positions.remove( m.pos )
            hmap = hotmaps.HotMap( self.scene, attack_positions, avoid_models=True )

            while self.ap_spent[ chara ] < chara.get_move():
                result = self.step( explo, chara, hmap )
                if chara in self.camp.party:
                    self.scene.update_party_position( explo.camp.party )
                if result:
                    break

                redraw( explo.screen )
                pygame.display.flip()
                pygwrap.anim_delay()

            if chara.pos in attack_positions:
                # Close enough to attack. Make it so.
                self.attack( explo, chara, target, redraw )

        return result


    def end_turn( self, chara ):
        """End this character's turn."""
        self.ap_spent[ chara ] += chara.get_move()


    def attempt_stealth( self, explo, chara ):
        """Make a stealth roll for chara vs best enemy awareness roll."""
        # Determine the highest awareness of all enemies.
        hi = 0
        for m in self.active:
            if m.is_alright() and m.is_enemy( self.camp, chara ):
                awareness = m.get_stat( stats.AWARENESS ) + m.get_stat_bonus( stats.INTELLIGENCE )
                hi = max( hi, awareness )
        # The target number is clamped between 5 and 96- always 5% chance of success or failure.
        hi = min( max( hi - chara.get_stat( stats.STEALTH ) - chara.get_stat_bonus( stats.REFLEXES ) + 45 , 5 ), 96 )
        anims = list()
        if random.randint(1,100) >= hi:
            chara.hidden = True
            anims.append( animobs.Smoke( pos=chara.pos ) )
        else:
            anims.append( animobs.Smoke( pos=chara.pos ) )
            anims.append( animobs.Caption( "Fail!", pos=chara.pos ) )
        animobs.handle_anim_sequence( explo.screen, explo.view, anims )

        self.end_turn( chara )

    def attempt_awareness( self, explo, chara ):
        """Try to spot any hidden models taking part in combat."""
        awareness = chara.get_stat( stats.AWARENESS ) + chara.get_stat_bonus( stats.INTELLIGENCE ) + 55
        anims = list()
        for m in self.active:
            if m.is_alright() and m.is_enemy( self.camp, chara ) and m.hidden:
                spot_chance = max( awareness - m.get_stat( stats.STEALTH ) - chara.get_stat_bonus( stats.REFLEXES ), 10)
                if random.randint(1,100) <= spot_chance:
                    m.hidden = False
                    anims.append( animobs.PurpleSparkle( pos=m.pos ) )
        if not anims:
            anims.append( animobs.Caption( "Fail!", pos=chara.pos ) )
        animobs.handle_anim_sequence( explo.screen, explo.view, anims )
        self.end_turn( chara )

    def attempt_holy_sign( self, explo, chara ):
        """Attempt to disrupt the undead creatures in the area."""
        aoe = pfov.PointOfView(self.scene, chara.pos[0], chara.pos[1], 16).tiles
        explo.invoke_effect( HOLY_SIGN_EFFECT, chara, aoe, animobs.Marquee(chara.pos) )
        chara.holy_signs_used += 1
        self.end_turn( chara )

    def num_enemies_hiding( self, chara ):
        n = 0
        for m in self.active:
            if m.is_alright() and m.is_enemy( self.camp, chara ) and m.hidden:
                n += 1
        return n

    def pop_useitem_menu( self, explo, chara ):
        mymenu = rpgmenu.PopUpMenu( explo.screen, explo.view )
        for i in chara.contents:
            if hasattr( i, "use" ):
                mymenu.add_item( str( i ) , i )
        mymenu.sort()
        mymenu.add_alpha_keys()

        choice = mymenu.query()

        if choice:
            if choice.use( chara, explo ):
                self.end_turn( chara )

    def pop_combat_menu( self, explo, chara ):
        mymenu = rpgmenu.PopUpMenu( explo.screen, explo.view )

        # Add the techniques.
        techs = chara.get_invocations( True )
        for t in techs:
            mymenu.add_item( t.menu_str(), t )
        mymenu.sort()
        mymenu.add_alpha_keys()

        mymenu.add_item( "-----", False )
        if chara.can_use_holy_sign() and chara.holy_signs_used < chara.holy_signs_per_day():
            mymenu.add_item( "Skill: Holy Sign [{0}/{1}]".format(chara.holy_signs_per_day()-chara.holy_signs_used,chara.holy_signs_per_day()) , 6 )
        if chara.can_use_stealth() and not chara.hidden:
            mymenu.add_item( "Skill: Stealth", 4 )
        if self.num_enemies_hiding(chara):
            mymenu.add_item( "Skill: Awareness", 5 )
        if any( hasattr( i, "use" ) for i in chara.contents ):
            mymenu.add_item( "Use Item", 7 )
        mymenu.add_item( "View Inventory".format(str(chara)), 2 )
        mymenu.add_item( "Focus on {0}".format(str(chara)), 1 )
        mymenu.add_item( "End Turn".format(str(chara)), 3 )

        choice = mymenu.query()

        if choice == 1:
            explo.view.focus( explo.screen, *chara.pos )
        elif choice == 2:
            explo.view_party( self.camp.party.index(chara), can_switch=False )
            self.end_turn( chara )
        elif choice == 3:
            self.end_turn( chara )
        elif choice == 4:
            self.attempt_stealth( explo, chara )
        elif choice == 5:
            self.attempt_awareness( explo, chara )
        elif choice == 6:
            self.attempt_holy_sign( explo, chara )
        elif choice == 7:
            self.pop_useitem_menu( explo, chara )

        elif choice:
            # Presumably, this is an invocation of some kind.
            if explo.pc_use_technique( chara, choice, choice.com_tar ):
                self.end_turn( chara )

    def do_player_action( self, explo, chara ):
        #Start by making a hotmap centered on PC, to see how far can move.
        hm = hotmaps.MoveMap( self.scene, chara )

        tacred = TacticsRedraw( chara, self, explo, hm )

        while self.can_act( chara ) and self.still_fighting():
            # Get input and process it.
            gdi = pygwrap.wait_event()

            if gdi.type == pygwrap.TIMEREVENT:
                explo.view.overlays.clear()
                explo.view.overlays[ chara.pos ] = maps.OVERLAY_CURRENTCHARA
                explo.view.overlays[ explo.view.mouse_tile ] = maps.OVERLAY_CURSOR

                tacred( explo.screen )
                pygame.display.flip()

            else:
                if gdi.type == pygame.KEYDOWN:
                    if gdi.unicode == u"Q":
                        self.camp.save(explo.screen)
                        self.no_quit = False
                    elif gdi.unicode == u"i":
                        explo.view_party( self.camp.party.index(chara), can_switch=False )
                        self.end_turn( chara )
                    elif gdi.unicode == u"c":
                        explo.view.focus( explo.screen, *chara.pos )
                    elif gdi.unicode == u" ":
                        self.end_turn( chara )
                elif gdi.type == pygame.MOUSEBUTTONUP:
                    if gdi.button == 1:
                        # Left mouse button.
                        if ( explo.view.mouse_tile != chara.pos ) and self.scene.on_the_map( *explo.view.mouse_tile ):
                            tacred.hmap = None
                            target = explo.view.modelmap.get( explo.view.mouse_tile, None )
                            if target and target.is_hostile( self.camp ):
                                if chara.can_attack():
                                    self.move_to_attack( explo, chara, target, tacred )
                                else:
                                    explo.alert( "You are out of ammunition!" )
                            else:
                                self.move_player_to_spot( explo, chara, explo.view.mouse_tile, tacred )
                            tacred.hmap = hotmaps.MoveMap( self.scene, chara )
                    else:
                        self.pop_combat_menu( explo, chara )

    def do_npc_action( self, explo, chara ):
        tacred = TacticsRedraw( chara, self, explo )
        tacred( explo.screen )
        pygame.display.flip()

        chara.COMBAT_AI.act( explo, chara, tacred )
        self.end_turn( chara )

        # If very far from nearest PC, deactivate.
        for m in self.scene.contents:
            enemy_found = False
            if isinstance( m, characters.Character ) and chara.is_enemy( self.camp, m ) and self.scene.distance( chara.pos, m.pos ) <= 12:
                enemy_found = True
                break
        if not enemy_found:
            self.active.remove( chara )



    def do_combat_action( self, explo, chara ):
        """Give this character its turn."""
        started_turn_hidden = chara.hidden

        # If you start your turn in a field, you get affected by that field.
        fld = self.scene.get_field_at_spot( chara.pos )
        if fld:
            fld.invoke( explo )

        # Check the character's condition to see what they can do...
        if self.cstat[chara].paralysis > 0:
            # This character can do nothing this turn.
            self.end_turn( chara )
            self.cstat[chara].paralysis += -1
        elif self.cstat[chara].asleep:
            # This character can do nothing this turn... may wake up.
            self.end_turn( chara )
            if random.randint(1,3) == 2:
                self.cstat[chara].asleep = False
        else:
            # No special psychology or conditions- just do stuff.
            if chara in self.camp.party:
                self.do_player_action( explo, chara )
            else:
                self.do_npc_action( explo, chara )

        # If they started the turn hidden, random chance of decloaking.
        if started_turn_hidden and random.randint(1,10)==1:
            chara.hidden = False

    def give_xp_and_treasure( self, explo ):
        """Add up xp,gold from defeated monsters, and give to party."""
        xp = 0
        gold = 0
        for m in self.active:
            if m.is_hostile( self.camp ) and not m.is_alright() and not (hasattr(m,"combat_only") and m.combat_only):
                xp += m.xp_value()
                if hasattr( m, "gold" ) and m.gold > 0:
                    gold += m.gold
                # Killing faction members worsens faction score.
                if m.team.fac:
                    m.team.fac.reaction += -2
        xp = int( xp * self.camp.xp_scale ) // self.camp.num_pcs()
        explo.give_gold_and_xp( gold, xp, True )

    def do_first_aid( self, explo ):
        # At the end of combat, help anyone who was wounded.
        fx = effects.HealthRestore( dice=(1,6,explo.camp.party_rank()), stat_bonus=None )
        targets = list()
        for pc in explo.camp.party:
            if pc.is_alright() and hasattr( pc, "most_recent_wound" ) and pc.hp_damage > 0:
                targets.append( pc.pos )
                del pc.most_recent_wound
        explo.invoke_effect( fx, None, targets )

    def recover_fainted(self,explo):
        for pc in explo.camp.party:
            if not (pc.is_dead() or pc.is_alright()):
                # This PC is neither dead nor alright- in other words, fainted.
                pc.hp_damage = pc.max_hp() - 1
                pc.place( explo.camp.scene, services.Temple.get_return_pos(explo) )
                #explo.camp.scene.contents.append( pc )

    def everybody_is_dead(self,explo):
        # If the entire party is dead, dispose of their items and thwack their gold.
        for pc in explo.camp.party:
            pc.drop_everything(explo.camp.scene)
        explo.camp.gold = explo.camp.gold // 4

    def go( self, explo ):
        """Perform this combat."""

        n = 0
        while self.still_fighting():
            if n >= len( self.active ):
                # It's the end of the round.
                n = 0
                self.ap_spent.clear()
                explo.update_monsters()
            if self.active[n].is_alright():
                chara = self.active[n]
                self.do_combat_action( explo, chara )
                # After action, invoke enchantments and renew attacks of opportunity
                explo.invoke_enchantments( chara )
                self.cstat[chara].aoo_readied = True
                self.cstat[chara].attacks_so_far = 0
            n += 1

        if self.no_quit and not pygwrap.GOT_QUIT:
            # Combat is over. Deal with things.
            explo.check_trigger( "COMBATOVER" )
            if self.camp.num_pcs() > 0:
                # Combat has ended because we ran out of enemies. Dole experience.
                self.give_xp_and_treasure( explo )
                # Provide some end-of-combat first aid.
                #self.do_first_aid(explo)
                self.recover_fainted(explo)

        # PCs stop hiding when combat ends.
        for pc in self.camp.party:
            pc.hidden = False
            pc.condition.tidy( enchantments.COMBAT )

        # Tidy up any combat enchantments.
        for m in self.scene.contents[:]:
            if hasattr( m, "condition" ):
                m.condition.tidy( enchantments.COMBAT )
            if hasattr( m, "combat_only" ) and m.combat_only:
                self.scene.contents.remove( m )
            elif hasattr( m, "mitose" ) and hasattr( m, "hp_damage" ):
                # Slimes regenerate after battle, to prevent split/flee exploit.
                m.hp_damage = 0

# I do not intend to create one more boring derivative fantasy RPG. I intend to create all of the boring derivative fantasy RPGs.



