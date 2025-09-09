SET sql_mode = 'STRICT_TRANS_TABLES';
SET NAMES utf8mb4;
SET time_zone = '+00:00';

CREATE DATABASE IF NOT EXISTS jeb_incubator DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE jeb_incubator;

-- Startups
CREATE TABLE IF NOT EXISTS startups (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  legal_status VARCHAR(255),
  address TEXT,
  email VARCHAR(255) NOT NULL,
  phone VARCHAR(50),
  created_at DATE,
  description TEXT,
  website_url VARCHAR(255),
  social_media_url VARCHAR(255),
  project_status VARCHAR(100),
  needs TEXT,
  sector VARCHAR(100),
  maturity VARCHAR(100),
  UNIQUE KEY ux_startups_email (email),
  image_s3_key VARCHAR(512) NULL,
  view_count INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Founders
CREATE TABLE IF NOT EXISTS founders (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  startup_id INT NOT NULL,
  image_s3_key VARCHAR(512) NULL,
  FOREIGN KEY (startup_id) REFERENCES startups(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Investors
CREATE TABLE IF NOT EXISTS investors (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  legal_status VARCHAR(255),
  address TEXT,
  email VARCHAR(255) NOT NULL,
  phone VARCHAR(50),
  created_at DATE,
  description TEXT,
  investor_type VARCHAR(100),
  investment_focus VARCHAR(255),
  UNIQUE KEY ux_investors_email (email),
  image_s3_key VARCHAR(512) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Partners
CREATE TABLE IF NOT EXISTS partners (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  legal_status VARCHAR(255),
  address TEXT,
  email VARCHAR(255) NOT NULL,
  phone VARCHAR(50),
  created_at DATE,
  description TEXT,
  partnership_type VARCHAR(100),
  UNIQUE KEY ux_partners_email (email),
  image_s3_key VARCHAR(512) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- News
CREATE TABLE IF NOT EXISTS news (
  id INT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(255) NOT NULL,
  news_date DATE,
  location VARCHAR(255),
  category VARCHAR(100),
  startup_id INT,
  description TEXT,
  image_s3_key VARCHAR(512) NULL,
  FOREIGN KEY (startup_id) REFERENCES startups(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Events
CREATE TABLE IF NOT EXISTS events (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  dates TEXT,
  location VARCHAR(255),
  description TEXT,
  event_type VARCHAR(100),
  target_audience VARCHAR(255),
  image_s3_key VARCHAR(512) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Users
CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  email VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL,
  founder_id INT,
  investor_id INT,
  password_hash VARCHAR(512),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY ux_users_email (email),
  image_s3_key VARCHAR(512) NULL,
  FOREIGN KEY (founder_id) REFERENCES founders(id) ON DELETE SET NULL,
  FOREIGN KEY (investor_id) REFERENCES investors(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_startups_sector ON startups(sector);
CREATE INDEX IF NOT EXISTS idx_news_startup_id ON news(startup_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
-- Email verification codes
CREATE TABLE IF NOT EXISTS email_verifications (
    email VARCHAR(255) PRIMARY KEY,
    code VARCHAR(6) NOT NULL,
    created_at DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sync
CREATE TABLE IF NOT EXISTS sync_state (
  entity VARCHAR(32) PRIMARY KEY,
  last_id INT NOT NULL DEFAULT 0,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO sync_state (entity, last_id) VALUES
  ('startups', 0),
  ('investors', 0),
  ('partners', 0),
  ('news', 0),
  ('events', 0),
  ('users', 0);


  [
  {
    "email": "admin@jeb.com",
    "name": "Victoria",
    "role": "admin",
    "founder_id": null,
    "investor_id": null,
    "id": 1
  },
  {
    "email": "super.admin@jeb.com",
    "name": "Victoria",
    "role": "admin",
    "founder_id": null,
    "investor_id": null,
    "id": 2
  },
  {
    "email": "contact@brightcapital.com",
    "name": "Marie",
    "role": "investor",
    "founder_id": null,
    "investor_id": 1,
    "id": 3
  },
  {
    "email": "info@futureedge.app",
    "name": "Jean",
    "role": "investor",
    "founder_id": null,
    "investor_id": 2,
    "id": 4
  },
  {
    "email": "us@impactventures.be",
    "name": "Jeanne",
    "role": "investor",
    "founder_id": null,
    "investor_id": 3,
    "id": 5
  },
  {
    "email": "invest@greenvision.eu",
    "name": "Pierre",
    "role": "investor",
    "founder_id": null,
    "investor_id": 4,
    "id": 6
  },
  {
    "email": "info@eurogrowth.com",
    "name": "Chantal",
    "role": "investor",
    "founder_id": null,
    "investor_id": 5,
    "id": 7
  },
  {
    "email": "info@alphaventures.eu",
    "name": "Philippe",
    "role": "investor",
    "founder_id": null,
    "investor_id": 6,
    "id": 8
  },
  {
    "email": "contact@sparkcapital.com",
    "name": "Sylvie",
    "role": "investor",
    "founder_id": null,
    "investor_id": 7,
    "id": 9
  },
  {
    "email": "bonjour@horizonfund.fr",
    "name": "Alain",
    "role": "investor",
    "founder_id": null,
    "investor_id": 8,
    "id": 10
  },
  {
    "email": "info@nextwave.eu",
    "name": "Nathalie",
    "role": "investor",
    "founder_id": null,
    "investor_id": 9,
    "id": 11
  },
  {
    "email": "contact@urbanseed.fr",
    "name": "Christophe",
    "role": "investor",
    "founder_id": null,
    "investor_id": 10,
    "id": 12
  },
  {
    "email": "hello@blueoceaninvestments.eu",
    "name": "Valérie",
    "role": "investor",
    "founder_id": null,
    "investor_id": 11,
    "id": 13
  },
  {
    "email": "info@innovatenow.it",
    "name": "Nicolas",
    "role": "investor",
    "founder_id": null,
    "investor_id": 12,
    "id": 14
  },
  {
    "email": "invest@civiccapital.com",
    "name": "Céline",
    "role": "investor",
    "founder_id": null,
    "investor_id": 13,
    "id": 15
  },
  {
    "email": "startup@techelevate.com",
    "name": "Laurent",
    "role": "investor",
    "founder_id": null,
    "investor_id": 14,
    "id": 16
  },
  {
    "email": "contact@ecofund.com",
    "name": "Stéphanie",
    "role": "investor",
    "founder_id": null,
    "investor_id": 15,
    "id": 17
  },
  {
    "email": "contact@venturebridge.com",
    "name": "Stéphane",
    "role": "investor",
    "founder_id": null,
    "investor_id": 16,
    "id": 18
  },
  {
    "email": "contact@capitalroots.com",
    "name": "Isabelle",
    "role": "investor",
    "founder_id": null,
    "investor_id": 17,
    "id": 19
  },
  {
    "email": "investissements@newleafcapital.fr",
    "name": "David",
    "role": "investor",
    "founder_id": null,
    "investor_id": 18,
    "id": 20
  },
  {
    "email": "innovate@foundersfirst.com",
    "name": "Sophie",
    "role": "investor",
    "founder_id": null,
    "investor_id": 19,
    "id": 21
  },
  {
    "email": "contact@smartinvest.fr",
    "name": "Patrick",
    "role": "investor",
    "founder_id": null,
    "investor_id": 20,
    "id": 22
  },
  {
    "email": "info@novatrust.eu",
    "name": "Anne",
    "role": "investor",
    "founder_id": null,
    "investor_id": 21,
    "id": 23
  },
  {
    "email": "info@truenorthventures.com",
    "name": "Olivier",
    "role": "investor",
    "founder_id": null,
    "investor_id": 22,
    "id": 24
  },
  {
    "email": "info@ideaforge.eu",
    "name": "Catherine",
    "role": "investor",
    "founder_id": null,
    "investor_id": 23,
    "id": 25
  },
  {
    "email": "contact@bridgepointcapital.fr",
    "name": "Frédéric",
    "role": "investor",
    "founder_id": null,
    "investor_id": 24,
    "id": 26
  },
  {
    "email": "info@riseinvest.eu",
    "name": "Laurence",
    "role": "investor",
    "founder_id": null,
    "investor_id": 25,
    "id": 27
  },
  {
    "email": "manon.leroy@gmail.com",
    "name": "Manon Leroy",
    "role": "founder",
    "founder_id": 1,
    "investor_id": null,
    "id": 28
  },
  {
    "email": "camille.rousseau@outlook.com",
    "name": "Camille Rousseau",
    "role": "founder",
    "founder_id": 2,
    "investor_id": null,
    "id": 29
  },
  {
    "email": "julien.moreau@gmail.com",
    "name": "Julien Moreau",
    "role": "founder",
    "founder_id": 3,
    "investor_id": null,
    "id": 30
  },
  {
    "email": "alexandre.dubois@gmail.com",
    "name": "Alexandre Dubois",
    "role": "founder",
    "founder_id": 4,
    "investor_id": null,
    "id": 31
  },
  {
    "email": "marie.leclerc@gmail.com",
    "name": "Marie Leclerc",
    "role": "founder",
    "founder_id": 5,
    "investor_id": null,
    "id": 32
  },
  {
    "email": "lucas.garcia@gmail.com",
    "name": "Lucas Garcia",
    "role": "founder",
    "founder_id": 6,
    "investor_id": null,
    "id": 33
  },
  {
    "email": "marie.leclerc7@hotmail.com",
    "name": "Marie Leclerc",
    "role": "founder",
    "founder_id": 7,
    "investor_id": null,
    "id": 34
  },
  {
    "email": "lea.martin@gmail.com",
    "name": "Léa Martin",
    "role": "founder",
    "founder_id": 8,
    "investor_id": null,
    "id": 35
  },
  {
    "email": "emma.roux@gmail.com",
    "name": "Emma Roux",
    "role": "founder",
    "founder_id": 9,
    "investor_id": null,
    "id": 36
  },
  {
    "email": "camille.rousseau10@gmail.com",
    "name": "Camille Rousseau",
    "role": "founder",
    "founder_id": 10,
    "investor_id": null,
    "id": 37
  },
  {
    "email": "camille.rousseau11@hotmail.com",
    "name": "Camille Rousseau",
    "role": "founder",
    "founder_id": 11,
    "investor_id": null,
    "id": 38
  },
  {
    "email": "nicolas.bernard@outlook.com",
    "name": "Nicolas Bernard",
    "role": "founder",
    "founder_id": 12,
    "investor_id": null,
    "id": 39
  },
  {
    "email": "louis.moreau@gmail.com",
    "name": "Louis Moreau",
    "role": "founder",
    "founder_id": 13,
    "investor_id": null,
    "id": 40
  },
  {
    "email": "emma.roux14@gmail.com",
    "name": "Emma Roux",
    "role": "founder",
    "founder_id": 14,
    "investor_id": null,
    "id": 41
  },
  {
    "email": "julien.moreau15@gmail.com",
    "name": "Julien Moreau",
    "role": "founder",
    "founder_id": 15,
    "investor_id": null,
    "id": 42
  },
  {
    "email": "louis.moreau16@gmail.com",
    "name": "Louis Moreau",
    "role": "founder",
    "founder_id": 16,
    "investor_id": null,
    "id": 43
  },
  {
    "email": "marie.leclerc17@outlook.com",
    "name": "Marie Leclerc",
    "role": "founder",
    "founder_id": 17,
    "investor_id": null,
    "id": 44
  },
  {
    "email": "gabriel.durand@hotmail.com",
    "name": "Gabriel Durand",
    "role": "founder",
    "founder_id": 18,
    "investor_id": null,
    "id": 45
  },
  {
    "email": "emma.roux19@gmail.com",
    "name": "Emma Roux",
    "role": "founder",
    "founder_id": 19,
    "investor_id": null,
    "id": 46
  },
  {
    "email": "louis.moreau20@outlook.com",
    "name": "Louis Moreau",
    "role": "founder",
    "founder_id": 20,
    "investor_id": null,
    "id": 47
  },
  {
    "email": "gabriel.durand21@hotmail.com",
    "name": "Gabriel Durand",
    "role": "founder",
    "founder_id": 21,
    "investor_id": null,
    "id": 48
  },
  {
    "email": "louis.moreau22@hotmail.com",
    "name": "Louis Moreau",
    "role": "founder",
    "founder_id": 22,
    "investor_id": null,
    "id": 49
  },
  {
    "email": "lea.martin23@hotmail.com",
    "name": "Léa Martin",
    "role": "founder",
    "founder_id": 23,
    "investor_id": null,
    "id": 50
  },
  {
    "email": "chloe.petit@outlook.com",
    "name": "Chloé Petit",
    "role": "founder",
    "founder_id": 24,
    "investor_id": null,
    "id": 51
  },
  {
    "email": "manon.leroy25@gmail.com",
    "name": "Manon Leroy",
    "role": "founder",
    "founder_id": 25,
    "investor_id": null,
    "id": 52
  }
]