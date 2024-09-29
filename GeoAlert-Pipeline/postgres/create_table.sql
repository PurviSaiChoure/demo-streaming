CREATE TABLE disaster_news (
    id SERIAL PRIMARY KEY,
    website VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    headline TEXT NOT NULL,
    entities JSONB NOT NULL,
    persons TEXT[] NOT NULL,
    organizations TEXT[] NOT NULL,
    gpes TEXT[] NOT NULL,
    dates TEXT[] NOT NULL,
    times TEXT[] NOT NULL,
    money TEXT[] NOT NULL,
    quantities TEXT[] NOT NULL,
    ordinals TEXT[] NOT NULL,
    cardinals TEXT[] NOT NULL,
    locations TEXT[] NOT NULL,
    events TEXT[] NOT NULL,
    works_of_art TEXT[] NOT NULL,
    laws TEXT[] NOT NULL,
    products TEXT[] NOT NULL,
    facilities TEXT[] NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE UNIQUE INDEX idx_disaster_news_url ON disaster_news(url);

CREATE INDEX idx_disaster_news_website ON disaster_news(website);

CREATE INDEX idx_disaster_news_persons ON disaster_news USING GIN (persons);
CREATE INDEX idx_disaster_news_organizations ON disaster_news USING GIN (organizations);
CREATE INDEX idx_disaster_news_gpes ON disaster_news USING GIN (gpes);
CREATE INDEX idx_disaster_news_dates ON disaster_news USING GIN (dates);
CREATE INDEX idx_disaster_news_times ON disaster_news USING GIN (times);
CREATE INDEX idx_disaster_news_money ON disaster_news USING GIN (money);
CREATE INDEX idx_disaster_news_quantities ON disaster_news USING GIN (quantities);
CREATE INDEX idx_disaster_news_ordinals ON disaster_news USING GIN (ordinals);
CREATE INDEX idx_disaster_news_cardinals ON disaster_news USING GIN (cardinals);
CREATE INDEX idx_disaster_news_locations ON disaster_news USING GIN (locations);
CREATE INDEX idx_disaster_news_events ON disaster_news USING GIN (events);
CREATE INDEX idx_disaster_news_works_of_art ON disaster_news USING GIN (works_of_art);
CREATE INDEX idx_disaster_news_laws ON disaster_news USING GIN (laws);
CREATE INDEX idx_disaster_news_products ON disaster_news USING GIN (products);
CREATE INDEX idx_disaster_news_facilities ON disaster_news USING GIN (facilities);
CREATE INDEX idx_disaster_news_entities ON disaster_news USING GIN (entities);
