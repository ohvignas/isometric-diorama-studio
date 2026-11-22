---
name: diorama-livraison
description: Produire un film Blender et une boucle de travail séparée, conserver transparence et ombres et tester le passage entre les deux vidéos sur le web.
---

# Du rendu RGBA à deux vidéos

Régler film transparent, caméra définitive et receveur d’ombre. Dans l’atelier inclus, Cycles utilise un plan shadow catcher. Pour un master EEVEE, le film Illith utilisait un matériau de réception calibré sur un rendu des lumières et du sol seuls. Sauvegarder une copie du projet et tester le coin transparent, un pixel d’objet opaque et un pixel d’ombre partielle sur deux fonds.

Rendre une petite plage en PNG RGBA. Vérifier les contours du néon, des plantes et des cheveux après composition sur clair et sombre. Pour redimensionner une image à alpha droit, prémultiplier couleur et alpha avant le filtrage puis rétablir l’alpha droit à l’encodage. Fixer la résolution selon la taille réelle du hero et préserver une copie des sources. Sur un poste limité, traiter un lot à la fois, suivre RAM et espace, valider le lot avant d’effacer ses fichiers de travail.

Avec `scripts/diorama.py encode`, renseigner la cadence de la scène et le nombre **entier** d’images de la boucle. Vérifier au décodage dimensions, nombre d’images, première et dernière image du film et de la boucle. Essayer le déplacement du dernier acteur, le clignotement et la phase des mains avant de décider où couper. H.264 sert au visionnage avec fond fixé. VP9 et HEVC avec alpha servent à la superposition sur la page. [Exercice complet](../../docs/atelier.md)

Sur la page, jouer la première vidéo une seule fois. Précharger le petit deuxième fichier à l’approche de la fin et maintenir la dernière image du film jusqu’à la présentation de la première de la boucle. Prévoir mouvement réduit, contrôle pause et onglet masqué. Vérifier la transparence réellement décodée dans les navigateurs cibles, deux tours et un rechargement. Le design Illith utilisait 720p et 1080p, avec le QHD en réserve. [Film de référence](../../docs/cas-illith.md) · [Lecteur adaptable](../../templates/hero.html)
