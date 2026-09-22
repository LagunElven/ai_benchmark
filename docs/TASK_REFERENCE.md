# Référence synthétique des tâches qualité

Ce document est destiné à la préparation, à l'analyse et à la lecture des
campagnes. Il résume les 74 tâches du catalogue sans reproduire les réponses
attendues ni les valeurs exactes des fixtures cachées.

La source de vérité opérationnelle reste `catalogue.yaml`, puis le
`task.yaml`, le `prompt.md` et les validateurs de chaque tâche. Une tâche est
réussie lorsque sa validation déterministe aboutit dans un workspace propre,
avec le protocole de sortie accepté. Une réponse plausible ou une explication
correcte ne suffit pas si le code ne compile pas, si le contrat d'interface est
incorrect ou si un test caché échoue.

## Lire les critères

- **Réussite** : comportement attendu sur les cas publics et cachés, sans
  régression observable.
- **Échec** : résultat fonctionnel incorrect, compilation impossible, protocole
  de sortie invalide, timeout, modification incomplète ou régression.
- **Pièges** : familles de cas limites couvertes par les validateurs. Ils sont
  décrits à un niveau suffisant pour comprendre la capacité évaluée, mais les
  données et réponses de référence restent privées.
- Pour les tests de contexte, un refus du serveur pour fenêtre trop courte est
  une **limite de capacité** à distinguer d'un échec fonctionnel du modèle.
- Les tâches legacy marquées synthétiques évaluent la compréhension d'un
  comportement fourni ; elles ne constituent pas une validation d'une
  toolchain propriétaire absente de l'environnement.

## Java

| ID | Ce que le test évalue | Réussite attendue | Pièges principaux |
|---|---|---|---|
| JAVA-01 | Null-safety avec streams et `Optional`. | Résultat normalisé correct et absence d'exception pour les entrées admissibles. | Liste ou élément nul, valeur vide/blanche et normalisation indépendante de la locale. |
| JAVA-02 | Dates, fuseaux et changements d'heure. | Intervalle converti correctement avec une règle temporelle déterministe. | Trou de printemps, chevauchement d'automne et distinction entre instant et heure locale. |
| JAVA-03 | Modification sûre d'une collection parcourue. | Éléments ciblés supprimés sans exception et ordre restant conservé. | Collection vide, tous les éléments expirés et éléments expirés répétés. |
| JAVA-04 | Synchronisation et thread-safety d'un inventaire. | Aucune survente sous concurrence ; le verrouillage reste propre à chaque inventaire. | Interleavings concurrents et solution qui sérialise globalement l'application. |
| JAVA-05 | Refactorisation d'un calcul métier sans changer le comportement. | Montants exacts au centime, validations conservées et cas vide traité correctement. | Confusion entre commande vide et frais de livraison, dépassement numérique et arrondis. |
| JAVA-06 | Diagnostic d'une condition de course. | Identifiants uniques et contigus, y compris sous exécution concurrente. | Compteur partagé non atomique, résultats intermittents et faux correctif limité au cas séquentiel. |
| JAVA-07 | Optimisation d'une recherche sans régression. | Même résultat métier avec normalisation, ordre et absence d'alias de collection respectés. | Entrées nulles, variantes de casse/espaces, ordre et modification accidentelle du résultat retourné. |
| JAVA-08 | Évolution rétrocompatible d'une API. | Ancienne surcharge inchangée et nouvelle variante locale correctement supportée. | Rupture des appelants existants, locale implicite et changement de format historique. |

## Spring, JPA et Reactor

| ID | Ce que le test évalue | Réussite attendue | Pièges principaux |
|---|---|---|---|
| SPRING-01 | Contrat de validation d'une requête REST. | Statuts, erreurs et données valides respectent le contrat. | Champ manquant, type invalide, valeur limite et format d'erreur non conforme. |
| SPRING-02 | Traduction des exceptions REST. | Chaque erreur connue donne le statut/code prévu sans divulgation interne. | Exception inattendue, détails sensibles et mapping statut/code incohérent. |
| SPRING-03 | Transaction et rollback. | Une panne de destination laisse l'état source inchangé, sans débit partiel. | Ordre des opérations, exception aval et transaction simulée trop étroite. |
| SPRING-04 | Dirty checking Hibernate. | Champ absent, champ explicitement nul et champ inconnu ont chacun le traitement prévu. | PATCH assimilé à PUT, écrasement d'une valeur non fournie et colonne inconnue acceptée. |
| SPRING-05 | Verrouillage optimiste et prévention du lost update. | Écriture concurrente périmée rejetée ou traitée selon le contrat, sans perte silencieuse. | Version obsolète, interleavings et retry qui réécrit une donnée devenue périmée. |
| SPRING-06 | `@DynamicUpdate` et compare-and-set concurrent. | Mise à jour versionnée des seuls champs concernés ; écriture périmée refusée. | Réinitialisation d'autres champs, stale write accepté et version non incrémentée. |
| SPRING-07 | Diagnostic et correction du N+1 JPA. | Une requête de commande puis une requête client groupée, avec résultat complet. | Requête par client dans une boucle, doublons et solution qui masque seulement le compteur. |
| SPRING-08 | Retry Reactor asynchrone. | Les erreurs transitoires sont retentées dans la limite prévue ; les permanentes échouent. | Retry illimité, erreur permanente retentée et scheduler bloqué ou non libéré. |
| SPRING-09 | Bearer, CSRF et règles de sécurité. | En-têtes, origine et méthode déterminent l'autorisation attendue. | Casse des en-têtes, méthodes sûres versus mutantes, token vide et fuite d'identifiants. |
| SPRING-10 | Transaction distribuée simulée entre commande et paiement. | Ordre, idempotence et compensation donnent un état cohérent après chaque panne. | Double paiement, retry non idempotent et compensation absente ou exécutée trop tôt. |

## Axon et event sourcing

| ID | Ce que le test évalue | Réussite attendue | Pièges principaux |
|---|---|---|---|
| AXON-01 | Projection par gestionnaire d'événement. | Événement valide appliqué correctement ; événements invalides ne créent pas d'état incohérent. | Événement inconnu, stock négatif et mutation partielle. |
| AXON-02 | Upcaster d'une seule révision. | La bonne révision est transformée en conservant les autres propriétés. | Champ absent ou nul, mauvais type d'événement, mauvaise révision et propriétés inconnues. |
| AXON-03 | Chaîne d'upcasters multi-révisions. | Chaque révision est convertie dans l'ordre, sans modifier l'entrée ni perdre de données. | Révision non supportée, propriété inconnue, devise existante et upcaster non immuable. |
| AXON-04 | Filtrage de snapshots obsolètes. | Seuls les snapshots de l'agrégat concerné et obsolètes sont filtrés. | Filtrage global, agrégat différent et snapshot valide supprimé par erreur. |
| AXON-05 | Associations de saga. | Clés indépendantes, terminaison propre et état cohérent après completion. | Clé invalide, association croisée et nettoyage partiel. |
| AXON-06 | Plusieurs chemins de démarrage de saga. | Une saga par commande métier et toutes ses associations sont nettoyées. | Double démarrage pour une même commande, association résiduelle et chemin alternatif oublié. |
| AXON-07 | Projection idempotente. | Livraison répétée ou concurrente produit une seule application métier. | Double livraison, course entre workers et absence de clé d'idempotence. |
| AXON-08 | Replay et reconstruction de projection. | L'état est vidé puis reconstruit dans l'ordre ; les invariants métier restent valides. | État précédent conservé, ordre d'événements et retrait accepté par erreur. |
| AXON-09 | Verrouillage optimiste, propagation et retry. | Commande périmée sans mutation et nombre de retries borné conformément au contrat. | Retry non borné, état partiellement modifié et exception aval masquée. |
| AXON-10 | Routage de commandes multi-agrégats. | Chaque commande atteint l'agrégat correspondant et les commandes invalides sont refusées. | Identité mélangée, état partagé entre agrégats et validation trop tardive. |

## Web, Angular, RxJS et Ionic

| ID | Ce que le test évalue | Réussite attendue | Pièges principaux |
|---|---|---|---|
| WEB-01 | Frontière `Observable<T>` / valeur scalaire. | Le composant consomme le flux selon le contrat et s'abonne correctement. | Traiter l'observable comme une valeur immédiate, abonnement oublié et observable minimal. |
| WEB-02 | Cycle de vie des abonnements. | Nettoyage explicite, complétion, erreur et émission synchrone ne laissent pas de fuite. | Désabonnement absent, cleanup trop tardif et émission synchrone ignorée. |
| WEB-03 | Recherche RxJS avec `switchMap`. | Une nouvelle recherche annule l'ancienne et seul le résultat courant est publié. | Résultats hors ordre, subscription concurrente et propagation d'erreur. |
| WEB-04 | Contrat d'intercepteur HTTP. | Requête immuable, en-tête remplacé correctement et méthode transmise au backend. | Casse des en-têtes, mutation en place, identifiant vide et méthodes mutantes. |
| WEB-05 | Propagation Bearer/CSRF. | Credentials ajoutés uniquement au périmètre autorisé et anciens headers supprimés. | Requête cross-origin, headers immuables, token vide et credential obsolète. |
| WEB-06 | Formulaire réactif complexe. | Contraintes, confirmation, champs conditionnels et normalisation sont cohérents. | Champ conditionnel ignoré, mot de passe différent, valeur non normalisée et erreur au mauvais niveau. |
| WEB-07 | État Signals/RxJS. | Mise à jour immuable et notifications cohérentes, sans contaminer l'ancien état. | Référence mutée, abonnement incomplet et notification en double. |
| WEB-08 | Navigation Ionic. | Push, replace et back respectent les guards asynchrones et le comportement de la racine. | Guard refusé, retour depuis la racine, stack modifiée avant décision et promesse non attendue. |
| WEB-09 | OAuth et deep-link Capacitor. | Endpoint, état, erreur et consommation unique sont validés avant échange. | Fragment accepté, mauvais `state`, endpoint non autorisé et callback réutilisé. |
| WEB-10 | Fonctionnalité web multi-couches. | DTO API, modèle service, états loading/error et bindings UI restent cohérents. | Mapping de centimes, formatage, payload invalide et état d'erreur oublié. |

## COBOL

| ID | Ce que le test évalue | Réussite attendue | Pièges principaux |
|---|---|---|---|
| COBOL-01 | Compréhension d'un programme COBOL à format fixe. | Le comportement métier est expliqué et reproduit par la cible portable. | Confusion entre clauses, ordre des traitements et hypothèse sur une syntaxe non exécutée. |
| COBOL-02 | Correction d'une règle métier COBOL. | Les sorties respectent le seuil et l'arrondi définis sur tout le corpus. | Seuil inclusif, classe nulle et arrondi en centimes entiers. |
| COBOL-03 | Fichier séquentiel et montant signé `COMP-3`. | Les enregistrements sont lus et les montants calculés exactement. | Signe, position décimale, longueur fixe et approximation en flottants. |
| COBOL-04 | Modification COBOL conservant l'ancien comportement. | Le cas unitaire reste compatible et le traitement batch conserve ordre et montants. | Régression du chemin historique, ordre des lignes et précision packed-decimal. |
| COBOL-05 | Migration COBOL vers Java. | Les sorties Java sont équivalentes sur entrées unitaires, lots et invalides. | Échelle décimale, cas limites et confusion entre référence source et exécution native. |

## Delphi / Object Pascal

| ID | Ce que le test évalue | Réussite attendue | Pièges principaux |
|---|---|---|---|
| DELPHI-01 | Compréhension d'un programme Object Pascal. | La cible portable restitue le comportement métier attendu. | Cycle de vie implicite, types et ordre des effets. |
| DELPHI-02 | Propriété des ressources et cycle de vie. | Libération idempotente, ownership clair et copies défensives. | Double libération, ressource conservée trop longtemps et alias mutable. |
| DELPHI-03 | Correction d'un traitement métier Delphi. | Règle métier et sorties restent exactes sur cas normaux et limites. | Branche limite, valeur nulle et calcul monétaire approximatif. |
| DELPHI-04 | Migration Delphi vers Java. | Équivalence fonctionnelle, notamment pour la fonction monétaire fournie. | Arrondi, bornes et différence entre `Currency` et types flottants. |

## WinDev / WLanguage

| ID | Ce que le test évalue | Réussite attendue | Pièges principaux |
|---|---|---|---|
| WL-01 | Compréhension d'un traitement WLanguage. | La sémantique décrite est reproduite par la cible Java. | Syntaxe propriétaire synthétique et interprétation erronée des valeurs absentes. |
| WL-02 | Logique de requête HFSQL. | Filtrage, sélection et résultat suivent la sémantique de référence. | Confusion entre filtre et post-traitement, égalité de types et ordre des résultats. |
| WL-03 | Correction d'un traitement métier. | Règle de facturation et calcul décimal exacts. | Ordre des frais, limites et arrondi intermédiaire. |
| WL-04 | Migration WLanguage vers Java. | Le comportement défini par la référence sémantique est conservé. | Pseudocode présenté comme syntaxe propriétaire vérifiée, valeurs nulles et échelle décimale. |

## ABAL (Advanced Business Application Language)

Ces tâches sont explicitement synthétiques tant qu'une implémentation ou une
documentation ABAL vérifiée n'est pas disponible. ABAL ne doit pas être
interprété comme ABAP.

| ID | Ce que le test évalue | Réussite attendue | Pièges principaux |
|---|---|---|---|
| ABAL-01 | Compréhension ABAL sans documentation fournie. | Le comportement décrit est compris et reproduit par la cible Java. | Répondre en ABAP, inventer une syntaxe propriétaire ou négliger la cible exécutable. |
| ABAL-02 | Modification d'une règle métier ABAL. | La règle fournie est appliquée sans changer les autres cas. | Seuils, arrondis, valeurs absentes et confusion ABAL/ABAP. |
| ABAL-03 | Migration ABAL vers Java. | Équivalence décimale exacte sur les vecteurs et bornes cachés. | Flottants, limites métier et syntaxe source non vérifiée. |
| ABAL-04 | Utilisation d'une documentation ABAL fournie. | La référence fournie est exploitée et la cible Java respecte son comportement. | Ne pas utiliser la documentation, extrapoler hors de son périmètre et oublier les cas invalides. |

## Documents et OCR

| ID | Ce que le test évalue | Réussite attendue | Pièges principaux |
|---|---|---|---|
| DOC-01 | Extraction depuis un document numérique simple. | Champs et types extraits exactement depuis le texte disponible. | Confondre texte de présentation et valeur métier, champ manquant et schéma incorrect. |
| DOC-02 | Post-traitement d'un scan 300 DPI. | Identifiants, dates, montant et devise normalisés sans perte. | Confusions OCR, zéros/lettres, ponctuation et champs critiques. |
| DOC-03 | Post-traitement d'un scan 150 DPI. | Règle de confusion explicitement définie corrigée, extraction intacte. | Sur-correction d'un caractère valide et séparation normalisation/extraction. |
| DOC-04 | Document tourné. | Champs récupérés malgré orientation, ordre de lignes et présentation de date. | Dépendance à l'ordre visuel, rotation supposée correcte et dates ambiguës. |
| DOC-05 | Document bruité ou compressé. | Ponctuation et nombres locaux normalisés ; entrées invalides traitées selon le contrat. | Séparateurs mixtes, ponctuation des libellés, montant mal formé et conversion permissive. |
| DOC-06 | Extraction de tableau. | Cellules, lignes, montants et arrondis sont conservés ; bruit ignoré. | Virgule décimale, lignes parasites, nombres mal formés et décalage de colonnes. |
| DOC-07 | Extraction de formulaire structuré. | Champs normalisés et données mal formées rejetées proprement. | Champ absent versus vide, format d'identifiant et acceptation d'un payload partiel. |
| DOC-08 | Agrégation d'un document multi-page. | Pages fusionnées dans l'ordre, en-têtes répétés ignorés et montants exacts. | Doublon d'en-tête, ordre des lignes, rupture de page et valeur monétaire. |
| DOC-09 | Mélange de factures et reçus. | Schémas supportés validés strictement et blocs non supportés ignorés. | Mauvais schéma, mélange de champs et acceptation d'un bloc inconnu. |
| DOC-10 | Extraction JSON complexe et structurée. | JSON valide, champs attendus exacts, sans champs inventés ni omissions. | Types imbriqués, champs obligatoires, nombres/dates et hallucination de propriétés. |

## Long-context

Les six variantes conservent le même défaut et la même solution ; seule la
quantité de contexte parasite augmente. La réussite combine correction du
défaut, localisation du fichier pertinent et précision du patch. Une
modification de nombreux fichiers distracteurs est donc un échec de précision
même si le cas principal fonctionne.

| ID | Taille cible | Réussite attendue | Pièges principaux |
|---|---:|---|---|
| CTX-01 | ~10k tokens | Trouver le fichier pertinent, corriger la règle de facturation et limiter le patch. | Se laisser guider par un distracteur proche et modifier des fichiers inutiles. |
| CTX-02 | ~30k tokens | Même correction et même précision malgré davantage de bruit déterministe. | Perte du fichier cible, changement de comportement hors périmètre et tokens insuffisants. |
| CTX-03 | ~60k tokens | Même résultat fonctionnel, avec rappel/precision des fichiers conservés. | Dégradation de localisation, contexte tronqué et patch plus large que nécessaire. |
| CTX-04 | ~100k tokens | Correction stable si la fenêtre effective accepte la requête. | Refus HTTP dû à la fenêtre réelle, confondu à tort avec une erreur de code. |
| CTX-05 | ~150k tokens | Même correction sur le dépôt enrichi, sans toucher aux distracteurs. | Limite de contexte, saturation de sortie et modifications parasites. |
| CTX-06 | ~200k tokens | Réussite uniquement si le serveur et le modèle acceptent réellement le contexte. | Requête trop grande, refus de capacité et conclusion abusive sur la qualité fonctionnelle. |

## End-to-end

| ID | Ce que le test évalue | Réussite attendue | Pièges principaux |
|---|---|---|---|
| E2E-01 | Contrat Spring REST → DTO → Angular UI. | Mapping API/UI correct, centimes et formatage conservés, payload invalide géré. | Mauvaise unité monétaire, état d'erreur oublié et forme JSON modifiée. |
| E2E-02 | Angular → commande REST → agrégat/event → projection JPA. | Flux complet cohérent avec versions, validation, ordre et projection immuable. | Version obsolète, événements séquentiels, mutation d'un objet partagé et validation partielle. |
| E2E-03 | Modernisation d'une règle legacy vers Java/Spring. | Service Java équivalent pour entrées unitaires, lots, décimales et invalides. | Écart COBOL/Java, échelle monétaire, ordre des lots et modification hors du fichier attendu. |

## Interprétation des résultats

Les rapports doivent conserver séparément le résultat par tâche, la catégorie,
les erreurs de protocole/client, les échecs de validation et les limites de
capacité de contexte. Une moyenne de catégorie ne doit pas masquer ces causes.
Pour les documents et l'OCR, les champs critiques (montants, dates,
identifiants, devises) doivent être lus avec les métriques CER/WER, exactitude
des champs, validité JSON et taux de champs manquants ou hallucinés lorsque ces
mesures sont disponibles.

Ce document décrit le contrat d'évaluation ; toute modification du prompt, des
fixtures, du scoring ou des validateurs doit faire évoluer la révision de la
tâche et être inscrite dans `docs/CHANGELOG.md`.
