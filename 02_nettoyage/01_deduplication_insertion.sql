/* 
   ÉTAPE 2 — Transformation, dédoublonnage et insertion
   Statut : VÉRIFIÉ (script réellement exécuté)

   Rôle :
   - Convertit les colonnes texte de la table brouillon
     `dpe_donnees_propres` vers les types finaux (DATE, FLOAT,
     SMALLINT), avec TRY_CONVERT/TRY_CAST 
   - Remplace les virgules décimales par des points (format
     français des données ADEME → format attendu par SQL Server).
   - Élimine les doublons d'import via une CTE + ROW_NUMBER()
     partitionné par numero_dpe (ne garde que la 1ère occurrence).
   - Supprime la table brouillon une fois les données propres
     insérées, pour ne pas garder deux copies des données.
    */

-- 1. Repérage et numérotation des doublons éventuels
WITH LignesUniques AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY numero_dpe ORDER BY (SELECT NULL)) AS numero_ligne
    FROM dpe_donnees_propres
)

-- 2. Insertion des données transformées (une seule ligne par numero_dpe)
INSERT INTO dpe_donnees_propres_final
SELECT
    numero_dpe,
    TRY_CONVERT(DATE, date_fin_validite_dpe, 103),
    etiquette_dpe,
    type_batiment,
    TRY_CAST(annee_construction AS SMALLINT),
    TRY_CAST(REPLACE(surface_habitable_logement, ',', '.') AS FLOAT),
    nom_commune_ban,
    code_postal_ban,
    code_departement_ban,
    TRY_CAST(REPLACE(conso_5_usages_par_m2_ep, ',', '.') AS FLOAT),
    TRY_CAST(REPLACE(cout_total_5_usages, ',', '.') AS FLOAT)
FROM LignesUniques
WHERE numero_ligne = 1;
GO

-- 3. Suppression de la table brouillon, devenue inutile
DROP TABLE dpe_donnees_propres;
GO
