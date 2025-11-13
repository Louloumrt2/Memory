import pygame
import os
import random
import math
import sys
import time
pygame.init()

# --- CONFIGURATION ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
random.seed(2)

FPS = 60
FLIP_SPEED = 10
SELECTED_SPEED = 50
SELECTION_LIMIT = 2
SELECTION_BIGGER_SCALE = 1.05
# REVEAL_DELAY = 1500  # ms (1.5 s)

BEFORE_ADDING = 200  # ms (1 s)
DUREE_ECLAT_FADING = 1000
ADDING_SPEED = 1.1

DZITT_SPEED = 15
BONCE_EFFECT_TIME = 300
BONCE_EFFECT_INTENSITY = 30
SHOW_PREVIOUS_SPEED = 0.05

SWITCH_BACKGROUND_SPEED = 1000

run_parameter = {}

# SEED=1893894
# random.seed(1893894)

best_score = 0


SCORES = {
    "match" : 5,
    "dontmatch" : 0,
    "end_play" : 10
}

UPGRADES_COST = {
    "8_Volt" : 2,
    "Michel" : 4,
    "Max" : 5,
    "Flosette":5,
    "Le_Vrilleur":6,
    "Lame_Sadique":5,
    "Bulle_D_Eau":6,
    "Reveil_Endormi":4,
    "Allumette":4,
    "Pipette_Elementaire":5,
    "Tireur_Pro":5,
    "Piquante":6,
    "Chat_De_Compagnie":4,
    "Canon_A_Energie":6,
    "Bouquet_Medicinal":5,
    "Ghosting":8,
    "Maniak":7,
    "Mc_Cookie":5,
    "Fantome_A_Cheveux":4,
}



# --- INITIALISATION ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Brutal Memory")
clock = pygame.time.Clock()

from font import *



# --- CHARGEMENT DES IMAGES ---
def resource_path(relative_path):
    """Retourne le bon chemin, même dans le .exe"""
    try:
        base_path = sys._MEIPASS  # dossier temporaire PyInstaller
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def load_images(folder):
    images = []
    folder_path = resource_path(folder)
    if not os.path.exists(folder_path):
        print("⚠️ Dossier introuvable :", folder_path)
        return images

    for file in os.listdir(folder_path):
        if file.lower().endswith((".png", ".jpg", ".jpeg")):

            name = os.path.splitext(file)[0]
            img = pygame.image.load(os.path.join(folder_path, file)).convert_alpha()
            images.append((name, img))
    return images

all_images = load_images("cards_pict")

all_objects_images = load_images("objects_pict")

all_images_dict = dict(all_images)
all_objects_dict = dict(all_objects_images)

last_score_change_tick = pygame.time.get_ticks()
last_live_change_tick = pygame.time.get_ticks()
last_eclat_change_tick = pygame.time.get_ticks()

# PLAYER INFO

selection : list["Card"] = [] # sera la liste des cartes sélectionné -> passe à 2 = révèlent
selection_locked = False

selection_overload = 0

last_selection = []
showing_time = 1200
fighters_lvl = {}
objects_lvl = {}
level_upgrade_base = 1
apparation_probability = {}
player_lives = [20, 0, 0, 0]
player_score = [0, 0, 0]
eclat = [10,0,0]
regain_PV_manche = 2

combo = 0
last_succeed_move = 0
move= 0
charge = 8 # augmenté grâc à certaines actions dont dzzit

training_choices = 3
proposal_after_training_prob = 0.3
shop_choices = 3
bonus_lvl_probabilities = [0.3]+[0.2**i for i in range(2,10)]

scores_constantes_modifiers_plus = {}
scores_constantes_modifiers_mult = {}

def start_run(start_lives=20, start_eclat=10, p_regain_PV_manche=2, p_level_upgrade_base=1, p_showing_time=1200, p_training_choices=3, p_proposal_after_training=0.3, p_shop_choices=3) :
    global last_score_change_tick, last_live_change_tick, last_eclat_change_tick, selection_locked, selection_overload, showing_time, level_upgrade_base, regain_PV_manche, combo, last_succeed_move, move, charge, training_choices, proposal_after_training_prob, shop_choices
    
    last_score_change_tick = pygame.time.get_ticks()
    last_live_change_tick = pygame.time.get_ticks()
    last_eclat_change_tick = pygame.time.get_ticks()

    # PLAYER INFO

    selection.clear() # sera la liste des cartes sélectionné -> passe à 2 = révèlent
    selection_locked = False

    selection_overload = 0

    last_selection.clear()
    showing_time = p_showing_time
    fighters_lvl.clear()
    objects_lvl.clear()
    level_upgrade_base = p_level_upgrade_base
    apparation_probability.clear()
    player_lives.clear()
    player_lives.extend([start_lives, 0, 0, 0])
    player_score.clear()
    player_score.extend([0, 0, 0])
    eclat.clear()
    eclat.extend([start_eclat,0,0])
    regain_PV_manche = p_regain_PV_manche

    combo = 0
    last_succeed_move = 0
    move= 0
    charge = 8 # augmenté grâc à certaines actions dont dzzit

    training_choices = p_training_choices
    proposal_after_training_prob = p_proposal_after_training
    shop_choices = p_shop_choices
    bonus_lvl_probabilities.clear()
    bonus_lvl_probabilities.extend([0.3]+[0.2**i for i in range(2,10)])

    scores_constantes_modifiers_plus.clear()
    scores_constantes_modifiers_mult.clear()

    game.clear()
    
    global memo_shop_
    last_cards_shop.clear()
    game["state"] = "play"
    game["round"]=1

    




def bonus_score(action, extravar=None) :
    base = (SCORES.get(action,0)+scores_constantes_modifiers_plus.get(action, 0))*scores_constantes_modifiers_mult.get(action,1)

    if action in ("match") :
        if lvl := objects_lvl.get("Allumette",0) :
            if combo > 1 :
                add_show_effect("Allumette")
                base += (combo-1) * (3+lvl)

        if lvl := objects_lvl.get("Lame_Sadique",0) :
            add_show_effect("Lame_Sadique")
            base *= (1 + lvl)

    if action in ("live_gained") :
        if lvl := objects_lvl.get("Chat_De_Compagnie",0) :
            if not any(name for name,_,__ in enclenched_effect):
                add_show_effect("Chat_De_Compagnie")
            base += 5

    
    return int(base)



# GAME INFO
game = {"state":"play", "round":1}

BG_COLORS = {
    "play" : (30,30,40),
    "proposal": (60,10,60),
    "training":(50,10,10),
    "end":(80,0,0),
    "shop":(70,75,10),
}

bg_color = BG_COLORS["play"]
new_bg_color = None 
starting_transition_tick = 0
switch_bg_speed = 0
awaiting_time = 0
fading_eclat_start = 0


enclenched_effect = [] # tuple (nom, temps_debut, temps)


COLORS_MODIFIERS = {
    "dzzit" : lambda r,g,b,p : (int(min(255, r+(add:= 30*(1-p)))), int(min(255, g+add)),int( max(0, b-add)) )
}

def gtick() :
    return pygame.time.get_ticks()

def blend_multi(colors, ratio) :
    nb_couleur = len(colors)
    index = (nb_couleur - 1) * ratio
    col1_idx = int(index)
    col2_idx = min(col1_idx + 1, nb_couleur - 1)
    local_ratio = index - col1_idx
    col1 = colors[col1_idx]
    col2 = colors[col2_idx]
    return blend(col1, col2, local_ratio)


def blend(col1,col2, ratio) :
    anti = 1-ratio
    return (col1[0]*anti+col2[0]*ratio, col1[1]*anti+col2[1]*ratio, col1[2]*anti+col2[2]*ratio)

def draw_bg() :
    global bg_color, new_bg_color, starting_transition_tick


    if starting_transition_tick and new_bg_color:
        ratio = min(1,(pygame.time.get_ticks() - starting_transition_tick) / switch_bg_speed)
        screen.fill(blend(bg_color, new_bg_color, ratio))
        if ratio == 1 :
            bg_color = new_bg_color
            starting_transition_tick = 0
    else :
        screen.fill(bg_color)

def switch_bg_to(color, speed = SWITCH_BACKGROUND_SPEED):
    global switch_bg_speed
    
    global bg_color, new_bg_color, starting_transition_tick
    if starting_transition_tick and new_bg_color :
        ratio = min(1,(pygame.time.get_ticks() - starting_transition_tick) / switch_bg_speed)
        bg_color = (blend(bg_color, new_bg_color, ratio))
    
    switch_bg_speed = speed 
    starting_transition_tick = pygame.time.get_ticks()

    new_bg_color = color

def add_show_effect(name, time = 350):
    enclenched_effect.append((name, time, gtick()))

def show_effects(surface = screen) :
    to_remove = []
    for name, time, start_time in enclenched_effect :
            image = all_objects_dict[name]

            elapsed = max(0, gtick() - start_time)
            ratio = min(1.0, elapsed / time) if time > 0 else 1.0

            if ratio == 1 :
                to_remove.append((name, time, start_time))


            radius = SCREEN_WIDTH // 5
            center_x = SCREEN_WIDTH
            center_y = SCREEN_HEIGHT // 2

            theta = -math.pi / 2 + ratio * math.pi
            x = center_x - radius * math.cos(theta)
            y = center_y + radius * math.sin(theta)

            # bounce = math.sin(ratio * math.pi) * 20
            # y -= bounce

            angle_deg =  ratio * 360

            scale = 0.2 + 0.1 * (1 - abs(0.5 - ratio) * 2)

            # préparer et blitter l'image transformée
            try:
                surf = pygame.transform.rotozoom(image, angle_deg, scale)
                rect = surf.get_rect(center=(int(x), int(y)))
                surface.blit(surf, rect.topleft)
            except Exception:
                # si l'image n'est pas correcte, ne rien faire
                print(Exception)

        
    
    for effect in to_remove :
        enclenched_effect.remove(effect)


# --- CLASSE CARTE ---
class Card:
    def __init__(self, x, y, name, image, color, size, location = "play"):
        self.x, self.y = x, y
        self.init_x, self.init_y = x,y
        self.name = name
        self.init_size = size
        self.image = pygame.transform.smoothscale(image, (size, size))
        self.color = color
        self.stack_color_modifiers = []
        self.initial_color = color
        self.rect = pygame.Rect(x, y, size, size)
        self.flipped = False
        self.matched = False
        self.flip_progress = 0
        self.remove = False
        self.tags : set[tuple[str, int]] = set()
        
        self.selected = False
        self.bigger_selected_progress = 0

        self.dziit_progress = 0
        self.dziited = False

        self.row = 0
        self.col = 0

        self.location = location

        self.character_copied = [] # pour fantome a cheveux

    def update(self):
        if self.flipped and self.flip_progress < 1:
            self.flip_progress += FLIP_SPEED / (100 if self.location!="proposal" else 500)
        elif not self.flipped and self.flip_progress > 0:
            self.flip_progress -= FLIP_SPEED / (100 if self.location!="proposal" else 500)
        
        self.flip_progress = max(0, min(1, self.flip_progress))

        if self.selected and self.bigger_selected_progress < 1:
            self.bigger_selected_progress += SELECTED_SPEED / 100
        elif not self.selected and self.bigger_selected_progress > 0:
            self.bigger_selected_progress -= SELECTED_SPEED / 100
        
        scale_factor = 1 + ((SELECTION_BIGGER_SCALE - 1) * self.bigger_selected_progress)

        # compute integer sizes to keep the rect consistent with blitting and collisions
        new_width = max(1, int(self.init_size * scale_factor))
        new_height = max(1, int(self.init_size * scale_factor))
        self.rect.width = new_width
        self.rect.height = new_height
        self.x = self.init_x - (self.rect.width - self.init_size) / 2

        self.y = self.init_y - (self.rect.height - self.init_size) / 2
        if self.location == "proposal" : self.y += BONCE_EFFECT_INTENSITY * math.cos((gtick() - self.tick_appear) / BONCE_EFFECT_TIME)
        # keep the rect's topleft in sync with the visible position (use integers)

        self.rect.topleft = (int(self.x), int(self.y))
        self.bigger_selected_progress = max(0, min(1, self.bigger_selected_progress))

        if self.dziited and self.dziit_progress < 1:
            self.dziit_progress += DZITT_SPEED / 100
        elif not self.dziited and self.dziit_progress > 0:
            self.dziit_progress -= DZITT_SPEED / 100
        self.dziit_progress = max(0, min(1, self.dziit_progress))
        if self.dziited :
            self.color = COLORS_MODIFIERS["dzzit"](*self.initial_color, self.dziit_progress)
        if self.dziit_progress == 1 :
            self.dziited, self.dziit_progress = False, 0
            try : self.stack_color_modifiers.remove(COLORS_MODIFIERS["dzzit"])
            except : None
        
    def put_tag(self, tag) :

        remove_tags = set()
        for tag_ in self.tags :
            if tag_[0] == tag[0] :
                if tag_[1] >= tag[1] :
                    return False
                else :
                    remove_tags.add(tag_)
        
        add_score("add_tag", extravar=tag)
        self.tags -= remove_tags
        self.tags.add(tag)
        return True

    
    def activate_effect(self, nb_match, selection, lesnoms, cards, lvl, already_done, nb_move, custom_name = None) :
        global awaiting_time

        if lvl :
            ability_name = self.name if not custom_name else custom_name
            match ability_name :
                case "8_Volt" :
                    for card in cards :
                        if card != self and card.name == "8_Volt" and est_adjacent(self, card, lvl) and (card not in selection) :
                            card.dzzit()
    
                case "Michel" :
                    cards_michelled = []
                    for card in selection :
                        if card != self :
                            try_put = card.put_tag(("michel",lvl,(0,255,0)))
                            if try_put : cards_michelled.append(card)
                    if cards_michelled : pop_up(cards_michelled, "michellifié !", cards, message_color=(0,255,150),font=pop_up_font)
    
                case "Max" :
                    cards_maxee = []
                    max_effect = []
                    for card in selection :
                        if card != self and ca_match(card, self) :
                            max_effect.append(card)
                    if nb_match>0 and not "Max" in already_done: 
                        
                        for i in range((lvl)//3+1) :
                            for unmax in [self]+max_effect :
                                row = get_row(cards, unmax.row)
                                try :
                                    if row[i].flipped == False and (row[i] not in cards_maxee) : cards_maxee.append(row[i])
                                except IndexError : ...
                                try:
                                    if row[-1-i].flipped == False and (row[-1-i] not in cards_maxee) : cards_maxee.append(row[-1-i])
                                except IndexError : ...
                        
                        if cards_maxee : small_reveal(cards_maxee, cards, "On envoie du son !", message_color=(240,40,240),font=font, time=showing_time, me=[self]+max_effect)
                        already_done.append("Max")

                case "Flosette" :
                    
                    flosette_effect = []
                    for card in selection :
                        if card != self and ca_match(card, self) :
                            flosette_effect.append(card) # On regarde toutes les flosette Non sois meme qui remplisse la condition
                    if nb_match>0 and not "Flosette" in already_done: 
                        cards_soignee = []
                        for flo in [self]+flosette_effect : # On effectue une recherche de voisin sur chacune des flosettes
                            for card in not_removed_cards(cards) :
                                if card != flo and est_adjacent(flo, card, math.ceil(math.sqrt(lvl))) : # On ajoute les cartes voisines
                                    cards_soignee.append(card)
                        if cards_soignee :
                            card_success = []
                            for card in cards_soignee :
                                try_put = card.put_tag(("soin", (lvl+2)//2, (255,120,120))) # On tente d'appliquer le tag
                                if try_put : card_success.append(card)
                            if card_success :
                                pop_up(card_success, "Soin !", cards, (255,100,100))
                        already_done.append("Flosette")
                    
                case "Le_Vrilleur" :
                    proxi = [card for card in not_removed_cards(cards) if est_adjacent(self, card, 1) and not card.flipped]
                    eclats = (2+lvl)*len(proxi)
                    if eclats :
                        pop_up(proxi, "Drrrr", cards, (70,70,70),time=500)
                        add_score(eclats)
                
                case "Tireur_Pro" :
                    cards_a_cible = []
                    for card in selection :
                        if card != self :
                            try_put = card.put_tag(("cible",lvl,(60,60,60)))
                            if try_put : cards_a_cible.append(card)
                    if cards_a_cible : pop_up(cards_a_cible, "Ciblé !", cards, message_color=(150,150,150),font=pop_up_font)
                
                case "Piquante" :
                    if nb_match == 0 :
                        add_lives(1 + lvl//3)
                        pop_up([self], "Piquée !", cards, (255,0,0), pop_up_font, time=800)
                    else :
                        for _ in range(1 + lvl//3) :
                            add_score("match")
                        pop_up([self], "Butin !", cards, (230,200,0), pop_up_font, time=800)
                
                case "Mc_Cookie" :
                    if nb_match > 0 :
                        add_eclat((lvl+1)//2 + ((lvl//2)*len(self.tags)))
                        pop_up([self], "Vente !", cards, (230,230,0), pop_up_font, time=500)
                
                case "Fantome_A_Cheveux" :
                    if not custom_name :
                        print("On rentre dans le no_custom_name")
                        for copied_ability in self.character_copied :
                            print("On copie l'ability de ",copied_ability)
                            self.activate_effect(nb_match, selection, lesnoms, cards, min(fighters_lvl.get("Fantome_A_Cheveux",1), fighters_lvl.get(copied_ability,1)),already_done, nb_move, custom_name=copied_ability)
                
                case "Catchy" :
                    adjacent_cards = [card for card in cards if est_adjacent(self, card) and not card.remove and card!=self]

                    if len(adjacent_cards)>1 :
                        the_twos = random.sample(adjacent_cards, k=2)
                        switch_place(the_twos[0], the_twos[1], cards, 250, message="Et hop !", message_color=(255,40,230),me=[self])
                        add_score(2+lvl*4)
                    
                    if lvl>5:
                        if random.random()<0.25 :
                            other_guys = [card for card in cards if card != self and not card.remove]
                            if other_guys :
                                wait_with_cards(cards,100)
                                switch_place(self, other := random.choice(other_guys), cards, 100+100*distance(self,other), "ET HOP !!", message_color=(255,80,210), font=big, me=[self])
                                add_eclat((lvl+6)//2)



                    
                

            
        
        if self.tags :
            for tag in self.tags :
                if "michel" == tag[0] :
                    card_revealed = []
                    for card in (c for c in cards if (not c.remove) and (c!=self) and (not c.flipped) and est_adjacent(self, c, 1)) :
                        if random.random() <= (tag[1])/(tag[1]+3) :
                            card_revealed.append(card)
                    
                    if card_revealed : small_reveal(card_revealed, cards, time = 400+tag[1]*150, message="Michel ! Michel ?", message_color=(0,255,100), me=[self])
                if "soin" == tag[0] :
                    if nb_match > 0 :
                        pop_up([self], "Soigné !", cards, tag[2], pop_up_font, time=100)
                        add_lives(1)
        
        # Activer les effets des tags des autres cartes

        cible_effect = []
        for card in cards :
            for tag in card.tags :
                if tag[0] == "cible" :
                    if card.flipped == False and ca_match(card, self) :
                        cible_effect.append(card)
        
        if cible_effect :
            for card in cible_effect :
                card.dzzit()
            pop_up(cible_effect, "Ici !", cards, (255,255,255), pop_up_font, time=600)
        

                

        
    def check_modification(self, nb_move) :
        removed_tags = set()
        added_tag = set()
        for tag in self.tags :
            if tag[0] == "soin" :
                soin_restant = tag[1] - 1
                
                removed_tags.add(tag)
                if soin_restant > 0 : added_tag.add(("soin", soin_restant, (tag[2])))

        
        self.tags |= added_tag
        self.tags -= removed_tags
        
                    

                            

    
    # VERSION CHAT GPT
    # def draw(self, surface):
    #     if self.remove:
    #         return

    #     progress = abs(1 - 2 * self.flip_progress)
    #     width = max(1, int(self.rect.width * (1 - progress)))

    #     card_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

    #     if self.flip_progress >= 0.5:
    #         pygame.draw.rect(card_surface, (255, 255, 255), (0, 0, self.rect.width, self.rect.height), border_radius=10)
    #         img = pygame.transform.smoothscale(self.image, (self.rect.width - 10, self.rect.height - 10))
    #         card_surface.blit(img, (5, 5))
    #     else:
    #         pygame.draw.rect(card_surface, self.color, (0, 0, self.rect.width, self.rect.height), border_radius=10)

    #     scaled = pygame.transform.smoothscale(card_surface, (width, self.rect.height))
    #     offset_x = (self.rect.width - width) // 2
    #     surface.blit(scaled, (self.x + offset_x, self.y))


    def draw(self, surface):
        if self.remove:
            return      
        
        progress = abs(1 - 2 * self.flip_progress)
        width = max(1, int(self.rect.width * (progress)))   
        card_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)     
        if self.flip_progress >= 0.5:
            pygame.draw.rect(card_surface, (255, 255, 255), (0, 0, self.rect.width, self.rect.height), border_radius=10)
            if self.tags:
                num_tags = len(self.tags)
                tag_colors = [tag[2] for tag in self.tags]
                perimeter = 2 * (self.rect.width + self.rect.height)
                segment_length = perimeter / num_tags
                w = int(self.rect.width)
                h = int(self.rect.height)
                thickness = max(1, min(w, h) // 20)

                corners = [(0, 0), (w, 0), (w, h), (0, h), (0, 0)]
                edges = [w, h, w, h]

                def pos_to_edge_offset(pos):
                    pos = max(0, min(pos, perimeter))
                    cum = 0
                    for idx, length in enumerate(edges):
                        if pos <= cum + length:
                            return idx, pos - cum
                        cum += length
                    # fallback to last edge
                    return 3, edges[3]

                def point_on_edge(edge_idx, offset):
                    if edge_idx == 0:  # top
                        return (int(offset), 0)
                    if edge_idx == 1:  # right
                        return (w, int(offset))
                    if edge_idx == 2:  # bottom (goes right->left)
                        return (int(w - offset), h)
                    # edge_idx == 3 left (goes bottom->top)
                    return (0, int(h - offset))

                for i, color in enumerate(tag_colors):
                    start_pos = int(i * segment_length)
                    end_pos = int((i + 1) * segment_length)
                    end_pos = min(end_pos, perimeter)

                    s_edge, s_off = pos_to_edge_offset(start_pos)
                    e_edge, e_off = pos_to_edge_offset(end_pos)

                    p_start = point_on_edge(s_edge, s_off)
                    p_end = point_on_edge(e_edge, e_off)

                    if s_edge == e_edge:
                        pygame.draw.line(card_surface, color, p_start, p_end, thickness)
                    else:
                        # from start to its edge corner
                        corner_after_start = corners[s_edge + 1]
                        pygame.draw.line(card_surface, color, p_start, corner_after_start, thickness)

                        # full edges between start and end
                        idx = s_edge + 1
                        while idx <= e_edge - 1:
                            c1 = corners[idx]
                            c2 = corners[idx + 1]
                            pygame.draw.line(card_surface, color, c1, c2, thickness)
                            idx += 1

                        # from corner before end to end point
                        corner_before_end = corners[e_edge]
                        pygame.draw.line(card_surface, color, corner_before_end, p_end, thickness)
            else:
                pygame.draw.rect(card_surface, (0, 0, 0), (0, 0, self.rect.width, self.rect.height), width=min(self.rect.width, self.rect.height)//20, border_radius=10)
        
            img = pygame.transform.smoothscale(self.image, (self.rect.width - 10, self.rect.height - 10))
            card_surface.blit(img, (5, 5))
        else:
            # print(self.color)
            pygame.draw.rect(card_surface, self.color, (0, 0, self.rect.width, self.rect.height), border_radius=10) 
            pygame.draw.rect(card_surface, (0, 0, 0), (0, 0, self.rect.width, self.rect.height), width=min(self.rect.width, self.rect.height)//20, border_radius=10)
    

        scaled = pygame.transform.smoothscale(card_surface, (width, self.rect.height))
        offset_x = (self.rect.width - width) // 2

        # rotation based on dziit_progress (0..1 -> 0..360 degrees)
        angle = (-1 if ((self.dziit_progress*100)//25)%2 else 1)*((self.dziit_progress*100)//25*4)
        rotated = pygame.transform.rotate(scaled, angle)

        # keep rotation centered on the card's visible area
        center_x = self.x + offset_x + width / 2
        center_y = self.y + self.rect.height / 2
        rot_rect = rotated.get_rect(center=(center_x, center_y))

        surface.blit(rotated, rot_rect.topleft)
    
    def dzzit(self) :
        global charge
        charge += 1
        self.dziited = True
        self.stack_color_modifiers.append(COLORS_MODIFIERS["dzzit"])

# --- FONCTION DE CREATION DU PLATEAU ---
def create_board(num_pairs, forced_pairs = None):
    total_cards = num_pairs * 2

    chosen_images = random.sample(all_images, num_pairs)
    if (lvl := objects_lvl.get('Ghosting',0)) :
                removed = []

                for name,im in chosen_images : # On tente de retirer (avec proba) tous les combattants de niveau 0
                    if not fighters_lvl.get(name, 0) and random.random() < (lvl/(lvl+15)):
                        removed.append((name,im))
                
                upgrades = [e for e in all_images if e not in chosen_images and fighters_lvl.get(e[0],0)] # On regarde les cartes pas encore tirées et de niveau > 0
                chosen_images = [e for e in chosen_images if e not in removed] # On retire les carte de removed à chosen_image
               
                nb_to_fill = num_pairs - len(chosen_images) # nombre de carte a rajouter

                chosen_images += random.sample(upgrades,min(len(upgrades),nb_to_fill)) # On va les chercher dans les carte pas tirées et de niveau > 0

                if len(chosen_images) < num_pairs : # Si ça suffit toujours pas ???!!! on recommence avec les autres cartes supprimé avant (tant pis...)
                    chosen_images += random.sample([e for e in all_images if e in removed or e not in chosen_images], num_pairs - len(chosen_images)) 
    

    if forced_pairs : 
        for forced_pair_name in forced_pairs :
            if (pair := (forced_pair_name, all_images_dict[forced_pair_name])) in chosen_images :
                continue
            else :
                for i in range(len(chosen_images)) :
                    if chosen_images[i][0] not in forced_pairs :
                        chosen_images[i] = pair
                        break
                        
    
    cards_images = chosen_images * 2
    random.shuffle(cards_images)

    cols = int(math.sqrt(total_cards))
    rows = math.ceil(total_cards / cols)
    size = min(SCREEN_WIDTH // (cols + 1), SCREEN_HEIGHT // (rows + 1))

    cards = []
    for i in range(total_cards):
        x = (i % cols) * (size + 10) + 150
        y = (i // cols) * (size + 10) + 90
        color = (255,150,150)
        cards.append(card := Card(x, y, cards_images[i][0], cards_images[i][1], color, size))
        card.row = i // cols
        card.col = i % cols

        # # FOR TEST
        # card.tags.add(("michel",3))
    return cards


def update_draw_cards(cards) :
    for card in cards:
                card.update()
    for card in cards:
                card.draw(screen)




def get_color_life(bonus, malus, protec) :
    if malus :
        return (255,0,0)
    elif protec : 
        return (100,100,255)
    elif bonus :
        return (0,255,100)
    else :
        return (255,100,100)
    
def update_draw_score(score = player_score, lives = player_lives) :
        if score[1] > 0 and pygame.time.get_ticks() - last_score_change_tick > BEFORE_ADDING  :
            score[1] = score[1] / ADDING_SPEED
            if score[1]<1 : score[1]=0
        
        if score[2] < 0 and pygame.time.get_ticks() - last_score_change_tick > BEFORE_ADDING  :
            score[2] = score[2] / (max(1.1,ADDING_SPEED/2))
            if score[2]>-1 : score[2]=0
        
        score_display = math.ceil(score[0] - score[1] - score[2])
        score_text = font.render(f"Score : {score_display} {'+ '+str(math.floor(score[1])) if score[1] else ''} {'- '+str(math.floor(score[2])) if score[2] else ''}", True, (255, 255, 255) if (not score[1] and not score[2]) else (255,0,0) if not score[1] else (0,255,100))


        if lives[1] > 0 and pygame.time.get_ticks() - last_live_change_tick > BEFORE_ADDING  :
            lives[1] = lives[1] / ADDING_SPEED
            if lives[1]<1 : lives[1]=0
        
        if lives[2] < 0 and pygame.time.get_ticks() - last_live_change_tick > BEFORE_ADDING  :
            lives[2] = lives[2] / (max(1.1,ADDING_SPEED/2))
            if lives[2]>-1 : lives[2]=0
        
        if lives[3] < 0 and pygame.time.get_ticks() - last_live_change_tick > BEFORE_ADDING  :
            lives[3] = lives[3] / (max(1.1,ADDING_SPEED/40))
            if lives[3]>-0.3 : lives[3]=0

        
        
        life_display = math.ceil(lives[0] - lives[1] - lives[2])
        life_text = font.render(f"Vies : {life_display} {'+ '+str(math.floor(lives[1])) if lives[1] else ''} {'- '+str(abs(math.floor(lives[2]))) if lives[2] else ''} {'['+str(abs(math.floor(lives[3])))+']' if lives[3]<0 else '' }", True, get_color_life(lives[1], lives[2], lives[3]))



        screen.blit(score_text, (20, 20))
        screen.blit(life_text, (20, 60))

        if lives[0]<0 : game["state"] = "end_run"

def update_draw_eclats(fading = 0):
    global fading_eclat_start
    global fading_eclat_start
    # animer l'ajout / retrait comme update_draw_score
    if eclat[1] > 0 and pygame.time.get_ticks() - last_eclat_change_tick > BEFORE_ADDING*5:
        eclat[1] = eclat[1] / (max(1.1, ADDING_SPEED / 3))
        if eclat[1] < 1:
            eclat[1] = 0

    if eclat[2] < 0 and pygame.time.get_ticks() - last_eclat_change_tick > BEFORE_ADDING*5:
        eclat[2] = eclat[2] / (max(1.1, ADDING_SPEED / 3))
        if eclat[2] > -1:
            eclat[2] = 0
    
    if eclat[1] or eclat[2] :
        fading_eclat_start = gtick()




    eclat_display = math.ceil(eclat[0] - eclat[1] - eclat[2])
    color = (255, 255, 255) if (not eclat[1] and not eclat[2]) else ((255, 0, 0) if not eclat[1] else (255, 220, 30))
    eclat_text = font.render(f"Éclats : {eclat_display} {'+ '+str(math.floor(eclat[1]))+' ' if eclat[1] else ''}{'- '+str(abs(math.floor(eclat[2]))) if eclat[2] else ''}", True, color)

    eclat_text.set_alpha(int(255*(1-fading)))
    screen.blit(eclat_text, (SCREEN_WIDTH - eclat_text.get_width() - 20, 20))


OMBRES = {
    "contour" : lambda dx, dy : True,
    "sous" : lambda dx, dy : dx < 0,
}

def show_message(message, color=(255,255,255), pos=(20,20), font=font, recenterx=True, shadow_width=3, type_shadow = OMBRES["contour"], shadow_color = (0,0,0)):
    text_surf = font.render(message, True, color)
    shadow_surf = font.render(message, True, shadow_color)

    x = pos[0] - (text_surf.get_width() // 2 if recenterx else 0)
    y = pos[1]

    for dx in range(-shadow_width, shadow_width + 1):
        for dy in range(-shadow_width, shadow_width + 1):
            if dx == 0 and dy == 0 and type_shadow(dx,dy):
                continue
            screen.blit(shadow_surf, (x + dx, y + dy))

    screen.blit(text_surf, (x, y))

def curving(ratio) :
    progress = abs(1 - 2*ratio)
    return math.sqrt(progress)

def not_removed_cards(cards) :
    return [card for card in cards if not card.remove]

def get_row(cards, index) :
    return sorted([card for card in cards if card.row==index and not card.remove], key = lambda card : card.row)



def add_lives(ch, extra_var=None) :
    global move
    global last_live_change_tick
    last_live_change_tick = pygame.time.get_ticks()

    if (lvl_bulle_deau := objects_lvl.get("Bulle_D_Eau",0)) and ch<0:
        if move < lvl_bulle_deau+1 :
            player_lives[3]+=ch
            add_show_effect("Bulle_D_Eau")
            add_score("damage_dodge")
            return # on ne perd pas de vie du tout


    if (lvl_lame_sadique := objects_lvl.get("Lame_Sadique",0)) and ch<0 : 
        ch -= (lvl_lame_sadique // 4) + 1
        add_show_effect("Lame_Sadique")
    
    if (lvl_chat_comp := objects_lvl.get("Chat_De_Compagnie",0)) and ch>0 : 
        if random.random() < (lvl_chat_comp / lvl_chat_comp+4) : ch += 1
        add_show_effect("Chat_De_Compagnie")
        
    player_lives[0] += ch
    if ch>=0 :
        player_lives[1] += ch
    else :
        player_lives[2] += ch
    
    for i in range(ch) :
        if ch>0 : add_score("live_gained", extra_var)
        else : add_score("life_loosed", extra_var)

blend_constant = 0
hyper_blend_constant = 0
blend_var = 1
hyper_blend_var = 1
BLEND_VAR_SPEED = 100
HYPER_BLEND_VAR_SPED = 400

def update_clock(waiting = 0) :
    
        global blend_constant, blend_var, awaiting_time

        blend_constant += blend_var/BLEND_VAR_SPEED
        if blend_constant >= 1 :
            blend_constant = 1
            blend_var *= -1
        elif blend_constant <= 0 :
            blend_constant = 0
            blend_var *= -1

        global hyper_blend_constant, hyper_blend_var

        hyper_blend_constant += hyper_blend_var/HYPER_BLEND_VAR_SPED
        if hyper_blend_constant >= 1 :
            hyper_blend_constant = 1
            hyper_blend_var *= -1
        elif hyper_blend_constant <= 0 :
            hyper_blend_constant = 0
            hyper_blend_var *= -1

        ## On va représenter tout ce qui doit être présent dans ton contexte (passe au dessus)
        show_effects(screen)


        global fading_eclat_start
        ratio_fading = 0 if (gtick() - fading_eclat_start) < BEFORE_ADDING*3 else max(0,min(1,(gtick() - fading_eclat_start)/DUREE_ECLAT_FADING))

        update_draw_eclats(fading = ratio_fading)

        pygame.display.flip()
        clock.tick(FPS)

        if awaiting_time > 0 :
            awaiting_time -= 1
            if awaiting_time < 0 : awaiting_time = 0
            update_clock() # appel recursif pour gérer le temps d'attente
            

def add_score(action_or_int, extravar=None) :
    global last_score_change_tick
    last_score_change_tick = pygame.time.get_ticks()
    if isinstance(action_or_int, int) :
        player_score[0]+=action_or_int 
        if action_or_int >= 0 :
            player_score[1]+=action_or_int 
        else :
            player_score[2]+=action_or_int
    else :
        score_applique = bonus_score(action_or_int, extravar)
        player_score[0] += score_applique
        if score_applique >= 0 :
            player_score[1] += score_applique
        else :
            player_score[2] += score_applique

def add_eclat(quantity) :
    global last_eclat_change_tick
    last_eclat_change_tick = pygame.time.get_ticks()
    eclat[0] += quantity
    if quantity > 0 :
        eclat[1] += quantity
    elif quantity < 0 :
        eclat[2] += quantity
    add_score("gain_eclat",extravar=quantity)



def pop_up(cards:list[Card],message, all_cards, message_color=(255,255,255), font=pop_up_font, time=None) :
    if time is None : time = len(message)*30
    
    starting_time = pygame.time.get_ticks()

    while (timer := pygame.time.get_ticks() - starting_time) < time :
                draw_bg()
                update_draw_cards(all_cards)
                for card in cards :
                    show_message(message, message_color, font=font, pos=(card.rect.centerx, card.rect.y+10+5*(curving(timer/time))))
                update_draw_score(player_score, player_lives)
                update_clock()


    


def small_reveal(cards : list[Card], all_cards, message=None, message_color = (255,255,255), time=showing_time, font=font, me : None|list[Card]=None) :
        global selection_locked
        was_locked = selection_locked
        selection_locked = True

        if message is None : message = f"Révélation de {len(cards)} cartes"

        if len(cards)>0 :
            for card in cards :
                card.flipped=True 
            
            while not all(card.flip_progress==1 for card in cards) :
                draw_bg()
                show_message(message, message_color, recenterx=False)
                update_draw_cards(all_cards)
                update_clock()
            
            starting_time = pygame.time.get_ticks()

            if me and (pipette_lvl := objects_lvl.get("Pipette_Elementaire",0)) :
                card_enhanced = []
                all_tags = sorted(sum((list(troupe.tags) for troupe in me),start=[]), key= lambda t : t[1])
                for tag in all_tags :
                    tag_upgrade = (tag[0], tag[1]+max(0,pipette_lvl-1), tag[2])
                    for card in cards :
                        try_put = card.put_tag(tag_upgrade)
                        if try_put and card not in card_enhanced : card_enhanced.append(card)
              
                if card_enhanced :
                    add_show_effect("Pipette_Elementaire")
                    pop_up(card_enhanced, "Pipeté !", all_cards, (230,80,200), time=300)
            
            for card in cards : # Ceci sert pour Fantome a cheveux
                if card.name == "Fantome_A_Cheveux" and fighters_lvl.get(card.name,0) :
                    to_add = []
                    for character in me : # Je parcours tout ceux qui m'ont révélé
                        print("Character in me : ",character.name)
                        if fighters_lvl.get(character.name, 0) : # Je vérifie la personne qui m'a révélé a sa compétence activé
                            if character.name == "Fantome_A_Cheveux" : # Si c'est un autre fantome à cheveux, j'ajoute toutes ses copies que je n'ai pas
                                to_add.extend(added := [e.name for e in character.character_copied if e not in card.character_copied and e not in to_add])
                                print("added",added)
                            else :
                                if character.name not in card.character_copied : to_add.append(character.name) # Sinon j'ajoute directement le personnage
                    
                    print("to_add",to_add)
                    card.character_copied.extend(to_add)
                    
            
                


            while pygame.time.get_ticks() - starting_time < time :
                
                draw_bg()
                show_message(message, message_color, recenterx=False)
                update_draw_cards(all_cards)
                update_clock()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif acceleration(event) and starting_time :
                        starting_time -= time/2
                        break
            
            for card in cards : 
                card.flipped = False
            
            while not all(card.flip_progress==0 for card in cards) :
                draw_bg()
                show_message(message, message_color, recenterx=False)
                update_draw_cards(all_cards)
                update_clock()
        
        selection_locked = was_locked
            
        
        



def activate_effect(selection, cards : list[Card], nb_move) :
    lesnoms = [card.name for card in selection]
    matches = {card.name : sum(1 for card2 in selection if card2 != card and ca_match(card,card2)) for card in selection}
    already_done = []
    for card in selection: 
        card.activate_effect(matches[card.name], selection, lesnoms, cards, fighters_lvl.get(card.name, 0), already_done, nb_move)


def random_cols(cards, priviligies_bigger_col = 0, include_remove = False) : # renvoit les colonnes disponibles dans un ordre aléatoire. priviligies_bigger_col : 0 = inactif / n = impacte : colonne plus occupé = plus fort
    if not priviligies_bigger_col :
        num_col = random.choices(list( cols := set(card.col for card in cards if not card.remove or include_remove)), k=len(cols))[0]
    else :
        poids_dict = {}
        for card in cards :
            if not card.remove or include_remove :
                poids_dict[card.col] = poids_dict.get(card.col,0)+1
        colonnes = [i for i in poids_dict]
        poids = [poids_dict[i]*priviligies_bigger_col for i in poids_dict]
        num_col = random.choices(colonnes, weights=poids, k=len(colonnes))[0]
    
    return [card for card in cards if card.col==num_col and not card.remove]






def activate_object_effect(objet, lvl, cards) :
    if objet == "Canon_A_Energie" :
        global charge 
        if charge >= 9 :
            add_show_effect("Canon_A_Energie", (200+lvl*50)*((charge//9)))
            wait_with_cards(cards, 200)
        while charge >= 9 :
            charge = max(0,charge-9)
            col = random_cols(cards, lvl>=3 and lvl/3)
            add_score(2*len(col))
            small_reveal(col, cards, "BOOOOOOM", message_color=(240,240,100),font=font, time=200+lvl*100, me=None)




def ca_match(card1,card2):
    return card1.name == card2.name

def distance(card1, card2) :
    return abs(card1.row - card2.row) + abs(card1.col - card2.col)

def est_adjacent(card1,card2, radius=1) :
    if (card2.name=="Maniak" and fighters_lvl.get("Maniak",0)) : return True 
    elif (card1.name=="Maniak" and fighters_lvl.get("Maniak",0)>3) : radius += fighters_lvl.get("Maniak",0)//3


    # print(f"{card1.name, card1.row, card1.col =}", f"{card2.name, card2.row, card2.col =}", sep=" | ")
    return abs(card1.row - card2.row) + abs(card1.col - card2.col)<=radius

def wait_with_cards(cards,time) :
    init = gtick()
    while gtick() - init < time :
        draw_bg()
        update_draw_cards(cards)
        update_draw_score(player_score,player_lives)
        update_clock()

def wait_finish_return(cards):
    # Attendre tant qu'il y a au moins une carte en cours d'animation (0 < progress < 1)
    while any((card.flip_progress!=1 and card.flipped) or (card.flip_progress!=0 and not card.flipped) for card in cards):
        draw_bg()
        update_draw_cards(cards)
        update_draw_score(player_score, player_lives)
        update_clock()

# --- JEU PRINCIPAL ---
def play_memory(num_pairs=8, forced_cards = None):
    global selection_locked, move, last_succeed_move, combo
    cards = create_board(num_pairs, forced_cards)
    player_score[0]
    last_selection_time = 0
    running = True
    start_show_time = 0
    ending = 0
    move = 1

    while running:
        draw_bg()

        # événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif validation(event) and ending :
                running = False 
                break

            elif acceleration(event) and start_show_time :
                start_show_time -= showing_time/2
                break

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not selection_locked :
                    if getattr(event, "button", None) == 2 : # touche de pré-selection (clique molette)
                        for card in cards:
                            if card.rect.collidepoint(event.pos) and not card.matched and not card.flipped and not card.remove and (card not in selection):
                                if card.selected :
                                    card.selected = False
                                    selection.remove(card)
                                elif len(selection) < SELECTION_LIMIT:
                                    card.selected = True
                                    selection.append(card)
                                    last_selection_time = pygame.time.get_ticks()
                    
                    if getattr(event, "button", None) == 3 : # touche de déselection (clique droit)
                        for card in cards:
                            if not card.flipped and not card.remove and card.selected:
                                if card.selected :
                                    card.selected = False
                                    selection.remove(card)
                    
                    if getattr(event, "button", None) == 1 : # touche de révellation (montre une carte : clic gauche)
                        for card in cards:
                            if card.selected and not card.remove and not card.flipped :
                                card.flipped = True
                            
                            if not card in selection and not card.remove and not card.selected and len(selection) < SELECTION_LIMIT and card.rect.collidepoint(event.pos)  :
                                card.selected = True 
                                selection.append(card)
                                card.flipped = True
                                last_selection_time = pygame.time.get_ticks()
                        

        # mise à jour
        for card in cards:
            card.update()

        # logique du jeu
        if len(selection) == SELECTION_LIMIT:
            selection_locked = True
            for card in selection :
                card.flipped=True

            # attendre que les deux soient bien visibles
            if all(card.flip_progress==1 for card in selection):

                selection_locked = True
                if not start_show_time :
                    start_show_time = pygame.time.get_ticks()
                    activate_effect(selection, cards, nb_move=move)
                
                elif pygame.time.get_ticks() - start_show_time > showing_time :
                    names = [t.name for t in selection]
                    if any(names.count(name)>1 for name in names):


                        if last_succeed_move == move-1 :
                            combo = combo + 1
                        else :
                            combo = 1
                        
                        last_succeed_move = move
                        add_score("match")



                        for c in selection:
                            c.matched = True
                            c.flipped = False
                            c.remove = True
                    else:
                        add_lives(-1)
                        add_score("dontmatch")
                        for c in selection:
                            c.flipped = False
                    
                    for card in cards :
                        card.selected = False
                    
                    for card in cards :
                        card.check_modification(move)
                    
                    wait_finish_return(cards)

                    for o, lvl in objects_lvl.items() :
                        activate_object_effect(o,lvl, cards)
                    
                    last_selection.clear()
                    last_selection.extend(selection)
                    selection.clear()

                    start_show_time = 0
                    selection_locked = False

                    move += 1

        # dessin des cartes
        for card in cards:
            card.draw(screen)

        # texte
        update_draw_score(player_score, player_lives)
        

        # conditions de fin
        if all(c.remove for c in cards) and player_lives[0] > 0:
            
            update_draw_score(player_score, player_lives)
            end_text = font.render(f"Grille finite ! Eclats Gagnés : {game['round']*3}", True, (255, 255, 0))
            screen.blit(end_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2))
            end_text2 = font.render(f"PV regagné : {regain_PV_manche}", True, (255,150,150))
            screen.blit(end_text2, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + end_text.get_height()+5))
            if not ending :
                add_score("end_play")
                add_eclat(game['round']*3)
                add_lives(regain_PV_manche)
            ending = True

        
        elif player_lives[0] <= 0:
            refresh()
            cards.clear()
            end_text = font.render("💀 Plus de vies !", True, (255, 50, 50))
            screen.blit(end_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
            selection_locked = True
            ending = True
        
        
        update_clock()

def get_apparition_cards() :
    res = []
    for name, prob in apparation_probability.items() :
        if random.random() <= prob :
            res.append(name)
    
    return res

def refresh() :
    draw_bg()

def get_next_prob(current_prob) :
    return (0.2 if current_prob==0 else current_prob + 0.1) + random.randint(0,10)/100

def proposal(card_name) :
    global selection_locked
    selection.clear()
    from description import generer_apparition_message, generer_message_de_description
    selection_locked = False
    
    # Create and display the card in the center
    msg = font.render("Un combattant souhaite collaborer avec vous !", True, (255, 255, 255))
    card_display = Card(
        SCREEN_WIDTH // 2 - 150,
        SCREEN_HEIGHT // 2 - 250 + 100,
        card_name,
        all_images_dict[card_name],
        (255, 150, 150),
        250,
        location="proposal"
    )
    card_display.tick_appear = gtick()

    card_display.flipped = True


    description_surface = generer_apparition_message(
        {"nom": card_name,
         "ancienne_probability": apparation_probability.get(card_name, 0)*100,
         "new_probability": int((new_prob := get_next_prob(apparation_probability.get(card_name, 0)))*100),
         "prix": (prix:=math.ceil(UPGRADES_COST.get(card_name, 5)*(apparation_probability.get(card_name, 0)+0.1)*10))},width=SCREEN_WIDTH - 20, height=SCREEN_HEIGHT - 200)
    waiting = True

    description_surface_carte = generer_message_de_description(
                    {"nom": card_name, "lvl":fighters_lvl.get(card_name, 1), "lvl_init": fighters_lvl.get(card_name, 1), "proposal":True},
                    width=SCREEN_WIDTH - 20,
                    height=SCREEN_HEIGHT - card_display.rect.height - 220
    )
    
    while waiting:
        refresh()

        screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 130))
        if description_surface :
            screen.blit(description_surface, (10, SCREEN_HEIGHT // 2 + description_surface.get_height() + card_display.rect.height // 2))
        
        if description_surface_carte:
            screen.blit(description_surface_carte, (10, SCREEN_HEIGHT - description_surface_carte.get_height() - 10))
        
        update_draw_eclats()
        update_draw_cards([card_display])
        # update_draw_score(player_score, player_lives)
  
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif validation(event) and eclat[0]>=prix :
                apparation_probability[card_name] = new_prob
                add_eclat(-prix)
                waiting = False
            elif rejet(event) :
                waiting = False
        
        update_clock()

def borne(nb, borneInf=0, borneSup=1):
    return min(borneSup, max(borneInf, nb))

def acceleration(event) :
    return (event.type == pygame.KEYDOWN and event.key == (pygame.K_SPACE)) or (event.type == pygame.MOUSEBUTTONDOWN and getattr(event, "button", None) == 2)
def validation(event):
    return (
        (event.type == pygame.KEYDOWN and event.key in (pygame.K_y, pygame.K_SPACE, pygame.K_o))
        or (event.type == pygame.MOUSEBUTTONDOWN and getattr(event, "button", None) == 1)
    )

def rejet(event):
    return (
        (event.type == pygame.KEYDOWN and event.key in (pygame.K_n, pygame.K_ESCAPE, pygame.K_DELETE))
        or (event.type == pygame.MOUSEBUTTONDOWN and getattr(event, "button", None) == 3)
    )

def get_bonus_lvl(name) :
    if fighters_lvl.get(name,0) == 0 : return 1
    nb = random.random()
    return level_upgrade_base + sum(1 for threshold in bonus_lvl_probabilities if nb <= threshold)

from collections import deque
class Movement() :
    def __init__(self, stack_position_memory = 50):
        
        self.mode = None 
        self.enable = False
        self.ended = False
        self.stack_memory = stack_position_memory

        # Force effet 
        self.momentum_x = None
        self.momentum_y = None 
        
        self.gravity = 0 # peut être définit à autre chose que 9.81

        # Straight line or trajectory
        self.start_time = None 
        self.start_pause_time = None

        self.duration = None
        self.coords_start = None # tuple de coords x/y
        self.coords_end = None 
        self.speed = None
        self.actual_coords = None
        self.previous_coords = deque()
        self.trajectory = []
    
    def set_movement(self, duration = None, speed = None, special_trajectory = None, coords_start = None, coords_end = None) :
        """Met à jour la trajectoire en fonction des paramètres d'entrée. Plusieurs moyen de définir une trajectoire sont possibles
        - speed + coords_start + coords_end : déplacement à vitesse déterminé
        - duration + coords_start + coords_end : déplacement à durée déterminé
        - Vitesse + special_trajectory : trajectoire à vitesse déterminé
        - duration + special_trajectory : trajectoire à durée déterminé
        
        A l'heure actuelle seul les déplacements sont codés, ni les poursuites, ni les trajectoires, ni la physique"""
        self.mode, self.trajectory, self.speed, self.duration, self.start_time, self.coords_end, self.coords_start, self.actuel_cords, *self.reste = (None,)*30
        if speed and coords_start and coords_end :
            self.type = "move_speed"
            self.speed = speed
            self.coords_start = coords_start
            self.coords_end = coords_end
            self.actual_coords = coords_start
            self.previous_coords.append(coords_start)
        elif duration and coords_start and coords_end :
            self.type = "move_time"
            self.duration = duration
            self.coords_start = coords_start
            self.coords_end = coords_end
            self.actual_coords = coords_start
            self.previous_coords.append(coords_start)
        elif special_trajectory and speed :
            self.type = "path_speed"
            self.trajectory = special_trajectory
            self.previous_coords.append(special_trajectory[0])
        elif special_trajectory and duration :
            self.type = "path_duration"
            self.trajectory = special_trajectory
            self.previous_coords.append(special_trajectory[0])
        else :
            raise ValueError("Vous avez indiqué des mauvais paramètre pour le mouvement")
    
    def start(self):
        if self.ended : return False
        if self.start_pause_time :
            time_in_pause = gtick() - self.start_pause_time
            self.start_pause_time = 0
            self.start_time += time_in_pause

        if not self.start_time : self.start_time = gtick()
        self.enable = True

    def pause(self):
        self.enable = False
        self.start_pause_time = gtick() 
    
    def end(self) :
        self.enable = False
        self.ended = True
    
    def restart(self) :
        self.start_time = 0
        self.actual_coords = self.coords_start
        self.start_time = gtick()
        self.start_pause_time = 0
        self.enable = True
    
    def get_delta(self,from_time = 0) :
        if not from_time :
            return (self.actual_coords[0] - self.previous_coords[-1][0], self.actual_coords[1] - self.previous_coords[-1][1])
        else :
            raise NotImplemented
    
    def get_x(self) :
        return round(self.actual_coords[0])
    def get_y(self) :
        return round(self.actual_coords[1])
    def get_coords(self) :
        return (self.get_x(), self.get_y())
    
    def change_coords(self,new_cords) :
        self.previous_coords.append(self.actual_coords)
        if len(self.previous_coords)>self.stack_memory :
            self.previous_coords.popleft()
        self.actual_coords = new_cords
    
    def update(self) :
        if self.enable :
            match self.type :
                case "move_speed" :
                    direction = (self.coords_end[0] - self.actual_coords[0], self.coords_end[1] - self.actual_coords[1])
                    norm = math.sqrt((direction[0]**2) + (direction[1]**2))
                    move_norme = (direction[0]/norm, direction[1]/norm)
                    move_final = ((direction[0],move_norme[0]*self.speed), (direction[1],move_norme[1]*self.speed)) # evite de dépasser
                    self.change_coords(self.actual_coords[0] + move_final[0], self.actual_coords[1] + move_final[1])
                    if self.get_coords == self.coords_end :
                        self.end()
                case "move_time" :
                    completion_ratio = borne((gtick() - self.start_time) / self.duration)
                    self.change_coords((self.coords_start[0]*(1-completion_ratio) + self.coords_end[0]*(completion_ratio), self.coords_start[1]*(1-completion_ratio) + self.coords_end[1]*(completion_ratio)))
                    if completion_ratio == 1 :
                        self.end()










def switch_place(card1: Card,card2 : Card, all_cards, time=500, message=None, message_color = (255,255,255), font=font, me : None|list[Card]=None):
    assert card1 in all_cards and card2 in all_cards

    # Crééons 2 mouvements basé sur les positions des deux cartes
    switch1 = Movement()
    switch2 = Movement()
    coords_1 = (card1.init_x, card1.init_y)
    coords_2 = (card2.init_x, card2.init_y)
    print("c1",coords_1)
    print("c2",coords_2)
    switch1.set_movement(duration=time, coords_start=coords_1, coords_end=coords_2)
    switch2.set_movement(duration=time, coords_start=coords_2, coords_end=coords_1)
    switch1.start(), switch2.start()
    while (not switch1.ended) or (not switch2.ended) :

        # J'applique le temps qui passe sur les mouvements et je modifie la position des cartes
        switch1.update(), switch2.update()
        card1.init_x, card1.init_y = switch1.get_coords()
        card2.init_x, card2.init_y = switch2.get_coords()
        draw_bg()
        # update_draw_score()
        update_draw_cards(all_cards)
        if message :
            show_message(message, message_color, recenterx=False)
        update_clock()
    
    card1.col, card1.row, card2.col, card2.row = card2.col, card2.row, card1.col, card1.row


def go_training() :
    # Nettoie l'écran et affiche un écran "fresh" en attendant une action de l'utilisateur
    global selection_locked
    selection.clear()
    selection_locked = False
    from description import generer_message_de_description


    msg = font.render("C'est l'heure de l'entrainement ! Mais qui entrainer ?", True, (255, 255, 255))
    cards_upgrade = random.sample([card for card in all_images if UPGRADES_COST.get(card[0])],training_choices)
    displayer = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
    card_size = min((displayer.width - (training_choices + 1) * 20) // training_choices, displayer.height - 20)
    all_cards : list[Card] = []

    updrade_lvl = {c : get_bonus_lvl(c) for c,_ in cards_upgrade}
    


    for name, image in cards_upgrade :
        x = displayer.x + 20 + len(all_cards) * (card_size + 20)
        y = displayer.y + (displayer.height - card_size) // 2
        all_cards.append(Card(x, y, name, image, (150, 150, 255), card_size, location="training"))
        all_cards[-1].flipped = True

    show_previous_progress = 0
    waiting = True
    ending = False 
    ending_last_time_out = 0
    while waiting:
        refresh()

        screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 50))

        
        pygame.draw.rect(screen, blend_multi(((230,200,130), (180,70,160),(120,95,200)), blend_constant), displayer, border_radius=10)
        update_draw_cards(all_cards)
        # Afficher les éclats en haut à droite
        update_draw_eclats()


        
        # Détecter le passage de souris sur une carte
        mouse_pos = pygame.mouse.get_pos()
        for card in all_cards:
            if card.rect.collidepoint(mouse_pos) and card.flip_progress>=0.5 and not ending:
                lvl = fighters_lvl.get(card.name,0)
                description_surface = generer_message_de_description(
                    {"nom": card.name, "lvl":lvl+updrade_lvl[card.name],"lvl_init": lvl, "prix":UPGRADES_COST.get(card.name, 0)*(lvl+1)},
                    width=SCREEN_WIDTH - 20,
                    height=SCREEN_HEIGHT - displayer.height - 80
                )

                description_surface_previous = None
                if lvl >= 1 and show_previous_progress>0:
                    description_surface_previous = generer_message_de_description(
                        {"nom": card.name, "lvl":lvl, "show_previous":lvl, "lvl_init": lvl, "prix":UPGRADES_COST.get(card.name, 0)*(lvl+1)},
                        width=SCREEN_WIDTH - 20,
                        height=SCREEN_HEIGHT - displayer.height - 80
                    )

                if description_surface:
                    if description_surface_previous and show_previous_progress :
                        # afficher les deux descriptions en fondu selon show_previous_progress
                        alpha_prev = max(0, min(1, show_previous_progress))
                        alpha_curr = 1.0 - alpha_prev

                        # préparer copies pour ne pas modifier les surfaces d'origine
                        surf_prev = description_surface_previous
                        surf_curr = description_surface

                        w_prev, h_prev = surf_prev.get_size()
                        w_curr, h_curr = surf_curr.get_size()
                        max_w = max(w_prev, w_curr)
                        max_h = max(h_prev, h_curr)

                        # appliquer l'alpha (0-255)
                        surf_prev.set_alpha(int(255 * alpha_prev))
                        surf_curr.set_alpha(int(255 * alpha_curr))

                        # fond noir derrière les descriptions
                        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(8, SCREEN_HEIGHT - max_h - 9, max_w+3, max_h+3), border_radius=2)

                        # blit : previous (plus opaque) puis current (plus transparent)
                        screen.blit(surf_prev, (10, SCREEN_HEIGHT - h_prev - 10))
                        screen.blit(surf_curr, (10, SCREEN_HEIGHT - h_curr - 10))
                    else :
                        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(8, SCREEN_HEIGHT - 9 - description_surface.get_height(), description_surface.get_width()+3, description_surface.get_height()+3), border_radius=2)
                        screen.blit(description_surface, (10, SCREEN_HEIGHT - description_surface.get_height() - 10))

                break

        if ((keys := pygame.key.get_pressed())[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                show_previous_progress = min(1,show_previous_progress+SHOW_PREVIOUS_SPEED)
        else :
                show_previous_progress = max(0,show_previous_progress-SHOW_PREVIOUS_SPEED)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif rejet(event):
                waiting = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r :
                cards_upgrade = random.sample(all_images,training_choices)
                displayer = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                card_size = min((displayer.width - (training_choices + 1) * 20) // training_choices, displayer.height - 100)
                all_cards = []
                for name, image in cards_upgrade :
                    x = displayer.x + 20 + len(all_cards) * (card_size + 20)
                    y = displayer.y + (displayer.height - card_size) // 2
                    all_cards.append(Card(x, y, name, image, (150, 150, 255), card_size, location="training"))
                    all_cards[-1].flipped = True
                
            elif event.type == pygame.MOUSEBUTTONDOWN and not selection_locked:
                mouse_pos = event.pos
                for card in all_cards:
                    if card.rect.collidepoint(mouse_pos) and UPGRADES_COST.get(card.name) is not None :
                        cost = UPGRADES_COST.get(card.name, 0) * (fighters_lvl.get(card.name, 0) + 1)
                        if eclat[0] >= cost:
                            add_eclat(-cost)
                            fighters_lvl[card.name] = fighters_lvl.get(card.name,0) + updrade_lvl[card.name]  # Augmenter le niveau du combattant
                            last_selection.clear()
                            last_selection.append(card)
                            selection_locked = True
                            for card in all_cards :
                                card.flipped = False
                            ending = True
        
        if ending :
            if all(card.flip_progress==0 for card in all_cards) :
                if not ending_last_time_out : ending_last_time_out = pygame.time.get_ticks()

                if pygame.time.get_ticks() - ending_last_time_out > 300 :
                    waiting = False

        update_clock()






def end_run() :
    from description import DISPLAY_NAMES
    global best_score
    refresh()
    waiting = 2 
    # Afficher le score et les éclats restants + toutes les cartes amélioré (et leur niveau en survolant dessus)
    while waiting>0:
        refresh()
        
        # Display final score
        final_score_text = font.render(f"Score Final : {player_score[0]}", True, (255, 255, 0))
        screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, 50))

        y_offset = 0

        if player_score[0]>best_score :
            final_score_text_best = desc_italic_font.render(f"Meilleur score !", True, (255, 255, 0))
            screen.blit(final_score_text_best, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, 50 + final_score_text.get_height()+5))
            y_offset += final_score_text_best.get_height() + 10
        
        # Display remaining eclats
        eclat_text = font.render(f"Éclats Restants : {eclat[0]} | Manche : {game["round"]}", True, (255, 200, 100))
        screen.blit(eclat_text, (SCREEN_WIDTH // 2 - eclat_text.get_width() // 2, 100+y_offset))
        
        # Display upgraded fighters
        upgraded_text = font.render("Combattants Améliorés :", True, (150, 200, 255))
        screen.blit(upgraded_text, (50, 150+y_offset))
        
        y_offset += 200
        for fighter_name, level in fighters_lvl.items():
            display_name = DISPLAY_NAMES.get(fighter_name, fighter_name)
            fighter_text = font.render(f"{display_name} - Niveau {level}", True, (200, 200, 255))
            screen.blit(fighter_text, (70, y_offset))
            y_offset += 40
        
        upgraded_text = font.render("Objets :", True, (150, 200, 255))
        screen.blit(upgraded_text, (50, y_offset))
        y_offset += 50

        for o_name, level in objects_lvl.items():
            display_name = DISPLAY_NAMES.get(o_name, o_name)
            o_text = font.render(f"{display_name} - Niveau {level}", True, (200, 200, 255))
            screen.blit(o_text, (70, y_offset))
            y_offset += 40
        # # Display exit message

        if waiting == 1 :
            exit_text = font.render("Appuyez sur ESPACE ou CLIQUEZ pour recommencer", True, (255, 255, 255))
            screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, SCREEN_HEIGHT - 50))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif validation(event) or rejet(event):
                waiting -= 1
        
        update_clock()


# VARIABLES POUR LE SHOP :
last_cards_shop = []

def memo_shop_present():
    cards_images = random.sample(all_objects_images,shop_choices)
    
    last_cards_shop.clear()

    all_x = (20+((SCREEN_WIDTH-40)//shop_choices)*i for i in range(shop_choices))
    for i,card_image in enumerate(cards_images) :
        card_name, card_im = card_image
        card = Card(next(all_x), SCREEN_HEIGHT//2, card_name, card_im, (230,230,20), 200, "shop")
        card.flipped = True
        card.flip_progress = 1
        last_cards_shop.append(card)
    
    msg = font.render("Retenez bien l'ordre de ces cartes pour plus tard !", True, (255, 255, 255))
    waiting = True
    previewed_card = None
    while waiting :
        refresh()
        screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 50))
        
        update_draw_cards(last_cards_shop)
        

        

        mouse_pos = pygame.mouse.get_pos()
        for card in last_cards_shop:
            if card.rect.collidepoint(mouse_pos) and (not previewed_card or not previewed_card.rect.collidepoint(mouse_pos)) and waiting :
                if previewed_card : previewed_card.selected = False
                previewed_card = card
                previewed_card.selected = True
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and not selection_locked:
                waiting = False
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif validation(event) or rejet(event):
                waiting = False
        
        if previewed_card : previewed_card.draw(screen)

        update_clock()
    
    for card in last_cards_shop :
        card.flipped = False
    
    while not all(card.flip_progress==0 for card in last_cards_shop) :
        refresh()
        screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 50))

        for card in last_cards_shop :
            card.selected = False
        update_draw_cards(last_cards_shop)
        if previewed_card : previewed_card.draw(screen)
        update_clock()


def memo_shop_receive() :

    assert last_cards_shop, "Petite visite au shop avant quand meme ?"
    global selection_locked, wait_for_respons
    selection.clear()
    selection_locked = False
    from description import generer_message_de_description
    from description import desc_italic_font


    msg = font.render("Rebienvenu ! Vous vous souvenez bien de tous ?", True, (255, 255, 255))
    msg2 = desc_italic_font.render("Effectuer une paire pour que l'achat vous soit proposé", True, (255, 255, 255))

    cards_upgrade =  2*last_cards_shop

    order = [i for i in range(len(last_cards_shop))]
    random.shuffle(order)

    selection.clear()
    for i,card in enumerate(cards_upgrade) :
        card.selected = False
        if i < len(cards_upgrade)//2 :
            cards_upgrade[i] = Card(last_cards_shop[order[i]].x, card.y-150, card.name, card.image, card.color, card.rect.width, location="shop")
            cards_upgrade[i].flipped = True
        else :
            card.flipped = False
            card.init_y += card.rect.height - 120
            card.y = card.init_y

        card.flip_progress = 0


    wait_for_respons = False
    ending = False 
    ending_last_time_out = 0
    while not ending:
        refresh()

        screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 50))
        screen.blit(msg2, (SCREEN_WIDTH // 2 - msg2.get_width() // 2, 60 + msg.get_height()))

        
        # pygame.draw.rect(screen, blend_multi(((230,200,130), (180,70,160),(120,95,200)), blend_constant), displayer, border_radius=10)
        update_draw_cards(cards_upgrade)
        # Afficher les éclats en haut à droite
        update_draw_eclats()


        
        # Détecter le passage de souris sur une carte
        mouse_pos = pygame.mouse.get_pos()
        for card in cards_upgrade:
            if card.rect.collidepoint(mouse_pos) and card.flip_progress>=0.5 and not card.remove and not ending:
                description_surface = generer_message_de_description(
                    {"nom": card.name, "lvl":objects_lvl.get(card.name, 0)+1,"lvl_init": objects_lvl.get(card.name, 0), "prix":UPGRADES_COST.get(card.name, 0)*(objects_lvl.get(card.name, 0)+1)},
                    width=SCREEN_WIDTH - 20,
                    height=SCREEN_HEIGHT - 90
                )
                if description_surface:
                    pygame.draw.rect(screen, (0,0,0), pygame.Rect(8,SCREEN_HEIGHT - description_surface.get_height() - 9, description_surface.get_width(), description_surface.get_height()),border_radius=3)
                    screen.blit(description_surface, (10, SCREEN_HEIGHT - description_surface.get_height() - 10))
                break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()    
            elif event.type == pygame.MOUSEBUTTONDOWN and not selection_locked:
                mouse_pos = event.pos
                for card in cards_upgrade:
                    if card.rect.collidepoint(mouse_pos) and card in selection :
                        card.selected = False
                        selection.remove(card)  
                    elif card.rect.collidepoint(mouse_pos) and card not in selection and len(selection)<2 :
                        card.selected = True
                        selection.append(card)

                        #cost = UPGRADES_COST.get(card.name, 0) * (fighters_lvl.get(card.name, 0) + 1)
                        # if eclat[0] >= cost:
                        #     add_eclat(-cost)
                        #     fighters_lvl[card.name] = fighters_lvl.get(card.name,0) + updrade_lvl[card.name]  # Augmenter le niveau du combattant
                        #     last_selection.clear()
                        #     last_selection.append(card)
                        #     selection_locked = True
                        #     for card in all_cards :
                        #         card.flipped = False
                        #     ending = True
            elif rejet(event) and wait_for_respons :
                selection_locked = False 
                wait_for_respons = False
                
                for card in selection :
                    card.selected = False
                    card.remove = True 
                    for card2 in cards_upgrade :
                        if card2.name==card.name :
                            card2.remove = True
                selection.clear()
            elif validation(event) and wait_for_respons :
                if selection[0].name == selection[1].name and (cost := UPGRADES_COST.get(selection[0].name, 0)*objects_lvl.get(selection[0].name, 1)) <= eclat[0] :
                    add_eclat(-cost)
                    objects_lvl[selection[0].name] = objects_lvl.get(selection[0].name,0)+1
                    add_object(selection[0].name)
                
                selection_locked = False 
                wait_for_respons = False
                
                for card in selection :
                    card.selected = False
                    card.remove = True 
                    for card2 in cards_upgrade :
                        if card2.name==card.name :
                            card2.remove = True
                
                selection.clear()
                
                
        
        if len(selection) == 2 :
            for card in selection : card.flipped = True
            if all(card.flip_progress==1 for card in selection) :
                if selection[0].name == selection[1].name :
                    msg = font.render("Voulez vous acheter ceci pour "+str(UPGRADES_COST.get(selection[0].name,5)*objects_lvl.get(selection[0].name, 1)) +" éclats ?", True, (255, 255, 255))
                    
                else :
                    msg = font.render("Mauvaise réponses, cartes perdus !", True, (255, 150, 150))
                
                wait_for_respons = True 
                selection_locked = True
        
        elif len([card for card in cards_upgrade if not card.remove]) == 0 :
            ending = True
        
        else :
            msg = font.render("Rebienvenu ! Vous vous souvenez bien de tous ?" if len([card for card in cards_upgrade if not card.remove])==2*len(last_cards_shop) else "Continuez continuez !!", True, (255, 255, 255))
            

        
        update_clock()
    
    last_cards_shop.clear()



    

def do_next() :
    global selection_locked
    global move

    memo_shopped = False
    while player_lives[0]>0 :
        move = 0

        if game["round"]%2==0 and not memo_shopped and (not "proposal" in game["state"]):
            game["state"]="memo_shop"
            memo_shopped = True
        if game["state"] == "play" :
            switch_bg_to(BG_COLORS["play"])

            selection_locked = False
            play_memory(num_pairs= 2+(game["round"]//2), forced_cards=get_apparition_cards())

            memo_shopped = False

            if player_lives[0]>0 :
                game["round"] += 1
                game["state"] = "proposal_To_training"
            else :
                game["state"] = "end_run"
        
        elif game["state"] == "training" :
            switch_bg_to(BG_COLORS["training"])
            selection_locked = False
            go_training()
            if random.random() < proposal_after_training_prob :
                game["state"] = "proposal_To_play"
            else :
                game["state"] = "play"
        
        elif "proposal" in game["state"]  :
            switch_bg_to(BG_COLORS["proposal"])
            selection_locked = False
            cards_to_propose = last_selection[-1]
            proposal(cards_to_propose.name)

            game["state"] = game["state"].split("_To_", maxsplit=1)[1] or "play"
        
        elif game["state"] == "memo_shop" :
            switch_bg_to(BG_COLORS["shop"])

            if not last_cards_shop :
                memo_shop_present()
            else :
                memo_shop_receive()
            
            game["state"]= "training"
    switch_bg_to(BG_COLORS["end"])
    end_run()

    start_run(**run_parameter)
    do_next()


def add_object(name):
    lvl = objects_lvl.get(name,0)

    if name == "Reveil_Endormi" :
        global showing_time
        showing_time += 300
        add_show_effect("Reveil_Endormi",1500)
    
    if name == "Bouquet_Medicinal" :
        add_lives(lvl*5,"from_heal_object")
        add_show_effect("Bouquet_Medicinal")



# --- LANCEMENT DU JEU ---
if __name__ == "__main__":

    # # Pour beta_test :
    # guaranted = [("8_Volt",4),("Tireur_Pro",4)] # (nom, niveau)
    # guaranted_objet = [("Canon_A_Energie",5)] # (nom, niveau)

    # for name, lvl in guaranted :
    #     apparation_probability[name] = 1
    #     fighters_lvl[name] = lvl
    
    # for o, lvl in guaranted_objet :
    #     objects_lvl[o] = lvl 
    #     add_object(o)



    start_run(**run_parameter)
    # apparation_probability["Catchy"]=1
    # fighters_lvl["Catchy"]=1
    while True :
        do_next()
