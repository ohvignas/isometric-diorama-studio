# Refaire les vérifications

Depuis la racine du dépôt, exécuter `python3 tests/package_check.py`. Le test vérifie les manifestes, leurs entrées de catalogue et de serveurs, les six skills, les cibles de liens locaux et les ressources exécutables. `claude plugin validate plugins/illith-diorama` vérifie la structure Claude Code.

Pour le test réel des connecteurs, installer les deux CLI selon le [guide](../plugins/illith-diorama/docs/connexion.md). Exécuter `uv run --with 'mcp>=1.2,<2' python tests/mcp_smoke.py`. Le client négocie le protocole stdio, compte les outils, lit la scène d’exercice avec Blender Lab en arrière-plan et interroge l’aide Tripo. Le test ne nécessite aucune génération payante.

Pour reproduire le transfert, suivre les quatre commandes de la section **Rejouer le contrôle du mouvement** de [l’atelier](../plugins/illith-diorama/docs/atelier.md). Sur Blender 5.2.3 LTS, l’aller-retour de la prise clavier sur le mannequin a couvert 24 poses et 15 os, avec un écart maximal de 0,000014 degré et 0 mm au bassin. Le plateau a une excursion nulle entre les images 73 et 144. Ces chiffres décrivent le donneur FK fourni. Tester à nouveau les contacts sur tout autre corps.

Pour l’export, rendre les images 73 à 80 puis encoder avec `--first 73 --last 80 --fps 24 --loop-frames 3`. Vérifier huit images dans le film et trois dans la boucle avec `ffprobe -v error -count_packets -show_streams fichier`. Avec un fond qui diffère de celui du navigateur, regarder les contours et l’ombre. Le test client doit lire le film, deux tours de boucle puis la première image après rechargement.

Avec Playwright et Chromium installés, exécuter `python3 tests/hero_smoke.py /chemin/exports`. L’option `--chrome /chemin/du/navigateur` choisit un exécutable Chrome déjà présent. Le test sert uniquement le dossier exporté sur localhost, vérifie le poster en mode mouvement réduit, déclenche la lecture, observe deux retours de boucle puis recharge la page.
