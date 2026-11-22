# Brancher les deux connecteurs

Le plugin enregistre deux serveurs stdio. Le client les lance quand on ouvre une session avec le plugin activé. Les mêmes exécutables servent depuis un terminal.

| Nom dans le plugin | Exécutable | Usage |
| --- | --- | --- |
| `blender-lab` | `blender-mcp` de Blender Lab | Inspecter une scène, lire la documentation Blender et agir dans une instance interactive connectée |
| `tripo-api` | `tripo mcp --toolset full` | Préparer, suivre et récupérer les opérations de l’API développeur Tripo |

## Blender Lab

1. Installer Blender 5.1 ou ultérieur, Python 3.10+, Git et uv. Depuis le terminal, vérifier `blender --version`. Sur macOS, la commande du kit accepte aussi `BLENDER_PATH=/Applications/Blender.app/Contents/MacOS/Blender`.
2. Installer le serveur depuis le projet de Blender Lab. La commande suivante expose `blender-mcp` dans le répertoire des exécutables de uv. Ajouter ce répertoire au PATH du client IA si son lancement graphique utilise un autre environnement.

   ```sh
   uv tool install 'git+https://projects.blender.org/lab/blender_mcp.git#subdirectory=mcp'
   uv tool dir --bin
   ```

3. Dans Blender, installer l’extension **MCP** depuis le dépôt Blender Lab indiqué sur la page officielle. Activer **Allow Online Access** si l’extension le demande. Dans ses préférences, choisir `127.0.0.1` et le port `9876`, puis démarrer le serveur de l’extension. Une copie de la scène de travail suffit pour le premier essai.
4. Dans une nouvelle conversation, demander au connecteur Blender le nom de la scène, celui de la caméra et la plage d’images. Comparer le résultat à l’interface Blender. Si le serveur annonce ses outils mais que la scène ne répond pas, vérifier la fenêtre ouverte et le port. Certaines commandes du serveur fonctionnent en arrière-plan même quand la fenêtre est fermée.
5. Pour utiliser le kit sans fenêtre, lancer `scripts/diorama.py`. Le script utilise Blender en arrière-plan avec l’exécution automatique des scripts du fichier désactivée.

Le projet historique utilise le serveur **Blender Lab**, dont le module Python se nomme `blmcp`. Plusieurs distributions installent une commande appelée `blender-mcp` avec des protocoles d’extension différents. Associer le serveur et l’extension du même projet. [Blender Lab](https://www.blender.org/lab/mcp-server/) · [Installation amont](https://projects.blender.org/lab/blender_mcp/src/branch/main/mcp)

## Tripo API et Tripo Studio

Installer Node.js 20+ et le CLI officiel utilisé pour les tests.

```sh
npm install --global tripo-cli@0.11.2
tripo --version
tripo models
tripo login --region ov
tripo balance
```

Choisir `ov` pour le compte développeur international, `cn` pour le compte développeur chinois. Le parcours de connexion se termine dans le navigateur du propriétaire. Un secret peut aussi être fourni dans l’environnement du processus via `TRIPO_API_KEY`. Pour un CLI installé hors du PATH, utiliser un chemin absolu dans la configuration locale du client. Les paramètres publics du plugin ne contiennent aucune donnée de compte.

**Choisir le bon portefeuille avant la première génération.** Le CLI et le serveur `tripo-api` utilisent le compte API. Le film Illith a utilisé les crédits de **Studio**. Pour des crédits Studio, vérifier le modèle et le devis dans Studio. Pour piloter le connecteur Studio de l’éditeur, suivre son guide de connexion authentifiée, puis tester la lecture de la liste des modèles dans le client. Le dépôt officiel Studio fournit aussi une skill installable. Utiliser le DCC Bridge ou exporter le GLB/FBX livré. Le compte, les offres et les opérations disponibles se vérifient chez Tripo. [Tripo Studio](https://studio.tripo3d.ai/) · [Guide officiel du connecteur Studio](https://github.com/Tripo-Developer/Tripo-Studio-MCP/blob/main/INSTALL.md) · [CLI et MCP développeur](https://developers.tripo3d.com/en/mcp) · [DCC Bridge Blender](https://www.tripo3d.ai/integrations/blender)

Pour installer les instructions Studio de l’éditeur dans Codex ou Claude Code, utiliser les commandes correspondantes ci-dessous. L’activation du compte Studio se fait ensuite dans le client. Tester la connexion par la liste des cinq derniers modèles avant de préparer une génération. [Installation Studio par client](https://github.com/Tripo-Developer/Tripo-Studio-MCP/blob/main/INSTALL.md)

| Codex, terminal | Claude Code, dans la conversation |
| --- | --- |
| `codex plugin marketplace add Tripo-Developer/Tripo-Studio-MCP` | `/plugin marketplace add Tripo-Developer/Tripo-Studio-MCP` |
| `codex plugin add tripo-studio-mcp@tripo-studio` | `/plugin install tripo-studio-mcp@tripo-studio` |

**Test sans dépense**. Depuis le dossier du plugin, lancer `python3 scripts/diorama.py plan /chemin/personnage.png`. Le plan local indique le modèle normalisé et l’estimation de génération lorsqu’elle existe. Les frais de segmentation, de rig et de texture s’ajoutent. Vérifier chaque poste sur le compte qui sera débité.
