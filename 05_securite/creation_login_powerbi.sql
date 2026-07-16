/* 
   SÉCURITÉ — Login SQL Server dédié à Power BI
   Statut : VÉRIFIÉ dans sa logique, MAIS mot de passe remplacé
   par un placeholder avant publication (voir avertissement).

   Principe du moindre privilège : Power BI ne se connecte jamais
   avec un compte administrateur. Il utilise un login dédié,
   en lecture seule, limité au schéma dbo.
   */

-- 1. Création du login au niveau du serveur
CREATE LOGIN powerbi_user
WITH PASSWORD = 'REMPLACER_PAR_UN_MOT_DE_PASSE_FORT';

-- 2. Octroi de l'accès en lecture seule sur la base du projet
USE données_pour_gestion_locative;
CREATE USER powerbi_user FOR LOGIN powerbi_user;
GRANT SELECT ON SCHEMA::dbo TO powerbi_user;
GO
