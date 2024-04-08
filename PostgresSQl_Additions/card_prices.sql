CREATE TABLE card_prices (
    id SERIAL PRIMARY KEY,
    price NUMERIC NOT NULL,
    date DATE NOT NULL
);

CREATE TABLE card_printing_prices (
    card_printing_id VARCHAR(21) NOT NULL,
    card_price_id INTEGER NOT NULL,
    PRIMARY KEY (card_printing_id, card_price_id),
    FOREIGN KEY (card_printing_id) REFERENCES card_printings (unique_id),
    FOREIGN KEY (card_price_id) REFERENCES card_prices (id)
);