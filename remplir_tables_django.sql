-- A executer une seule fois : remplit les tables de reference
-- creees par Django (core_departement, core_devise, core_statut)
-- avec les memes donnees que la base SQL d'origine.

INSERT INTO core_departement (nom) VALUES
('administration'), ('construction'), ('diaconat'), ('ecodim'),
('electricite'), ('entretien'), ('fiancailles'), ('finance'),
('groupe d''adoration'), ('intendance'), ('intercession'), ('jeunesse'),
('maman'), ('ouvrier'), ('papa'), ('partenariat'),
('presse et communication'), ('protocole'), ('securite'), ('social'),
('suivi et evangelisation'), ('technique')
ON CONFLICT (nom) DO NOTHING;

INSERT INTO core_devise (code) VALUES ('usd'), ('cdf')
ON CONFLICT (code) DO NOTHING;

INSERT INTO core_statut (nom) VALUES
('attente'), ('en cours'), ('realise'), ('reporte'), ('annule')
ON CONFLICT (nom) DO NOTHING;
