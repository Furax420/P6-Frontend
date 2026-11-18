#!/usr/bin/env python3
"""Lance les tests du projet et génère un rapport JUnit."""

import json
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


if os.name == "nt":
    # Garder des messages lisibles dans les terminaux et les journaux CI Windows.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = PROJECT_DIR / "test-results"
REPORT_FILE = RESULTS_DIR / "junit.xml"


def error(message):
    print(f"Erreur : {message}", file=sys.stderr)
    return 1


def main():
    # Supprimer seulement le rapport produit par ce script, jamais tout le dossier.
    try:
        if RESULTS_DIR.is_symlink():
            return error("test-results doit être un dossier local, pas un lien symbolique.")
        RESULTS_DIR.mkdir(exist_ok=True)
        REPORT_FILE.unlink(missing_ok=True)
    except OSError as exc:
        return error(f"Impossible de préparer le rapport : {exc}")

    try:
        package = json.loads((PROJECT_DIR / "package.json").read_text(encoding="utf-8"))
        dependencies = package.get("dependencies", {})
        dev_dependencies = package.get("devDependencies", {})
        scripts = package.get("scripts", {})
        if not all(isinstance(item, dict) for item in (dependencies, dev_dependencies, scripts)):
            raise ValueError("la configuration npm est invalide")
    except (OSError, ValueError, AttributeError) as exc:
        return error(f"Impossible de lire package.json : {exc}")

    is_frontend = "react" in dependencies and "vite" in dev_dependencies
    is_backend = "@nestjs/core" in dependencies
    if is_frontend == is_backend:
        return error("Type de projet non reconnu ou ambigu : React/Vite ou NestJS attendu.")
    project_type = "frontend React" if is_frontend else "backend NestJS"

    if not scripts.get("test"):
        return error("Aucune commande npm test n'est définie dans package.json.")
    if not shutil.which("node"):
        return error("Node.js est introuvable. Active ou installe Node.js 22.")
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not npm:
        return error("npm est introuvable. Vérifie ton installation de Node.js.")

    for dependency in ("jest", "jest-junit"):
        if not (PROJECT_DIR / "node_modules" / dependency / "package.json").is_file():
            return error(f"{dependency} est absent. Lance npm ci dans ce projet.")

    # Jest choisit sa propre configuration selon le projet courant.
    command = [
        npm, "test", "--", "--ci", "--runInBand",
        "--reporters=default", "--reporters=jest-junit",
    ]
    env = os.environ.copy()
    env["JEST_JUNIT_OUTPUT_FILE"] = str(REPORT_FILE)
    env["JEST_JUNIT_UNIQUE_OUTPUT_NAME"] = "false"

    print(f"Projet détecté : {project_type}", flush=True)
    print("Exécution des tests unitaires avec Jest...", flush=True)
    try:
        result = subprocess.run(command, cwd=PROJECT_DIR, env=env, check=False)
    except OSError as exc:
        return error(f"Impossible de lancer npm : {exc}")

    if result.returncode != 0:
        if REPORT_FILE.is_file():
            print(f"Rapport JUnit : {REPORT_FILE}", flush=True)
        print(f"Les tests ont échoué (code {result.returncode}).", file=sys.stderr)
        return result.returncode if result.returncode > 0 else 1

    try:
        report = ET.parse(REPORT_FILE).getroot()
        if report.tag not in ("testsuite", "testsuites"):
            raise ValueError("format JUnit inattendu")
        test_count = len(list(report.iter("testcase")))
        if test_count == 0:
            raise ValueError("aucun cas de test dans le rapport")
    except (OSError, ET.ParseError, ValueError) as exc:
        return error(f"Rapport JUnit absent ou invalide : {exc}")

    print(f"Rapport JUnit : {REPORT_FILE}")
    print(f"{test_count} cas de test enregistrés.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
