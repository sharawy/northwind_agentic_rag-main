# Business & Querying Notes

- "Top customers" usually means by revenue unless otherwise stated.
- "Top selling categories" measured by total quantity or revenue; specify which. Default to revenue if ambiguous.
- For geographies: France, UK, USA, etc. Use Orders.ShipCountry when the destination matters (sales shipped to), Customers.Country when the customer's registered country matters.
- Always include ORDER BY when returning ranked results.
- Default LIMIT 50 to keep responses fast.
- Prefer non-null date ranges; if user asks for a year not present (e.g., 2024) adjust to nearest available year and note that in SQL as a comment.
