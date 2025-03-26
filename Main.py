import pyodbc
import configparser # Dodano import do obsługi plików konfiguracyjnych

def connect_to_db():
    """Nawiązuje połączenie z bazą danych na podstawie danych z pliku config.ini."""
    config = configparser.ConfigParser()
    try:
        # Odczytanie pliku konfiguracyjnego
        config.read('config.ini')
        db_config = config['Database'] # Pobranie sekcji [Database]

        # Pobranie poszczególnych wartości z konfiguracji
        driver = db_config['Driver']
        server = db_config['Server']
        database = db_config['Database']
        uid = db_config['UID']
        pwd = db_config['PWD'] # Pamiętaj o bezpieczeństwie haseł w rzeczywistych aplikacjach!

        # Budowanie łańcucha połączenia z danych konfiguracyjnych
        connection_string = (
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={uid};"
            f"PWD={pwd}"
        )
    except FileNotFoundError:
        print("Błąd: Plik konfiguracyjny 'config.ini' nie został znaleziony.")
        return None # Zwróć None, jeśli plik nie istnieje
    except KeyError as e:
        print(f"Błąd: Brak klucza '{e}' w sekcji [Database] pliku config.ini.")
        return None # Zwróć None, jeśli brakuje klucza
    except Exception as e:
        print(f"Błąd podczas odczytu pliku konfiguracyjnego: {e}")
        return None # Zwróć None w przypadku innego błędu odczytu

    # Nawiązanie połączenia za pomocą zbudowanego łańcucha
    return pyodbc.connect(connection_string)

def show_tables(connection):
    """Wyświetla listę dostępnych tabel w bazie danych."""
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
    """Wyświetla dane z wybranej tabeli wraz z nagłówkami."""
    cursor = connection.cursor()

    # Pobranie nagłówków kolumn
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        # Sprawdzenie, czy zapytanie zwróciło opis kolumn
        if cursor.description is None:
             print(f"\nNie można pobrać informacji o kolumnach dla tabeli '{table_name}'. Może być pusta lub niedostępna.")
             return

        columns = [column[0] for column in cursor.description]
        # Pobranie danych z tabeli (zrobimy to raz)
        rows = cursor.fetchall()
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"\nBłąd podczas wykonywania zapytania dla tabeli '{table_name}': {ex}")
        print(f"SQLSTATE: {sqlstate}")
        # Spróbuj podać bardziej szczegółowe informacje, jeśli to możliwe
        if '42S02' in sqlstate:
            print("Wygląda na to, że tabela nie istnieje lub nie masz do niej uprawnień.")
        return # Wyjście z funkcji w przypadku błędu

    if not columns:
        print(f"\nTabela '{table_name}' nie ma kolumn.")
        return

    # --- Początek dodanego kodu do tabulacji ---

    # Obliczenie maksymalnej szerokości dla każdej kolumny
    # Zaczynamy od szerokości nagłówków
    col_widths = [len(str(col)) for col in columns]

    # Przeglądamy dane, aby znaleźć najdłuższą wartość w każdej kolumnie
    for row in rows:
        for i, value in enumerate(row):
            # Aktualizujemy maksymalną szerokość dla kolumny i
            col_widths[i] = max(col_widths[i], len(str(value) if value is not None else "NULL"))

    # Formatowanie wiersza nagłówków
    header_line = " | ".join(f"{col:<{col_widths[i]}}" for i, col in enumerate(columns))
    separator_line = "-" * len(header_line) # Separator odpowiada długości nagłówka

    # --- Koniec dodanego kodu do tabulacji ---


    print("\nNagłówki kolumn:")
    print(separator_line) # Używamy obliczonego separatora
    # print(" | ".join(columns)) # Stary kod
    print(header_line) # Nowy sformatowany nagłówek
    print(separator_line) # Używamy obliczonego separatora

    print("\nDane z tabeli:")
    # print("-" * 50) # Stary kod
    if not rows:
        print("<brak danych>")
    else:
        for row in rows:
            # print(" | ".join(str(value) for value in row)) # Stary kod
            # Formatujemy każdy wiersz danych zgodnie z szerokością kolumn
            formatted_row = " | ".join(f"{str(value) if value is not None else 'NULL':<{col_widths[i]}}" for i, value in enumerate(row))
            print(formatted_row) # Nowy sformatowany wiersz

    print(separator_line) # Używamy obliczonego separatora


def main():
    connection = None # Inicjalizujemy connection tutaj
    try:
        # Nawiązywanie połączenia z bazą danych za pomocą nowej funkcji
        connection = connect_to_db()

        # Sprawdzenie, czy połączenie zostało pomyślnie nawiązane
        if connection is None:
            print("Nie udało się nawiązać połączenia z bazą danych. Sprawdź plik konfiguracyjny i komunikaty błędów.")
            return # Zakończ program, jeśli nie ma połączenia

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
            except Exception as inner_ex: # Łapiemy możliwe błędy podczas wyświetlania danych tabeli
                print(f"Wystąpił błąd podczas wyświetlania danych tabeli: {inner_ex}")


            print("\n" + "="*50 + "\n")

    except pyodbc.Error as ex: # Bardziej specyficzny wyjątek dla błędów bazy danych
        sqlstate = ex.args[0]
        print(f"Błąd połączenia lub zapytania do bazy danych: {ex}")
        print(f"SQLSTATE: {sqlstate}")
        # Można dodać sprawdzanie konkretnych kodów błędów, np. dla nieprawidłowych danych logowania.
        if '08001' in sqlstate or '28000' in sqlstate:
             print("Sprawdź dane logowania w pliku config.ini lub dostępność serwera.")
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {str(e)}")
    finally:
        # Sprawdzenie, czy zmienna 'connection' została pomyślnie utworzona i czy istnieje
        if connection:
            connection.close()
            print("\nPołączenie z bazą danych zostało zamknięte.")
        # Usunięto else, bo informacja o braku połączenia jest już w bloku try

if __name__ == "__main__":
    main()