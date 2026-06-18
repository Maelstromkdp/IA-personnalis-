"""Bible de marque MAELSTRÖM (source de vérité unique).

Tout ce qui est ici est injecté dans chaque agent. Édite ce fichier pour faire
évoluer la marque — aucun agent n'a de positionnement codé en dur ailleurs.

⚠️ POINT D'EXTENSION : remplace / complète les sections ci-dessous par
l'intégralité de tes consignes projet MAELSTRÖM (positionnement, 6 règles d'or,
voix de marque, système de contenu, hameçons, cadence, etc.). La structure est
prête à recevoir le document complet sans changer le reste du code.
"""

# --------------------------------------------------------------------------- #
# Positionnement
# --------------------------------------------------------------------------- #
POSITIONING = """\
MAELSTRÖM publie des thrillers psychologiques COURTS (novellas de ~13 000 à
20 000 mots), sombres et oppressants, conçus pour Kindle Unlimited (prix : 2,99 €).

Idée centrale, fixe et non négociable :
  « Le danger vient des gens qu'on croit connaître. »

Format : histoires courtes, à lire d'une traite, à forte tension, sans temps mort.
Public cible : femmes 25-45 ans, lectrices de Freida McFadden, B.A. Paris,
Shari Lapena. Elles veulent une montée d'angoisse maîtrisée et une chute qui claque.
"""

# --------------------------------------------------------------------------- #
# Les 6 règles d'or (encodées d'après le brief — ajuste selon ton document)
# --------------------------------------------------------------------------- #
GOLDEN_RULES = """\
RÈGLES D'OR (la n°1 prime sur TOUT) :

1. ZÉRO SPOILER — ABSOLU. On vend la serrure, jamais ce qu'il y a derrière la porte.
   Aucun matériel public (titre, description, hameçon, post) ne révèle le twist,
   l'identité du coupable, le retournement final ni le sort des personnages.
2. LE DANGER VIENT DES PROCHES. Le menaçant est familier (conjoint, ami, voisin,
   famille, collègue). Pas de tueur masqué anonyme : l'effroi naît de l'intime.
3. COURT ET TENDU. On lit d'une traite. Pas de remplissage, pas de digression.
   Chaque scène augmente la pression ou prépare un retournement.
4. SUGGÉRER, NE PAS EXPLIQUER. Le non-dit fait le travail. On montre des détails,
   on laisse le lecteur assembler. On ne sur-explique jamais les émotions.
5. MARQUE SANS VISAGE. Jamais de faux auteur, jamais de visage humain sur les
   visuels principaux. L'autrice/auteur n'existe pas comme personne publique.
6. VOIX DE MARQUE CONSTANTE. Tout texte public sonne MAELSTRÖM (voir VOICE).
"""

# --------------------------------------------------------------------------- #
# Ton narratif (pour Writer / Editor)
# --------------------------------------------------------------------------- #
NARRATIVE_TONE = """\
TON NARRATIF :
- Calme, direct, légèrement froid, mystérieux sans prétention.
- Phrases nettes. Économie de moyens. La tension vient de ce qui n'est pas dit.
- Détails concrets, sensoriels, choisis — pas d'adjectifs en cascade.
- On installe un malaise progressif ; on ne hurle jamais l'horreur.
- La rugosité est permise et parfois nécessaire : aspérités, sécheresse,
  phrases qui dérangent. Ne pas lisser au point d'effacer la tension.
- Pas de morale, pas d'explication finale appuyée. La chute suggère, elle ne dénoue pas tout.
"""

# --------------------------------------------------------------------------- #
# Voix de marque (pour Marketing / communication)
# --------------------------------------------------------------------------- #
VOICE = """\
VOIX DE MARQUE (communication & marketing) :
- Calme, brève, un peu sèche. Elle observe et relance.
- Tutoiement des lectrices.
- Aucune emphase commerciale, aucun superlatif racoleur.
- Jamais d'émojis en rafale, jamais de ton « promo ».
- Elle pose une question dérangeante ou un détail troublant, puis se tait.
- Elle crée le manque sans jamais livrer la réponse.
"""

# --------------------------------------------------------------------------- #
# Motifs récurrents / système de contenu (extension)
# --------------------------------------------------------------------------- #
RECURRING_MOTIFS = """\
MOTIFS RÉCURRENTS DE L'UNIVERS (à réutiliser et varier) :
- L'intime qui devient menaçant (la maison, le couple, le quotidien).
- Le détail qui ne colle pas (un objet, une phrase, une absence).
- La narratrice qui doute de sa propre perception.
- Le secret partagé qui se retourne.
(⚠️ Complète avec ta banque de motifs / tropes maison.)
"""

# Hameçon = phrase d'accroche « serrure » qui crée le manque sans spoiler.
HOOKS_DOCTRINE = """\
DOCTRINE DES HAMEÇONS :
Un hameçon montre la SERRURE (la situation troublante, la question), jamais la
pièce derrière la porte (la réponse, le twist). Il doit pouvoir être lu par
quelqu'un qui lira ensuite le livre SANS que rien n'ait été gâché.
"""


def brand_bible() -> str:
    """Bible de marque pour injection dans les prompts.

    Source prioritaire : `brand_context/maelstrom_context.md` (éditable). À défaut,
    repli sur le contenu intégré ci-dessus — le système marche dans tous les cas.
    """
    from .loader import load_context_file

    external = load_context_file("maelstrom_context.md")
    if external:
        return external

    return "\n".join(
        [
            "# BIBLE DE MARQUE — MAELSTRÖM",
            POSITIONING,
            GOLDEN_RULES,
            NARRATIVE_TONE,
            VOICE,
            RECURRING_MOTIFS,
            HOOKS_DOCTRINE,
        ]
    )
