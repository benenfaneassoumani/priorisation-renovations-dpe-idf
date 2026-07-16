/* 
   VUE : vue_priorite_renovation
   Rôle : calcule pour chaque logement F/G le coût de rénovation,
          le gain financier, le gain écologique et le score de
          priorité utilisés par le dashboard Power BI.
   Source : dpe_donnees_propres_final (base donnees_pour_gestion_locative)
       */

ALTER VIEW vue_priorite_renovation AS
SELECT
    numero_dpe,
    nom_commune_ban,
    code_postal_ban,
    code_departement_ban,
    etiquette_dpe,
    surface_habitable_logement,
    conso_5_usages_par_m2_ep,

    -- 1. Coût des travaux estimé (proportionnel à la surface)
    --    Hypothèse : 800 €/m² pour une étiquette G, 500 €/m² pour une étiquette F
    --    Ordre de grandeur cohérent avec les fourchettes publiques de rénovation
    --    F/G → C/B (400 à 800 €/m² selon koutravo.fr ; 400-700 €/m² pour une
    --    rénovation globale performante selon l'ADEME, cité par
    --    blog.moteurimmo.fr). Aucune source publique ne distingue précisément
    --    un coût au m² propre à F vs propre à G : l'écart retenu ici (800
    --    contre 500) est une hypothèse de modélisation, pas une valeur
    --    officielle par étiquette.
    CASE
        WHEN etiquette_dpe = 'G' THEN surface_habitable_logement * 800
        WHEN etiquette_dpe = 'F' THEN surface_habitable_logement * 500
    END AS cout_travaux,

    -- 2. Gain financier : loyer annuel estimé maintenu grâce à la rénovation
    --    Hypothèse : 18 €/m²/mois (loyer intermédiaire francilien)
    (surface_habitable_logement * 18 * 12) AS gain_financier,

    -- 3. Gain écologique : économie d'énergie convertie en euros
    --    Hypothèse : cible de consommation 150 kWh/m²/an (classe C)
    --    Hypothèse : 0,25 €/kWh économisé
    ((conso_5_usages_par_m2_ep - 150) * surface_habitable_logement * 0.25)
        AS gain_ecologique_euros,

    -- 4. Score de priorité : ratio (gain / coût) pondéré par un bonus
    --    pour les logements G (x1,5)
    
    ROUND(
        (
            (surface_habitable_logement * 18 * 12) +
            ((conso_5_usages_par_m2_ep - 150) * surface_habitable_logement * 0.25)
        )
        * CASE WHEN etiquette_dpe = 'G' THEN 1.5 ELSE 1.0 END
        /
        CASE
            WHEN etiquette_dpe = 'G' THEN surface_habitable_logement * 800
            ELSE surface_habitable_logement * 500
        END
    , 4) AS score_priorite

FROM dpe_donnees_propres_final
WHERE surface_habitable_logement > 0
  AND conso_5_usages_par_m2_ep IS NOT NULL;

