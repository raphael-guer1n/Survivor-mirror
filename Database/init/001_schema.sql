
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
  UNIQUE KEY ux_startups_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Founders
CREATE TABLE IF NOT EXISTS founders (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  startup_id INT NOT NULL,
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
  UNIQUE KEY ux_investors_email (email)
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
  UNIQUE KEY ux_partners_email (email)
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
  target_audience VARCHAR(255)
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
  FOREIGN KEY (founder_id) REFERENCES founders(id) ON DELETE SET NULL,
  FOREIGN KEY (investor_id) REFERENCES investors(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Indexes
CREATE INDEX idx_startups_sector ON startups(sector);
CREATE INDEX idx_news_startup_id ON news(startup_id);
CREATE INDEX idx_users_role ON users(role);
