/**
 * Created by liutongtong on 2018/7/15 10:21
 */

DROP TABLE IF EXISTS dongqiudi_articles;
CREATE TABLE IF NOT EXISTS dongqiudi_articles (
    id INT,
    title VARCHAR(127),
    description VARCHAR(255),
    user_id INT,
    `type` VARCHAR(31),
    display_time TIMESTAMP,
    thumb VARCHAR(255),
    comments_total INT,
    web_url VARCHAR(255),
    official_account VARCHAR(255),
    save_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    save_html BOOL DEFAULT FALSE,
    PRIMARY KEY (id)
);
