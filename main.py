import pygame
import os
import random
import math
import sys
import time
pygame.init()

# --- CONFIGURATION ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
grids = [] # cette liste globale contient l'ensemble des objets de classe grid instanciés. Cela permet d'aisément modifier leur taille en modifier la taille de l'ecran
last_window_size_change= pygame.time.get_ticks()


DEBUG_SHOW_GRID = False


FPS = 60
FLIP_SPEED = 10 # vitesse de retournement des cartes
SELECTED_SPEED = 50 # vitesse d'agrandissement des cartes sélectionnées
SELECTION_LIMIT = 2
SELECTION_BIGGER_SCALE = 1.05 # échelle d'agrandissement des cartes sélectionnées
# REVEAL_DELAY = 1500  # ms (1.5 s)

BEFORE_ADDING = 200  # ms pendant lequel l'affichage des variations restent afficher
DUREE_ECLAT_FADING = 1000 # ms durée de l'effet de fading des éclats qui se désafichent
ADDING_SPEED = 1.1 # Vitesse à laquelle les éclats gagné/perdus sont "déposé" dans le compteur 

# Pour les vibrations des cartes
DZITT_SPEED = 15

# Pour les effets visuels de rebondissement
BONCE_EFFECT_TIME = 300
BONCE_EFFECT_INTENSITY = 30
SHOW_PREVIOUS_SPEED = 0.05 # Vitesse de transition entre les stats du niveau actuel et celle du nouveau niveau

SWITCH_BACKGROUND_SPEED = 1000

accelere = False # quand vaut True, certaines annimations passent plus vite
run_parameter = {} # Modifiers pour le lancement de la prochaine run
last_proposal_accepted = None # deviendra la derniere carte accéptée dans une Proposition
this_level_score = 0


# SEED=1893894
# random.seed(1893894)

best_score = 0



# SCORES représente les gains initiaux de points pour chaque action du jeu (les actions ne sont pas toutes rentrées ici)
SCORES = {
    "match" : 5,
    "dontmatch" : 0,
    "end_play" : 10
}

# Prix d'achat / d'amélioration de toutes les cartes du jeu (objet comme personnages)
UPGRADES_COST = {
    "8_Volt" : 2,
    "Michel" : 5,
    "Max" : 5,
    "Flosette":5,
    "Le_Vrilleur":6,
    "Lame_Sadique":5,
    "Bulle_D_Eau":6,
    "Reveil_Endormi":4,
    "Allumette":4,
    "Pipette_Elementaire":7,
    "Tireur_Pro":5,
    "Piquante":6,
    "Chat_De_Compagnie":6,
    "Canon_A_Energie":5,
    "Bouquet_Medicinal":5,
    "Ghosting":8,
    "Maniak":7,
    "Mc_Cookie":3,
    "Fantome_A_Cheveux":4,
    "Catchy":4,
    "Bubble_Man":2,
    "Piouchador":4,
    "Lo" : 4,
    "Felinfeu":5,
    "Lori_Et_Les_Boaobs":3,
    "Celeste":5,
    "Trognon":4,
    "Bossu_Etoile":4,
}



# --- INITIALISATION ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Brutal Memory")
clock = pygame.time.Clock()

from font import *



#============================== DATA LOADING ===============================#

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

all_images = load_images("cards_pict") # Contient les paires (nom, Image) des personnages
all_objects_images = load_images("objects_pict")
all_benec_malec_images = load_images("benec_malec_pict") # Contient les paires (nom, Image) des personnages

all_images_dict = dict(all_images) # De même mais avec comme clé le nom et comme valeur l'image
all_objects_dict = dict(all_objects_images)
all_belec_malec_dict = dict(all_benec_malec_images)
all_benec = [name for name, _ in all_benec_malec_images if "benec" in name]
all_malec = [name for name, _ in all_benec_malec_images if "malec" in name and name!="default_malec_malus"]
all_malus = [name for name,_ in all_benec_malec_images if "malus" in name]
all_benec_dict = { name: all_belec_malec_dict[name] for name in all_benec }
all_malec_dict = { name: all_belec_malec_dict[name] for name in all_malec }
all_malus_dict = { name: all_belec_malec_dict[name] for name in all_malus }

#=============================== RANDOMISERS =============================#

run_seed = int(random.random()*10000)
random_event_use = {} # dictionnaire qui compte le nombre d'utilisation d'un event aléatoire donné

def get_event_id(event_name) : 
    """Définit l'ID de l'évènement en prenant [nom de l'évenement] + [seed de la run] + [nombre d'utilisation de l'évènement dans la run]
    Cela garantit que chaque appel à un évènement aléatoire donné dans une run donnée produira toujours le même résultat, mais que deux appels successifs à un même évènement produiront des résultats différents"""
    random_event_use[event_name] = random_event_use.get(event_name,0)+1
    return f"{event_name}+{run_seed}+{random_event_use[event_name]}"

def get_random(event_name="generic_event") :
    """Retourne un float aléatoire entre 0 et 1, en fonction de l'event_name et du run_seed"""
    event_id = get_event_id(event_name)

    random.seed(event_id)
    res = random.random()
    random.seed(run_seed)
    return res

def seed_choice(population, event_name="generic_choice") :
    """Retourne un élément aléatoire de la population donnée, en fonction de l'event_name et du run_seed"""
    event_id = get_event_id(event_name)

    random.seed(event_id)
    choice = random.choice(population)
    random.seed(run_seed)
    return choice

def seed_choices(population, k=1, cum_weight=None, event_name="generic_choices") :
    """Retourne k éléments aléatoires de la population donnée, en fonction de l'event_name et du run_seed"""
    event_id = get_event_id(event_name)

    random.seed(event_id)
    if not cum_weight :
        choices = random.choices(population,k=k)
    else :
        choices = random.choices(population,k=k, cum_weights=cum_weight)
    random.seed(run_seed)
    return choices

def seed_sample(things, k=1, event_name="generic_sample") :
    """Retourne k éléments aléatoires distincts de la population donnée, en fonction de l'event_name et du run_seed"""
    event_id = get_event_id(event_name)

    random.seed(event_id)
    choice = random.sample(things, k=k)
    random.seed(run_seed)
    return choice

def seed_shuffle(things, event_name="generic_shuffle") :
    """Mélange la liste donnée en place, en fonction de l'event_name et du run_seed"""
    event_id = get_event_id(event_name)
    random.seed(event_id)
    random.shuffle(things)
    random.seed(run_seed)





#================================= PLAYER_INFO ===================================#

# PLAYER INFO

# Utile pour faire afficher les variations de score un certains temps
last_score_change_tick = pygame.time.get_ticks() 
last_live_change_tick = pygame.time.get_ticks()
last_eclat_change_tick = pygame.time.get_ticks()

selection : list["Card"] = [] # sera la liste des cartes sélectionné -> passe à 2 = révèlent
selection_locked = False

selection_overload = 0 # innutilisé pour l'instant

last_selection : list["Card"] = [] # sera la liste des cartes sélectionné au tour précédent
showing_time = 1200 # Durée initial d'affichage des cartes jouées
fighters_lvl = {} # Stock les niveaux actuels de chaque personnages (pas de niv : competence non débloqué)
objects_lvl = {} # idem pour les objets
level_upgrade_base = 1 # niveau de base des personnages/objets proposés à l'amélioration
apparation_probability = {} # probabilité d'apparition de chaque personnage/objet (pourra être modifié par des effets en jeu)
player_lives = [20, 0, 0, 0] # vies du joueur + affichage des variations de gains de vie + affichage des variations des pertes de vie + affichage des PV tanké
max_player_live = 30 # vie MAX
player_score = [0, 0, 0] # comme pour player_lives
eclat = [10,0,0] # comme pour player_lives
regain_PV_manche = 2 # gain de PV à chaque manche
exhaustion_effect = 0
expansion_effect = 0
gain_eclat_bonus_manche = 1

combo = 0 # nombre de match consécutif (se réinitialise en cas de paires sans match)
last_succeed_move = 0 # numero du dernier mouvement réussi (pour le combo)
move= 0 # numéro du mouvement actuel
charge = 0 # augmenté grâce à certaines actions dont dzzit. Sert pour le canon à énergie

training_choices = 3 # Nombre de choix en entrainement
proposal_after_training_prob = 0.3 # Probabilité de créer une Proposition avec la carte entrainée
shop_choices = 3 # Choix dans le memo_shop
bonus_lvl_probabilities = [0.3]+[0.2**i for i in range(2,10)] # Les probabilités d'avoir un bonus de niveau 1,2,3,...
increase_difficulty = 2.5

# pas utilisés pour l'instant
scores_constantes_modifiers_plus = {}
scores_constantes_modifiers_mult = {}

# Benec et malec
benec_and_malec = []

# lance une run. Utilisez run_parameter pour lancer une run selon des conditions précises
def start_run(start_lives=20, start_eclat=10, p_regain_PV_manche=2, p_level_upgrade_base=1, p_showing_time=1200, p_training_choices=3, p_proposal_after_training=0.3, p_shop_choices=3, p_benec_and_malec = None, p_exhaustion_effect=0, p_expansion_effect=0, seed_input=None, p_gain_eclat_bonus_manche=1) :
    global last_score_change_tick, last_live_change_tick, last_eclat_change_tick, selection_locked, selection_overload, showing_time, level_upgrade_base, regain_PV_manche, combo, last_succeed_move, move, charge, training_choices, proposal_after_training_prob, shop_choices, max_player_live, exhaustion_effect, expansion_effect, gain_eclat_bonus_manche,this_level_score
    
    last_score_change_tick = pygame.time.get_ticks()
    last_live_change_tick = pygame.time.get_ticks()
    last_eclat_change_tick = pygame.time.get_ticks()
    this_level_score = 0

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
    max_player_live = 30
    player_score.clear()
    player_score.extend([0, 0, 0])
    eclat.clear()
    eclat.extend([start_eclat,0,0])
    regain_PV_manche = p_regain_PV_manche
    exhaustion_effect = p_exhaustion_effect
    expansion_effect = p_expansion_effect

    combo = 0
    last_succeed_move = 0
    move= 0
    charge = 0 

    training_choices = p_training_choices
    proposal_after_training_prob = p_proposal_after_training
    shop_choices = p_shop_choices
    bonus_lvl_probabilities.clear()
    bonus_lvl_probabilities.extend([0.3]+[0.2**i for i in range(1,10)])
    gain_eclat_bonus_manche = p_gain_eclat_bonus_manche

    scores_constantes_modifiers_plus.clear()
    scores_constantes_modifiers_mult.clear()

    benec_and_malec.clear()
    if p_benec_and_malec :
        for bm in benec_and_malec :
            apply_benection_or_pacte(bm)

    game.clear()
    
    global memo_shop_
    last_cards_shop.clear()
    game["state"] = "play"
    game["round"]=1

    global run_seed 
    if seed_input :
        run_seed = seed_input
    else :
        run_seed = int(random.random()*10000)
    
    random_event_use.clear()

    

#=========================== MOUVEMENT ============================*
from collections import deque

# La classe mouvement sert à calculer la position d'un objet en fonction du temps, de la vitesse, de la trajectoire, etc.
class Movement() :
    def __init__(self, stack_position_memory = 50):
        """Initialise un objet Movement. Le paramètre stack_position_memory détermine le nombre de positions précédentes à mémoriser pour le calcul des deltas"""
        
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
        """Démarre ou reprend le mouvement"""
        if self.ended : return False
        if self.start_pause_time :
            time_in_pause = gtick() - self.start_pause_time
            self.start_pause_time = 0
            self.start_time += time_in_pause

        if not self.start_time : self.start_time = gtick()
        self.enable = True

    def pause(self):
        """Met en pause le mouvement"""
        self.enable = False
        self.start_pause_time = gtick() 
    
    def end(self) :
        """Termine le mouvement"""
        self.enable = False
        self.ended = True
    
    def restart(self) :
        """Redémarre le mouvement depuis le début"""
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


from pygame import Surface
#========================= DISPLAYS ==========================#
# --- CLASSE GRID ---
# Permet de diviser une zone rectangulaire en une grille de cases, et de positionner des éléments dans ces cases facilement
class grid() :
    def __init__(self, corner_left=(0,0), width=0, height=0, from_screen=False, rows = 8, cols = 8, square=False):
        """Initialise une grille, soit à partir de la taille de l'écran (from_screen=True), soit à partir des paramètres corner_left, width et height."""
        self.follow_screen = from_screen
        self.corner_left = from_screen and (0,0) or corner_left
        self.init_corner_left = from_screen and (0,0) or corner_left
        self.init_width = width
        self.init_height = height
        self.width = from_screen and SCREEN_WIDTH or width
        self.height = from_screen and SCREEN_HEIGHT or height
        self.square = square 

        self.rows = rows
        self.cols = cols
        self.last_place = {}

        if self.square : # ajuste la grille pour qu'elle soit carrée
            a_square_size = min(self.width/self.cols, self.height/self.rows) # on prend la plus petite taille possible pour que ça rentre
            self.width, self.height = (a_square_size*self.cols,a_square_size*self.rows) # on ajuste la taille de la grille

            init_x, init_y = self.init_corner_left

            x = init_x + round((self.init_width - self.width) / 2)
            y = init_y + round((self.init_height - self.height) / 2)

            self.corner_left = (x,y) # on centre la grille dans la zone initiale
        



        self.top_stack = [None for _ in range(rows)]

        self.saved_size = None

        try :
            grids.append(self)
        except : pass
    
    def ratio_x(self,ratio) :
        return round(self.corner_left[0] + self.width*ratio) 
    def ratio_y(self, ratio) :
        return round(self.corner_left[1] + self.height*ratio)
    
    def update_width_height(self,width, height, new_corner = None) :
        self.init_width = width
        self.init_height = height
        self.width = width
        self.height = height
        self.corner_left = new_corner
        self.last_place.clear()

        if self.square :
            a_square_size = min(self.width/self.cols, self.height/self.rows)
            self.width, self.height = (a_square_size*self.cols,a_square_size*self.rows)

            if new_corner : self.init_corner_left = new_corner
            init_x, init_y = self.init_corner_left
            

            x = init_x + round((self.init_width - self.width) / 2)
            y = init_y + round((self.init_height - self.height) / 2)

            self.corner_left = (x,y)
        
    
    def min_size(self, nb=1) :
        return min(self.col_size(nb), self.row_size(nb))

    def coords(self, col, row, marging=0):

        return (
            round(self.ratio_x(col / self.cols) + marging),
            round(self.ratio_y(row / self.rows) + marging)
        )
    
    def place(self,e : Surface|tuple[int,int],  col, row, nb_col, nb_row) :
        if (isinstance(e, Surface)) :
            e = e.get_width(), e.get_height()
        if (already_placed := self.last_place.get((col, row, nb_col, nb_row, *e))) :
                return already_placed

        we, he = e
        w = self.col_size(nb_col)
        h = self.row_size(nb_row)

        new_placement =  (round(self.ratio_x(col / self.cols) + w/2 - we/2),
                round(self.ratio_y(row / self.rows) + h/2 - he/2))
        
        self.last_place[(col, row, nb_col, nb_row, *e)] = new_placement
        
        return new_placement

    
    def col_size(self, nb=1) :
        return round(self.width/self.cols*nb)
    def row_size(self, nb=1) :
        return round(self.height/self.rows*nb)
    def size_of(self, nb_cols = 1, nb_rows = 1) :
        return (round(self.width/self.cols*nb_cols), round(self.height/self.rows*nb_rows))
    
    def create_rect_info(self, col, row, nb_col=1, nb_row=1, marging=0) :
        x, y = self.coords(col, row)

        width, height = self.size_of(nb_col, nb_row)

        width -= 2*marging
        height -= 2*marging 

        return (x,y,width, height)
    
    def create_rect(self, col, row, nb_col=1, nb_row=1, marging=0) -> pygame.Rect :
        a =  pygame.Rect(self.create_rect_info(col, row, nb_col, nb_row, marging))
        return a
    
    def my_rect_info(self, marging = 0) :
        return (*self.corner_left, self.width - 2*marging, self.height - 2*marging)
    
    def my_rect(self, marging = 0) -> pygame.Rect :
        return pygame.Rect(self.my_rect_info(marging))
    
    def all_grid_infos(self,marging=0, col_interval = None, row_interval=None) :
        if not col_interval : col_interval = (0, self.cols-1)
        if not row_interval : row_interval = (0, self.rows-1)


        grid = []
        for row in range(row_interval[0], row_interval[1]+1) :
            a_row = []
            grid.append(a_row)
            for col in range(col_interval[0], col_interval[1]+1):
                a_row.append(self.create_rect_info(col, row, marging=marging))
        return grid
    
    def all_grid_rect(self,marging=0, col_interval = None, row_interval=None) :
        if not col_interval : col_interval = (0, self.cols-1)
        if not row_interval : row_interval = (0, self.rows-1)


        grid = []
        for row in range(row_interval[0], row_interval[1]+1) :
            a_row = []
            grid.append(a_row)
            for col in range(col_interval[0], col_interval[1]+1):
                a_row.append(self.create_rect(col, row, marging=marging))
        return grid
    
    def duplicate(self, marging=0) :
        a,b,c,d = self.my_rect_info(marging=marging)
        return grid((a,b),c,d,self.rows, self.cols)

    def update_from_screen(self) :
        if self.follow_screen :
            self.width = SCREEN_WIDTH
            self.height = SCREEN_HEIGHT
            self.last_place.clear()
    
    def save_size(self) :
        self.saved_size = (self.width, self.height)

    def add_from_top(self, e,  element_height = 1, element_width=1, col=None, marging=0) :
        if col == None : col=self.cols/2
        # Trouver la premiere place dispo :
        try :
            dispo = next(row for row in range(self.rows) if all(self.top_stack[i] is None for i in range(row, row+element_height)))
        except StopIteration :
            return False 
        
        self.top_stack[dispo:dispo+element_height] = e
        return self.create_rect_info(dispo,col, element_width, element_height, marging )
    
    def draw(self, surface, epaisseur=1, color=(0,0,0)):

        # lignes horizontales
        for row in range(self.rows + 1):
            y = self.corner_left[1] + int(row * self.height / self.rows)
            pygame.draw.rect(surface, color,
                            pygame.Rect(self.corner_left[0],
                                        y - epaisseur,
                                        self.width,
                                        2 * epaisseur))

        # lignes verticales
        for col in range(self.cols + 1):
            x = self.corner_left[0] + int(col * self.width / self.cols)
            pygame.draw.rect(surface, color,
                            pygame.Rect(x - epaisseur,
                                        self.corner_left[1],
                                        2 * epaisseur,
                                     self.height))
        


    

# Initialisation de la grille 10x10 globale (qui peut être utilisée partout)
global_grid = grid(from_screen=True, rows=10, cols=10)





def bonus_score(action, extravar=None) :
    base = (SCORES.get(action,0)+scores_constantes_modifiers_plus.get(action, 0))*scores_constantes_modifiers_mult.get(action,1)

    if action in ("match") :
        if lvl := objects_lvl.get("Allumette",0) :
            if combo > 1 :
                add_show_effect("Allumette")
                base += (combo-1) * (2+lvl)

        if lvl := objects_lvl.get("Lame_Sadique",0) :
            add_show_effect("Lame_Sadique")
            base *= (1 + lvl*0.5)

    if action in ("live_gained") :
        if lvl := objects_lvl.get("Chat_De_Compagnie",0) :
            if not any(name for name,_,__ in enclenched_effect):
                add_show_effect("Chat_De_Compagnie")
            base += 5
    
    if action in ("add_tag") :
        tag, self, from_ = extravar
        if benit := self.get_tag('benit') :
            base += tag[1] * (1+(benit[1]//2)) # On ajoute le produit des niveaux entre le tag ajouté et le tag bénit

    
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
    "dzzit" : lambda r,g,b,p : (int(min(255, r+(add:= 30*(1-p)))), int(min(255, g+add)),int( max(0, b-add)) ),
    "englue" : lambda r,g,b,p : (int(min(255, r+(add:= 50*(1-p)))), int(min(255, g-(add/2))),int( max(0, b+(add/2))))
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
        self.init_image = image
        self.image = pygame.transform.smoothscale(image, (size, size))
        self.color = color
        self.stack_color_modifiers = []
        self.initial_color = color
        self.rect = pygame.Rect(x, y, size, size)
        self.flipped = False
        self.matched = False
        self.flip_progress = 0
        self.remove = False
        self.locked = False
        self.tags : set[tuple[str, int]] = set()
        
        self.selected = False
        self.bigger_selected_progress = 0

        self.boncing = 0

        self.dziit_progress = 0
        self.dziited = False
        self.englued = False
        self.delete_stack = []
        self.break_barageau = False

        self.row = 0
        self.col = 0

        self.location = location
        self.tick_appear = gtick()

        self.character_copied = [] # pour fantome a cheveux
    
    def glue_factor(self) :  
        global accelere              
        if accelere : 
            return 0.5
        new_flip = self.flip_progress if self.flip_progress>0.85 else 0.15 + (1/2*(self.flip_progress-0.15))
        return max(1.5,((new_flip**4) * (2+self.englued)*10)) if self.englued else 1
    def update(self):
        if self.remove : self.flip_progress = 0

        if self.flipped and self.flip_progress < 1:
            self.flip_progress += FLIP_SPEED / (100 if self.location!="proposal" else 500) 
        elif not self.flipped and self.flip_progress > 0:
            self.flip_progress -= max(0.001, FLIP_SPEED / (100 if self.location!="proposal" else 500) / self.glue_factor())
        
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
        if self.location == "training" : self.y += self.boncing * math.cos((gtick() - self.tick_appear) / BONCE_EFFECT_TIME)
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
    
    def put_tag_to_selection(self, tag, selection, message="", all_cards=None, message_color=(255,255,255)) :
        card_modified = []
        for card in selection :
                        if card != self :
                            try_put = card.put_tag(tag, all_cards, from_=[self])
                            if try_put : card_modified.append(card)
        if card_modified : pop_up(card_modified, message, all_cards, message_color=message_color,font=pop_up_font)
        
    def put_tag(self, tag, all_cards, from_=None, piouchador_break=False) :
        if from_ and not piouchador_break and self.name == "Piouchador" and (lvl:=fighters_lvl.get("Piouchador",0)) :
            reussite = []
            for troupe in from_ :
                if troupe.put_tag((tag[0], tag[1]+lvl, tag[2]), all_cards, from_=[self], piouchador_break=True) : reussite.append(troupe)
            if reussite :
                self.dzzit()
                pop_up([self], "Contré !", all_cards, message_color=(255,0,0),time= 500)
                pop_up(reussite, f"Reçu !", all_cards, tag[2], time=500)
            return False
        
        tag = (tag[0], tag[1] + exhaustion_effect, tag[2])
        add_score("add_tag", extravar=(tag,self, from_))
        remove_tags = set()
        for tag_ in self.tags :
            if tag_[0] == tag[0] :
                if tag_[1] >= tag[1] :
                    return False
                else :
                    remove_tags.add(tag_)

        for tag_r in remove_tags :
            self.delete_tag(tag_r)
        if tag[0] == "englue" : self.englued = tag[1]

        self.tags.add(tag)
        return True
    
    def delete_tag(self,tag) :
        if tag in self.tags :
            self.tags.remove(tag)
        if tag[0]=="englue" :
            self.englued=0
    
    def get_tag(self, tag_name) :
        for tag in self.tags :
                if tag[0] == tag_name :
                    return tag
            
        return None
    
    def set_lock(self,duration=1) :
        self.locked = max(self.locked, duration)

    
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
                            try_put = card.put_tag(("michel",lvl,(0,255,0)), cards, from_=[self])
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
                                try_put = card.put_tag(("soin", 2+((lvl)//2), (255,120,120)), cards, from_=flosette_effect) # On tente d'appliquer le tag
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
                            try_put = card.put_tag(("cible",lvl,(60,60,60)), cards, from_=[self])
                            if try_put : cards_a_cible.append(card)
                    if cards_a_cible : pop_up(cards_a_cible, "Ciblé !", cards, message_color=(150,150,150),font=pop_up_font)
                
                case "Piquante" :
                    if nb_match == 0 :
                        add_lives(- (1 + lvl//3), from_=[self], all_cards=cards)
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
                        for copied_ability in self.character_copied :
                            self.activate_effect(nb_match, selection, lesnoms, cards, min(fighters_lvl.get("Fantome_A_Cheveux",1), fighters_lvl.get(copied_ability,1)),already_done, nb_move, custom_name=copied_ability)
                
                case "Catchy" :
                    adjacent_cards = [card for card in cards if est_adjacent(self, card) and not card.remove and card!=self]

                    if len(adjacent_cards)>1 :
                        the_twos = random.sample(adjacent_cards, k=2)
                        switch_place(the_twos[0], the_twos[1], cards, 250, message="Et hop !", message_color=(255,40,230),me=[self])
                        add_score(2+lvl*4)
                    
                    if lvl>5:
                        if get_random("catchy_jump")<0.25 :
                            other_guys = [card for card in cards if card != self and not card.remove]
                            if other_guys :
                                wait_with_cards(cards,100)
                                switch_place(self, other := seed_choice(other_guys, event_name="catchy_where_jump"), cards, 100+100*distance(self,other), "ET HOP !!", message_color=(255,80,210), font=big, me=[self])
                                add_eclat((lvl+6))
                
                case "Bubble_Man" :
                    cards_bubbled = []
                    for card in selection :
                        if card != self :
                            try_put = card.put_tag(("englue",lvl,(255,190,210)), cards, from_=[self])
                            if try_put : cards_bubbled.append(card)
                    if cards_bubbled : pop_up(cards_bubbled, "Englué !", cards, message_color=(255,190,210),font=pop_up_font)

                    if lvl >= 4 and nb_match>0 and not "Bubble_Man" in already_done:
                        bb_cards = []
                        for card in selection :
                            if card != self and ca_match(card, self) :
                                bb_cards.append(card) 
                        cartes_englues = []
                        for bb in [self]+bb_cards :
                            for card in not_removed_cards(cards) :
                                if card != bb and est_adjacent(bb, card, 1) :
                                    cartes_englues.append(card)
                        if cartes_englues :
                            card_success = []
                            for card in cartes_englues :
                                try_put = card.put_tag(("englue", lvl+2, (255,190,210)), cards, from_=bb_cards)
                                if try_put : card_success.append(card)
                            if card_success :
                                pop_up(card_success, "Englué !", cards, (255,100,100))
                        already_done.append("Bubble_Man")
                    
                case "Lo" :
                    les_lo = []
                    for card in selection :
                        if card != self and ca_match(card, self) :
                            les_lo.append(card)
                    if nb_match>0 and not "Lo" in already_done: 
                        les_lignes = [get_row(cards, lo.row) for lo in [self]+les_lo]
                        protected_cards = []
                        for row in les_lignes :
                            for troupe in row :
                                success = troupe.put_tag(("barageau", lvl, (200,200,255)), all_cards=cards, from_=[self]+les_lo)
                                if success :
                                    protected_cards.append(troupe)
                        if protected_cards :
                            pop_up(protected_cards, "Barag'eau !", cards, (200,200,255))
                    already_done.append("Lo")
                
                case "Felinfeu" :
                    if nb_match > 0 :
                        global combo
                        if combo>1 : 
                            add_score(combo*(1+(lvl//2)))
                            pop_up([self], f"+ {combo} x {lvl} !", cards, (255,120,30), pop_up_font, time=800)
                
                case "Lori_Et_Les_Boaobs" :

                    if nb_match == 0 :
                        cards_loried_heal = []
                        cards_loried_poisoned = []

                        for card in selection :
                            if card != self :
                                if est_adjacent(self, card, 1) :
                                    try_put = card.put_tag(("soin", (lvl+1), (255,120,120)), cards, from_=[self])
                                    if try_put : cards_loried_heal.append(card)
                                else :
                                    try_put = card.put_tag(("poison",(lvl+1)//2,(160,10,160)), cards, from_=[self])
                                    if try_put : cards_loried_poisoned.append(card)
                        if cards_loried_heal : pop_up(cards_loried_heal, "Soigné !", cards, message_color=(0,255,150),font=pop_up_font)
                        if cards_loried_poisoned : pop_up(cards_loried_poisoned, "Empoisonné !", cards, message_color=(160,10,160),font=pop_up_font)

                    if lvl >= 3 and nb_match>0 and not "Lori_Et_Les_Boaobs" in already_done:
                        already_poisoned_cards = []
                        converting_cards = []
                        points = 0
                        for card in cards :
                            if not card.remove :
                                if poison := card.get_tag("poison") :
                                    already_poisoned_cards.append((card, poison))
                        if already_poisoned_cards :
                            for card, poison in already_poisoned_cards :
                                card.delete_tag(poison)
                                success = card.put_tag(("soin", poison[1], (255,120,120)), cards, from_=[self])
                                points += poison[1]
                                if success :
                                    converting_cards.append(card)
                            if converting_cards :
                                add_score(points*((lvl+3)//5))
                                pop_up(converting_cards, "Reconvertie !", cards, (0,255,150))


                        already_done.append("Lori_Et_Les_Boaobs")
                
                case "Celeste" :
                    card_celeste = []
                    celeste_cards = []
                    for card in selection :
                        if card != self and ca_match(card, self) :
                            celeste_cards.append(card)
                    if nb_match>0 and not "Celeste" in already_done: 
                        for card in not_removed_cards(cards) :
                            if card != self and any(est_adjacent(cel, card, 1) for cel in [self]+celeste_cards) and not card.flipped :
                                if get_random("celeste") <= (lvl)/(lvl+2) :
                                    card_celeste.append(card)
                        if card_celeste :
                            for card in card_celeste :
                                card.put_tag(("benit", lvl, (255,255,0)), cards, from_=[self]+celeste_cards)
                            small_reveal(card_celeste, cards, "Bénédiction !", message_color=(255,255,0),font=font, time=showing_time, me=[self]+celeste_cards)
                        
                        already_done.append("Celeste")
                
                case "Bossu_Etoile" :
                    bossu_effect = []
                    for card in selection :
                        if card != self and ca_match(card, self) :
                            bossu_effect.append(card)
                    if nb_match>0 and not "Bossu Etoile" in already_done:
                        card_starified = []
                        for card in not_removed_cards(cards) :
                            if not card.flipped and get_random("bossu_etoile") < (lvl)/(lvl+7) :
                                card_starified.append(card)
                        if card_starified :
                            for card in card_starified :
                                card.put_tag(("benit", lvl, (255,255,0)), cards, from_=[self]+bossu_effect)
                                card.dzzit()
                            small_reveal(card_starified, cards, "Étoilé !", message_color=(255,255,50),font=font, time=showing_time*min(2,(1 + (len(card_starified)/10))), me=[self]+bossu_effect)
                        already_done.append("Bossu Etoile")



                        




                    
                

            
        
        if self.tags :
            for tag in self.tags :
                if "michel" == tag[0] :
                    card_revealed = []
                    for card in (c for c in cards if (not c.remove) and (c!=self) and (not c.flipped) and est_adjacent(self, c, 1)) :
                        if get_random("michel") <= (tag[1])/(tag[1]+3) :
                            card_revealed.append(card)
                    
                    if card_revealed : small_reveal(card_revealed, cards, time = 400+tag[1]*150, message="Michel ! Michel ?", message_color=(0,255,100), me=[self])
                if "soin" == tag[0] :
                    if nb_match > 0 :
                        pop_up([self], "Soigné !", cards, tag[2], pop_up_font, time=100)
                        add_lives(1, from_=[self], all_cards=cards)
        
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
        

    def change_size_cords(self, new_size, x, y) :
        self.init_x = x 
        self.init_y = y
        self.init_size = new_size
    
    def change_size(self, new_size) :
        self.init_size = new_size
    
    def change_coords(self, x, y) :
        self.init_x = x 
        self.init_y = y

        
    def check_modification(self, nb_move) :
        removed_tags = set()
        added_tag = set()
        for tag in self.tags :
            if tag[0] == "soin" :
                soin_restant = tag[1] - 1
                
                removed_tags.add(tag)
                if soin_restant > 0 : added_tag.add(("soin", soin_restant, (tag[2])))
            
            if tag[0] == "poison" :
                if not self.matched :
                    poison_restant = tag[1] - 1
                    self.dzzit()
                    add_score(-tag[1])
                    
                    removed_tags.add(tag)
                    if poison_restant > 0 : added_tag.add(("poison", poison_restant, (tag[2])))

        
        self.tags |= added_tag
        for tag in removed_tags | set(self.delete_stack) :
            self.delete_tag(tag)
        
        self.delete_stack.clear()
        self.break_barageau = False


        if self.locked :
            self.locked -= 1
            if self.locked <= 0 :
                self.locked = 0
        
                    

                            

    
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
            
            progress = abs(1 - 2 * self.flip_progress) if not self.locked else 1
            width = max(1, int(self.rect.width * (progress)))   
            card_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)     
            if self.flip_progress >= 0.5 and not self.locked:
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
                if self.locked:
                    line_width = max(2, min(self.rect.width, self.rect.height) // 15)
                    pygame.draw.line(card_surface, (100, 100, 100), (5, 5), (self.rect.width - 5, self.rect.height - 5), line_width)
                    pygame.draw.line(card_surface, (100, 100, 100), (self.rect.width - 5, 5), (5, self.rect.height - 5), line_width) 
                    
                pygame.draw.rect(card_surface, (0, 0, 0), (0, 0, self.rect.width, self.rect.height), width=min(self.rect.width, self.rect.height)//20, border_radius=10)
                
                # Dessiner une croix rouge si la carte est verrouillée
                
        

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
    def dzzit(self, color=COLORS_MODIFIERS["dzzit"]) :
        global charge
        if objects_lvl.get("Canon_A_Energie",0) : charge += 1
        self.dziited = True
        self.stack_color_modifiers.append(color)


# --- FONCTION DE CREATION DU PLATEAU ---
def create_board(num_pairs, x, y, width, height,  forced_pairs = None, only_lvl_up_disponible=False):
    

    total_cards = num_pairs * 2

    rows = int(math.sqrt(total_cards))
    cols = math.ceil(total_cards / rows)
    playing_field = grid((x,y), width, height, cols=cols, rows=rows,square=True)
    

    if only_lvl_up_disponible :
        try :
            chosen_images = seed_sample([(name, image) for name, image in all_images if UPGRADES_COST.get(name)], num_pairs)
        except :
            chosen_images = seed_sample(all_images, num_pairs)
    else :
        chosen_images = seed_sample(all_images, num_pairs)
    if (lvl := objects_lvl.get('Ghosting',0)) :
                removed = []

                for name,im in chosen_images : # On tente de retirer (avec proba) tous les combattants de niveau 0
                    if not fighters_lvl.get(name, 0) and get_random("ghosting") < (lvl/(lvl+15)):
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
    seed_shuffle(cards_images)

    
    size = round(playing_field.col_size()*0.9)
    margin = round(playing_field.col_size()*0.05)

    cards = []
    for i in range(total_cards):
        x,y = playing_field.coords(i%cols, i//cols, marging=margin)
        color = (255,150,150)
        cards.append(card := Card(x, y, cards_images[i][0], cards_images[i][1], color, size))
        card.row = i // cols
        card.col = i % cols



        # # FOR TEST
        # card.tags.add(("michel",3))
        # card.locked = 2
    return playing_field, cards, cols, rows


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
    
def update_draw_score(score = player_score, lives = player_lives, from_boss : "Boss" =False) :
        from_boss : "Boss" = from_boss or actual_boss # Si on est dans un combat de boss, on affiche le score à atteindre
        
        if score[1] > 0 and pygame.time.get_ticks() - last_score_change_tick > BEFORE_ADDING  :
            score[1] = score[1] / ADDING_SPEED
            if score[1]<1 : score[1]=0
        
        if score[2] < 0 and pygame.time.get_ticks() - last_score_change_tick > BEFORE_ADDING  :
            score[2] = score[2] / (max(1.1,ADDING_SPEED/2))
            if score[2]>-1 : score[2]=0
        
        global this_level_score
        score_display = math.ceil((this_level_score if from_boss and from_boss.score_to_reach else score[0]) - score[1] - score[2])
        score_text = font.render(f"Score : {score_display}{' + '+str(math.floor(score[1])) if score[1] else ''}{' - '+str(abs(math.floor(score[2]))) if score[2] else ''}{' / '+str(from_boss.score_to_reach) if from_boss and from_boss.score_to_reach else ''}", True, (255, 255, 255) if (not score[1] and not score[2]) else (255,0,0) if not score[1] else (0,255,100))


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
        max_atteint = life_display==max_player_live
        life_text = font.render(f"Vies : {life_display}{'/'+str(max_player_live) if max_atteint else ''} {'+ '+str(math.floor(lives[1])) if lives[1] else ''} {'- '+str(abs(math.floor(lives[2]))) if lives[2] else ''} {'['+str(abs(math.floor(lives[3])))+']' if lives[3]<0 else '' }", True, get_color_life(lives[1], lives[2], lives[3]))

        if from_boss and from_boss.nb_errors_tolerated :
            errors_text = font.render(f"Erreurs : {from_boss.nb_errors}/{from_boss.nb_errors_tolerated}", True, (255, 255, 255))
            screen.blit(errors_text, (20, 100))
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

def get_row(cards, index) -> list[Card] :
    return sorted([card for card in cards if card.row==index and not card.remove], key = lambda card : card.col)



def add_lives(ch, extra_var=None, from_ : list[Card]|None = None, all_cards=None) :
    global move
    global last_live_change_tick
    last_live_change_tick = pygame.time.get_ticks()

    if from_ and all_cards :
        tanked = False
        for troupe in from_ :
            troupe_act = troupe
            tag = not troupe.break_barageau and troupe.get_tag("barageau")
            if tag and (get_random("barageau") < (tag[1]/(tag[1]+4))) :
                tanked = True
                tag_break = get_random("barageau_break") < (max(0.25,40/(50+tag[1])))
                break
        if tanked :
            pop_up([troupe_act], "Protégé !", all_cards, message_color=(200,200,255))
            if tag_break :
                pop_up([troupe_act], "Détruit !", all_cards, message_color=(100,100,175))
                troupe_act.delete_stack.append(tag)
                troupe_act.break_barageau = True
            add_score("damage_dodge")
            return 
            


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
        if get_random("chat_de_compagnie") < (lvl_chat_comp / (lvl_chat_comp+9)) :
            ch += 1
            add_show_effect("Chat_De_Compagnie")
    
    player_lives[0] += ch
    if player_lives[0]>max_player_live :
        player_lives[0] = max_player_live
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
HYPER_BLEND_VAR_SPED = 20

def update_clock(waiting = 0) :
    
        global blend_constant, blend_var, awaiting_time

        blend_constant += blend_var/BLEND_VAR_SPEED
        if blend_constant >= 1 :
            blend_constant = 1
            blend_var *= -1
        elif blend_constant <= 0 :
            blend_constant = 0
            blend_var *= -1

        global hyper_blend_constant, hyper_blend_var, omega_blend_constant

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

        if DEBUG_SHOW_GRID :
            for i,grid in enumerate(grids) :
                grid.draw(screen,color=(120*i%255, 10*i%255, 40*i%255))
        
        pygame.display.flip()
        clock.tick(FPS)

        global accelere
        clavier = pygame.key.get_pressed()
        if clavier[pygame.K_LSHIFT] and clavier[pygame.K_e]:
            player_lives[0]=0
        global accelere 
        if clavier[pygame.K_SPACE]:
            accelere = 1
        else :
            accelere = 0

        
        


        if awaiting_time > 0 :
            awaiting_time -= 1
            if awaiting_time < 0 : awaiting_time = 0
            update_clock() # appel recursif pour gérer le temps d'attente
            

def add_score(action_or_int, extravar=None) :
    global last_score_change_tick
    global this_level_score
    last_score_change_tick = pygame.time.get_ticks()
    if isinstance(action_or_int, int) :
        player_score[0]+=action_or_int 
        this_level_score += action_or_int
        if action_or_int >= 0 :
            player_score[1]+=action_or_int 
        else :
            player_score[2]+=action_or_int
    else :
        score_applique = bonus_score(action_or_int, extravar)
        player_score[0] += score_applique
        this_level_score += score_applique
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
                all_tags = sorted(sum((list(troupe.tags) for troupe in me),start=[]), key= lambda t : t[1], reverse=True)[:(pipette_lvl)]
                for tag in all_tags :
                    for card in cards :
                        try_put = card.put_tag(tag, all_cards, me)
                        if try_put and card not in card_enhanced : card_enhanced.append(card)
              
                if card_enhanced :
                    add_show_effect("Pipette_Elementaire")
                    pop_up(card_enhanced, "Pipeté !", all_cards, (230,80,200), time=300)
            
            for card in cards : # Ceci sert pour Fantome a cheveux
                if card.name == "Fantome_A_Cheveux" and fighters_lvl.get(card.name,0) and me :
                    to_add = []
                    for character in me : # Je parcours tout ceux qui m'ont révélé
                        # print("Character in me : ",character.name)
                        if fighters_lvl.get(character.name, 0) : # Je vérifie la personne qui m'a révélé a sa compétence activé
                            if character.name == "Fantome_A_Cheveux" : # Si c'est un autre fantome à cheveux, j'ajoute toutes ses copies que je n'ai pas
                                to_add.extend(added := [e for e in character.character_copied if e not in card.character_copied and e not in to_add])
                                # print("added",added)
                            else :
                                if character.name not in card.character_copied : to_add.append(character.name) # Sinon j'ajoute directement le personnage
                    
                    # print("to_add",to_add)
                    card.character_copied.extend(to_add)
                    
            
                


            while pygame.time.get_ticks() - starting_time < time :
                
                draw_bg()
                show_message(message, message_color, recenterx=False)
                update_draw_cards(all_cards)
                update_clock()

                for event in pygame.event.get():
                    check_resize(event)
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif acceleration(event) and starting_time :
                        starting_time -= time/2
                        break
            
            for card in cards : 
                card.flipped = False
            
            while not all(card.flip_progress==0 for card in cards) :
                for event in pygame.event.get():
                    check_resize(event)
                    acceleration(event)
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


def random_cols(cards, priviligies_bigger_col = 0, include_remove = False, event_name="generic_random_column") : # renvoit les colonnes disponibles dans un ordre aléatoire. priviligies_bigger_col : 0 = inactif / n = impacte : colonne plus occupé = plus fort
    if not priviligies_bigger_col :
        num_col = seed_choices(list( cols := set(card.col for card in cards if not card.remove or include_remove)), k=len(cols), event_name=event_name)[0]
    else :
        poids_dict = {}
        for card in cards :
            if not card.remove or include_remove :
                poids_dict[card.col] = poids_dict.get(card.col,0)+1
        colonnes = [i for i in poids_dict]
        poids = [poids_dict[i]*priviligies_bigger_col for i in poids_dict]
        num_col = seed_choices(colonnes, weights=poids, k=len(colonnes), event_name=event_name)[0]
    
    return [card for card in cards if card.col==num_col and not card.remove]






def activate_object_effect(objet, lvl, cards, start_of_round_effect=False) :
    if objet == "Canon_A_Energie" :
        global charge 
        if charge >= 9 :
            add_show_effect("Canon_A_Energie", (200+lvl*50)*((charge//9)))
        while charge >= 9 :
            wait_with_cards(cards, 200)
            charge = max(0,charge-9)
            col = random_cols(cards, lvl>=3 and lvl/3)
            add_score(2*len(col))
            small_reveal(col, cards, "BOOOOOOM", message_color=(240,240,100),font=font, time=200+lvl*100, me=None)
    
    if objet=="Trognon" and start_of_round_effect :
        card_to_poison = seed_sample(cards, min(1+(lvl//2), len(cards)))
        poisonned_cards=[]
        add_lives(lvl, "from_heal_object")
        add_show_effect("Trognon", 600)
        for card in card_to_poison :
            success = card.put_tag(("poison", lvl, (160,10,160)), cards)
            if success : poisonned_cards.append(card)
        if success :
            pop_up(poisonned_cards, "Trognon !!", cards, (200,60,150))







def ca_match(card1,card2):
    return card1.name == card2.name

def distance(card1, card2) :
    return abs(card1.row - card2.row) + abs(card1.col - card2.col)

def est_adjacent(card1,card2, radius=1) :
    if (card2.name=="Maniak" and fighters_lvl.get("Maniak",0)) : return True 
    elif (card1.name=="Maniak" and fighters_lvl.get("Maniak",0)>3) : radius += fighters_lvl.get("Maniak",0)//3

    radius += expansion_effect


    # print(f"{card1.name, card1.row, card1.col =}", f"{card2.name, card2.row, card2.col =}", sep=" | ")
    return abs(card1.row - card2.row) + abs(card1.col - card2.col)<=radius

def wait_with_cards(cards,time, fun=None) :
    init = gtick()
    while gtick() - init < time :
        draw_bg()
        update_draw_cards(cards)
        update_draw_score(player_score,player_lives)
        if fun : fun()
        update_clock()
        

def wait_finish_return(cards):
    # Attendre tant qu'il y a au moins une carte en cours d'animation (0 < progress < 1)
    while any(((card.flip_progress!=1 and card.flipped) or (card.flip_progress!=0 and not card.flipped)) and not card.remove for card in cards):
        for event in pygame.event.get() :
            check_resize(event)
            acceleration(event)
        draw_bg()
        update_draw_cards(cards)
        update_draw_score(player_score, player_lives)
        update_clock()

def get_end_of_round_eclat(cards):
    return 3+int(1.5*game["round"]*gain_eclat_bonus_manche)

def check_resize(event) :
    if event.type == pygame.VIDEORESIZE:
        global screen
        screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        global SCREEN_HEIGHT, SCREEN_WIDTH
        SCREEN_HEIGHT = event.h
        SCREEN_WIDTH = event.w
        for grid in grids :
            grid.update_from_screen()
        
        global last_window_size_change
        last_window_size_change = gtick()

class Boss():

    def __init__(self, nom="Boss_Test", nb_errors_tolerated=None, score_to_reach=100, skills=None):
        self.nom = nom
        self.nb_errors_tolerated = nb_errors_tolerated
        self.nb_errors = 0
        self.score_to_reach = score_to_reach
        self.skills = skills or []
        
    def activate_skills(self, cards, move_number):
        for skill in self.skills:
            skill(cards, move_number)
    



# --- JEU PRINCIPAL ---
def play_memory(num_pairs=8, forced_cards = None, from_boss=None):
    global selection_locked, move, last_succeed_move, combo, this_level_score, actual_boss
    cards : list["Card"]



    
    taille = round(min(SCREEN_HEIGHT*6/8, SCREEN_WIDTH*6/8)) # de carte
    bords = SCREEN_WIDTH//2 - taille//2, SCREEN_HEIGHT//2 - taille//2 # position du plateau
    playing_field, cards, cols, rows = create_board(num_pairs,bords[0],bords[1],taille,taille,forced_pairs=forced_cards) # créer les cartes nécessaires
    last_selection_time = 0
    running = True
    start_show_time = 0
    ending = 0
    move = 1
    first_move_effect = 0
    this_level_score = 0
    actual_boss = from_boss
    kill_by_boss = False

    message_boss = f"Combat contre {from_boss.nom} !" if from_boss else ""
    message_boss_surf = None
    if message_boss :
        message_boss_surf = create_optimal_msg(message_boss, global_grid.col_size(4), global_grid.row_size(1), bold=True, color = (255,100,100))

    last_window_changed_local = gtick()

    while running:

        # if last_window_size_change > last_window_changed_local :

        #     for card in cards :
        #         cards.change



        draw_bg()



        # événements
        for event in pygame.event.get():
            acceleration(event)
            check_resize(event)

            if event.type == pygame.VIDEORESIZE :
                
                # On remodifie dynamicament le plateau de jeu
                taille = round(min(SCREEN_HEIGHT*6/8, SCREEN_WIDTH*6/8))
                bords = SCREEN_WIDTH//2 - taille//2, SCREEN_HEIGHT//2 - taille//2
                playing_field.update_width_height(taille, taille, new_corner=(bords[0], bords[1]))

                # on change la taille des cartes en conséquance
                size = round(playing_field.col_size()*0.9)
                margin = round(playing_field.col_size()*0.05)
                for card in cards :
                    card.change_size_cords(size, *playing_field.coords(card.col, card.row, marging=margin))
                
                if message_boss :
                    message_boss_surf = create_optimal_msg(message_boss, global_grid.col_size(4), global_grid.row_size(1), bold=True, color = (255,100,100))

            

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif validation(event) and ending : # ending signifie que toute les paires ont étées trouvées ou que le joueur a perdu
                running = False 
                break

            elif acceleration(event) and start_show_time :
                start_show_time -= showing_time/2 # raccourcie les animations de révélation
                break

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not selection_locked :
                    if getattr(event, "button", None) == 2 : # touche de pré-selection (clique molette)
                        for card in cards:
                            if card.rect.collidepoint(event.pos) and not card.matched and not card.flipped and not card.remove and not card.locked and (card not in selection): # on vérifie que la carte est cliquée et qu'elle n'est pas déjà retirée / révélée
                                if card.selected : # si la carte est déjà sélectionnée (sans avoir été retournée), on la désélectionne 
                                    card.selected = False
                                    selection.remove(card)
                                elif len(selection) < SELECTION_LIMIT:
                                    card.selected = True
                                    selection.append(card)
                                    last_selection_time = pygame.time.get_ticks()
                    
                    if getattr(event, "button", None) == 3 : # touche de déselection (clique droit)
                        for card in cards:
                            if not card.flipped and not card.remove and card.selected: # on vérifie que la carte est cliquée et qu'elle n'est pas déjà retirée / révélée
                                if card.selected :
                                    card.selected = False
                                    selection.remove(card)
                    
                    if getattr(event, "button", None) == 1 : # touche de révellation (montre une carte : clic gauche)
                        for card in cards:
                            if card.selected and not card.remove and not card.flipped :
                                card.flipped = True
                            
                            if not card in selection and not card.remove and not card.selected and len(selection) < SELECTION_LIMIT and card.rect.collidepoint(event.pos) and not card.locked :
                                card.selected = True 
                                selection.append(card)
                                card.flipped = True
                                last_selection_time = pygame.time.get_ticks()
        
         

        # mise à jour
        for card in cards:
            card.update()
        
        if message_boss_surf :
            screen.blit(message_boss_surf, global_grid.place(message_boss_surf, 3, 0, 4, 1))

        # effets de début de manche
        if not first_move_effect :
            first_move_effect = True

            for o, lvl in objects_lvl.items() :
                activate_object_effect(o,lvl, cards, start_of_round_effect=True)


        # logique du jeu
        if len(selection) == SELECTION_LIMIT: # on a sélectionné le nombre maximum de cartes
            selection_locked = True # on bloque la sélection pour éviter d'en sélectionner d'autres pendant l'animation
            for card in selection :
                card.flipped=True

            # attendre que les deux soient bien visibles
            if all(card.flip_progress==1 for card in selection):

                selection_locked = True
                

                if not start_show_time :
                    start_show_time = pygame.time.get_ticks() # on lance le timer d'affichage

                    names = [t.name for t in selection]
                    if any(names.count(name)> 1 for name in names) :
                        combo = combo + 1
                    else :
                        if fighters_lvl.get("Felinfeu",0) >= 4 and any(card.name=="Felinfeu" for card in selection) :
                            pop_up([card for card in selection if card.name=="Felinfeu"], "COMBO INNARETABLE", cards, (255,200,30))
                        else :
                            combo = 0
                    
                    activate_effect(selection, cards, nb_move=move) # appelle les effets des cartes sélectionnées
                
                elif pygame.time.get_ticks() - start_show_time > showing_time : # apres avoir attendu le temps d'affichage, on ajoute le score et on retire ou retourne les cartes
                    names = [t.name for t in selection]
                    if any(names.count(name)>1 for name in names): # = un match a lieu
                        
                        last_succeed_move = move # dernier mouvement réussis
                        add_score("match")

                        for c in selection: # On marque les cartes comme appariées et on les retire
                            c.matched = True
                            c.flipped = False
                            c.remove = True
                    else:
                        add_lives(-1, from_ = selection, all_cards=cards) # perte de vie si pas de match
                        add_score("dontmatch") 
                        if from_boss : from_boss.nb_errors += 1
                        for c in selection: # on retourne les cartes
                            c.flipped = False

                    # dans tous les cas, on les déselectionnent
                    for card in cards :
                        card.selected = False
                    
                    for card in cards :
                        card.check_modification(move)
                    
                    wait_finish_return(cards) # On attends qu'elles soit bien retournées / retirées

                    for o, lvl in objects_lvl.items() : # on active les effets des objets
                        activate_object_effect(o,lvl, cards)
                    
                    if from_boss :
                        from_boss.activate_skills(cards, move)

                    # on prépare le prochain tour
                    
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

            if from_boss and this_level_score < from_boss.score_to_reach :
                refresh()
                cards.clear()
                end_text = font.render(f"{from_boss.nom} n'a pas été convaincu(e) ...", True, (255, 50, 50))
                screen.blit(end_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
                selection_locked = True
                ending = True
                add_lives(-player_lives[0]) # on met les vies à 0
                kill_by_boss = True
            else :
                update_draw_score(player_score, player_lives, from_boss=actual_boss)
                gain_eclat = get_end_of_round_eclat(cards)
                end_text = font.render(f"Grille terminée ! Eclats Gagnés : {gain_eclat}", True, (255, 255, 0))
                screen.blit(end_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2))
                end_text2 = font.render(f"PV regagné : {regain_PV_manche}", True, (255,150,150))
                screen.blit(end_text2, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + end_text.get_height()+5))
                if not ending :
                    add_score("end_play")
                    add_eclat(gain_eclat)
                    add_lives(regain_PV_manche)
                ending = True
                

        
        elif player_lives[0] <= 0 and not kill_by_boss:
            refresh()
            cards.clear()
            end_text = font.render("Plus de vies !", True, (255, 50, 50))
            screen.blit(end_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
            selection_locked = True
            ending = True
        
        elif from_boss and from_boss.nb_errors_tolerated and from_boss.nb_errors >= from_boss.nb_errors_tolerated :
            refresh()
            cards.clear()
            end_text = font.render(from_boss.nom+" n'a pas été convaincu(e) ...", True, (255, 50, 50))
            screen.blit(end_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
            selection_locked = True
            ending = True
            add_lives(-player_lives[0]) # on met les vies à 0
            kill_by_boss = True
        
        
        update_clock()

def get_apparition_cards() :
    """Renvoit la liste des cartes qui apparaitrons spontannément"""
    res = []
    for name, prob in apparation_probability.items() :
        if get_random("apparation_"+name) <= prob :
            res.append(name)
    
    return res

def refresh() :
    draw_bg()

def get_next_prob(current_prob) :
    """Permet de définir le bonus de probabilité d'apparition lors d'une proposition"""
    return (0.2 if current_prob==0 else current_prob + 0.1) + random.randint(0,10)/100

def proposal(card_name, from_bonus = False) :
    """Génère une proposition de contrat avec un personnage mis en entré (mettez seulement son nom).
    from_bonus : indique si la proposition vient d'un bonus d'objet ou non (impacte l'affichage et le comportement)"""

    global selection_locked
    selection.clear()
    from description import generer_apparition_message, generer_message_de_description
    selection_locked = False
    
    msg = render_multiline("Un combattant souhaite collaborer avec vous !", width= global_grid.col_size(6), height=global_grid.row_size(1), bold=True, color=(255, 255, 255))
    
    card_display = Card(
        SCREEN_WIDTH//2 - (size:=global_grid.min_size(2))//2, global_grid.coords(3,3)[1],
        card_name,
        all_images_dict[card_name],
        (255, 150, 150),
        size,
        location="proposal"
    )

    card_display.flipped = True


    description_surface = generer_apparition_message(
        {"nom": card_name,
         "ancienne_probability": apparation_probability.get(card_name, 0)*100,
         "new_probability": int((new_prob := get_next_prob(apparation_probability.get(card_name, 0)))*100),
         "prix": (prix:=math.ceil(UPGRADES_COST.get(card_name, 5)*(apparation_probability.get(card_name, 0)+0.1)*10)),
         "from_bonus":from_bonus},
         width=global_grid.col_size(8), height=global_grid.row_size(2))
    
    waiting = True

    description_surface_carte = generer_message_de_description(
                    {"nom": card_name, "lvl":fighters_lvl.get(card_name, 1), "lvl_init": fighters_lvl.get(card_name, 1), "proposal":True},
                    width=global_grid.col_size(8), height=global_grid.row_size(3)
    )
    
    while waiting:
        refresh()

        screen.blit(msg, global_grid.place(msg, 2, 1, 6, 1))
        if description_surface :
            screen.blit(description_surface, global_grid.place(description_surface, 1,5,8,2))
        
        if description_surface_carte:
            screen.blit(description_surface_carte, global_grid.place(description_surface_carte, 1,7, 8, 3))
        
        update_draw_eclats()
        update_draw_cards([card_display])
        # update_draw_score(player_score, player_lives)
  
        for event in pygame.event.get():
            check_resize(event)
            if event.type == pygame.VIDEORESIZE :
                msg = render_multiline("Un combattant souhaite collaborer avec vous !", width= global_grid.col_size(6), height=global_grid.row_size(1), bold=True, color=(255, 255, 255))
                description_surface = generer_apparition_message(
                {"nom": card_name,
                "ancienne_probability": apparation_probability.get(card_name, 0)*100,
                "new_probability": int((new_prob := get_next_prob(apparation_probability.get(card_name, 0)))*100),
                "prix": (prix:=math.ceil(UPGRADES_COST.get(card_name, 5)*(apparation_probability.get(card_name, 0)+0.1)*10)),
                "from_bonus":from_bonus},
                width=global_grid.col_size(8), height=global_grid.row_size(2))

                description_surface_carte = generer_message_de_description(
                            {"nom": card_name, "lvl":fighters_lvl.get(card_name, 1), "lvl_init": fighters_lvl.get(card_name, 1), "proposal":True},
                            width=global_grid.col_size(8), height=global_grid.row_size(3)
                )
                card_display.change_size_cords((size:=global_grid.min_size(2)), SCREEN_WIDTH//2 - size//2, global_grid.coords(3,3)[1])

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif validation(event) and eclat[0]>=prix :
                apparation_probability[card_name] = new_prob
                add_eclat(-prix)
                if not from_bonus :
                    global last_proposal_accepted
                    last_proposal_accepted = card_display
                waiting = False
            elif rejet(event) :
                waiting = False
                last_proposal_accepted = None
        
        update_clock()

def borne(nb, borneInf=0, borneSup=1):
    return min(borneSup, max(borneInf, nb))

def acceleration(event) :
    if pygame.key.get_pressed()[pygame.K_SPACE] :
        global accelere
        accelere = 1
    else :
        accelere = 0
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
    if fighters_lvl.get(name,0) == 0 : return 1 + benec_and_malec.count('default_malec')
    nb = get_random("bonus_lvl")
    return level_upgrade_base + sum(1 for threshold in bonus_lvl_probabilities if nb <= threshold)

def switch_place(card1: Card,card2 : Card, all_cards, time=500, message=None, message_color = (255,255,255), font=font, me : None|list[Card]=None):
    assert card1 in all_cards and card2 in all_cards

    # Vérifions que l'échange est possible
    card_englued : list[Card] = []
    for card in (card1,card2) :
        if (t:=card.get_tag("englue")) :
            card_englued.append(card)
    
    if card_englued :
        for card in card_englued :
            card.dzzit(color=COLORS_MODIFIERS["englue"])
        pop_up(card_englued, "Collé !", all_cards, message_color=(255,190,210))
        return False


    # Crééons 2 mouvements basé sur les positions des deux cartes
    switch1 = Movement()
    switch2 = Movement()
    coords_1 = (card1.init_x, card1.init_y)
    coords_2 = (card2.init_x, card2.init_y)
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
        for event in pygame.event.get():
            check_resize(event)
            acceleration(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        update_clock()
    
    card1.col, card1.row, card2.col, card2.row = card2.col, card2.row, card1.col, card1.row



    return True

def find_font_size_msg(message, width, height, initial_font_size=10, police=font_police,
                       bold=False, italic=False):

    font_size = initial_font_size

    # Fonction interne pour calculer les dimensions du texte
    def get_size(fs):
        font = pygame.font.SysFont(police, fs, bold=bold, italic=italic)
        msg = font.render(message, False, (0, 0, 0))
        return msg.get_width(), msg.get_height()

    w, h = get_size(font_size)


    # Tant que ça rentre, on augmente
    while w < width and h < height:
        font_size += 1
        w, h = get_size(font_size)

    # On a dépassé → on redescend d’un cran
    font_size -= 1
    w, h = get_size(font_size)

    # Si jamais on dépasse encore, on ajuste vers le bas
    while (w > width or h > height) and font_size > 1:
        font_size -= 1
        w, h = get_size(font_size)

    return max(font_size, 1)


def create_optimal_msg(message, width, height, initial_font_size = 10, police=font_police, bold=False, italic=False, color=(0,0,0), antialias = True) :
    font = pygame.font.SysFont(police, find_font_size_msg(message,width,height, initial_font_size, police, bold, italic), bold=bold, italic=italic)
    return font.render(message, antialias, color)


def wrap_text(message, font, max_width):
    words = message.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            # On pousse la ligne actuelle et on recommence
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines

def find_max_font_size_multiline(message, width, height, police, bold=False, italic=False):
    low, high = 1, 300
    best = 1

    while low <= high:
        mid = (low + high) // 2
        font = pygame.font.SysFont(police, mid, bold=bold, italic=italic)

        lines = wrap_text(message, font, width)
        total_height = len(lines) * font.get_linesize()

        if total_height <= height:
            best = mid
            low = mid + 1
        else:
            high = mid - 1

    return best

def render_multiline(
    message, width, height, police=font_police,
    bold=False, italic=False, color=(0,0,0), antialias=True,
    align="left", valign="top"
):
    optimal_size = find_max_font_size_multiline(
        message, width, height, police, bold, italic
    )

    font = pygame.font.SysFont(police, optimal_size, bold=bold, italic=italic)
    lines = wrap_text(message, font, width)

    # Surface finale
    surf = pygame.Surface((width, height), pygame.SRCALPHA)

    # Hauteur totale du bloc de texte
    total_height = len(lines) * font.get_linesize()

    # --- Gestion verticale ---
    if valign == "center":
        y = (height - total_height) // 2
    elif valign == "bottom":
        y = height - total_height
    else:  # top
        y = 0

    for line in lines:
        txt = font.render(line, antialias, color)

        # --- Gestion horizontale ---
        if align == "center":
            x = (width - txt.get_width()) // 2
        elif align == "right":
            x = width - txt.get_width()
        else:  # left
            x = 0

        surf.blit(txt, (x, y))
        y += font.get_linesize()

    return surf



from pygame import Rect

def middle(nb1) :
    if nb1%2 :
        return nb1//2 + 1
    else :
        return nb1//2


def go_training() :
    # Nettoie l'écran et affiche un écran "fresh" en attendant une action de l'utilisateur
    global selection_locked
    selection.clear()
    selection_locked = False
    from description import generer_message_de_description

    training_grid = grid(from_screen=True,rows=8, cols=8)

    cards_upgrade = seed_sample([card for card in all_images if UPGRADES_COST.get(card[0])],training_choices, event_name="training_choices")
    global last_proposal_accepted
    if last_proposal_accepted and UPGRADES_COST.get(last_proposal_accepted.name):
        already_in = -1
        for i,card in enumerate(cards_upgrade) :
            if card[0] == last_proposal_accepted.name :
                already_in = i 
        
        if already_in > -1:
            cards_upgrade[already_in], cards_upgrade[middle(training_choices-1)], cards_upgrade[already_in], cards_upgrade[middle(training_choices)]
        else :
            cards_upgrade[middle(training_choices-1)] = (last_proposal_accepted.name, all_images_dict.get(last_proposal_accepted.name))
    all_cards : list[Card] = []
    updrade_lvl = {c : get_bonus_lvl(c) for c,_ in cards_upgrade}

    for name, image in cards_upgrade :
            all_cards.append(Card(0, 0, name, image, (150, 150, 255), 100, location="training"))
            all_cards[-1].flipped = True

    show_previous_progress = 0
    waiting = True
    ending = False 
    ending_last_time_out = 0

    last_msg_generated_tick = -1

    while waiting:
        refresh()
        
        if last_window_size_change > last_msg_generated_tick :
            # creation du message
            titre_zone = training_grid.create_rect(1,1,6,1)
            msg = render_multiline("C'est l'heure de l'entrainement ! Mais qui entrainer ?", width=titre_zone.width, height=titre_zone.height, bold=True, color=(255, 255, 255), align="center")
            msgx,msgy = titre_zone.centerx - msg.get_width()/2,titre_zone.centery- msg.get_height()/2
            # Creation du displayer de cartes
            d_w, d_h = 6, 4
            displayer = training_grid.create_rect(1,2,d_w,d_h)
            
            displayer_grid = grid(training_grid.coords(1,2), *training_grid.size_of(d_w,d_h), rows=1, cols=training_choices)
            displayers : list[Rect] = displayer_grid.all_grid_rect()[0]
            card_size = min(displayer_grid.col_size(), displayer_grid.row_size()) - 20
            
            # Création des cartes en elle
            for i in range(len(all_cards)) :
                flip_before = all_cards[i].flip_progress
                x,y=displayer_grid.coords(i,0)
                x+=10 ; y+=10
                all_cards[i] = Card(x,y + ((displayer_grid.row_size()-10)//2) - (card_size//2),name=all_cards[i].name, image=all_images_dict[all_cards[i].name], color=all_cards[i].color, size = card_size, location="training")
                all_cards[i].flipped = True
                all_cards[i].flip_progress = flip_before
                all_cards[i].boncing = ((displayer_grid.row_size()-10)//2) - (card_size//2)
                all_cards[i].tick_appear -= i*(1000//training_choices)
            
            description_zone = training_grid.create_rect(1,6,6,3)
            
            last_msg_generated_tick = gtick()
        
        mouse_pos = pygame.mouse.get_pos()

        #training_grid.draw(screen)
        #displayer_grid.draw(screen, 1, (255,0,0))
        screen.blit(msg, (msgx,msgy))
        for i, disp in enumerate(displayers) :
            if disp.collidepoint(mouse_pos) :

                if (lvl := updrade_lvl.get(all_cards[i].name,1))>1 :
                    pygame.draw.rect(screen, blend_multi(((230,200,130), (180,70,160),(120,95,200)), hyper_blend_constant), disp, border_radius=10)
                else :
                    pygame.draw.rect(screen, blend_multi(((230,200,130), (180,70,160),(120,95,200)), blend_constant), disp, border_radius=10)
            else :
                if (lvl := updrade_lvl.get(all_cards[i].name,1))>1 :
                    pygame.draw.rect(screen, blend((50,50,50),blend_multi(((230,200,130), (180,70,160),(120,95,200)), hyper_blend_constant),0.3), disp, border_radius=10)
                else :
                    pygame.draw.rect(screen, blend((50,50,50),blend_multi(((230,200,130), (180,70,160),(120,95,200)), blend_constant),0.2), disp, border_radius=10)
            pygame.draw.rect(screen, (0,0,0), disp, width=1, border_radius=10)
        update_draw_cards(all_cards)
        # Afficher les éclats en haut à droite
        update_draw_eclats()


        
        # Détecter le passage de souris sur une carte
        
        for i,card in enumerate(all_cards):
            if displayers[i].collidepoint(mouse_pos) and card.flip_progress>=0.5 and not ending:
                lvl = fighters_lvl.get(card.name,0)
                description_surface = generer_message_de_description(
                    {"nom": card.name, "lvl":lvl+updrade_lvl[card.name],"lvl_init": lvl, "prix":UPGRADES_COST.get(card.name, 0)*(lvl+1)},
                    width=description_zone.width-4,
                    height=description_zone.height-4
                )

                description_surface_previous = None
                if lvl >= 1 and show_previous_progress>0:
                    description_surface_previous = generer_message_de_description(
                        {"nom": card.name, "lvl":lvl, "show_previous":lvl, "lvl_init": lvl, "prix":UPGRADES_COST.get(card.name, 0)*(lvl+1)},
                        width=description_zone.width-4,
                        height=description_zone.height-4
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

                        # appliquer l'alpha (0-255)
                        surf_prev.set_alpha(int(255 * alpha_prev))
                        surf_curr.set_alpha(int(255 * alpha_curr))

                        # fond noir derrière les descriptions
                        pygame.draw.rect(screen, (0, 0, 0), description_zone, border_radius=2)

                        # blit : previous (plus opaque) puis current (plus transparent)
                        screen.blit(surf_prev, (description_zone.left + 2, description_zone.top + 2))
                        screen.blit(surf_curr, (description_zone.left+ 2, description_zone.top+ 2))
                    else :
                        pygame.draw.rect(screen, (0, 0, 0), description_zone, border_radius=2)
                        screen.blit(description_surface, (description_zone.left+ 2, description_zone.top+ 2))

                break

        if ((keys := pygame.key.get_pressed())[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                show_previous_progress = min(1,show_previous_progress+SHOW_PREVIOUS_SPEED)
        else :
                show_previous_progress = max(0,show_previous_progress-SHOW_PREVIOUS_SPEED)
        
        for event in pygame.event.get():
            check_resize(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif rejet(event):
                waiting = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r :
                cards_upgrade = seed_sample(all_images,training_choices, event_name="training")
                all_cards = []
                for name, image in cards_upgrade :
                    all_cards.append(Card(0, 0, name, image, (150, 150, 255), card_size, location="training"))
                    all_cards[-1].flipped = True
                    updrade_lvl.clear()
                    updrade_lvl.update({c : get_bonus_lvl(c) for c,_ in cards_upgrade})
                    last_msg_generated_tick = 0
                
            elif event.type == pygame.MOUSEBUTTONDOWN and not selection_locked:
                mouse_pos = event.pos
                for i,card in enumerate(all_cards):
                    if displayers[i].collidepoint(mouse_pos) and UPGRADES_COST.get(card.name) is not None :
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

        if last_msg_generated_tick : update_clock()



seed_input = None


def end_run() :
    from description import DISPLAY_NAMES
    global best_score
    refresh()
    waiting = 2 
    seed = []
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
            best_score = player_score[0]
        
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
            exit_text = font.render("CLIQUEZ pour recommencer", True, (255, 255, 255))
            screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, SCREEN_HEIGHT - 50))



        
        for event in pygame.event.get():
            check_resize(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_1 : seed.append(1)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_2 : seed.append(2)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_3 : seed.append(3)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_4 : seed.append(4)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_5 : seed.append(5)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif validation(event) or rejet(event):
                waiting -= 1
        
        update_clock()
    
    global seed_input
    seed_input = str(seed)


# VARIABLES POUR LE SHOP :
last_cards_shop = []

def memo_shop_present():
    cards_images = seed_sample(all_objects_images,shop_choices, event_name="memo_shop_present")
    
    last_cards_shop.clear()


    
    msg = render_multiline("Retenez bien l'ordre de ces cartes pour plus tard !",width=global_grid.col_size(8), height=global_grid.row_size(2), bold=True,color= (255, 255, 255), align="center")

    card_display = grid(global_grid.coords(1,3), global_grid.col_size(8), global_grid.row_size(4), cols=shop_choices, rows=1)


    for i,card_image in enumerate(cards_images) :
        card_name, card_im = card_image
        card = Card(0,0, card_name, card_im, (230,230,20), card_display.min_size(), "shop")
        card.change_size(round(size := card_display.min_size()*0.9))
        card.change_coords(*card_display.place((size,size), i, 0, 1, 1))
        
        card.flipped = True
        card.flip_progress = 1
        last_cards_shop.append(card)

    waiting = True
    previewed_card = None
    while waiting :
        refresh()
        # card_display.draw(screen)
        screen.blit(msg, (global_grid.place(msg,1,1,8,2)))
        
        update_draw_cards(last_cards_shop)
        

        

        mouse_pos = pygame.mouse.get_pos()
        for card in last_cards_shop:
            if card.rect.collidepoint(mouse_pos) and (not previewed_card or not previewed_card.rect.collidepoint(mouse_pos)) and waiting :
                if previewed_card : previewed_card.selected = False
                previewed_card = card
                previewed_card.selected = True
        
        for event in pygame.event.get():
            check_resize(event)
            if event.type == pygame.VIDEORESIZE :
                card_display.update_width_height(global_grid.col_size(7), global_grid.row_size(4), global_grid.coords(1,3))
                msg = render_multiline("Retenez bien l'ordre de ces cartes pour plus tard !",width=global_grid.col_size(8), height=global_grid.row_size(2), bold=True,color= (255, 255, 255), align="center")
                for i,card in enumerate(last_cards_shop) :
                    card.change_size(size := round(card_display.min_size()*0.9))
                    card.change_coords(*card_display.place((size,size), i, 0, 1, 1))
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
        screen.blit(msg, (global_grid.place(msg,1,1,8,2)))

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

    msg = render_multiline("Rebienvenu ! Vous vous souvenez bien de tous ?", width=global_grid.col_size(8), height=global_grid.row_size(1) ,align="center", bold=True, color=(255, 255, 255))
    msg2 = render_multiline("Effectuer une paire pour que l'achat vous soit proposé", width=global_grid.col_size(7), height=global_grid.row_size(0.5) ,align="center", italic=True, color=(255, 255, 255))

    

    order = [i for i in range(len(last_cards_shop))]
    seed_shuffle(order)

    card_display = grid(global_grid.coords(1,4),global_grid.col_size(8), global_grid.row_size(4), cols=shop_choices, rows=2)

    selection.clear()
    card_upgrades = []
    size = round(card_display.min_size()*0.9)
    for row in range(2) :
        if row==0 :
            for i,card in enumerate(last_cards_shop) :
                card : Card
                card.selected = False
                card.change_size(size)
                card.change_coords(*card_display.place((size,size), order[i], 0,1,1))

                card.flip_progress = 1
                card.flipped=True
                card_upgrades.append(card)
        if row==1 :
            for i in range(len(last_cards_shop)) :
                card = Card(*card_display.place((size,size), i, 1, 1, 1), card_upgrades[i].name, image= card_upgrades[i].image, color=card_upgrades[i].color,size=size, location="shop")
                card_upgrades.append(card)

    

    wait_for_respons = False
    ending = False 
    ending_last_time_out = 0
    while not ending:
        refresh()

        screen.blit(msg, global_grid.place(msg,1,1,8,1))
        screen.blit(msg2, global_grid.place(msg2,1,2,8,1))

        
        # pygame.draw.rect(screen, blend_multi(((230,200,130), (180,70,160),(120,95,200)), blend_constant), displayer, border_radius=10)
        update_draw_cards(card_upgrades)
        # Afficher les éclats en haut à droite
        update_draw_eclats()


        
        # Détecter le passage de souris sur une carte
        mouse_pos = pygame.mouse.get_pos()
        for card in card_upgrades:
            if card.rect.collidepoint(mouse_pos) and card.flip_progress>=0.5 and not card.remove and not ending:
                description_surface = generer_message_de_description(
                    {"nom": card.name, "lvl":objects_lvl.get(card.name, 0)+1,"lvl_init": objects_lvl.get(card.name, 0), "prix":UPGRADES_COST.get(card.name, 0)*(objects_lvl.get(card.name, 0)+1)},
                    width=global_grid.col_size(8), height=global_grid.row_size(2)
                )
                if description_surface:
                    pygame.draw.rect(screen, (0,0,0), global_grid.create_rect(1,8,8,2) ,border_radius=3)
                    screen.blit(description_surface, global_grid.place(description_surface, 1,8,8,2))
                break

        for event in pygame.event.get():
            check_resize(event)
            if event.type == pygame.VIDEORESIZE :
                msg = render_multiline("Rebienvenu ! Vous vous souvenez bien de tous ?", width=global_grid.col_size(8), height=global_grid.row_size(1) ,align="center", bold=True, color=(255, 255, 255))
                msg2 = desc_italic_font.render("Effectuer une paire pour que l'achat vous soit proposé", width=global_grid.col_size(7), height=global_grid.row_size(1) ,align="center", bold=True, color=(255, 255, 255))

                size=round(card_display.min_size()*0.9)
                for i,card in enumerate(card_upgrades) :
                    card.change_size(size)
                    card.change_coords(*card_display.place((size,size), i%shop_choices, i//shop_choices, 1, 1))




            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()    
            elif event.type == pygame.MOUSEBUTTONDOWN and not selection_locked:
                mouse_pos = event.pos
                for card in card_upgrades:
                    if card.rect.collidepoint(mouse_pos) and card in selection :
                        card.selected = False
                        selection.remove(card)  
                    elif card.rect.collidepoint(mouse_pos) and card not in selection and len(selection)<2 and not card.remove :
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
                    for card2 in card_upgrades :
                        if card2.name==card.name :
                            card2.remove = True
                selection.clear()
            elif validation(event) and wait_for_respons :
                if selection[0].name == selection[1].name and (cost := UPGRADES_COST.get(selection[0].name, 0)*(objects_lvl.get(selection[0].name, 0)+1)) <= eclat[0] :
                    add_eclat(-cost)
                    objects_lvl[selection[0].name] = objects_lvl.get(selection[0].name,0)+1
                    add_object(selection[0].name)
                
                selection_locked = False 
                wait_for_respons = False
                
                for card in selection :
                    card.selected = False
                    card.remove = True 
                    for card2 in card_upgrades :
                        if card2.name==card.name :
                            card2.remove = True
                
                selection.clear()
                
                
        
        if len(selection) == 2 :
            for card in selection : card.flipped = True
            if all(card.flip_progress==1 for card in selection) :
                if selection[0].name == selection[1].name :
                    msg = render_multiline("Voulez vous acheter ceci pour "+str(UPGRADES_COST.get(selection[0].name,5)*objects_lvl.get(selection[0].name, 1)) +" éclats ?", width=global_grid.col_size(8),height= global_grid.row_size(1) ,color= (255, 255, 255))
                    
                else :
                    msg = render_multiline("Mauvaise réponse : cartes perdues !", width=global_grid.col_size(8),height= global_grid.row_size(1) ,color= (255, 255, 255))
                
                wait_for_respons = True 
                selection_locked = True
        
        elif len([card for card in card_upgrades if not card.remove]) == 0 :
            ending = True
        
        else :
            msg = render_multiline("Rebienvenu ! Vous vous souvenez bien de tous ?", width=global_grid.col_size(8), height=global_grid.row_size(1) ,align="center", bold=True, color=(255, 255, 255))
            

        
        update_clock()
    
    last_cards_shop.clear()

def card_panel(card_names, width, height, show_competence=True, show_probs=False, page_len=None, is_previous=False, bg_panel_color=(55,55,55)):
    result = []

    nb_card = len(card_names)
    nb_pages = (nb_card // page_len + (1 if nb_card % page_len else 0)) if page_len else 1
    panel_grid = grid((0,0), width, height, cols=(1 + (show_competence * 2) + show_probs),
                      rows=page_len or nb_card)

    from description import generer_message_de_description

    for n_page in range(nb_pages):
        total_surf = Surface((panel_grid.width, panel_grid.height))
        pygame.draw.rect(total_surf, bg_panel_color, panel_grid.my_rect())


        start = n_page * (page_len or nb_card)
        end = start + (page_len or nb_card)
        page_cards = card_names[start:end]

        for n_card, c_name in enumerate(page_cards):
            card_size = panel_grid.min_size(0.9)
            xx, yy = panel_grid.place((card_size, card_size), 0, n_card, 1, 1)

            card = Card(xx, yy, c_name, all_images_dict.get(c_name), (0, 0, 0), card_size, "panel")
            card.flipped=True
            card.flip_progress=1
            

            if show_competence:
                if fighters_lvl.get(c_name, 0) - is_previous:
                    desc = generer_message_de_description(
                        {"nom": c_name, "lvl": fighters_lvl.get(c_name, 0) - is_previous,
                        "lvl_init": fighters_lvl.get(c_name, 0) - is_previous, "panel": True, "small":panel_grid.rows>3,
                        "show_previous": is_previous},
                        height=panel_grid.row_size(1),
                        width=panel_grid.col_size(2),
                    )
                    if desc:
                        total_surf.blit(desc, panel_grid.place(desc, 1, n_card, 2, 1))
            
            card.update()
            card.draw(total_surf)

        result.append(total_surf)

    return result

    
            










def lvl_rain(num_pairs=8, forced_cards = None):
    global selection_locked, move, last_succeed_move, combo
    cards : list["Card"]


    taille = round(min(SCREEN_HEIGHT*6/8, SCREEN_WIDTH*6/8))
    bords = SCREEN_WIDTH//2 - taille//2, SCREEN_HEIGHT//2 - taille//2
    playing_field, cards, cols, rows = create_board(num_pairs,bords[0],bords[1],taille,taille,forced_pairs=forced_cards, only_lvl_up_disponible=True)
    last_selection_time = 0
    running = True
    start_show_time = 0
    ending = 0
    move = 1
    show_previous_progress = 0
    first_move_effect = False

    last_window_changed_local = gtick()

    for card in cards :
        card.flipped = True

    wait_finish_return(cards)

    def retiens() :
        show_message("Retenez !", pos=global_grid.place((global_grid.col_size(4), global_grid.row_size(2)), 2, 1, 4, 1), recenterx=False)
    wait_with_cards(cards, showing_time*3, fun = retiens)

    for card in cards :
        card.flipped = False

    wait_finish_return(cards)



    while running:

        # if last_window_size_change > last_window_changed_local :

        #     for card in cards :
        #         cards.change



        draw_bg()
        
        if ((keys := pygame.key.get_pressed())[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                show_previous_progress = min(1,show_previous_progress+SHOW_PREVIOUS_SPEED)
        else :
                show_previous_progress = max(0,show_previous_progress-SHOW_PREVIOUS_SPEED)
        # événements
        for event in pygame.event.get():
            acceleration(event)
            check_resize(event)

            if event.type == pygame.VIDEORESIZE :

                if not ending :
                
                    # print(bords)
                    taille = round(min(SCREEN_HEIGHT*6/8, SCREEN_WIDTH*6/8))
                    bords = SCREEN_WIDTH//2 - taille//2, SCREEN_HEIGHT//2 - taille//2
                    playing_field.update_width_height(taille, taille, new_corner=(bords[0], bords[1]))
                    # print(playing_field.my_rect_info())

                    size = round(playing_field.col_size()*0.9)
                    margin = round(playing_field.col_size()*0.05)
                    for card in cards :
                        card.change_size_cords(size, *playing_field.coords(card.col, card.row, marging=margin))
                
                else :
                    end_text = create_optimal_msg(f"Fin de la pluie des niveaux ! Niveaux gagnés : {len(matched)}", width = global_grid.col_size(8), height=global_grid.row_size(1) ,color=(255, 255, 0))
                    recap_w, recap_h = global_grid.col_size(8), global_grid.row_size(6)
                    recap_surfaces = card_panel(list(matched), recap_w, recap_h)
                    recap_old_surface = card_panel(list(matched), recap_w, recap_h, is_previous=True)
                    recap_rect= global_grid.create_rect(1,2,8,7)


            

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
        
        if not first_move_effect :
            first_move_effect = True

            for o, lvl in objects_lvl.items() :
                activate_object_effect(o,lvl, cards)

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

                    names = [t.name for t in selection]
                    if any(names.count(card.name)> 1 for name in names) :
                        combo = combo + 1
                    else :
                        if fighters_lvl.get("Felinfeu",0) >= 4 and any(card.name=="Felinfeu" for card in selection) :
                            pop_up([card for card in selection if card.name=="Felinfeu"], "COMBO INNARETABLE", cards, (255,200,30))
                        else :
                            combo = 0
                            
                    activate_effect(selection, cards, nb_move=move)
                
                elif pygame.time.get_ticks() - start_show_time > showing_time :
                    names = [t.name for t in selection]
                    if any(names.count(name)>1 for name in names):
                    
                        add_score("match")

                        for c in selection:
                            c.matched = True
                            c.flipped = False
                            c.remove = True
                    else:
                        # add_lives(-1)
                        add_score("dontmatch")
                        for c in selection:
                            c.flipped = False
                    
                        names = [c.name for c in selection]
                        for card in cards :
                            card.selected = False
                            if card.name in names :
                                card.remove = True
                    
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
        if ending or all(c.remove for c in cards):
            if not ending :
                add_score("end_play")
                matched = set((card.name for card in cards if card.matched))
                for name in matched :
                    fighters_lvl[name] = fighters_lvl.get(name,0)+1
                recap_w, recap_h = global_grid.col_size(8), global_grid.row_size(6)
                recap_surfaces = card_panel(list(matched), recap_w, recap_h)
                recap_old_surface = card_panel(list(matched), recap_w, recap_h, is_previous=True)
                recap_rect= global_grid.create_rect(1,2,8,7)
                end_text = create_optimal_msg(f"Fin de la pluie des niveaux ! Niveaux gagnés : {len(matched)}", width = global_grid.col_size(8), height=global_grid.row_size(1) ,color=(255, 255, 0))

            pygame.draw.rect(screen, (55,55,55), recap_rect, border_radius=5)

            if not show_previous_progress :
                recap_surfaces[0].set_alpha(int(255*(1-show_previous_progress)))
                screen.blit(recap_surfaces[0], global_grid.place((recap_w, recap_h), 1,2,8,7))
            else :
                recap_surfaces[0].set_alpha(int(255*(1-show_previous_progress)))
                recap_old_surface[0].set_alpha(int(255*(show_previous_progress)))
                screen.blit(recap_surfaces[0], global_grid.place((recap_w, recap_h), 1,2,8,7))
                screen.blit(recap_old_surface[0], global_grid.place((recap_w, recap_h), 1,2,8,7))

            update_draw_score(player_score, player_lives)
            # gain_eclat = get_end_of_round_eclat(cards)
            
            screen.blit(end_text, global_grid.place(end_text, 1,1,8,1))
            
            ending = True
        
        update_clock()

def benediction_ou_pacte() :
    ## Proposer au joueur de choisir entre une bénédiction (1 effet aléatoire puissant) ou un pacte (1 effet aléatoire très puissant mais avec un effet néfaste derrière)
    global selection_locked
    selection.clear()
    from description import generer_apparition_message, generer_message_de_description
    selection_locked = False
    
    proposition = render_multiline("Deux voies s'offrent à vous ! Récupérer la bénédiction de Mère Féline, ou signer un pacte avec le culte de l'Ombre...", width= global_grid.col_size(6), height=global_grid.row_size(1), bold=True, color=(255, 255, 255))
    benec = render_multiline("La Bénédiction de Mère Féline : acceptez son généreux cadeau", width= global_grid.col_size(4*0.9), height=global_grid.row_size(1), bold=False, color=(255, 255, 100))
    malec = render_multiline("Un puissant pacte ! Cet effet dévastateur pourrait bien caché un sombre maléfice...", width= global_grid.col_size(4*0.9), height=global_grid.row_size(1), bold=False, color=(150, 50, 50))


    benec_name = seed_choice(all_benec, "benediction_choice")
    malec_name = seed_choice(all_malec, "pacte_choice")
    malec_name_malus = seed_choice([malus for malus in all_malus if malus!="solitude_malus" or sum(apparation_probability.values())>0.8], "pacte_malus_choice")

    card_benec = Card(
        max(0,SCREEN_WIDTH//4 - (size:=global_grid.min_size(2))//2), global_grid.coords(1,5)[1],
        benec_name,
        all_belec_malec_dict[benec_name],
        (255, 150, 150),
        size,
        location="benediction_or_pacte"
    )

    card_benec.flipped = True

    card_malec = Card(
        max(size,SCREEN_WIDTH - SCREEN_WIDTH//4 - size//2), global_grid.coords(1,5)[1],
        malec_name,
        all_belec_malec_dict[malec_name],
        (255, 150, 150),
        size,
        location="benediction_or_pacte"
    )

    # card_malec_malus = Card(
    #     int(max(size*1.2,SCREEN_WIDTH //2 - size*1.2//2)), global_grid.coords(1,5)[1],
    #     malec_name,
    #     all_belec_malec_dict[malec_name_malus],
    #     (255, 150, 150),
    #     int(size*1.2),
    #     location="benediction_or_pacte"
    # )

    card_malec.flipped = True


    description_surface_benec = generer_message_de_description(
        {"nom": benec_name,
         "for_benec_or_malec": True},
         width=global_grid.col_size(4), height=global_grid.row_size(2), for_benec=True)
    
    description_surface_malec = generer_message_de_description(
        {"nom": malec_name,
        "for_benec_or_malec": True},
        width=global_grid.col_size(4), height=global_grid.row_size(2), for_benec=True)
    
    waiting = True
    
    while waiting:
        refresh()

        screen.blit(benec, global_grid.place(benec, 1, 3, 4, 1))
        screen.blit(malec, global_grid.place(malec, 5, 3, 4, 1))

        screen.blit(proposition, global_grid.place(proposition, 2, 1, 6, 1))
        if description_surface_benec :
            screen.blit(description_surface_benec, global_grid.place(description_surface_benec, 1,7,4,2))
        
        if description_surface_malec :
            screen.blit(description_surface_malec, global_grid.place(description_surface_malec, 5,7,4,2))
        
        update_draw_eclats()
        update_draw_cards([card_benec, card_malec])
        # update_draw_score(player_score, player_lives)
  
        for event in pygame.event.get():
            check_resize(event)
            if event.type == pygame.VIDEORESIZE :
                proposition = render_multiline("Deux voies s'offrent à vous ! Récupérer la bénédiction de Mère Féline, ou signer un pacte avec le culte de l'Ombre...", width= global_grid.col_size(6), height=global_grid.row_size(1), bold=True, color=(255, 255, 255))
                benec = render_multiline("La Bénédiction de Mère Féline : acceptez son généreux cadeau", width= global_grid.col_size(4*0.9), height=global_grid.row_size(1), bold=False, color=(255, 255, 100))
                malec = render_multiline("Un puissant pacte ! Cet effet dévastateur pourrait bien cacher un sombre maléfice...", width= global_grid.col_size(4*0.9), height=global_grid.row_size(1), bold=False, color=(150, 50, 50))

                size = global_grid.min_size(2)
                card_benec.change_size(size)
                card_benec.change_coords(max(0,SCREEN_WIDTH//4 - (size:=global_grid.min_size(2))//2), global_grid.coords(1,5)[1])

                card_malec.change_size(size)
                card_malec.change_coords(max(size,SCREEN_WIDTH - SCREEN_WIDTH//4 - size//2), global_grid.coords(1,5)[1])

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif validation(event):
                if card_benec.rect.collidepoint(pygame.mouse.get_pos()) :
                    apply_benection_or_pacte(benec_name)
                    waiting = False
                elif card_malec.rect.collidepoint(pygame.mouse.get_pos()) :
                    apply_benection_or_pacte(malec_name)
                    waiting = False

                     # Faire apparaitre un nouveau ecran temporaire avec l'effet du malus qui été jusque la caché
                    show_malus_effect(malec_name_malus)
                
               



            elif rejet(event) :
                waiting = False
        
        update_clock()

def show_malus_effect(malus_name) :

    from description import generer_message_de_description
    description_surface_malus = generer_message_de_description(
        {"nom": malus_name,
        "for_benec_or_malec": True},
        width=global_grid.col_size(6), height=global_grid.row_size(3), for_benec=True)
    
    # On affiche également une carte
    card_malus = Card(
        max(0,SCREEN_WIDTH//2 - (size:=global_grid.min_size(2))//2), global_grid.coords(1,2)[1],
        malus_name,
        all_belec_malec_dict[malus_name],
        (255, 150, 150),
        size,
        location="benediction_or_pacte")
    card_malus.flipped = True

    
    waiting = True

    msg = render_multiline("Il été écrit en tout petit que vous subiriez aussi ceci... :", width= global_grid.col_size(8), height=global_grid.row_size(1), bold=True, color=(200, 50, 50))

    while waiting :
        refresh()

        # representer la carte
        update_draw_cards([card_malus])

        screen.blit(msg, global_grid.place(msg, 1,1,8,1))
        if description_surface_malus :
            screen.blit(description_surface_malus, global_grid.place(description_surface_malus, 1,4,6,3))
        
        for event in pygame.event.get():
            check_resize(event)
            if event.type == pygame.VIDEORESIZE :
                msg = render_multiline("Effet Néfaste du Pacte :", width= global_grid.col_size(6), height=global_grid.row_size(1), bold=True, color=(200, 50, 50))
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif validation(event) or rejet(event):
                waiting = False
                apply_benection_or_pacte(malus_name)
        
        update_clock()

    
def apply_benection_or_pacte(name_bonus):
    if name_bonus :
        match name_bonus :
            case "default_benec":
                global regain_PV_manche
                regain_PV_manche += 2
            
            case "default_malec_malus" :
                global max_player_live
                max_player_live = max(1, max_player_live - 10)
                if max_player_live > player_lives[0] :
                    player_lives[0] = max_player_live
            case "exhaustion_malec" :
                global exhaustion_effect
                exhaustion_effect += 2
            case "expansion_malec" :
                global expansion_effect
                expansion_effect += 1
            case "fier_entrainement_benec" :
                global training_choices
                training_choices += 1
            case "gloire_benec" :
                scores_constantes_modifiers_plus["match"] = scores_constantes_modifiers_plus.get("match",0) + 1
            case "honte_malus" :
                scores_constantes_modifiers_plus["match"] = scores_constantes_modifiers_plus.get("match",0) - 2
            case "solitude_malus" :
                for prob in apparation_probability :
                    apparation_probability[prob] = apparation_probability[prob]/2
            case "trou_malus" :
                global gain_eclat_bonus_manche 
                gain_eclat_bonus_manche * 0.8
            case "benec_providence" :
                scores_constantes_modifiers_plus["add_tag"]= scores_constantes_modifiers_plus.get("match",0) + 2
            case "fatigue_malus" :
                global showing_time
                showing_time = int(showing_time*0.8) + 1
                
    
    benec_and_malec.append(name_bonus)


def a_random_shuffle(cards, _):
    # Prends 2 cartes non retirés et les mélange
    
    available_cards = [card for card in cards if not card.remove]
    if len(available_cards) < 2 :
        return
    else :
        card1, card2 = seed_sample(available_cards, 2, "a_random_shuffle_choice")
        switch_place(card1, card2, cards, 800, "Mélange !", message_color=(240, 40, 200))

def lock_cards(cards, cards_to_lock=3, lock_duration=1, nb_preserved_cards=3):

    cards_to_lock = min(max(0,sum(1 for card in cards if not card.locked and not card.remove)-nb_preserved_cards), cards_to_lock)
    cards_locked = seed_sample(cards, cards_to_lock, "lock_cards_boss") 
    card:Card
    for card in cards_locked:
        card.set_lock(lock_duration)
    
    if cards_locked : pop_up(cards_locked, "VERROUILLÉ", cards, (100,100,100), time=1000)


ALL_BOSS_SKILLS  = {"shuffle": a_random_shuffle, "lock" : lock_cards}
ALL_BOSS_SKILLS_LIST = list(ALL_BOSS_SKILLS.values())


def get_boss(round_number, nb_pairs):
    is_boss = False

    to_reach = None
    errors = None
    name = ""

    skills = []

    score_pallier = (10, 30, 50, 100, 200, 1000, 3000, 8000, 15000, 50000, 100000, 1000000, 1000000000, 100000000000000)


    if round_number == 10 :
        is_boss = True
        errors = nb_pairs * 2
        skills.append(ALL_BOSS_SKILLS["shuffle"])
        name = "Le Grand Mélangeur"
    elif round_number == 15 :
        is_boss = True
        to_reach = nb_pairs * 5 + score_pallier[0]
        name = "Premier Testeur"
    elif round_number >= 20 and round_number % 5 == 0 :
        is_boss = True
        errors = int(nb_pairs * 2.5)
        to_reach = nb_pairs * 5 + score_pallier[((round_number-20)//5)]

        name = "Le "+str((round_number-20)//5 + 2)+"ème Testeur"
        skills.append(ALL_BOSS_SKILLS["lock"])
        # skills.append(ALL_BOSS_SKILLS_LIST[round_number//5 % len(ALL_BOSS_SKILLS_LIST)])
    
    if is_boss:
        return Boss(name, to_reach, errors, skills)

    


    


def do_next() :
    global selection_locked
    global move

    memo_shopped = False
    while player_lives[0]>0 :
        move = 0
        if game["round"]%8 == 0 and game["state"]=="play": # dernier element car pour l'instant la pluie est soft_lock à la deuxieme occurence
            selection_locked = False
            lvl_rain(forced_cards=get_apparition_cards())
        
        if (game["round"]+5)%10 == 0 and game["state"]=="play": # dernier element car pour l'instant la pluie est soft_lock à la deuxieme occurence
            selection_locked = False
            benediction_ou_pacte()

        if game["round"]%2==0 and not memo_shopped and (not "proposal" in game["state"]):
            game["state"]="memo_shop"
            memo_shopped = True
        
        if game["state"] == "play" :
            switch_bg_to(BG_COLORS["play"])

            selection_locked = False
            play_memory((num_pairs:= round(2+((game["round"])/increase_difficulty))), forced_cards=get_apparition_cards(), from_boss=get_boss(game["round"], num_pairs))

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
            if get_random("proposal_after_training_prob") < proposal_after_training_prob :
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


def add_object(name, sp_lvl=None):
    lvl = sp_lvl or objects_lvl.get(name,0)

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
    

    # for name, lvl in guaranted :
    #     apparation_probability[name] = 1
    #     fighters_lvl[name] = lvl
    
    # for o, lvl in guaranted_objet :
    #     objects_lvl[o] = lvl 
    #     add_object(o)

    start_run(**run_parameter)
    # apparation_probability["Lori_Et_Les_Boaobs"]=1
    # fighters_lvl["Lori_Et_Les_Boaobs"]=7
    # apparation_probability["Lo"]=1
    # fighters_lvl["Lo"]=4
    # run_seed="m"

    # guaranted_objet = [("Trognon",1)] # (nom, niveau)
    # for o, lvl in guaranted_objet :
    #     objects_lvl[o] = lvl 
    #     add_object(o)


    # game["state"]="training"


    while True :
        do_next()
