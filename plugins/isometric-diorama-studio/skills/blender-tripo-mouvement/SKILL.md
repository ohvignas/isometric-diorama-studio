---
name: blender-tripo-mouvement
description: Animer un humanoïde Tripo, Mixamo ou compatible dans Blender à partir d’une prestation approuvée ou d’une capture de mouvement. Utiliser pour créer et réutiliser des marches, des saluts, des levers, des contacts avec une chaise ou un accessoire, et diagnostiquer les pieds qui glissent, les bras raides et les déformations du visage.
---

# Animer un humanoïde dans Blender

Commencer avec un seul personnage, une action et une caméra où les pieds, les mains et le visage sont lisibles. Conserver le fichier source et les prises approuvées. Livrer une action réutilisable, un aperçu à vitesse réelle et le résultat des contrôles sur le fichier enregistré.

## Retrouver le mouvement

1. Relever le fichier, la scène, l’armature déformante, les parents animés, les pistes NLA ou Actions actives, le sol, les dates et la cadence. Identifier la source de chaque geste. Un salut, une marche et un lever peuvent provenir de trois prestations différentes.
2. Quand une prestation précise a été approuvée, échantillonner le personnage **après** ses corrections de semelle, de bassin et de posture. Archiver une copie d’étude. Dans le coworking Illith, lire [le cas de la conceptrice](references/coworking-illith.md).
3. Pour un geste nouveau, choisir une prise de la même famille et du bon état initial. Pour se lever du bureau, chercher une personne assise qui porte le poids sur ses pieds puis libère les mains. Inspecter plusieurs secondes autour du geste. Consigner fréquence source, première et dernière pose, unités, provenance et droits associés au fichier.
4. Pour un personnage déjà riggé, repartir de son FBX ou GLB. Inspecter les coudes, poignets, bassin, genoux et extrémités du pied sur le maillage déformé. Un pli au cou peut venir des poids du col sur le crâne. Tester une rotation isolée avant de retoucher une animation entière.

## Transférer et mettre en scène

- **Rigs FK en poses de repos proches.** Utiliser [les commandes de capture et transfert](references/commandes.md). Vérifier d’abord le trajet aller-retour sur le rig donneur. Identifier ensuite les axes anatomiques, la longueur de jambe et la cadence sur le rig cible. Superposer huit silhouettes du même cycle avec un angle et un sol communs. Pour une pose A contre une pose T ou un rig à contrôleurs, calibrer la pose commune avec le flux Rokoko décrit dans [les tutoriels et outils](references/ressources.md).
- **Marche.** Repérer contact du talon, prise de poids, passage de la jambe libre et poussée des orteils. Caler la phase sur la distance que parcourt le bassin sur le chemin. Un cycle couvre deux pas. Garder les oscillations verticales et latérales de la prise en les adaptant aux proportions. Décélérer sur un dernier vrai pas. Dans un virage serré, transférer le poids sur une chaussure puis repositionner l’autre. Interrompre le cycle à un appui compatible avec le salut, l’assise ou la poignée à atteindre.
- **Contacts.** Suivre le talon et la pointe pendant le passage de l’un à l’autre. Pendant le contact ferme, verrouiller le contrôleur IK à un repère monde et animer progressivement son influence. Diriger le genou avec le pole target. Examiner les images adjacentes au relâchement. Un décalage constant au sol peut venir de l’épaisseur de la chaussure ou du tapis.
- **Saluer, parler, saisir.** Observer l’ordre regard, poitrine, épaule, coude, poignet et succession des doigts sur la prise. Pour un salut, vérifier la silhouette de la main et le visage image par image à l’apogée. Pour une poignée ou une tasse, placer un repère local au point de préhension, animer l’influence et conserver l’orientation du poignet au raccord. Pour boire, prévoir prise, levée, inclinaison, pause et repose.
- **Chaise et bureau.** Marquer la libération du clavier, le transfert de poids vers les pieds, le décollage du bassin et le premier pas. Vérifier pieds, accoudoirs, bord du plateau et dossier sur les vrais volumes. Pour reproduire une apparition, recopier les poses et la trajectoire dans les axes de chaque fauteuil en prenant comme origine la même phase de construction. Maintenir l’accessoire immobile lorsqu’il est vide, y compris ses pièces animées. Introduire un déplacement de roulettes seulement pendant une poussée identifiable.
- **Réutiliser.** Attribuer un mouvement à la racine une seule fois. Séparer cycle, trajet dans le décor et contacts ponctuels. Conserver les fins de tâches et les boucles déjà approuvées. Travailler sur une copie indépendante de l’Action lorsque plusieurs personnages la partagent.

## Vérifier et livrer

Sur chaque personnage, regarder une lecture à la cadence de livraison, puis au ralenti de profil. Dans la caméra finale, vérifier les trajectoires conjointes, les changements d’activité et l’image avant/après chaque raccord. Comparer à la référence à phase égale, caméra et échelle constantes.

Mesurer les points de semelle sur le maillage évalué, en coordonnées monde, à toutes les images de chaque appui. Examiner séparément pied gauche, pied droit, pelvis, chevilles, poignée et coussin. Consigner tolérances en unités physiques et en fonction de la taille du sujet. Une mesure géométrique accompagne la lecture du mouvement. [Outil de mesure, schéma et exemples](references/commandes.md)

Rouvrir le fichier sauvegardé, relire la prise exportée, contrôler la durée et la cadence du film. Livrer les extraits à vitesse réelle, le chemin du projet modifié et les défauts encore observés.
