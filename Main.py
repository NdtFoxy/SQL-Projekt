import pyodbc

def connect_to_db():
    # Łańcuch połączenia z bazą danych
    connection_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=mssql-2017.labs.wmi.amu.edu.pl;"
        "DATABASE=dbad_s498817;"
        "UID=dbad_s498817;"
        "PWD=K77GJq34h8"
    )
    
    return pyodbc.connect(connection_string)

def show_tables(connection):
    # Pobranie listy wszystkich tabel z bazy danych
    cursor = connection.cursor()
    cursor.execute("""
        SELECT table_name = t.name
        FROM sys.tables t
        ORDER BY t.name
    """)
    tables = cursor.fetchall()
    print("\nDostępne tabele w bazie danych:")
    for i, table in enumerate(tables, 1):
        print(f"{i}. {table[0]}")
    return [table[0] for table in tables]

def show_table_data(connection, table_name):
    cursor = connection.cursor()
    
    # Pobranie nagłówków kolumn
    cursor.execute(f"SELECT * FROM {table_name}")
    columns = [column[0] for column in cursor.description]
    print("\nNagłówki kolumn:")
    print("-" * 50)
    print(" | ".join(columns))
    print("-" * 50)
    
    # Pobranie danych z tabeli
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    print("\nDane z tabeli:")
    print("-" * 50)
    for row in rows:
        print(" | ".join(str(value) for value in row))
    print("-" * 50)

def main():
    try:
        # Nawiązywanie połączenia z bazą danych
        connection = connect_to_db()
        print("Pomyślnie połączono z bazą danych!")
        
        while True:
            # Wyświetlenie wszystkich tabel
            tables = show_tables(connection)
            
            if not tables:
                print("Brak tabel w bazie danych!")
                break
                
            # Pobieranie wyboru użytkownika
            choice = input("\nWybierz numer tabeli do wyświetlenia (lub 'q' aby wyjść): ")
            
            if choice.lower() == 'q':
                break
                
            try:
                table_index = int(choice) - 1
                if 0 <= table_index < len(tables):
                    selected_table = tables[table_index]
                    print(f"\nWybrana tabela: {selected_table}")
                    show_table_data(connection, selected_table)
                else:
                    print("Nieprawidłowy numer tabeli!")
            except ValueError:
                print("Proszę podać prawidłowy numer tabeli!")
            
            print("\n" + "="*50 + "\n")
            
    except Exception as e:
        print(f"Błąd: {str(e)}")
    finally:
        if 'connection' in locals():
            connection.close()
            print("\nPołączenie z bazą danych zostało zamknięte.")

if __name__ == "__main__":
    main() 