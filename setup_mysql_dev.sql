-- sql script


CREATE DATABASE IF NOT EXISTS chatbot_db;
       CREATE USER IF NOT EXISTS 'chat'@'localhost' IDENTIFIED BY 'Chat_pwd123@';
              GRANT ALL PRIVILEGES ON chatbot_db.* TO 'chat'@'localhost';
                                      GRANT SELECT ON performance_schema.* TO 'rent_user'@'localhost';
FLUSH PRIVILEGES;