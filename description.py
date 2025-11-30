import pygame
from font import desc_font, desc_italic_font, font_police, desc_font_panel, desc_italic_font_panel
import math


def romain(nb):
        if not isinstance(nb, int) or nb < 1 or nb > 1000:
            return ""
        vals = [
            (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
            (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
            (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")
        ]
        res = []
        n = nb
        for value, numeral in vals:
            if n == 0:
                break
            count, n = divmod(n, value)
            res.append(numeral * count)
        return "".join(res)


lvll = lambda args : args.get('lvl',1) 
romainlvl = lambda args : (romain(lvll(args)), False)
romainlvldesc = lambda args : (romain(lvll(args)), True)









upgrades = {
    "8_Volt" : ("Quand elle est jouée, elle fait vibrer les autres 8-Volt sur un rayon de ", lambda args: (args.get('lvl', 1),False), " autour d'elle"),
    "Michel" : ("Applique la marque michel aux cartes jouées avec lui.","","[sub]michel : pour chaque carte adjacente, vous avez ", lambda args: (args.get('lvl', 1), True), "[sub] chance sur ",lambda args: (args.get('lvl', 1) + 3, True),"[sub] de la réveller pour 0.4 + ", lambda args: (args.get('lvl', 1) * 0.15,True), "[sub] secondes"),
    "Max" : ("Quand ils sont matchés,",lambda args: (" révèlent la première et dernière carte de chaque ligne avec un Max (cette effet peut s'améliorer au niveau 3)" if args.get('lvl',1)<3 else f"révèlent les {args.get('lvl',1)//3+1} premières et dernières carte de chaque ligne avec un Max", False), ""),
    "Flosette" : ("Quand elles sont matchées, elles appliquent la marque Soin ",lambda args: (romain((args.get('lvl',2)+2)//2), False)," aux cartes","","dans un rayon de ", lambda args: (math.ceil(math.sqrt(args.get('lvl',1))),False)," autour d'elles","","[sub]Soin ", lambda args: (romain((args.get('lvl',2)+2)//2),True), "[sub] : régènère 1PV en produisant un match. Reste ",lambda args: ((args.get('lvl',2)+2)//2,True),"[sub] coups"),
    "Le_Vrilleur" : ("Quand il est joué, il génère ",lambda args:(args.get('lvl',1)+2,False)," de score pour chaque carte non retournée adjacente"),
    "Lame_Sadique" : ("Effectuer un match offre ", lambda args: ('x'+str(1+(args.get('lvl',1)*0.5)),False)," points, mais chaque perte de vie est augmentée de ",lambda args:(1+(args.get('lvl',1)//4),False),"PV"),
    "Bulle_D_Eau" : ("Vous êtes invincible pendant ",lambda a : (f"vos {lvll(a)} premiers coups" if lvll(a)>1 else 'votre premier coup',False)," de chaque partie"),
    "Reveil_Endormi" : (("A l'achat, augmente définitivement de 0.3 secondes le temps d'affichage des cartes jouées"),),
    "Allumette": ("Quand vous enchaînez les matchs, vous gagnez ",lambda args : (2+args.get('lvl',1),False)," points par match consécutif","","[sub]Exemple : votre 4 réussite d'affilé offrira ",lambda args : (2+args.get('lvl',1),True),"[sub]x4 points"),
    "Pipette_Elementaire": ("Quand une de vos cartes en révèle une autre, elle copie toutes ses marques à la carte révélée",lambda args : (f"Les marques copiées sont améliorées ( +{args.get('lvl',1) - 1})", False) if args.get('lvl',1)<=1 else ("(Un effet supplémentaire est révélé au niveau 2)",True)),
    "Tireur_Pro": ("Applique la marque Ciblé aux cartes jouées avec lui.","","[sub]Ciblé : la carte vibre si elle est de dos pendant que une carte identique est jouée sur une distance de ",lambda args:(args.get('lvl',1)+1,True),"[sub] cases"),
    "Piquante": ("Si elle est jouée sans qu'elle produise un match, vous perdez ",lambda args:(1 + args.get('lvl',1)//3,False)," PV","","Sinon, vous gagnez les points de ",lambda args:(1 + args.get('lvl',1)//3,False)," match"),
    "Chat_De_Compagnie": ("Gagnez ", lambda args : (lvll(args), False)," points par soin gagné.","","Vous avez ",lambda a : (lvll(a),False)," chance sur ",lambda a : (lvll(a)+9,False)," d'améliorer chaque soin subis de 1 PV"),
    "Ghosting": ("Lors de la selection des paires pour les prochaines manches, chaque carte sans compétence a ",lambda a : (lvll(a),False)," chance sur ",lambda a : (lvll(a)+14,False)," d'être remplacée par une troupe avec compétence'.","","[sub] Dans la limite du possible"),
    "Canon_A_Energie": ("Génère un rayon révellant toutes les cartes d'une colonne toute les 9 vibrations de carte effectuées.","","La révélation dure ",lambda a : ((200+100*lvll(a))/1000, False), " secondes et génère ",lambda a : (2*lvll(a), False)," points par carte révélée.","",lambda a : (f"La sélection de la colonne ciblée {'très '*((lvll(a)//3)-1)} est améliorée" if lvll(a)>=3 else "Une amélioration additionnelle est disponible au niveau 3", False)),
    "Bouquet_Medicinal":("A l'achat, vous guerris ",lambda a : (lvll(a)*5,False), "PV instantannément"),
    "Maniak":("Maniak est considéré comme autour de toute les autres cartes en jeu.",lambda a : (f"Le rayon de proximité de Maniak est agrandis de {(lvll(a)//3)} case{'s' if (lvll(a)//3)>1 else ''}" if lvll(a)>=3 else "Une amélioration additionnelle est disponible au niveau 3", False)),
    "Mc_Cookie":("Quand ils sont matchés, chacun produit ",lambda a : (lvll(a)+1//2, False)," éclat(s) + ",lambda a: (lvll(a)//2, False)," éclat(s) par marque placé sur lui-même"),
    "Fantome_A_Cheveux":("Quand il est joué, il active toutes les compétences des personnages qui l'ont révélé dans cette manche","","[sub]La puissance de cette compétence ne dépassera pas le niveau ", lambda a : (lvll(a),True),"[sub].","","[sub]Les compétences copiées sont uniquement celles qui s'active en jouant la carte (exemple : passif de Maniak est exclu)"),
    "Catchy":("Quand il est joué, et que au moins 2 cartes sont adjacentes, en mélange 2 et génère ", lambda a : (2+lvll(a)*4,False)," points.","",lambda a : (f"A également 1 chance sur 4 d'échanger ensuite sa propre place avec une carte du jeu, en générant {(lvll(a)+6)//2} éclats" if lvll(a)>=5 else "Une amélioration additionnelle est disponible au niveau 5", False)),
    "Bubble_Man":("Applique la marque Englué ", romainlvl, " aux carte jouées avec lui.","", lambda a : (f"Les Bubble Mans inflige Englué {romain(lvll(a)+2)} aux cartes qui leurs sont adjacente en faisant un match" if lvll(a)>=4 else "Une amélioration additionnelle est disponible au niveau 4", False) ,"","[sub]Englué ", romainlvldesc,"[sub] : Annule les déplacements impliquant la carte englué. La carte a ",lambda a : ((l:=lvll(a)) == 1 and "un peu" or l==2 and "relativement" or l==3 and "plutôt bien" or l==4 and "vraiment" or l==5 and "beaucoup trop" or "extrêmement",True),"[sub] du mal à se remettre face cachée"),
    "Piouchador":("Quand il est sencé recevoir une marque provenant d'une autre troupe, vibre et renvoit la marque à ceux qui l'ont envoyé.","Cette marque est amélioré de ", lambda a : (lvll(a),False)," niveau."),
    "Trognon":("Au début de chaque partie de memory, régénère ",lambda a : (lvll(a),False)," PV et applique la marque Poison ", romainlvl, " à ", lambda a : (1+(lvll(a)//2), False), " cartes en jeu","","[sub]Poison ", romainlvldesc, "[sub] : A chaque fois qu'un coup est joué, les cartes empoissonné ne matchant pas enlève ",lambda a : (lvll(a),True),"[sub] points et vibrent. Le poison diminue chaque tour"),
    "Lo":("Quand iels sont matché.es, iels appliquent à toutes les troupes de leur lignes Barageau ",romainlvl,"","[sub]Barag'eau ",romainlvldesc, "[sub] : Les pertes de vie provoquées avec cette troupe ont ",lambda a : (f'{100*lvll(a)/(lvll(a)+4):.2f}',True),"[sub]% de chance de s'annuler. En s'activant, a ",lambda a : (f'{100*(40/(50+lvll(a))):.2f}',True), "[sub]% de chance de se détruire."),
    "Felinfeu":("Génère ",lambda a : (1+(lvll(a)//2), False), " x [combo actuel] points en matchant.","", lambda a : (f"Un coup perdant qui contient Félinfeu ne remet plus le score à 0" if lvll(a)>=4 else "Une amélioration additionnelle est disponible au niveau 4", False)),
    "Lori_Et_Les_Boaobs":("Si ils sont joués sans produire un match, applique Soin ", lambda a : (romain(lvll(a)+1),False), " aux cartes jouées avec lui si elles sont adjacentes, ou Poison ",lambda a : (romain((lvll(a)+1)//2),False)," le cas échéant.","",lambda a : (f"En produisant un match, convertie toutes les marques de Poison en marque de Soin à durée égale, et génère [tours gueris]*{(lvll(a)+3)//5} points" if lvll(a) >= 3 else "un effet additionnel est disponible au niveau 3",True),"","[sub]Soin ", lambda a : (romain(lvll(a)+1),True), "[sub] : régènère 1PV en produisant un match. Reste ",lambda a : ((lvll(a)+1),True),"[sub] coups","","[sub]Poison ", lambda a : (romain((lvll(a)+1)//2),True), "[sub] : A chaque fois qu'un coup est joué, les cartes empoissonnées ne matchant pas enlèvent " ,lambda a : (((lvll(a)+1)//2),True),"[sub] points et vibrent. Le poison diminue chaque tour"),
    "Celeste":("En produisant un match, elles ont ", lambda a : (f'{100*(lvll(a)/(2+lvll(a))):.2f}',False), "% de chance pour chaque carte adjacente de la révéller et d'appliquer Bénit ", lambda a : (romain(lvll(a)),False) ,"","[sub]Bénit ", lambda a : (romain(lvll(a)),True), "[sub] : quand une carte bénite reçoit une marque, elle génère [niveau de la marque] x ", lambda a : (((1+lvll(a)//2)),True), "[sub] points"),
    "Bossu_Etoile":("Quand ils produisent un match, chaque carte non retournée a ", lambda a : (f'{100*(lvll(a)/(7+lvll(a))):.2f}',False), "% de chance de vibrer et d'obtenir Benit ", romainlvl,"","[sub]Bénit ", romainlvldesc, "[sub] : quand une carte bénite reçoit une marque, elle génère [niveau de la marque] x ", lambda a : (((1+lvll(a)//2)),True), "[sub] points"),}

benedictions_maledictions = lambda args : ({
     "default_benec": ("Vous obtenez définitivement +2 PV soignés à chaque fin de partie",),
     "default_malec": ("Débloquer une compétence en entrainement améliorera le personnage d'un niveau supplémentaire",),
     "default_malec_malus":("Vous perdez 10 PV MAX définitivement",),
     "gloire_benec": ("Chaque match vous rapporte +1 point supplémentaire",),
    "expansion_malec": ("Améliore le rayon de proximité de tous les personnage de 1 case",),
    "solitude_malus": ("Divise par 2 toutes les probabilités d'apparitions spontannées actuelles",),
    "honte_malus": ("Gagnez 2 points de moins par match définitivement",),
    "exhaustion_malec": ("Améliore le niveau des marques infligés de 2 pour toute les marques",),
    "fier_entrainement_benec": ("Vous avez 1 choix supplémentaire lors des entrainements",),
}).get(args.get("nom",""))




def find_font_size_msg(message, width, height, initial_font_size=10, police=font_police,
                       bold=False, italic=False):

    font_size = initial_font_size

    # Fonction interne pour calculer les dimensions du texte
    def get_size(fs):
        font = pygame.font.SysFont(police, fs, bold=bold, italic=italic)
        msg = font.render(message, False, (0, 0, 0))
        return msg.get_width(), msg.get_height()

    w, h = get_size(font_size)

    print(font_size)


    # Tant que ça rentre, on augmente
    while w < width and h < height:
        font_size += 1
        w, h = get_size(font_size)

    # On a dépassé → on redescend d’un cran
    font_size -= 1
    w, h = get_size(font_size)

    print(font_size)

    # Si jamais on dépasse encore, on ajuste vers le bas
    while (w > width or h > height) and font_size > 1:
        font_size -= 1
        w, h = get_size(font_size)

    return max(font_size, 1)


def create_optimal_msg(message, width, height, initial_font_size = 10, police=font_police, bold=False, italic=False, color=(0,0,0), antialias = True) :
    font = pygame.font.SysFont(police, find_font_size_msg(message,width,height, initial_font_size, police, bold, italic), bold=bold, italic=italic)
    return font.render(message, antialias, color)



DISPLAY_NAMES = {
    "8_Volt" : "8 Volt",
    "Les_Jumeaux" : "Les Jum'eaux",
    "Lori_Et_Les_Boaobs" : "Lori et les Boaobs",
    "Bossu_Etoile" : "Bossu Etoilé",
    "Masseuse_Des_Cieux" : "Masseuse des Cieux",
    "Le_Vrilleur": "Le Vrilleur",
    "Smacker_Girl" : "Smacker-Girl",
    "Bubble_Man" : "Bubble-Man",
    "Mc_Cookie":"Mc Cookie",
    "Tireur_Pro":"Tireur Pro",
    "Fantome_A_Cheveux":"Fantôme à Cheveux",
    "Croqueur_Avide":"Croqueur Avide",
    "Les_Elemetistes":"Les Elémétistes",
    "Reveil_Endormi":"Réveil Endormis",
    "Lame_Sadique":"Lame Sadique",
    "Bulle_D_Eau":"Bulle d'eau protectrice",
    "Canon_A_Energie":"Canon à Energie",
    "Pipette_Elementaire":"Pipette Elémentaire",
    "Bouquet_Medicinal":"Bouquet Médicinal",
    "Chat_De_Compagnie":"Chat de Compagnie",
    "Cheffe_Chauffocoeur":"Cheffe Chauffocoeur",
    "default_benec":"Bénédiction de Guérison",
    "default_malec":"Pacte de Puissace",
    "default_malec_malus":"Sappage d'énergie",
    "gloire_benec":"Bénédiction de la Gloire",
    "expansion_malec":"Pacte d'Expansion",
    "solitude_malus":"Isolement Eternel",
    "honte_malus":"Honte Infinie",
    "exhaustion_malec":"Pacte d'Exhaustion",
    "fier_entrainement_benec":"Bénédiction de l'Entraînement Fier",
}

PRONOUNS = {
    "8_Volt" : "elle",
    "Les_Jumeaux" : "ils",
    "Lori_Et_Les_Boaobs" : "ils",
    "Bossu_Etoile" : "il",
    "Masseuse_Des_Cieux" : "elle",
    "Le_Vrilleur": "il",
    "Smacker_Girl" : "elle",
    "Bubble_Man" : "il",
    "Mc_Cookie":"il",
    "Tireur_Pro":"il",
    "Fantome_A_Cheveux":"il",
    "Croqueur_Avide":"il",
    "Les_Elemetistes":"ils",
    "Reveil_Endormi":"il",
    "Lame_Sadique":"elle",
    "Bulle_D_Eau":"elle",
    "Canon_A_Energie":"il",
    "Pipette_Elementaire":"elle",
    "Bouquet_Medicinal":"il",
    "Chat_De_Compagnie":"il",
    "Cheffe_Chauffocoeur":"elle",
    "Max" : "il",
    "Catchy": "il",
    "Felinfeu": "il",
    "Flosette" : "elle",
    "Lo" : "il",
    "Maniak" : "iel",
    "Michel" : "il",
    "Ordinateur":"il",
    "Piouchador":'il',
    "Piquante":"elle",
    "Titanique":"elle"
}



def entete(args) : # détermine le titre
    text = tuple()
    display_name = DISPLAY_NAMES.get(args.get("nom","..."), args.get("nom","..."))
    lvl = args.get("lvl",0)

    if args.get('for_benec_or_malec') :
        text += ((f"Effet de "+display_name+" :"),)
        text += ((""),)
    elif args.get("proposal", False) :
        text += ((f"Compétence du personnage :{ ' (à débloquer dans la partie !)' if not lvl else '' }"),)
        text += ((""),)
    elif args.get("panel",False) :
        text += ((display_name+" au niveau "),)
        text += (lambda args : (args.get('lvl',0), False),)
        text += ((" : "),)
        text += ((""),)
    else :
        if args.get("lvl_init",0) == 0 :
            text += (("Débloquer la compétence de "+display_name+" pour "),)
            text += (lambda args : (args.get('prix',0), False),)
            text += ((" éclats ?"),)
        else :
            if args.get("show_previous",0) :
                text += (("Compétence à votre niveau actuelle ( "),)
                text += ((lambda args : (str(args.get("lvl",0)), False)),)
                text += ((" ) :"),)
            else :
                text += (("Contre "+str(args.get('prix',"0"))+" éclat : gain de niveau de " +display_name+": "+str(args.get("lvl_init",0)) +" -> "),)
                text += ((lambda args : (str(args.get("lvl",0)), False)),)
                text += ((" ?"),)
        
        text += ((""),)
    
    return text


def generer_apparition_message(args, width, height):
    nom = args.get("nom", "")
    ancienne_proba = args.get("ancienne_probability",0)
    if ancienne_proba == int(ancienne_proba) : ancienne_proba = int(ancienne_proba)
    else : ancienne_proba = round(ancienne_proba, 2)
    nouvelle_proba = args.get("new_probability",10)
    if nouvelle_proba == int(nouvelle_proba) : nouvelle_proba = int(nouvelle_proba)
    else : nouvelle_proba = round(nouvelle_proba, 2)
    prix = args.get("prix", 0)
    display_name = DISPLAY_NAMES.get(args.get("nom","..."), args.get("nom","..."))
    pronons = PRONOUNS.get(nom, "iel")


    # Construire une liste de "tokens" : {text, color, italic, jump}
    tokens = (
        [{"text": f"Enrôler {display_name} pour {prix} eclats :", "color": (255, 255, 255), "italic": False},
         {"jump":True},
         {"text": f"{pronons.capitalize()} aura ", "color": (255, 255, 255), "italic": False },
         {"text": f"{nouvelle_proba}%", "color": (200, 80, 200), "italic": False},
         {"text": f" de chance d'apparaître spontanément à chaque partie", "color": (255, 255, 255), "italic": False},
         ] 
         if args.get("ancienne_probability") == 0 else
        [{"text": f"Renforcer l'engagement avec {nom} pour {prix} eclats : proba d'apparition spontanée", "color": (255, 255, 255), "italic": False},
         {"text": f" {ancienne_proba}%", "color": (255, 50, 50), "italic": False},
         {"text": f" -> ", "color": (0, 255, 150), "italic": False},
         {"text": f"{nouvelle_proba}%", "color": (200, 80, 200), "italic": False}]
    )
    if not args.get("from_bonus") :
        tokens.append({"jump":True})
        tokens.append({"text":f"(Ceci va également vous garantir que {display_name} sera proposé au prochain entrainement)", "color":(255,255,255), "italic":True})

    return generer_message_via_tokens(tokens, width, height)


def generer_message_via_tokens(tokens, width, height,): 
    final_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    x_offset = 0
    y_offset = 0
    line_spacing = 5
    max_width = max(0, width - 10)  # marge

    for token in tokens:
        # gestion du saut de ligne explicite
        if token.get("jump"):
            # avancer d'une ligne vide
            font_to_use = (desc_italic_font if token.get("italic") else desc_font) 
            y_offset += font_to_use.get_height() + line_spacing
            x_offset = 0
            continue

        font_to_use = desc_italic_font if token.get("italic") else desc_font
        color = token["color"] if token.get("color") else (255, 255, 255)
        text = token["text"]

        # découper en mots pour faire le retour à la ligne automatiquement
        words = text.split(" ")
        for i, word in enumerate(words):
            # conserver l'espace sauf après le dernier mot
            piece = word + (" " if i < len(words) - 1 else "")
            if piece == "":
                continue

            word_surf = font_to_use.render(piece, True, color)
            tw = word_surf.get_width()
            th = max(word_surf.get_height(), font_to_use.get_height())

            # retour à la ligne si dépassement
            if x_offset + tw > max_width and x_offset != 0:
                y_offset += th + line_spacing
                x_offset = 0

            # si on dépasse la hauteur, on arrête (ou on pourrait clipper)
            if y_offset + th > height:
                break

            final_surface.blit(word_surf, (x_offset, y_offset))
            x_offset += tw

        # après chaque token non-jump, on peut continuer sur la même ligne
        # (les sauts de token vides sont gérés ci-dessus)


    # Re-evaluer la hauteur total 
    total_height = y_offset + font_to_use.get_height()
    if total_height < height:
        final_surface = final_surface.subsurface((0, 0, width, total_height))
    return final_surface

def generer_message_de_description(args, width, height, green_value=(0, 255, 150), for_benec = False):
    if args.get('show_previous') : green_value = (180, 50, 200)

    nom = args.get("nom", "")
    if nom not in upgrades and not for_benec:
        return None

    description = entete(args) + (not for_benec and upgrades[nom] or benedictions_maledictions(args) or ("Description indisponible.",))

    # Construire une liste de "tokens" : {text, green, italic, jump}
    tokens = []
    current = {"text": "", "green": False, "italic": False, "jump": False}

    for element in description:
        if callable(element):
            # finalize current si besoin
            if current["text"] != "":
                tokens.append(current)
                current = {"text": "", "green": False, "italic": False, "jump": False}
            eval_text, eval_italique = (element(args))
            tokens.append({"text": str(eval_text), "green": True, "italic": eval_italique, "jump": False})
        else:
            if element == "":
                if current["text"] != "":
                    tokens.append(current)
                    current = {"text": "", "green": False, "italic": False, "jump": False}
                tokens.append({"text": "", "green": False, "italic": False, "jump": True})
            elif element.startswith("[sub]"):
                current["text"] += element[5:]
                current["italic"] = True
            else:
                current["text"] += str(element)

    # append remaining current
    if current["text"] != "" or current["italic"] or current["green"]:
        tokens.append(current)

    # Création de la surface finale
    final_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    x_offset = 0
    y_offset = 0
    line_spacing = 5
    max_width = max(0, width - 10)  # marge

    for token in tokens:
        # gestion du saut de ligne explicite
        if token["jump"]:
            # avancer d'une ligne vide
            font_to_use = (desc_italic_font if token["italic"] else desc_font) if not args.get("small") else (desc_italic_font_panel if token["italic"] else desc_font_panel)
            y_offset += font_to_use.get_height() + line_spacing
            x_offset = 0
            continue

        font_to_use = (desc_italic_font if token["italic"] else desc_font) if not args.get("small") else (desc_italic_font_panel if token["italic"] else desc_font_panel)
        color = green_value if token["green"] else (255, 255, 255)
        text = token["text"]

        # découper en mots pour faire le retour à la ligne automatiquement
        words = text.split(" ")
        for i, word in enumerate(words):
            # conserver l'espace sauf après le dernier mot
            piece = word + (" " if i < len(words) - 1 else "")
            if piece == "":
                continue

            word_surf = font_to_use.render(piece, True, color)
            tw = word_surf.get_width()
            th = max(word_surf.get_height(), font_to_use.get_height())

            # retour à la ligne si dépassement
            if x_offset + tw > max_width and x_offset != 0:
                y_offset += th + line_spacing
                x_offset = 0

            # si on dépasse la hauteur, on arrête (ou on pourrait clipper)
            if y_offset + th > height:
                break

            final_surface.blit(word_surf, (x_offset, y_offset))
            x_offset += tw

        # après chaque token non-jump, on peut continuer sur la même ligne
        # (les sauts de token vides sont gérés ci-dessus)


    # Re-evaluer la hauteur total 
    total_height = y_offset + font_to_use.get_height()
    if total_height < height:
        final_surface = final_surface.subsurface((0, 0, width, total_height))
    return final_surface



