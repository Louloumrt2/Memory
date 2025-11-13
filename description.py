import pygame
from font import desc_font, desc_italic_font
import math

lvll = lambda args : args.get('lvl',1) 

upgrades = {
    "8_Volt" : ("Quand elle est jouée, elle fait vibrer les autres 8-Volt sur un rayon de ", lambda args: (args.get('lvl', 1),False), " autour d'elle"),
    "Michel" : ("Applique la marque michel aux cartes jouées avec lui.","","[sub]michel : pour chaque carte adjacente, vous avez ", lambda args: (args.get('lvl', 1), True), "[sub] chance sur ",lambda args: (args.get('lvl', 1) + 3, True),"[sub] de la réveller pour 0.4 + ", lambda args: (args.get('lvl', 1) * 0.15,True), "[sub] secondes"),
    "Max" : ("Quand ils sont matchés,",lambda args: (" révèlent la première et dernière carte de chaque ligne avec un Max (cette effet peut s'améliorer au niveau 3)" if args.get('lvl',1)<3 else f"révèlent les {args.get('lvl',1)//3+1} premières et dernières carte de chaque ligne avec un Max", False), ""),
    "Flosette" : ("Quand elles sont matchées, elles appliquent la marque Soin ",lambda args: (romain((args.get('lvl',2)+2)//2), False)," aux cartes","","dans un rayon de ", lambda args: (math.ceil(math.sqrt(args.get('lvl',1))),False)," autour d'elles","","[sub]Soin ", lambda args: (romain((args.get('lvl',2)+2)//2),True), "[sub] : régènère 1PV en produisant un match. Reste ",lambda args: ((args.get('lvl',2)+2)//2,True),"[sub] coups"),
    "Le_Vrilleur" : ("Quand il est joué, il génère ",lambda args:(args.get('lvl',1)+2,False)," de score pour chaque carte non retournée adjacente"),
    "Lame_Sadique" : ("Effectuer un match offre ", lambda args: ('x'+str(1+(args.get('lvl',1)*0.5)),False)," points, mais chaque perte de vie est augmentée de ",lambda args:(1+(args.get('lvl',1)//4),False),"PV"),
    "Bulle_D_Eau" : ("Vous immunise ", lambda args: (('à la ' if (lvl:=args.get('lvl',1)) == 1 else 'aux ') + ('première perte' if lvl == 1 else str(lvl)+' premières pertes '),False)," de PV de chaque partie de memory qui suit"),
    "Reveil_Endormi" : (("A l'achat, augmente définitivement de 0.3 secondes le temps d'affichage des cartes jouées"),),
    "Allumette": ("Quand vous enchaînez les matchs, vous gagnez ",lambda args : (2+args.get('lvl',1),False)," points par match consécutif","","[sub]Exemple : votre 4 réussite d'affilé offrira ",lambda args : (2+args.get('lvl',1),True),"x4 points"),
    "Pipette_Elementaire": ("Quand une de vos cartes en révèle une autre, elle copie toutes ses marques à la carte révélée",lambda args : (f"Les marques copiées sont améliorées ( +{args.get('lvl',1) - 1})", False) if args.get('lvl',1)<=1 else ("(Un effet supplémentaire est révélé au niveau 2)",True)),
    "Tireur_Pro": ("Applique la marque Ciblé aux cartes jouées avec lui.","","[sub]Ciblé : la carte vibre si elle est de dos pendant que une carte identique est jouée sur une distance de ",lambda args:(args.get('lvl',1)+1,True),"[sub] cases"),
    "Piquante": ("Si elle est jouée sans qu'elle produise un match, vous perdez",lambda args:(1 + args.get('lvl',1)//3,False)," PV","","Sinon, vous gagnez les points de ",lambda args:(1 + args.get('lvl',1)//3,False)," match"),
    "Chat_De_Compagnie": ("Gagnez ", lambda args : (lvll(args), False)," points par soin gagné.","","Vous avez ",lambda a : (lvll(a),False)," chance sur ",lambda a : (lvll(a)+4,False)," d'améliorer chaque soin subis de 1 PV"),
    "Ghosting": ("Lors de la selection des paires pour les prochaines manches, chaque carte sans compétence a ",lambda a : (lvll(a),False)," chance sur ",lambda a : (lvll(a)+14,False)," d'être remplacée par une troupe avec compétence'.","[sub] Dans la limite du possible"),
    "Canon_A_Energie": ("Génère un rayon révellant toutes les cartes d'une colonne toute les 9 vibrations de carte effectuées.","","La révélation dure ",lambda a : (200+50*lvll(a)/1000, False), " secondes et génère ",lambda a : (2*lvll(a), False)," points par carte révélée.","",lambda a : (f"La sélection de la colonne ciblée {'très '*((lvll(a)//3)-1)} est améliorée" if lvll(a)>3 else "Une amélioration additionnelle est disponible au niveau 3", False)),
    "Bouquet_Medicinal":("A l'achat, vous guerris ",lambda a : (lvll(a)*5,False), "PV instantannément"),
    "Maniak":("Maniak est considéré comme autour de toute les autres cartes en jeu.",lambda a : (f"Le rayon de proximité de Maniak est agrandis de {(lvll(a)//3)} case{'s' if (lvll(a)//3)>1 else ''}" if lvll(a)>3 else "Une amélioration additionnelle est disponible au niveau 3", False)),
    "Mc_Cookie":("Quand ils sont matchés, chacun produit ",lambda a : (lvll(a)+1//2, False)," éclat(s) + ",lambda a: (lvll(a)//2, False)," éclat(s) par marque placé sur lui-même"),
    "Fantome_A_Cheveux":("Quand il est joué, il active toutes les compétences des personnages qui l'ont révélé dans cette manche","","[sub]La puissance de cette compétence ne dépassera pas le niveau ", lambda a : (lvll(a),True),"[sub].","","[sub]Les compétences copiées sont uniquement celles qui s'active en jouant la carte (exemple : passif de Maniak est exclu)")}


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
}

def entete(args) : # détermine le titre
    text = tuple()
    display_name = DISPLAY_NAMES.get(args.get("nom","..."), args.get("nom","..."))

    if args.get("proposal", False) :
        text += (("Compétence du personnage :"),)
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
    nouvelle_proba = args.get("new_probability",10)
    prix = args.get("prix", 0)
    display_name = DISPLAY_NAMES.get(args.get("nom","..."), args.get("nom","..."))


    # Construire une liste de "tokens" : {text, color, italic, jump}
    tokens = (
        [{"text": f"Enrôler {display_name} pour {prix} eclats : iel aura ", "color": (255, 255, 255), "italic": False, "jump": False},
         {"text": f"{nouvelle_proba}%", "color": (200, 80, 200), "italic": False, "jump": False},
         {"text": f" de chance d'apparaître spontannément à chaque partie", "color": (255, 255, 255), "italic": False, "jump": False}] if args.get("actual_probability") is None else
        [{"text": f"Renforcer l'engagement avec {nom} pour {prix} eclats : proba d'apparition spontannée", "color": (255, 255, 255), "italic": False, "jump": False},
         {"text": f" {ancienne_proba}%", "color": (255, 50, 50), "italic": False, "jump": False},
         {"text": f" -> ", "color": (0, 255, 150), "italic": False, "jump": False},
         {"text": f"{nouvelle_proba}%", "color": (200, 80, 200), "italic": False, "jump": False}]
    )

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
            font_to_use = desc_italic_font if token.get("italic") else desc_font
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

def generer_message_de_description(args, width, height, green_value=(0, 255, 150)):
    if args.get('show_previous') : green_value = (180, 50, 200)

    nom = args.get("nom", "")
    if nom not in upgrades:
        return None

    description = entete(args) + upgrades[nom]

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
            font_to_use = desc_italic_font if token["italic"] else desc_font
            y_offset += font_to_use.get_height() + line_spacing
            x_offset = 0
            continue

        font_to_use = desc_italic_font if token["italic"] else desc_font
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



