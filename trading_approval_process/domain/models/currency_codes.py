# Immutable reference list of valid ISO 4217 currency codes.
# The list is intentionally short and representative for the prototype.
# In production, this data would be refreshed automatically from IBAN.com once daily.

VALID_CURRENCY_CODES: frozenset[str] = frozenset({
    "USD",  # US Dollar
    "EUR",  # Euro
    "GBP",  # British Pound
    "CHF",  # Swiss Franc
    "JPY",  # Japanese Yen
    "AUD",  # Australian Dollar
    "CAD",  # Canadian Dollar
    "NZD",  # New Zealand Dollar
    "SEK",  # Swedish Krona
    "NOK",  # Norwegian Krone
    "DKK",  # Danish Krone
    "ZAR",  # South African Rand
    "INR",  # Indian Rupee
    "CNY",  # Chinese Yuan
})
