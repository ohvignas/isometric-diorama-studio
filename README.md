# Illith Diorama

**Un plugin pour Codex et Claude Code qui transforme une scène Blender en décor miniature animé.** Il relie Tripo au poste de création, fournit des outils pour transférer et contrôler les mouvements humains, puis exporte un film et une boucle transparente pour le web.

[![Les six premières secondes du coworking Illith, de la construction à l’arrivée dans l’allée](showcase/construction.gif)](showcase/coworking-1080.mp4)

[Voir le film complet · 1 min 30](showcase/coworking-1080.mp4) · [Voir la boucle aux bureaux · 3 s](showcase/boucle-bureau.mp4) · [Ouvrir le modèle Blender d’exercice](plugins/illith-diorama/examples/atelier.blend) · [Parcourir le carnet des sources](plugins/illith-diorama/docs/sources.md)

## Installer dans son agent

Le catalogue s’appelle `illith-tools`. Choisir la commande de son client, puis ouvrir une nouvelle conversation.

| Codex | Claude Code |
| --- | --- |
| `codex plugin marketplace add ohvignas/illith-diorama` | `claude plugin marketplace add ohvignas/illith-diorama` |
| `codex plugin add illith-diorama@illith-tools` | `claude plugin install illith-diorama@illith-tools` |

Pour utiliser les deux connecteurs fournis, installer **Blender 5.1+**, son extension officielle **Blender Lab MCP**, le serveur local du même projet et le CLI officiel **Tripo** sous Node.js 20+. Pour la livraison vidéo, installer **FFmpeg** avec libx264 et libvpx, et **Python 3.10+** pour les commandes du kit. Le premier exercice Blender fonctionne sans compte Tripo. [Installation des connecteurs, commandes et connexion Studio/API](plugins/illith-diorama/docs/connexion.md)

## Premier essai

Dans une conversation avec le plugin activé, coller cette demande.

> Ouvre une copie de l’atelier d’exemple. Identifie son mannequin, ses Actions et sa caméra. Rends huit images du personnage au clavier. Montre-moi le plan fixe et vérifie que le bureau reste immobile. Pour l’instant, travaille uniquement dans Blender.

Pour essayer le même parcours au terminal, commencer dans un clone.

```sh
git clone https://github.com/ohvignas/illith-diorama.git
cd illith-diorama/plugins/illith-diorama
python3 scripts/diorama.py doctor
python3 scripts/diorama.py inspect examples/atelier.blend --report work/inventaire.json
python3 scripts/diorama.py render examples/atelier.blend work/images --first 73 --last 80 --scale 50 --samples 8
```

Le tutoriel complet ajoute un modèle, capture une prestation sur le mannequin et exporte deux clips indépendants. [Suivre l’atelier](plugins/illith-diorama/docs/atelier.md)

## Six skills, de la mise en scène à la livraison

| Skill | Ce qu’elle apporte |
| --- | --- |
| [Cadrage et scénario](plugins/illith-diorama/skills/diorama-cadrage/SKILL.md) | Plan de caméra commun, trajectoires, chronologie et dernier état de boucle |
| [Personnage Tripo](plugins/illith-diorama/skills/tripo-personnage/SKILL.md) | Smart Mesh P2.0, segmentation équilibrée, rig humanoïde, coût, UV et atlas |
| [Mouvement humain](plugins/illith-diorama/skills/blender-tripo-mouvement/SKILL.md) | Capture du donneur évalué, transfert FK, comparaison des rotations et mesure des appuis |
| [Décor et lumière](plugins/illith-diorama/skills/diorama-decor/SKILL.md) | Mobilier à l’échelle, PBR, néon, plantes et construction par éléments |
| [Interactions](plugins/illith-diorama/skills/diorama-interactions/SKILL.md) | Contacts main–poignée, chaises, regards, accessoires et attribution des bulles |
| [Livraison web](plugins/illith-diorama/skills/diorama-livraison/SKILL.md) | Ombre et transparence, H.264, VP9, HEVC alpha Apple et passage film–boucle |

Le [guide des agents](AGENTS.md) décrit la conduite du travail. Claude Code dispose également de l’[agent de revue d’animation](plugins/illith-diorama/agents/regie-animation.md).

## Ce que le film nous a appris

Une marche peut sembler correcte au niveau du squelette alors que la semelle glisse sur le parquet. Nous avons repris la marche approuvée de la conceptrice **après** correction des appuis, puis transféré cette prestation sur ses collègues. Pour le lever de chaise, une capture distincte a fourni le transfert de poids. La vérification porte sur la chaussure, le pantalon, les mains et le coussin évalués dans Blender.

Au baby-foot, la cible du regard passe de la balle au visage du collègue. À l’entrée, la poignée se met en mouvement au moment où la main l’atteint. À la fin, un fichier de trois secondes maintient les trois personnages au clavier. Une nouvelle visite du site relance la construction. [Lire l’étude de cas et la chronologie](plugins/illith-diorama/docs/cas-illith.md)

## Exemples et ressources

- **Atelier Blender éditable** · caméra orthographique, construction échelonnée, mannequin FK, cycle au clavier, plantes, mobilier, receveur d’ombre et marqueur du début de boucle. [Fichier Blender](plugins/illith-diorama/examples/atelier.blend) · [Générateur](plugins/illith-diorama/templates/atelier.py)
- **Import d’un modèle de bibliothèque** · poisson récifal avec armature, textures et animations. [GLB de démonstration](plugins/illith-diorama/examples/reef-fish.glb) · [Provenance](plugins/illith-diorama/examples/PROVENANCE.md)
- **Rendu de production** · film Illith en 1080p, boucle autonome et poster. [Vitrine](showcase/) · [Crédits du mobilier, des matières et des personnages](plugins/illith-diorama/docs/credits.md)
- **Validation et installation** · handshake des deux serveurs MCP, vérification des fichiers, contrôle FK et contacts, exports testés. [Reproduire les contrôles](tests/README.md)

Le code original et l’exercice d’atelier sont distribués sous MIT. Le poisson de Tevy est sous CC0. Les rendus du coworking présentent le travail d’Illith, avec son identité et ses éléments sous droits distincts. [Licence](LICENSE) · [Crédits](plugins/illith-diorama/docs/credits.md)
