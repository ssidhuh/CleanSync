"""Database management module."""

import mysql.connector
from mysql.connector import Error


class DatabaseManager:
    """
    Centralises MySQL connection and schema management.

    A dedicated database manager keeps repository classes focused on
    entity persistence instead of repeating connection setup logic.
    """

    HOST = "localhost"
    USER = "root"
    PASSWORD = ""
    DATABASE = "Cleansync"

    ACTIVE_CONNECTIONS = []

    @classmethod
    def get_connection(cls):
        """Provide one controlled entry point for database access."""
        try:
            connection = mysql.connector.connect(
                host=cls.HOST,
                user=cls.USER,
                password=cls.PASSWORD,
                database=cls.DATABASE,
            )
            cls.ACTIVE_CONNECTIONS.append(connection)
            return connection

        except Error as error:
            print(f"Database connection error: {error}")
            raise

    @classmethod
    def close_database(cls) -> None:
        """Close tracked connections so the app exits cleanly."""
        for connection in cls.ACTIVE_CONNECTIONS:
            cls._close_connection_safely(connection)

        cls.ACTIVE_CONNECTIONS.clear()
        print("Database disconnected successfully.")

    @classmethod
    def initialise_database(cls) -> None:
        """Keep schema creation centralised before the UI starts."""
        connection = cls.get_connection()
        cursor = connection.cursor()

        cls._create_customers_table(cursor)
        cls._create_cleaners_table(cursor)
        cls._create_services_table(cursor)
        cls._create_bookings_table(cursor)
        cls._create_invoices_table(cursor)
        cls._create_payments_table(cursor)

        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def _close_connection_safely(connection) -> None:
        """Avoid exit crashes if a connection is already closed."""
        try:
            if connection.is_connected():
                connection.close()
        except Error as error:
            print(f"Error while closing database connection: {error}")

    @staticmethod
    def _create_customers_table(cursor) -> None:
        """Keep customer schema changes isolated from startup flow."""
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                customer_id VARCHAR(255) PRIMARY KEY,
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255) NOT NULL,
                phone_number VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                address TEXT NOT NULL,
                created_at VARCHAR(255) NOT NULL
            )
            """
        )

    @staticmethod
    def _create_cleaners_table(cursor) -> None:
        """Keep cleaner schema changes isolated from startup flow."""
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cleaners (
                cleaner_id VARCHAR(255) PRIMARY KEY,
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                phone_number VARCHAR(255) NOT NULL,
                hourly_rate FLOAT NOT NULL,
                rating FLOAT NOT NULL,
                status VARCHAR(255) NOT NULL,
                specializations TEXT NOT NULL,
                service_area VARCHAR(255) NOT NULL,
                created_at VARCHAR(255) NOT NULL
            )
            """
        )

    @staticmethod
    def _create_services_table(cursor) -> None:
        """Keep service schema changes isolated from startup flow."""
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cleaning_services (
                service_id VARCHAR(255) PRIMARY KEY,
                service_name VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                duration_hours FLOAT NOT NULL,
                base_price FLOAT NOT NULL,
                created_at VARCHAR(255) NOT NULL
            )
            """
        )

    @staticmethod
    def _create_bookings_table(cursor) -> None:
        """Define booking relationships in one schema method."""
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id VARCHAR(255) PRIMARY KEY,
                customer_id VARCHAR(255) NOT NULL,
                cleaner_id VARCHAR(255) NOT NULL,
                service_id VARCHAR(255) NOT NULL,
                booking_date VARCHAR(255) NOT NULL,
                status VARCHAR(255) NOT NULL,
                created_at VARCHAR(255) NOT NULL,
                booking_number VARCHAR(255),
                end_time VARCHAR(255),
                address TEXT,
                total_amount FLOAT DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                FOREIGN KEY (cleaner_id) REFERENCES cleaners(cleaner_id),
                FOREIGN KEY (service_id) REFERENCES cleaning_services(service_id)
            )
            """
        )

    @staticmethod
    def _create_invoices_table(cursor) -> None:
        """Keep billing relationships separate from booking creation."""
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS invoices (
                invoice_id VARCHAR(255) PRIMARY KEY,
                booking_id VARCHAR(255) NOT NULL,
                total_amount FLOAT NOT NULL,
                payment_status VARCHAR(255) NOT NULL,
                created_at VARCHAR(255) NOT NULL,
                invoice_number VARCHAR(255),
                due_date VARCHAR(255),
                line_description TEXT,
                quantity INTEGER DEFAULT 1,
                unit_price FLOAT DEFAULT 0,
                tax_rate FLOAT DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
            )
            """
        )

    @staticmethod
    def _create_payments_table(cursor) -> None:
        """Keep payment records linked to invoices at schema level."""
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
                 payment_id VARCHAR(255) PRIMARY KEY,
                 invoice_id VARCHAR(255) NOT NULL,
                 amount FLOAT NOT NULL,
                 payment_date VARCHAR(255) NOT NULL,
                 method VARCHAR(255) NOT NULL,
                 reference_number VARCHAR(255) NOT NULL,
                 status VARCHAR(255) NOT NULL,
                 notes TEXT,
                 created_at VARCHAR(255) NOT NULL,
                 FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
            )
            """
        )