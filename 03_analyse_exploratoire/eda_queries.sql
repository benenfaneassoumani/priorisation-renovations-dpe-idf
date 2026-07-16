/*
   ANALYSE EXPLORATOIRE 
   

   Objectif : premier état des lieux du parc de logements F/G
   avant de construire la vue de priorisation — combien de
   logements par étiquette, et comment ils se répartissent par
   commune.
    */

-- Nombre de logements par étiquette DPE (F vs G)
SELECT
    etiquette_dpe,
    COUNT(numero_dpe) AS nombre_logements
FROM dpe_donnees_propres_final
GROUP BY etiquette_dpe;

-- Répartition du nombre de logements par commune, du plus au moins concerné
SELECT
    nom_commune_ban,
    COUNT(*) AS nombre_logements
FROM dpe_donnees_propres_final
GROUP BY nom_commune_ban
ORDER BY nombre_logements DESC;
