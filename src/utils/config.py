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

    def get_database_path(self) -> str:
        pass

    def is_email_configured(self) -> bool:
            pass

    def string_representation_config(self) -> str:
            pass

    def __str__(self) -> str:
            pass


