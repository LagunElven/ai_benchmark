# Fixtures legacy

Les tâches legacy évaluent une règle métier et sa migration, pas la capacité à
deviner une syntaxe propriétaire. Chaque fixture possède un
workspace/fixtures/manifest.json validé par
schemas/legacy-fixture.schema.json.

## Statut de la source

- verified_syntax : source dans un sous-ensemble documenté et contrôlable
  (COBOL fixed-format et Object Pascal standard dans cette milestone).
- synthetic_pseudocode : sémantique fournie, syntaxe explicitement non
  vérifiée (WLanguage et ABAL).
- reference_only : documentation sans source exécutable.

Un statut ne doit jamais être interprété comme la présence d'un compilateur. Les
vecteurs input/expected constituent la vérité terrain de la migration Java,
et les tests cachés couvrent les limites et l'arithmétique décimale.

## Catalogue de la milestone 7

| tâche | source | statut | cible |
|---|---|---|---|
| COBOL-05 | order-total.cbl | verified_syntax | Java BigDecimal |
| DELPHI-04 | CustomerBalance.pas | verified_syntax | Java BigDecimal |
| WL-04 | late-fee.wlanguage.pseudo | synthetic_pseudocode | Java BigDecimal |
| ABAL-04 | benefit.abal.pseudo | synthetic_pseudocode | Java BigDecimal |

ABAL signifie Advanced Business Application Language, et non SAP ABAP. Le
fixture ABAL contient une référence fournie et teste explicitement l'usage de
la documentation.

## Toolchains natives

La détection est informative et non destructive :

~~~powershell
python scripts/check_legacy_toolchains.py --json
~~~

Les commandes candidates sont cobc pour GnuCOBOL, dcc32/dcc64 pour Delphi et
les noms courants wdcompiler/wdcomp pour WinDev. Aucun compilateur ABAL
portable n'est supposé. Une campagne peut ajouter un validateur natif quand
son image d'exécution et sa version sont figées.

Pour un contrôle COBOL natif optionnel (avec sortie JSON et timeout), utiliser :

~~~powershell
python scripts/run_cobol_native.py tasks/legacy/cobol/COBOL-05/workspace/legacy/order-total.cbl --output-dir .tmp/cobol --run
~~~

Sans GnuCOBOL, la commande retourne `skipped` sans considérer la tâche comme
échouée ; l'équivalence Java reste la validation portable.

## Vérification locale

~~~powershell
python scripts/run_legacy_equivalence.py
~~~

Cette commande utilise un adaptateur fake uniquement pour vérifier le runner et
les fixtures ; les résultats réels d'un modèle restent séparés de ces réponses
de test.
