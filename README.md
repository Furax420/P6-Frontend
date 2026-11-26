# Olympic Participation Tracker

Application React pour visualiser les donnees de participation aux Jeux Olympiques, construite avec React 19, TypeScript, Vite et Tailwind CSS.

## Tech Stack

- **Framework :** React 19 + TypeScript
- **Build :** Vite 6
- **Styling :** Tailwind CSS 3.4
- **Routing :** React Router v7 en mode Data Router
- **Tests :** Jest + React Testing Library

## Prerequis

- **Node.js** 22.x ou superieur
- **npm** 10.x ou superieur

## Installation

```bash
git clone <repository-url>
cd p6-dfsjs-frontend
npm install
```

## Scripts disponibles

| Commande | Description |
|---|---|
| `npm run dev` | Serveur de developpement (port 5173) |
| `npm run build` | Verification TypeScript + build production (`dist/`) |
| `npm run preview` | Apercu du build de production |
| `npm test` | Lancer les tests |
| `npm run test:watch` | Tests en mode watch |
| `npm run test:coverage` | Tests avec rapport de couverture |

## Lancement avec Docker

Depuis le dossier du projet, avec Docker Desktop démarré :

```bash
docker compose up -d
```

L'application est disponible sur http://localhost. Au premier lancement, Compose construit l'image à partir du `Dockerfile`. Pour reconstruire l'image après une modification du code :

```bash
docker compose up -d --build
```

Pour voir les journaux ou arrêter le conteneur :

```bash
docker compose logs -f
docker compose down
```

### Tester l’image publiée dans GHCR

Dans GitHub, ouvre **Actions**, puis le résumé d’un push réussi. Copie la référence de l’image affichée dans **Docker image published on GHCR**. Pour un package privé, connecte Docker à GHCR avec un jeton GitHub *classic* qui a le droit `read:packages`. [Connexion au registre](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-to-the-container-registry).

Depuis ce dossier dans PowerShell, remplace `TAG` par le tag publié.

```powershell
$env:P6_IMAGE = 'ghcr.io/furax420/p6-frontend:TAG'
docker pull $env:P6_IMAGE
docker compose -f docker-compose.yml -f docker-compose.ghcr.yml up -d --no-build
docker compose -f docker-compose.yml -f docker-compose.ghcr.yml ps
```

Ouvre [le frontend livré](http://localhost:8081). Le fichier de surcharge sélectionne l’image téléchargée et le port local `8081`. Pour arrêter la démonstration, utilise les mêmes fichiers avec `down` à la place de `up -d --no-build`.

## Structure du projet

```
p6-dfsjs-frontend/
├── public/
│   └── mock/
│       └── olympic.json            # Donnees mock (5 pays, 3 participations chacun)
├── src/
│   ├── main.tsx                    # Point d'entree React 19
│   ├── App.tsx                     # Montage du RouterProvider
│   ├── router.tsx                  # Definition des routes et loaders
│   ├── index.css                   # Directives Tailwind CSS
│   ├── pages/
│   │   ├── Home.tsx                # Page d'accueil (liste des participations)
│   │   └── NotFound.tsx            # Page 404
│   ├── services/
│   │   └── olympicService.ts       # Service de donnees + loader de route
│   └── types/
│       └── olympic.ts              # Interfaces TypeScript (Olympic, Participation)
├── tests/
│   ├── polyfills.ts                # Polyfills pour React Router v7 dans jsdom
│   ├── setup.ts                    # Setup Jest (jest-dom)
│   └── components/
│       └── Home.test.tsx           # Tests du composant Home
├── index.html                      # Template HTML SPA
├── package.json
├── tsconfig.json                   # Configuration TypeScript stricte
├── vite.config.ts                  # Configuration Vite
├── jest.config.js                  # Configuration Jest
├── babel.config.json               # Presets Babel pour Jest (env, react, typescript)
├── tailwind.config.js              # Configuration Tailwind CSS
├── postcss.config.js               # Configuration PostCSS
└── CORRECTIONS.md                  # Journal des corrections appliquees
```

## Architecture

```
Pages (Composants UI)
    ↓ useLoaderData()
Router (Data Router + Loaders)
    ↓ loader()
Services (Fetch des donnees)
    ↓
Donnees (mock JSON)
```

Le projet utilise le **Data Router** de React Router v7. Les donnees sont chargees par un `loader` **avant** le rendu du composant, puis accessibles via `useLoaderData<T>()`.

### Routes

Les routes sont definies dans `src/router.tsx` :

| Route | Page | Loader |
|---|---|---|
| `/` | `Home` | `olympicLoader` (charge les donnees olympiques) |
| `*` | `NotFound` | - |

### Modele de donnees

```typescript
interface Olympic {
  id: number;
  country: string;
  participations: Participation[];
}

interface Participation {
  id: number;
  year: number;
  city: string;
  medalsCount: number;
  athleteCount: number;
}
```

### Donnees mock

5 pays avec 3 participations chacun (Londres 2012, Rio 2016, Tokyo 2020) :
France, United States, Germany, China, Great Britain.

## Tests

```bash
npm test
```

Les tests utilisent `createMemoryRouter` avec `hydrationData` pour injecter les donnees directement sans passer par le loader, ce qui evite les dependances aux Web APIs dans jsdom.

### Tests automatisés avec rapport JUnit

Avec Python 3.8 ou supérieur et les dépendances npm installées (`npm ci`), lancer :

```bash
python run-tests.py
```

Sur Linux, utiliser `python3 run-tests.py` si la commande `python` n'est pas disponible. Le script reconnaît le projet, lance les tests Jest et génère `test-results/junit.xml`. Il remplace son ancien rapport avant chaque exécution et retourne un code non nul si les tests échouent ou si le rapport ne peut pas être produit. Le dossier des rapports est ignoré par Git.

### Tests automatiques sur GitHub

Le workflow `.github/workflows/ci.yml` lance ces tests à chaque push et pull request. Dans l'onglet **Actions**, sélectionner une exécution pour consulter son résumé et télécharger le rapport JUnit dans l'artefact `junit-test-results`, y compris après un échec si le rapport a pu être généré.

## License

MIT
