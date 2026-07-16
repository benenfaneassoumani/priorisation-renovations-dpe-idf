/* =============================================================
   ÉTAPE 1 — Création de la table finale structurée
   Statut : VÉRIFIÉ (script réellement exécuté)

   Contexte : les données brutes ADEME sont d'abord chargées telles
   quelles (toutes colonnes en texte) dans une table brouillon
   nommée `dpe_donnees_propres`, via l'assistant d'import SQL Server
   / Power Query. Cette table brouillon n'est pas scriptée ici car
   elle est générée automatiquement par l'outil d'import — seule la
   table finale, avec les types corrects, est créée explicitement.
   ============================================================= */

CREATE TABLE dpe_donnees_propres_final (
    numero_dpe                  NVARCHAR(50) PRIMARY KEY,
    date_fin_validite_dpe       DATE,
    etiquette_dpe                NVARCHAR(10),
    type_batiment                 NVARCHAR(50),
    annee_construction          SMALLINT,
    surface_habitable_logement  FLOAT,
    nom_commune_ban               NVARCHAR(100),
    code_postal_ban               NVARCHAR(10),
    code_departement_ban        NVARCHAR(10),
    conso_5_usages_par_m2_ep    FLOAT,
    cout_total_5_usages          FLOAT
);
GO
