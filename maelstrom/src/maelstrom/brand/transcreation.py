"""Protocole de Transcréation v2 — FR → EN (US).

Injecté dans Writer et Editor lorsque `mode == "transcreation"`.

⚠️ POINT D'EXTENSION : remplace / complète par l'intégralité de ton Protocole de
Transcréation v2. La structure ci-dessous encode les principes que tu as
énoncés et sert de réceptacle au document complet.
"""

PROTOCOL = """\
PROTOCOLE DE TRANSCRÉATION v2 — FR → ANGLAIS US

Objectif : produire une version anglaise qui se lit comme un thriller écrit
NATIVEMENT en anglais US, tout en préservant intégralement l'effet de l'original.

Principes directeurs :
1. TRANSCRÉER, PAS TRADUIRE. On recrée l'effet, pas la lettre. On reformule
   librement pour que la phrase sonne native, sans calque du français.
2. PRÉSERVER LA TENSION. Le rythme de montée d'angoisse de l'original doit être
   intégralement conservé scène par scène.
3. PROTÉGER LES TWISTS. Aucun retournement n'est annoncé plus tôt ni affaibli
   par une formulation maladroite. Les indices semés (foreshadowing) restent
   aussi discrets qu'en français.
4. PRÉSERVER LE NON-DIT. Ce qui est suggéré reste suggéré. On ne sur-explicite
   jamais en anglais ce que le français laissait dans l'ombre.
5. GARDER LA RUGOSITÉ. Les aspérités volontaires du style (sécheresse, phrases
   qui dérangent, ellipses) sont conservées, pas lissées par souci de fluidité.
6. ADAPTER LE CULTUREL. Références, idiomes, unités, registres : adaptés au
   lecteur US sans trahir l'ambiance. Pas de britishismes involontaires.
7. COHÉRENCE TERMINOLOGIQUE. Noms, surnoms, objets-clés, formules récurrentes :
   traduits une fois, puis constants dans tout le manuscrit.
8. TEST DU NATIF. Chaque passage doit pouvoir passer pour l'œuvre d'un auteur
   anglophone : zéro tournure traduite, zéro maladresse syntaxique.
"""


def transcreation_protocol() -> str:
    return "# " + PROTOCOL
