conf = {
    'link': "https://www.w3schools.com/sql/trysql.asp?filename=trysql_select_all",
    'sql_req': {
        'select_all': "SELECT * FROM Customers;",
        'select_london': "SELECT * FROM Customers WHERE city='London';",
        'insert_new': "INSERT INTO Customers (CustomerID, CustomerName, ContactName, Address, City, PostalCode, Country) VALUES ('99','VermeShell', 'Egor Urgant', '66 Six Hellveny', 'Helsinki', '33624', 'Finland');",
        'check_new': "SELECT * FROM Customers WHERE CustomerID = '99';",
        'update_new': "UPDATE Customers SET CustomerName = 'NeVermeShell', ContactName = 'NeEgor NeUrgant', Address = 'Drugoi', City = 'Hellcity', PostalCode = '66666', Country = 'NeFinland' WHERE CustomerID = '99'"
    },
    'css': {
        'sql_btn': "div:nth-child(1) > button",
        'sql_state': "#tryitform > div",
        'res_number': "#divResultSQL > div > div",
        'made_changes': "div#divResultSQL > div",
        'restore_btn': "button#restoreDBBtn",
        'table_row': ".w3-table-all.notranslate tr"
    }
}
