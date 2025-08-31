# Northwind SQLite — Key Schema Notes

- Orders(OrderID PK, CustomerID FK → Customers.CustomerID, EmployeeID FK → Employees.EmployeeID, OrderDate, ShippedDate, ShipVia FK → Shippers.ShipperID, Freight, ShipCountry, ...)
- "Order Details"(OrderID FK → Orders.OrderID, ProductID FK → Products.ProductID, UnitPrice, Quantity, Discount)
- Products(ProductID PK, ProductName, SupplierID FK → Suppliers.SupplierID, CategoryID FK → Categories.CategoryID, UnitPrice, Discontinued)
- Customers(CustomerID PK, CompanyName, ContactName, Country, City, ...)
- Categories(CategoryID PK, CategoryName, Description)
- Suppliers(SupplierID PK, CompanyName, Country)
- Employees(EmployeeID PK, FirstName, LastName, Title, ReportsTo → Employees.EmployeeID)
- Shippers(ShipperID PK, CompanyName)

**Revenue formula**: SUM(od.UnitPrice * od.Quantity * (1 - od.Discount))

**Quoting**: Table name `Order Details` contains a space; quote as "Order Details".

**Dates**: `Orders.OrderDate` in this dataset uses ISO timestamps (e.g., 2016-07-04 ...).

**Common filters**:
- Country filters: Orders.ShipCountry (for shipping destination), Customers.Country (for customer location), Suppliers.Country (for supplier location).
- Year/month extraction in SQLite: STRFTIME('%Y', o.OrderDate), STRFTIME('%m', o.OrderDate).
