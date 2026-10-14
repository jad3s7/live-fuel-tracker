"""
This file handles the configuration settings for the project.
From the extract, transform and load stage to the viz.
Config also handles the API config, database, email, dashboard,
report and automation configuration.
"""

import os 
from dotenv import load_dotenv


class Config:
    """
    Class configuration that manages all the configuration settings
    for all phases of the lifecycel
    """

    def __init__(self) -> None:
        """ 
        This initializes the configuration by loading the 
        environment variables.
        """
        load_dotenv()

        # Database configuration
        self.database_path: str = os.getenv("DATABASE_PATH", "fuel_rates.db")
        # Also supports DB_PATH for older setups
        if not self.database_path or self.database_path == "fuel_rates.db":
              self.database_path = os.getenv("DB_PATH", "fuel_rate.db")

        # Fuel Price API configuration
        self.fuel_api_provider: str = os.getenv('FUEL_API_PROVIDER', 'simulated').lower()
        self.fuel_api_key: str = os.getenv('FUEL_API_KEY', '')
        self.api_timeout = int(os.getenv('API_TIMEOUT', '10'))
        self.fuel_api_base_url: str = os.getenv('FUEL_API_BASE_URL', '')
        if not self.fuel_api_base_url:
              self.fuel_api_base_url = os.getenv('API_BASE_URL', '')

        # Email configuration
        self.smtp_server: str = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email: str = os.getenv('SENDER_EMAIL', '')
        self.sender_password = os.getenv('SENDER_PASSWORD', '')

        # Dashboard configuration
        self.dashboard_port = int(os.getenv('DASHBOARD_PORT', '8501'))
        self.dashboard_host: str = os.getenv('DASHBOARD_HOST', 'localhost')

        # Report configuratiion
        self.reports_dir: str = os.getenv('REPORTS_DIR', 'reports')
        self.logs_dir: str = os.getenv('LOGS_DIR', 'logs')

        # Automation configuration
        self.auto_refresh_minutes = int(os.getenv('AUTO_REFRESH_MINUTES', '60'))
        self.enable_email_alerts: bool = os.getenv('ENABLE_EMAIL_ALERTS','false').lower() == 'true'


    def get_database_path(self) -> str:
        """ 
        Function retrieves the database path.


        Returns:
            The database path to the SQLite database file.
        """
        return self.database_path


    def is_email_configured(self) -> bool:
        """
        Function that checks if email configuration is set up.

        Returns:
            - Boolean True if email configuration is done.
            - Boolean False if email configuration is incomplete.            
        """
        return bool(self.sender_email and self.sender_password)

    def string_representation_config(self) -> str:
        """
        Displays the configuration.

        Returns:
        - config database path
        - api timeout
        - email config
        """
        return (f"Config(database_path: {self.database_path}), "
                f"api_time: {self.api_timeout}, "
                f"Emaill_configured: {self.is_email_configured()})")
    

    def __str__(self) -> str:
         return self.string_representation_config()

# Class Config: Global config
config = Config()

if __name__== "__main__":
    #  Test the configuration
    print("Testing the configuration setup:")
    print("=================================")
    print(f"Configuration: {config}")
    print(f"Database Path: {config.get_database_path()}")
    print(f"Email configuration: {config.is_email_configured()}")
    
	